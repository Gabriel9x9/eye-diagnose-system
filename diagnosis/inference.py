import argparse
import torch
import torchvision.transforms as T
from PIL import Image
from safetensors.torch import load_model
from torchvision import models
import torch.nn as nn
import cv2
import numpy as np
import os
from django.conf import settings
import logging
import traceback

# 配置日志
logger = logging.getLogger(__name__)

# 定义 EfficientNetB3Pretrained 模型
class EfficientNetB3Pretrained(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.DEFAULT)
        self.edd_head = nn.Sequential(nn.Linear(1000, 8))

    def forward(self, x):
        x = self.model(x)
        return self.edd_head(x)


# 获取模型的函数
def get_model(model_name, device):
    model = None
    if model_name == "EfficientNetB3Pretrained":
        model = EfficientNetB3Pretrained().to(device)
    else:
        raise Exception(f"不支持的模型: {model_name}")
    return model

def diatgnose(img_path):
    # 获取当前文件的父目录（diagnosis app 的目录）
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录
    BASE_DIR = os.path.dirname(APP_DIR)
    # 拼接静态文件的路径
    model_path = os.path.join(BASE_DIR, 'static', 'net.pth')

    parser = argparse.ArgumentParser(description='Inference Script')
    
    parser.add_argument('--model_name', default="EfficientNetB3Pretrained")
    parser.add_argument('--model_path', default=model_path)
    parser.add_argument('--device', default="cuda")
    parser.add_argument('--image_path', default="data/preprocessed_images/0_left.jpg")
    args = parser.parse_args()

    # 加载模型
    model = get_model(args.model_name, args.device)
    model.load_state_dict(torch.load(args.model_path, map_location=torch.device(args.device)))
    model.eval()

    # 图像预处理
    img_transform = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ])

    # 类别映射
    classes = {
        0: "N",
        1: "D",
        2: "G",
        3: "C",
        4: "A",
        5: "H",
        6: "M",
        7: "O"
    }

    # 推理
    img = Image.open(args.image_path)
    img = img_transform(img).unsqueeze(0).to(args.device)
    output = model(img)
    pred = output.argmax(dim=1, keepdim=True).item()

    print("Prediction : ", classes[pred])

class EyeDiseaseClassifier:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"使用设备: {self.device}")
        
        self.model_name = "EfficientNetB3Pretrained"
        model_path = os.path.join(settings.BASE_DIR, 'models', 'eye_disease_model.pth')
        
        # 如果模型文件不存在，使用默认模型
        if not os.path.exists(model_path):
            logger.warning(f"模型文件 {model_path} 不存在，使用预训练模型")
            self.model = get_model(self.model_name, self.device)
        else:
            try:
                self.model = get_model(self.model_name, self.device)
                self.model.load_state_dict(torch.load(model_path, map_location=torch.device(self.device)))
                logger.info(f"成功加载模型: {model_path}")
            except Exception as e:
                logger.error(f"加载模型失败: {str(e)}")
                self.model = get_model(self.model_name, self.device)
                
        self.model.eval()
        self.class_names = ["正常", "糖尿病", "青光眼", "白内障", "AMD", "高血压", "近视", "其他疾病/异常"]
        
        # 图像预处理
        self.transform = T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ])
        
    def preprocess_image(self, image_path):
        """预处理图像"""
        try:
            logger.info(f"预处理图像: {image_path}")
            # 检查文件是否存在
            if not os.path.exists(image_path):
                logger.error(f"图像文件不存在: {image_path}")
                return None
                
            # 使用PIL打开图像
            img = Image.open(image_path).convert('RGB')
            logger.info(f"图像尺寸: {img.size}")
            
            transformed_img = self.transform(img).unsqueeze(0).to(self.device)
            logger.info(f"转换后张量形状: {transformed_img.shape}")
            
            return transformed_img
        except Exception as e:
            logger.error(f"图像预处理失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
    def predict(self, image_path):
        """分析图像并返回诊断结果"""
        try:
            logger.info(f"开始分析图像: {image_path}")
            # 预处理图像
            processed_img = self.preprocess_image(image_path)
            if processed_img is None:
                logger.error("预处理图像失败，无法进行预测")
                return {"diagnosis": "图像处理失败", "error": "无法预处理图像"}
                
            # 确保不计算梯度
            with torch.no_grad():
                # 模型预测
                logger.info("开始模型推理")
                outputs = self.model(processed_img)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
                predicted_class = torch.argmax(probabilities).item()
                confidence = probabilities[predicted_class].item()
                
                logger.info(f"预测类别: {predicted_class}, 诊断结果: {self.class_names[predicted_class]}, 置信度: {confidence:.4f}")
            
            # 返回预测结果和置信度
            result = {
                'diagnosis': self.class_names[predicted_class],
                'confidence': float(confidence),
                'probabilities': {
                    class_name: float(prob) 
                    for class_name, prob in zip(self.class_names, probabilities.cpu().numpy())
                }
            }
            return result
            
        except Exception as e:
            logger.error(f"预测失败: {str(e)}")
            logger.error(traceback.format_exc())
            return {"diagnosis": "诊断失败", "error": str(e)}


# 提供给外部调用的函数
def analyze_image(image_path):
    """
    分析图像并返回诊断结果
    
    Args:
        image_path: 图像文件路径
        
    Returns:
        dict: 包含诊断结果、置信度和所有类别概率
    """
    try:
        logger.info(f"调用 analyze_image 函数，图像路径: {image_path}")
        
        # 处理路径
        if not os.path.exists(image_path):
            logger.warning(f"指定路径不存在，尝试另一种路径构建方式: {image_path}")
            # 尝试从媒体URL转换为绝对路径
            if image_path.startswith('/'):
                # 如果路径是绝对路径，直接使用
                pass
            else:
                # 如果是相对路径，尝试与MEDIA_ROOT结合
                alternate_path = os.path.join(settings.MEDIA_ROOT, image_path)
                logger.info(f"尝试替代路径: {alternate_path}")
                if os.path.exists(alternate_path):
                    image_path = alternate_path
                    logger.info(f"使用替代路径: {image_path}")
        
        # 如果文件仍然不存在，记录错误并返回
        if not os.path.exists(image_path):
            logger.error(f"图像文件不存在，无法分析: {image_path}")
            return {
                'diagnosis': '图像文件不存在',
                'error': f'文件路径无效: {image_path}'
            }
            
        # 模拟结果，真实环境中请删除这段代码
        if not os.path.exists(os.path.join(settings.BASE_DIR, 'models', 'eye_disease_model.pth')):
            logger.warning("未找到模型文件，使用模拟结果")
            import random
            class_names = ["正常", "糖尿病", "青光眼", "白内障", "AMD", "高血压", "近视", "其他疾病/异常"]
            predicted_class = random.randint(0, 7)
            confidence = random.uniform(0.7, 0.95)
            probabilities = [random.uniform(0.01, 0.2) for _ in range(8)]
            probabilities[predicted_class] = confidence
            # 归一化
            sum_probs = sum(probabilities)
            probabilities = [p/sum_probs for p in probabilities]
            
            result = {
                'diagnosis': class_names[predicted_class],
                'confidence': confidence,
                'probabilities': {
                    class_name: prob 
                    for class_name, prob in zip(class_names, probabilities)
                },
                'note': '模拟结果，未找到模型文件'
            }
            return result
            
        # 真实环境下的代码
        logger.info("创建分类器实例")
        classifier = EyeDiseaseClassifier()
        logger.info("开始预测")
        result = classifier.predict(image_path)
        logger.info(f"预测完成: {result}")
        return result
    except Exception as e:
        logger.error(f"分析失败: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            'diagnosis': '诊断失败',
            'error': str(e)
        }
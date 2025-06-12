import os
from django.conf import settings
from datetime import datetime
import cv2
import numpy as np

def get_processed_image_path(patient_id, eye_type, original_filename):
    """
    生成处理后的图像保存路径
    :param patient_id: 患者ID
    :param eye_type: 眼睛类型 ('left' 或 'right')
    :param original_filename: 原始文件名
    :return: 处理后的图像保存路径
    """
    # 构建完整的保存路径，保持原始文件名
    save_path = os.path.join(settings.MEDIA_ROOT, 'process', str(patient_id), original_filename)
    
    # 确保目录存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    return save_path

def get_combined_image_path(patient_id):
    """
    生成拼接图像的保存路径
    :param patient_id: 患者ID
    :return: 拼接图像的保存路径
    """
    save_path = os.path.join(settings.MEDIA_ROOT, 'process', str(patient_id), 'combined.jpg')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    return save_path

def combine_images(left_image_path, right_image_path, output_path):
    """
    将左右眼图像横向拼接
    :param left_image_path: 左眼图像路径
    :param right_image_path: 右眼图像路径
    :param output_path: 输出路径
    :return: 拼接后的图像路径
    """
    # 读取图像
    left_img = cv2.imread(left_image_path)
    right_img = cv2.imread(right_image_path)
    
    if left_img is None or right_img is None:
        raise ValueError("无法读取图像")
    
    # 确保两张图片高度相同
    height = min(left_img.shape[0], right_img.shape[0])
    left_img = cv2.resize(left_img, (left_img.shape[1], height))
    right_img = cv2.resize(right_img, (right_img.shape[1], height))
    
    # 横向拼接
    combined_img = np.hstack((left_img, right_img))
    
    # 保存拼接后的图像
    cv2.imwrite(output_path, combined_img)
    return output_path

def ensure_directory_exists(directory):
    """
    确保目录存在，如果不存在则创建
    :param directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_relative_path(full_path):
    """
    获取相对于MEDIA_ROOT的路径
    :param full_path: 完整路径
    :return: 相对路径
    """
    return os.path.relpath(full_path, settings.MEDIA_ROOT)

def parse_image_filename(filename):
    """
    解析图像文件名，获取患者ID和眼睛类型
    :param filename: 文件名 (格式: id_eye_type.jpg)
    :return: (patient_id, eye_type)
    """
    try:
        # 去掉扩展名
        name = os.path.splitext(filename)[0]
        # 分割文件名
        parts = name.split('_')
        if len(parts) != 2:
            raise ValueError("文件名格式错误")
        
        patient_id = int(parts[0])
        eye_type = parts[1].lower()
        
        if eye_type not in ['left', 'right']:
            raise ValueError("眼睛类型必须是 'left' 或 'right'")
            
        return patient_id, eye_type
    except Exception as e:
        raise ValueError(f"文件名解析错误: {str(e)}") 
import cv2
import numpy as np
from PIL import Image
import os
from django.conf import settings
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim

class ImagePreprocessor:
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    
    def preprocess_image(self, image_path, output_path=None):
        """
        对眼底图像进行预处理
        :param image_path: 输入图像路径
        :param output_path: 输出图像路径，如果为None则覆盖原图
        :return: 处理后的图像路径
        """
        try:
            # 读取图像
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"无法读取图像: {image_path}")
            
            # 进行眼底图像预处理
            processed_img = self._preprocess_fundus_image(img)
            
            # 保存处理后的图像
            if output_path is None:
                output_path = image_path
            
            cv2.imwrite(output_path, processed_img)
            return output_path
            
        except Exception as e:
            raise Exception(f"图像预处理失败: {str(e)}")
    
    def _remove_black_border(self, img):
        """去除黑色边框"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return img
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return img[y:y + h, x:x + w]
    
    def _adaptive_gamma_correction(self, img, base_gamma=1.3):
        """自适应 Gamma 校正"""
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        L, A, B = cv2.split(lab)
        mean_L = np.mean(L)

        gamma = base_gamma - 0.5 * (mean_L / 128)
        gamma = max(0.8, min(1.5, gamma))  # 限制范围

        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(256)]).astype("uint8")
        return cv2.LUT(img, table)
    
    def _preprocess_fundus_image(self, img, clahe_clip=1.3, clahe_grid=(10,10), gamma=1.1, median_ksize=3):
        """
        完整的眼底图像预处理流程
        :param img: 输入图像
        :param clahe_clip: CLAHE 的对比度限制
        :param clahe_grid: CLAHE 的网格大小
        :param gamma: Gamma 校正参数
        :param median_ksize: 中值滤波核大小
        :return: 处理后的图像
        """
        # 1. 去除黑边
        img = self._remove_black_border(img)
        
        # 2. 中值滤波去噪
        img_filtered = cv2.medianBlur(img, median_ksize)
        
        # 3. CLAHE 对比度增强
        lab = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2LAB)
        L, A, B = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=clahe_grid)
        L_clahe = clahe.apply(L)
        lab_clahe = cv2.merge((L_clahe, A, B))
        img_clahe = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)
        
        # 4. 自适应 Gamma 校正
        img_gamma = self._adaptive_gamma_correction(img_clahe)
        
        return img_gamma
    
    def evaluate_images(self, img1, img2):
        """
        计算 PSNR 和 SSIM
        :param img1: 第一张图像
        :param img2: 第二张图像
        :return: (PSNR值, SSIM值)
        """
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        psnr_value = psnr(img1_gray, img2_gray, data_range=img2_gray.max() - img2_gray.min())
        ssim_value = ssim(img1_gray, img2_gray, data_range=img2_gray.max() - img2_gray.min())
        return psnr_value, ssim_value
    
    def validate_image(self, image_path):
        """
        验证图像是否有效
        :param image_path: 图像路径
        :return: bool
        """
        if not os.path.exists(image_path):
            return False
        
        # 检查文件扩展名
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in self.supported_formats:
            return False
        
        # 尝试读取图像
        try:
            img = cv2.imread(image_path)
            return img is not None
        except:
            return False 
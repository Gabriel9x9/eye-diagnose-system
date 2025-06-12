import os, re, shutil
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from openpyxl import load_workbook
from diagnosis import models
from .image_processing import (
    get_combined_image_path,
    combine_images,
    get_relative_path,
    parse_image_filename
)


def handle_uploaded_files(folder_files, patient):
    """
    处理上传的文件，保存到 media/batch_uploads/<patient.id>/ 目录下
    返回保存后的文件夹路径
    """
    # 创建保存目录
    uploads_dir = os.path.join(settings.MEDIA_ROOT, 'batch_uploads', str(patient.id))
    os.makedirs(uploads_dir, exist_ok=True)

    for file in folder_files:
        # 保存文件
        file_path = os.path.join(uploads_dir, file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    return uploads_dir


def process_patient_images(patient, folder_path, doctor=None, batch=None):
    """
    处理患者的图像文件，创建诊断记录
    返回创建的记录，以便进行后续处理
    """
    from .models import PatientImage, Record
    from .image_processing import (
        ImagePreprocessor,
        get_processed_image_path,
        get_combined_image_path,
        combine_images,
        get_relative_path
    )

    # 查找文件夹中的所有图像
    left_image_path = None
    right_image_path = None

    preprocessor = ImagePreprocessor()

    # 处理文件夹中的图像文件
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(folder_path, filename)

            # 分析文件名，确定是左眼还是右眼
            if 'left' in filename.lower():
                eye_type = 'left'
            elif 'right' in filename.lower():
                eye_type = 'right'
            else:
                continue  # 跳过无法识别眼睛类型的文件

            # 验证图像
            if not preprocessor.validate_image(file_path):
                continue

            # 创建PatientImage
            patient_image = PatientImage.objects.create(
                patient=patient,
                image=os.path.join('batch_uploads', str(patient.id), filename)
            )

            # 预处理图像
            processed_image_path = get_processed_image_path(patient.id, eye_type, filename)
            preprocessor.preprocess_image(file_path, processed_image_path)

            if eye_type == 'left':
                left_image_path = processed_image_path
            elif eye_type == 'right':
                right_image_path = processed_image_path

    # 合并图像（如果有左右眼图像）
    final_image = None
    if left_image_path and right_image_path:
        combined_image_path = get_combined_image_path(patient.id)
        combine_images(left_image_path, right_image_path, combined_image_path)
        final_image = get_relative_path(combined_image_path)
    elif left_image_path:
        final_image = get_relative_path(left_image_path)
    elif right_image_path:
        final_image = get_relative_path(right_image_path)

    # 创建诊断记录
    record = None
    if final_image:
        # 将 Windows 反斜杠替换为正斜杠（若存在）
        final_image = final_image.replace('\\', '/')
        record = Record.objects.create(
            patient=patient,
            processed_image=final_image,
            result="待诊断",
            advice="图像已预处理完成，等待医生诊断",
            diagnosis_time=timezone.now(),
            doctor=doctor,
            batch=batch
        )

    return record  # 返回创建的记录对象



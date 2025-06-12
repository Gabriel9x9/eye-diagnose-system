# diagnosis/management/commands/create_test_data.py

import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Doctor
from diagnosis.models import Patient, Record, PatientImage

class Command(BaseCommand):
    help = "Create test data for Doctor, Patient, Record, and PatientImage models"

    def handle(self, *args, **options):
        # 1. 创建 5 个医生数据（Doctor）
        doctors = []
        for i in range(1, 6):
            username = f"doctor{i}"
            if not Doctor.objects.filter(username=username).exists():
                doctor = Doctor.objects.create_user(
                    username=username,
                    name=f"Doctor {i}",
                    password="test123",
                    role="doctor"
                )
                self.stdout.write(f"Created doctor: {username}")
            else:
                doctor = Doctor.objects.get(username=username)
                self.stdout.write(f"Doctor {username} already exists")
            doctors.append(doctor)

        # 2. 创建 20 个患者数据（Patient）
        patients = []
        for i in range(1, 21):
            patient = Patient.objects.create(
                name=f"Patient {i}",
                age=random.randint(20, 80),
                gender=random.choice(["Male", "Female"]),
                # 注意：这里 images 字段要求提供文件路径，测试时可以使用默认或占位字符串
                images="patient_images/sample.jpg"
            )
            patients.append(patient)
            self.stdout.write(f"Created patient: {patient.name}")

        # 3. 为每个患者创建一条诊断记录（Record），随机指定一个医生
        for patient in patients:
            doctor = random.choice(doctors)
            Record.objects.create(
                patient=patient,
                doctor=doctor,
                processed_image="process/processed_sample.jpg",  # 同样为文件字段提供占位字符串
                result="Test Result",
                advice="Test Advice",
                diagnosis_time=timezone.now()
            )
            self.stdout.write(f"Created record for patient: {patient.name}")

        # 4. 为每个患者再创建一条患者影像数据（PatientImage）
        for patient in patients:
            PatientImage.objects.create(
                patient=patient,
                image="patient_images/sample.jpg"  # 占位图片路径
            )
            self.stdout.write(f"Created patient image for: {patient.name}")

        self.stdout.write(self.style.SUCCESS("Test data creation complete."))

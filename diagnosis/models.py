from django.db import models
from accounts.models import Doctor  # 引用 accounts 下的 Doctor 模型

class Patient(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    # id 字段 Django 会自动创建为自增主键
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="患者姓名")
    age = models.PositiveIntegerField(verbose_name="年龄")
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, verbose_name="性别")
    images=models.FileField(verbose_name="医疗影像")

    def __str__(self):
        return self.name if self.name else "Unknown"

class Batch(models.Model):
    """批量诊断批次模型"""
    batch_name = models.CharField(max_length=100, verbose_name="批次名称")
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    total_patients = models.PositiveIntegerField(default=0, verbose_name="患者总数")
    processed_patients = models.PositiveIntegerField(default=0, verbose_name="已处理患者数")
    status = models.CharField(max_length=20, default="处理中", verbose_name="状态")
    doctor = models.ForeignKey(Doctor, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="处理医生")

    def __str__(self):
        return f"{self.batch_name} ({self.upload_time.strftime('%Y-%m-%d %H:%M')})"

class Record(models.Model):
    # 外键关联到 Patient 模型，删除患者时其诊断记录级联删除
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='records', verbose_name="患者")
    # 外键关联到 Doctor 模型，医生删除时将该字段置为NULL，故需设置 null=True, blank=True
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='records', verbose_name="医生")
    # 外键关联到 Batch 模型，批次删除时将该字段置为NULL
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name='records', verbose_name="批次")
    processed_image = models.FileField(max_length=255, blank=True, null=True, verbose_name="处理后影像地址",upload_to='process/')
    result = models.CharField(max_length=255, verbose_name="诊断结果")
    advice = models.TextField(blank=True, null=True, verbose_name="诊断建议")
    diagnosis_time = models.DateTimeField(verbose_name="诊断时间")

    def __str__(self):
        return f"Record {self.pk} for {self.patient}"


class PatientImage(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_images')
    image = models.ImageField(upload_to='patient_images/')
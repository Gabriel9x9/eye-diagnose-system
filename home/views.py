from django.shortcuts import render
from django.utils import timezone
from diagnosis.models import Record, Patient
from django.db.models import Count  # 全局导入

import datetime
import json


def index(request):
    # 1. 统计 Record 中各 result 数量（注意和前端选项保持一致）
    result_labels = ["正常", "糖尿病视网膜病变", "青光眼", "白内障", "年龄相关性黄斑变性", "高血压视网膜病变", "近视", "其他疾病/异常"]
    # 初始化计数字典
    record_data = {label: 0 for label in result_labels}
    records = Record.objects.values('result').annotate(count=Count('result'))
    for item in records:
        result = item['result']
        if result in record_data:
            record_data[result] = item['count']
    disease_labels = list(record_data.keys())
    disease_data = list(record_data.values())

    # 2. 统计诊断趋势（最近7天）
    today = timezone.now().date()
    trend_data = []
    trend_labels = []
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        count = Record.objects.filter(diagnosis_time__date=date).count()
        trend_data.append(count)
        trend_labels.append(date.strftime('%m-%d'))

    # 3. 其他统计
    # 总诊断数：只统计已完成诊断的记录
    total_diagnoses = Record.objects.exclude(result='待诊断').count()

    # 医生自己的诊断数
    doctor_diagnoses = 0
    if request.user.is_authenticated:
        doctor_diagnoses = Record.objects.filter(doctor=request.user).exclude(result='待诊断').count()

    # 待诊断数：当前所有待诊断的记录
    pending_diagnoses = Record.objects.filter(result='待诊断').count()

    # 今日诊断数：只统计今天完成的诊断
    today_diagnoses = Record.objects.exclude(result='待诊断').filter(
        diagnosis_time__date=today
    ).count()

    # 总患者数
    total_patients = Patient.objects.count()

    # 今日登录次数
    from django.contrib.admin.models import LogEntry
    today_logins = LogEntry.objects.filter(
        action_time__date=today
    ).count()

    # 4. 年龄性别分布数据
    age_ranges = ['0-10岁', '10-20岁', '20-30岁', '30-40岁', '40-50岁', '50-60岁', '60岁以上']
    male_data = []
    female_data = []
    
    for i, age_range in enumerate(age_ranges):
        # 解析年龄范围
        if i < len(age_ranges) - 1:  # 不是最后一个范围
            min_age = i * 10
            max_age = (i + 1) * 10
            males = Patient.objects.filter(age__gte=min_age, age__lt=max_age, gender='Male').count()
            females = Patient.objects.filter(age__gte=min_age, age__lt=max_age, gender='Female').count()
        else:  # 最后一个范围 "60岁以上"
            min_age = 60
            males = Patient.objects.filter(age__gte=min_age, gender='Male').count()
            females = Patient.objects.filter(age__gte=min_age, gender='Female').count()
        
        male_data.append(males)
        female_data.append(females)

    context = {
        'total_diagnoses': total_diagnoses,
        'doctor_diagnoses': doctor_diagnoses,
        'pending_diagnoses': pending_diagnoses,
        'today_diagnoses': today_diagnoses,
        'total_patients': total_patients,
        'today_logins': today_logins,
        'disease_labels': json.dumps(disease_labels),
        'disease_data': json.dumps(disease_data),
        'trend_labels': json.dumps(trend_labels),
        'trend_data': json.dumps(trend_data),
        'age_ranges': json.dumps(age_ranges),
        'male_data': json.dumps(male_data),
        'female_data': json.dumps(female_data),
    }
    return render(request, 'index.html', context)

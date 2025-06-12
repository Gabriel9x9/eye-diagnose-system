from django.shortcuts import render
from django.core.paginator import Paginator
from diagnosis.models import Record, Patient
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse

from accounts.models import Doctor  # 确保正确导入 Doctor
from records.models import RecordForm  # 需要新建一个表单用于修改 Record

# 修改记录
from accounts.models import Doctor

def modify_record(request, record_id):
    record = get_object_or_404(Record, id=record_id)  # 获取记录
    doctors = Doctor.objects.filter(role='doctor')  # 获取所有医生

    if request.method == "POST":
        try:
            # 获取表单数据
            patient_name = request.POST.get('patient_name')
            doctor_id = request.POST.get('doctor')
            result = request.POST.get('result')
            advice = request.POST.get('advice')
            
            # 更新患者信息
            if patient_name and patient_name != record.patient.name:
                record.patient.name = patient_name
                record.patient.save()
            
            # 更新记录信息
            if doctor_id:
                record.doctor = get_object_or_404(Doctor, id=doctor_id)
            if result:
                record.result = result
            if advice:
                record.advice = advice
            record.save()
            
            messages.success(request, "记录已成功删除！")
            return redirect("records")
        except Exception as e:
            messages.error(request, f"删除失败：{str(e)}")


    return render(request, "modify_record.html", {
        "record": record,
        "doctors": doctors
    })

# 删除记录
def delete_record(request, record_id):
    record = get_object_or_404(Record, id=record_id)
    try:
        # 获取关联的患者
        patient = record.patient
        
        # 删除记录
        record.delete()
        
        # 检查患者是否还有其他记录，如果没有则删除患者
        if not Record.objects.filter(patient=patient).exists():
            patient.delete()
            
        messages.success(request, "记录已成功删除！")
    except Exception as e:
        messages.error(request, f"删除失败：{str(e)}")
        
    return redirect("records")


def records(request):
    # 1. 获取查询参数
    name = request.GET.get('name', '').strip()
    age = request.GET.get('age', '').strip()
    gender = request.GET.get('gender', '').strip()
    diseases = request.GET.getlist('disease')

    # 2. 获取所有记录，并预加载关联的 Patient 和 Doctor，同时加上排序以确保分页结果一致
    qs = Record.objects.select_related('patient', 'doctor').all().order_by('-diagnosis_time')

    # 3. 根据姓名、年龄、性别过滤 Patient 字段
    if name:
        qs = qs.filter(patient__name__icontains=name)
    if age:
        qs = qs.filter(patient__age=age)
    if gender == '男':
        qs = qs.filter(patient__gender='Male')
    elif gender == '女':
        qs = qs.filter(patient__gender='Female')

    # 4. 根据病种过滤，使用映射关系把前端的数字转换为文本
    diseases_map = {
        '1': '正常',
        '2': '糖尿病',
        '3': '青光眼',
        '4': '白内障',
        '5': 'AMD',
        '6': '高血压',
        '7': '近视',
        '8': '其他疾病/异常',
    }
    selected_disease = [diseases_map[d] for d in diseases if d in diseases_map]
    if selected_disease:
        qs = qs.filter(result__in=selected_disease)

    # 5. 分页，每页显示 10 条记录
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 复制 GET 参数并移除 page 参数
    get_params = request.GET.copy()
    get_params.pop('page', None)  # 删除所有 page 参数

    context = {
        'records': page_obj,  # 用于遍历显示
        'page_obj': page_obj, # 用于分页
        'get_params': get_params.urlencode(),
    }



    return render(request, 'records.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Count, F
from accounts.models import Doctor

def login(request):
    if request.method == 'GET':
        return render(request, "login.html", {"username": ""})
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        auth_login(request, user)
        messages.success(request, f"欢迎，{user.get_full_name() or user.username}！")
        return redirect('home')
    else:
        messages.error(request, "用户名或密码错误，请重试！")
        return render(request, "login.html", {"username": username})

def logout(request):
    auth_logout(request)
    return redirect('login')

def accounts(request):
    # 仅管理员可访问
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, "只有管理员才能访问该页面！")
        return redirect('login')

    doctor_name = request.GET.get('doctor_name', '').strip()
    username = request.GET.get('username', '').strip()
    role = request.GET.get('role', '').strip()

    # 加上 order_by 防止分页警告
    qs = Doctor.objects.all().order_by('id').annotate(
        diagnosis_count=Count('records', distinct=True),
        doctor_name=F('name')
    )
    if doctor_name:
        qs = qs.filter(name__icontains=doctor_name)
    if username:
        qs = qs.filter(username__icontains=username)
    if role:
        qs = qs.filter(role=role)

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    get_params = request.GET.copy()
    get_params.pop('page', None)

    return render(request, "accounts.html", {
        'accounts': page_obj,
        'page_obj': page_obj,
        'params': get_params
    })

def modify_account(request, account_id):
    # 仅管理员可操作
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, "只有管理员才能进行操作！")
        return redirect('accounts')
    account = get_object_or_404(Doctor, id=account_id)
    if request.method == "POST":
        name = request.POST.get('name')
        username = request.POST.get('username')
        role = request.POST.get('role')
        if not name or not username:
            return JsonResponse({'success': False, 'message': '姓名和用户名不能为空'})
        account.name = name
        account.username = username
        if role in ['admin', 'doctor']:
            account.role = role
        try:
            account.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    # GET 请求返回用于弹窗加载的表单部分
    return render(request, "modify_account.html", {"account": account})

def delete_account(request, account_id):
    # 仅管理员可删除
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, "只有管理员才能进行操作！")
        return redirect('accounts')
    doctor = get_object_or_404(Doctor, pk=account_id)
    if doctor.role == 'admin':
        messages.error(request, "不能删除管理员账号！")
        return redirect('accounts')
    doctor.delete()
    messages.success(request, "医生账号已删除！")
    return redirect('accounts')


def register(request):
    pass
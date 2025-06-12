"""
URL configuration for Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from django.views.static import serve
from django.conf import settings

from accounts import views as accounts_views
from diagnosis import views as diagnosis_views
from home import views as home_views
from records import views as records_views
from ai_chat import views as ai_chat_views

from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT},name='media'),

    # 网页路径
    path('register/', accounts_views.register,name='register'),
    path('',accounts_views.login,name='login'),
    path('index/',home_views.index,name='home'),
    path('personal/',diagnosis_views.personal_diagnose,name="personal_diagnose"),
    path('batch-diagnose/',diagnosis_views.batch_diagnose,name="batch_diagnose"),
    path('records/',records_views.records,name='records'),
    path('accounts/',accounts_views.accounts,name='accounts'),

    # 诊断页面按钮
    path('per-info/',diagnosis_views.personal_info,name='personal_info'),
    path('batch-info/',diagnosis_views.batch_info,name='batch_info'),


    # 记录页面具体函数
    path('records/<int:record_id>/modify/',records_views.modify_record,name='modify_record'),
    path('records/<int:record_id>/delete/',records_views.modify_record,name='delete_record'),

    # 账号管理具体函数
    path('accounts/<int:account_id>/modify/', accounts_views.modify_account, name='modify_account'),
    path('accounts/<int:account_id>/delete/', accounts_views.delete_account, name='delete_account'),


    path('logout',accounts_views.logout,name='logout'),

    path("modify_record/<int:record_id>/", records_views.modify_record, name="modify_record"),
    path("delete_record/<int:record_id>/", records_views.delete_record, name="delete_record"),

    # ai辅助
    path("gemini/gemini_pro/",diagnosis_views.gemini,name="gemini"),

    # AI聊天功能
    path("api/ai-chat/", ai_chat_views.ai_chat, name="ai_chat"),

]

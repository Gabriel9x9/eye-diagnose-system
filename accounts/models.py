from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# 自定义管理器
class DoctorManager(BaseUserManager):
    def create_user(self, username, name, password=None, **extra_fields):  # 添加 name 参数
        if not username:
            raise ValueError("用户名必须填写")
        if not name:  # 如果 name 是必填项
            raise ValueError("姓名必须填写")
        user = self.model(
            username=username,
            name=name,  # 传递 name 字段
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name, password=None, **extra_fields):  # 同样添加 name
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, name, password, **extra_fields)

# Doctor 用户模型
class Doctor(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255, verbose_name="姓名",blank=True)  # 新增姓名字段
    role = models.CharField(max_length=50, choices=[('admin', '管理员'), ('doctor', '医生')])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # 如果需要后台管理权限

    objects = DoctorManager()  # 绑定自定义用户管理器

    USERNAME_FIELD = 'username'  # 认证时使用的字段

    def get_full_name(self):
        return self.name  # 直接返回 name 字段

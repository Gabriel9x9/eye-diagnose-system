
from django import forms
from django.forms.widgets import ClearableFileInput


from openpyxl import load_workbook

####################
# 1. 多文件上传表单
####################
class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

class MultiFileField(forms.FileField):
    widget = MultiFileInput

    def to_python(self, data):
        if not data:
            return []
        if not isinstance(data, list):
            return [data]
        return data

from .models import Patient

class UpModelForm(forms.ModelForm):
    """单人诊断上传信息表单"""
    images = MultiFileField(required=False, label="上传图片")
    class Meta:
        model = Patient
        exclude = ('images',)

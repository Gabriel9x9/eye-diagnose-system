from django.db import models

# Create your models here.

from django import forms
from diagnosis.models import Record

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ["patient", "doctor", "result", "advice"]
        widgets = {
            "result": forms.TextInput(attrs={"class": "form-control"}),
            "advice": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


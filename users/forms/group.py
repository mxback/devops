from django.contrib.auth.models import Group
from .base import BootStrapModelForm
from django import forms


class GroupModelForm(BootStrapModelForm):
    name = forms.CharField(label='角色名称')
    class Meta:
        model = Group
        fields = ['name']
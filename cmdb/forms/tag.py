from users.forms.base import BootStrapModelForm
from django.forms import forms
from cmdb.models import Type, Tag


class TypeModelForm(BootStrapModelForm):
    class Meta:
        model = Type
        fields = ['name', 'name_cn']


class TagModelForm(BootStrapModelForm):
    class Meta:
        model = Tag
        fields = ['type', 'name', 'name_cn']

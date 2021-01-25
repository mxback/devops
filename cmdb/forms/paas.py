from users.forms.base import BootStrapModelForm
from django.forms import forms
from cmdb.models import Paas


class PaasModelForm(BootStrapModelForm):

    class Meta:
        model = Paas
        fields = ['title']


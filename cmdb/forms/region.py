from users.forms.base import BootStrapModelForm
from django.forms import forms
from cmdb.models import Region


class RegionModelForm(BootStrapModelForm):
    class Meta:
        model = Region
        fields = ['paas', 'name', 'region', 'endpoint']

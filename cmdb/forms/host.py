from users.forms.base import BootStrapModelForm
from cmdb.models import Host, HostUsername
from django import forms

class HostModelForm(BootStrapModelForm):
    class Meta:
        model = Host
        fields = ['paas', 'project_group', 'instance_name', 'cpu', 'memory', 'status', 'private_ip', 'os_type',
                  'os_name', 'instance_charge_type', 'tags']


class HostUsernameModelForm(BootStrapModelForm):
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
    class Meta:
        model = HostUsername
        fields = '__all__'

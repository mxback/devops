from users.forms.base import BootStrapModelForm
from django.forms import forms
from cmdb.models import Kubernetes


class K8SModelForm(BootStrapModelForm):
    class Meta:
        model = Kubernetes
        fields = "__all__"

from users.forms.base import BootStrapModelForm
from cmdb.models import ProjectGroup


class ProjectGroupModelForm(BootStrapModelForm):
    class Meta:
        model = ProjectGroup
        fields = ['title', 'name_cn']

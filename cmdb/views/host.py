# ? 权限
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# ? 视图
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, TemplateView
# ? model
from cmdb.models import Host, HostUsername, ProjectGroup
from django.db.models import Q
# ? forms
from cmdb.forms.host import HostModelForm, HostUsernameModelForm
# ? 反向生产URL
from users.tools.urls import memory_reverse


# ? 功能
from system.utils import SearchGroup, SearchOption

# ?
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse, JsonResponse

# ?
from cmdb.util import AutoUpdateHost

class HostListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    主机列表
    """
    template_name = 'cmdb/host_list.html'
    model = Host  # object_list = Group.object.get(pk=pk)
    ordering = 'id'
    paginate_by = 30
    permission_required = 'cmdb.view_host'
    search_group = SearchGroup(Host)
    search_group.search_group = [
        # SearchOption('gender'),
        SearchOption('paas'),
        SearchOption('project_group'),
        SearchOption('status'),
        SearchOption('tags'),
    ]

    def get_keyword(self):
        self.keyword = self.request.GET.get('keyword')
        return self.keyword

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.get_keyword()
        user = self.request.user
        host_set = set()
        for item in user.projectgroup_set.all():
            for i in item.host_set.all():
                host_set.add(i.id)
        filter_dict = self.search_group.get_search_group_condition(self.request)
        queryset = queryset.filter(id__in=host_set).filter(**filter_dict)
        # queryset = queryset.filter(**filter_dict)
        if keyword:
            queryset = queryset.filter(Q(instance_name__icontains=self.keyword) |
                                       Q(os_name__icontains=self.keyword) |
                                       Q(tags__name__icontains=self.keyword) |
                                       Q(tags__name_cn__icontains=self.keyword))
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        auto_host = AutoUpdateHost()
        auto_host.update_hosts
        context = super().get_context_data(**kwargs)
        context['keyword'] = self.keyword
        context['search_group_row_list'] = self.search_group.get_search_group_row_list(self.request, *args, **kwargs)
        return context


class HostAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    添加主机
    """
    template_name = "base/add.html"
    model = Host
    form_class = HostModelForm
    permission_required = 'auth.add_host'

    def get_success_url(self):
        return reverse('cmdb:host_list')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:host_list')
        return context


class HostDelateView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    删除主机
    """
    template_name = 'base/delete.html'
    model = Host
    permission_required = 'auth.delete_host'

    def get_success_url(self):
        return reverse('cmdb:host_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:host_list')
        return context


class HostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    更新主机
    """
    template_name = "base/change.html"
    model = Host  # object=User.objects.get(pk=pk)
    form_class = HostModelForm
    permission_required = 'auth.change_host'

    def get_success_url(self):
        return reverse('cmdb:host_list')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:host_list')
        return context


class HostUsernameListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    主机列表
    """
    template_name = 'cmdb/host_username_list.html'
    model = HostUsername  # object_list = Group.object.get(pk=pk)
    ordering = 'id'
    paginate_by = 30
    permission_required = 'cmdb.view_host_username'

    def get_keyword(self):
        self.keyword = self.request.GET.get('keyword')
        return self.keyword

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.get_keyword()
        if keyword:
            queryset = queryset.filter(Q(host__instance_name__icontains=self.keyword) |
                                       Q(host__private_ip__icontains=self.keyword) |
                                       Q(host__public_ip__icontains=self.keyword))
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context


class HostUsernameAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    添加主机
    """
    template_name = "base/add.html"
    model = HostUsername
    form_class = HostUsernameModelForm
    permission_required = 'auth.add_host_username'

    def get_success_url(self):
        return reverse('cmdb:host_username_list')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:host_username_list')
        return context


class HostUsernameDelateView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    删除主机
    """
    template_name = 'base/delete.html'
    model = HostUsername
    permission_required = 'auth.delete_host_username'

    def get_success_url(self):
        return reverse('cmdb:host_username_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:host_username_list')
        return context


class HostUsernameUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    更新主机
    """
    template_name = "base/change.html"
    model = HostUsername  # object=User.objects.get(pk=pk)
    form_class = HostUsernameModelForm
    permission_required = 'auth.change_host_username'

    def get_success_url(self):
        return reverse('cmdb:host_username_list')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:host_username_list')
        return context

class HostUsernameForPasswordView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'cmdb/view_host_password.html'
    permission_required = 'auth.view_host_password'

    def get_context_data(self, **kwargs):
        user_obj = HostUsername.objects.get(id=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context['name'] = user_obj.host.instance_name
        context['password'] = user_obj.password
        return context

@require_GET
@login_required
@permission_required(perm='cmdb.view_host')
def get_host_list(request):
    """
    获取主机列表接口，返回json
    :return:
    """
    hosts = Host.objects.all()
    tag = request.GET.get('tag',"")
    if tag:
        hosts = Host.objects.filter(tags__name=tag)
    host_list = []
    for host in hosts:
        host_list.append({'id': str(host.id), 'instance_name': host.instance_name, 'ip':host.private_ip})
    return JsonResponse({'code': 0, 'msg': '主机获取成功！', 'data': host_list})
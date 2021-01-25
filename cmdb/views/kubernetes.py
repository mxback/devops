# ? 权限
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# ? 视图
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, TemplateView
# ? model
from cmdb.models import Kubernetes
from django.db.models import Q
# ? forms
from cmdb.forms.kubernetes import K8SModelForm
# ? 反向生产URL
from users.tools.urls import memory_reverse

# ? 功能
from system.utils import SearchGroup, SearchOption

class K8SListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    主机列表
    """
    template_name = 'cmdb/kubernetes.html'
    model = Kubernetes  # object_list = Group.object.get(pk=pk)
    ordering = 'id'
    paginate_by = 30
    permission_required = 'cmdb.view_Kubernetes'
    search_group = SearchGroup(Kubernetes)
    search_group.search_group = [
        # SearchOption('gender'),
        SearchOption('paas'),
        SearchOption('project_group'),
        SearchOption('kind'),
    ]

    def get_keyword(self):
        self.keyword = self.request.GET.get('keyword')
        return self.keyword

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.get_keyword()
        filter_dict = self.search_group.get_search_group_condition(self.request)
        queryset = queryset.filter(**filter_dict)
        if keyword:
            queryset = queryset.filter(Q(name__icontains=self.keyword))
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['keyword'] = self.keyword
        context['search_group_row_list'] = self.search_group.get_search_group_row_list(self.request, *args, **kwargs)
        return context


class K8SAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    添加主机
    """
    template_name = "base/add.html"
    model = Kubernetes
    form_class = K8SModelForm
    permission_required = 'auth.add_Kubernetes'

    def get_success_url(self):
        return reverse('cmdb:k8s_list')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:k8s_list')
        return context


class K8SDelateView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    删除主机
    """
    template_name = 'base/delete.html'
    model = Kubernetes
    permission_required = 'auth.delete_Kubernetes'

    def get_success_url(self):
        return reverse('cmdb:k8s_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:k8s_list')
        return context


class K8SUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    更新主机
    """
    template_name = "base/change.html"
    model = Kubernetes  # object=User.objects.get(pk=pk)
    form_class = K8SModelForm
    permission_required = 'auth.change_Kubernetes'

    def get_success_url(self):
        return reverse('cmdb:k8s_list')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:k8s_list')
        return context

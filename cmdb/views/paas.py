#? 权限
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
#? 视图
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, View
#? model
from cmdb.models import Paas
from django.db.models import Q
#? forms
from cmdb.forms.paas import PaasModelForm
#? 反向生产URL
from users.tools.urls import memory_reverse

class PaasListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    组列表
    """
    template_name = 'cmdb/pass_list.html'
    model = Paas  # object_list = Group.object.get(pk=pk)
    ordering = 'id'
    paginate_by = 10
    permission_required = 'cmdb.view_paas'

    def get_keyword(self):
        self.keyword = self.request.GET.get('keyword')
        return self.keyword

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.get_keyword()
        if keyword:
            queryset = queryset.filter(Q(title__icontains=self.keyword))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context

class PaasAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    添加角色
    """
    template_name = "base/add.html"
    model = Paas
    form_class = PaasModelForm
    permission_required = 'auth.add_paas'

    def get_success_url(self):
        return reverse('cmdb:paas_list')

class PaasDelateView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    删除角色
    """
    template_name = 'base/delete.html'
    model = Paas
    permission_required = 'auth.delete_paas'

    def get_success_url(self):
        return reverse('cmdb:paas_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:paas_list')
        return context

class PaasUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    更新角色
    """
    template_name = "base/change.html"
    model = Paas   # object=User.objects.get(pk=pk)
    form_class = PaasModelForm
    permission_required = 'auth.change_paas'

    def get_success_url(self):
        return reverse('cmdb:paas_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:paas_list')
        return context

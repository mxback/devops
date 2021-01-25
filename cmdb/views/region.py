# ? 权限
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# ? 视图
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
# ? model
from cmdb.models import Region
from django.db.models import Q
# ? forms
from cmdb.forms.region import RegionModelForm
# ? 反向生产URL
from users.tools.urls import memory_reverse


class RegionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    组列表
    """
    template_name = 'cmdb/region_list.html'
    model = Region  # object_list = Group.object.get(pk=pk)
    ordering = 'id'
    paginate_by = 10
    permission_required = 'cmdb.view_region'

    def get_keyword(self):
        self.keyword = self.request.GET.get('keyword')
        return self.keyword

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.get_keyword()
        if keyword:
            queryset = queryset.filter(Q(paas__title__icontains=self.keyword) |
                                       Q(name__icontains=self.keyword) |
                                       Q(region__icontains=self.keyword) |
                                       Q(endpoint__icontains=self.keyword))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context


class RegionAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    添加角色
    """
    template_name = "base/add.html"
    model = Region
    form_class = RegionModelForm
    permission_required = 'auth.add_region'

    def get_success_url(self):
        return reverse('cmdb:region_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:region_list')
        return context


class RegionDelateView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    删除角色
    """
    template_name = 'base/delete.html'
    model = Region
    permission_required = 'auth.delete_region'

    def get_success_url(self):
        return reverse('cmdb:region_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:region_list')
        return context


class RegionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    更新角色
    """
    template_name = "base/change.html"
    model = Region  # object=User.objects.get(pk=pk)
    form_class = RegionModelForm
    permission_required = 'auth.change_region'

    def get_success_url(self):
        return reverse('cmdb:region_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:region_list')
        return context


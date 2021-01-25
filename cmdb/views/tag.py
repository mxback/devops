# ? 权限
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# ? 视图
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
# ? model
from cmdb.models import Type, Tag
from django.db.models import Q
# ? forms
from cmdb.forms.tag import TagModelForm, TypeModelForm
# ? 反向生产URL
from users.tools.urls import memory_reverse


class TypeListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    组列表
    """
    template_name = 'cmdb/type_list.html'
    model = Type  # object_list = Group.object.get(pk=pk)
    ordering = 'id'
    paginate_by = 10
    permission_required = 'cmdb.view_type'

    def get_keyword(self):
        self.keyword = self.request.GET.get('keyword')
        return self.keyword

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.get_keyword()
        if keyword:
            queryset = queryset.filter(Q(name__icontains=self.keyword) |
                                       Q(name_cn__icontains=self.keyword))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context


class TypeAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    添加角色
    """
    template_name = "base/add.html"
    model = Type
    form_class = TypeModelForm
    permission_required = 'auth.add_type'

    def get_success_url(self):
        return reverse('cmdb:type_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:tag_list')
        return context



class TypeDelateView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    删除角色
    """
    template_name = 'base/delete.html'
    model = Type
    permission_required = 'auth.delete_type'

    def get_success_url(self):
        return reverse('cmdb:type_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:type_list')
        return context


class TypeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    更新角色
    """
    template_name = "base/change.html"
    model = Type  # object=User.objects.get(pk=pk)
    form_class = TypeModelForm
    permission_required = 'auth.change_type'

    def get_success_url(self):
        if "reset" in self.request.POST:
            return reverse('cmdb:type_list')
        return reverse('cmdb:type_list')


class TagListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    组列表
    """
    template_name = 'cmdb/tag_list.html'
    model = Tag  # object_list = Group.object.get(pk=pk)
    ordering = 'id'
    paginate_by = 10
    permission_required = 'cmdb.view_tag'

    def get_keyword(self):
        self.keyword = self.request.GET.get('keyword')
        return self.keyword

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.get_keyword()
        if keyword:
            queryset = queryset.filter(Q(type__name_cn__icontains=self.keyword) |
                                       Q(name_cn__icontains=self.keyword) |
                                       Q(name__icontains=self.keyword))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context


class TagAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    添加角色
    """
    template_name = "base/add.html"
    model = Tag
    form_class = TagModelForm
    permission_required = 'auth.add_tag'

    def get_success_url(self):
        return reverse('cmdb:tag_list')


class TagDelateView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    删除角色
    """
    template_name = 'base/delete.html'
    model = Tag
    permission_required = 'auth.delete_tag'

    def get_success_url(self):
        return reverse('cmdb:tag_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:tag_list')
        return context


class TagUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    更新角色
    """
    template_name = "base/change.html"
    model = Tag  # object=User.objects.get(pk=pk)
    form_class = TagModelForm
    permission_required = 'auth.change_tag'

    def get_success_url(self):
        return reverse('cmdb:tag_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:tag_list')
        return context


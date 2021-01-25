# ? 权限
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
# ? 视图
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, View
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
# ? model
from cmdb.models import ProjectGroup
from django.db.models import Q
# ? forms
from cmdb.forms.projectgroup import ProjectGroupModelForm
# ? 反向生产URL
from users.tools.urls import memory_reverse


# ? 用户
from django.contrib.auth import get_user_model
Users = get_user_model()

class ProjectGroupListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    组列表
    """
    template_name = 'cmdb/project_group_list.html'
    model = ProjectGroup  # object_list = Group.object.get(pk=pk)
    ordering = 'id'
    paginate_by = 10
    permission_required = 'cmdb.view_project_group'

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


class ProjectGroupAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    添加角色
    """
    template_name = "base/add.html"
    model = ProjectGroup
    form_class = ProjectGroupModelForm
    permission_required = 'auth.add_project_group'

    def get_success_url(self):
        return reverse('cmdb:project_group_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:project_group_list')
        return context


class ProjectGroupDelateView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    删除角色
    """
    template_name = 'base/delete.html'
    model = ProjectGroup
    permission_required = 'auth.delete_project_group'

    def get_success_url(self):
        return reverse('cmdb:project_group_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:project_group_list')
        return context


class ProjectGroupUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    更新角色
    """
    template_name = "base/change.html"
    model = ProjectGroup  # object=User.objects.get(pk=pk)
    form_class = ProjectGroupModelForm
    permission_required = 'auth.change_project_group'

    def get_success_url(self):
        return reverse('cmdb:project_group_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'cmdb:project_group_list')
        return context


class AddUserToProjectGroupView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    批量将用户添加到组——原生View版本
    """
    permission_required = 'auth.change_project_group'

    def get(self, request, pk):
        group = get_object_or_404(ProjectGroup, pk=pk)
        users = Users.objects.all()
        context = {'group': group, 'users': users}
        return render(request, 'cmdb/project_group_add_user.html', context=context)

    def post(self, request, pk):
        uids = request.POST.getlist('users')
        group = get_object_or_404(ProjectGroup, pk=pk)
        if uids:
            users = Users.objects.filter(id__in=uids)
            group.userinfo.set(users)
        else:
            group.userinfo.clear()
        messages.success(request, '{}项目组添加用户或移除用户成功！'.format(group))
        if '_addanother' in request.POST:
            return HttpResponseRedirect(reverse('cmdb:project_group_add_user', kwargs={'pk': pk}))
        return HttpResponseRedirect(reverse('cmdb:project_group_list'))

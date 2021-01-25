from django.contrib.auth.models import Group, Permission
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, View
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from users.forms.group import GroupModelForm
from django.contrib import messages

#? 权限
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required

from django.contrib.auth import get_user_model
Users = get_user_model()

# ? 反向生产URL
from users.tools.urls import memory_reverse

class GroupListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    组列表
    """
    template_name = 'users/group_list.html'
    model = Group   # object_list = Group.object.get(pk=pk)
    ordering = 'id'
    paginate_by = 10
    permission_required = 'auth.view_group'

    def get_keyword(self):
        self.keyword = self.request.GET.get('keyword')
        return self.keyword

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.get_keyword()
        if keyword:
            queryset = queryset.filter(Q(name__icontains=self.keyword))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context

class GroupAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    添加角色
    """
    template_name = "base/add.html"
    model = Group
    form_class = GroupModelForm
    permission_required = 'auth.add_group'

    def get_success_url(self):
        return reverse('users:group_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'users:group_list')
        return context

class GroupDelateView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    删除角色
    """
    template_name = 'base/delete.html'
    model = Group
    permission_required = 'auth.delete_group'

    def get_success_url(self):
        return reverse('users:group_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'users:group_list')
        return context

class GroupUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    更新角色
    """
    template_name = "base/change.html"
    model = Group   # object=User.objects.get(pk=pk)
    form_class = GroupModelForm
    permission_required = 'auth.change_group'

    def get_success_url(self):
        return reverse('users:group_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'users:group_list')
        return context

class AddUserToGroupView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    批量将用户添加到组——原生View版本
    """
    permission_required = 'auth.change_group'

    def get(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        users = Users.objects.all()
        context = {'group': group, 'users': users}
        return render(request, 'users/group_add_user.html', context=context)

    def post(self, request, pk):
        uids = request.POST.getlist('users')
        group = get_object_or_404(Group, pk=pk)
        if uids:
            users = Users.objects.filter(id__in=uids)
            group.user_set.set(users)
        else:
            group.user_set.clear()
        messages.success(request, '{}组添加用户或移除用户成功！'.format(group))
        if '_addanother' in request.POST:
            return HttpResponseRedirect(reverse('users:group_add_user', kwargs={'pk': pk}))
        return HttpResponseRedirect(reverse('users:group_list'))
        return HttpResponseRedirect(reverse('users:group_list'))


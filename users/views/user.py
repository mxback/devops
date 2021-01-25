import re
from django import http
from django.db.models.expressions import Value
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views.generic.base import TemplateView, View
from users.forms.user import UserModelForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission, ContentType, Group
from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from system.utils import CreatePassword

# ? 测试2
from collections import OrderedDict
from users.models import Menu_Level_Two, Menu_Level_One

# ? 用户Model
from users.tools.urls import memory_reverse

Users = get_user_model()


# Create your views here.
class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    用户列表
    """
    template_name = "users/user_list.html"
    model = Users
    paginate_by = 5
    keyword = ""
    permission_required = 'users.view_userinfo'

    # 数据过滤
    def get_queryset(self):
        queryset = super(UserListView, self).get_queryset()
        queryset = queryset.exclude(username='admin')
        self.keyword = self.request.GET.get("keyword", "")
        if self.keyword:
            queryset = queryset.filter(
                Q(name__icontains=self.keyword)
                | Q(username__icontains=self.keyword)
                | Q(phone__icontains=self.keyword))

        return queryset

    # 搜索关键字传给前端
    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context


class UserAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    添加用户
    """
    template_name = "base/add.html"
    model = Users
    form_class = UserModelForm
    permission_required = 'users.add_userinfo'

    def get_success_url(self):
        return reverse('users:user_list')

    def form_valid(self, form):
        """
        用户默认密码为其用户名
        """
        password = form.cleaned_data['username']
        form.instance.password = make_password(password)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'users:user_list')
        return context


class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    用户更新
    """
    template_name = "base/change.html"
    model = Users
    form_class = UserModelForm
    permission_required = 'users.change_userinfo'

    # success_message = '%(name)s 更新成功！'

    def get_success_url(self):
        return reverse('users:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'users:user_list')
        return context


class UserDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    删除用户
    """
    template_name = 'base/delete.html'
    model = Users
    permission_required = 'users.delete_userinfo'

    def get_success_url(self):
        return reverse('users:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'users:user_list')
        return context


class PasswordChangeForAdminView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'account/change_password_for_admin.html'
    permission_required = 'users.change_userinfo'

    def get_context_data(self, **kwargs):
        password = CreatePassword().getPassword
        user_obj = Users.objects.get(id=self.kwargs['pk'])
        user_obj.password = make_password(password)
        user_obj.save()

        context = super().get_context_data(**kwargs)
        context['name'] = user_obj.name
        context['password'] = password
        return context


# ? AbstractUser(AbstractBaseUser, PermissionsMixin)
# ? Group -> permissions = models.ManyToManyField(Permission)
# ? 这样用户和组都是多对多的

# ? 权限测试函数

# [{"id":id, "title":"con_type_list.name","permission":[{"id":id, "codename":"", "name":name},{"id":id2, "codename":"", "name":name}}]

@login_required
@permission_required(perm='auth.view_permission')
def permissions(request):
    # ? 获取选中用户的ID
    user_id = request.GET.get('uid')

    # ? 获取选选中组的ID
    group_id = request.GET.get('gid')

    # ? 获取选中用户的的object
    user_object = Users.objects.filter(id=user_id).first()
    if not user_object:
        user_id = None

    # ? 获取选择组的object
    group_object = Group.objects.filter(id=group_id).first()
    if not group_object:
        group_id = None

    # ? 为用户分配组
    if request.method == 'POST' and request.POST.get('type') == 'group':
        role_id_list = request.POST.getlist('groups')
        # 用户和角色关系添加到第三张表（关系表）
        if not user_object:
            # messages.error(request, '请选择用户，然后再分配角色！')
            return HttpResponse('请选择用户，然后再分配角色！')
        user_object.groups.set(role_id_list)

    # ? 为用户和组分配权限
    if request.method == 'POST' and request.POST.get('type') == 'permission':
        permission_id_list = request.POST.getlist('permissions')
        if group_object:
            group_object.permissions.set(permission_id_list)
        elif user_object:
            user_object.user_permissions.set(permission_id_list)
        else:
            return HttpResponse('请选择角色，然后再分配权限！')
        # group_object.permissions.set(permission_id_list)

    # ? 获取选择用户的组:
    if user_object:
        user_groups = user_object.groups.all()
    else:
        user_groups = []
    user_has_groups_dict = {item.id: None for item in user_groups}

    # ? 选择用户或者组的权限
    if group_object:
        group_permissions = group_object.permissions.all()
        permissions_dict = {item.id: None for item in group_permissions}
    elif user_object:
        # user_permissions
        permissions_set = set()
        for item in user_object.groups.all():
            for i in item.permissions.all().values('id'):
                permissions_set.add(i['id'])
        for item in user_object.user_permissions.all().values('id'):
            permissions_set.add(item['id'])
        permissions_dict = {item: None for item in permissions_set}
    else:
        permissions_dict = {}

    user_list = Users.objects.all()
    group_list = Group.objects.all()

    # [{"id":id, "title":"con_type_list.name","permission":[{"id":id, "codename":"", "name":name},{"id":id2, "codename":"", "name":name}}]
    con_type_list = ContentType.objects.values()
    for item in con_type_list:
        item['title'] = ContentType.objects.get(id=item['id']).name
        permission_list = Permission.objects.filter(
            content_type_id=item['id']).values()
        item['permission'] = [item for item in permission_list]

    return render(
        request, 'users/permission.html', {
            'user_list': user_list,
            'group_list': group_list,
            'all_menu_list': con_type_list,
            'user_id': user_id,
            'group_id': group_id,
            'user_has_groups_dict': user_has_groups_dict,
            'permissions_dict': permissions_dict,
        })


def test2(request):
    user_object = Users.objects.get(id=request.user.id)
    permissions_set = set()
    for item in user_object.groups.all():
        for i in item.permissions.all().values('id'):
            permissions_set.add(i['id'])
    for item in user_object.user_permissions.all().values('id'):
        permissions_set.add(item['id'])

    # ? 获取所有的二级菜单
    menu_level_two_queryset = Menu_Level_Two.objects.filter(
        pid__in=list(permissions_set)).values()
    menu_level_two_id_list = []
    for item in menu_level_two_queryset:
        if item['menu_id']:
            menu_level_two_id_list.append(item['id'])

    # ? 获取所有的一级菜单
    menu_level_two_object_list = Menu_Level_Two.objects.filter(
        id__in=menu_level_two_id_list)
    # menu_level_one_id_set = set()

    # ?
    """
    {1: {'title': '用户权限', 'icon': 'fa-id-card', 'children': [{'id': 4, 'title': '用户管理', 'url': '/users/list/', 'name': 'users:list', 'menu': 1, 'pid': 32}, {'id': 6, 'title': '权限管理', 'url': '/users/test/', 'name': 'users:test', 'menu': 1, 'pid': 8}, {'id': 9, 'title': '菜单管理', 'url': '/users/test4/', 'name': 'users:test4', 'menu': 1, 'pid': 24}, {'id': 13, 'title': '批量管理', 'url': '/users/multi/permissions/', 'name': 'users:multi_permissions', 'menu': 1, 'pid': 28}]}, 2: {'title': '测试模块', 'icon': 'fa-heart', 'children': [{'id': 7, 'title': '二级菜单测试', 'url': '/users/test2/', 'name': 'users:test2', 'menu': 2, 'pid': 4}, {'id': 8, 'title': 'tamplatetags测试', 'url': '/users/test3/', 'name': 'users:test3', 'menu': 2, 'pid': 4}]}}
    """
    menu_dict = {}
    for item in menu_level_two_object_list:
        # if item.menu:
        #     menu_level_one_id_set.add(item.menu.id)
        menu_id = item.menu_id

        if not menu_id:
            continue
        menu_object = Menu_Level_One.objects.get(id=menu_id)
        if menu_id in menu_dict:
            menu_dict[menu_id]['children'].append(model_to_dict(item))
        else:
            menu_dict[menu_id] = {
                'title': menu_object.title,
                'icon': menu_object.icon,
                'children': [
                    model_to_dict(item),
                ]
            }

    # ? {menu_level_one:{title:一级菜单,icon:图标,class:XX,menu_level_two:{id:二级菜单的ID,title:二级菜单的名称,class:,style:,}}}
    # ? {menu_level_one:{title:一级菜单,icon:图标,class:XX,menu_level_two:{id:二级菜单的ID,title:二级菜单的名称,class:,style:,}}}
    # ? 拼装ordered_dict = OrderedDict()

    key_list = sorted(menu_dict)
    ordered_dict = OrderedDict()
    for key in key_list:
        val = menu_dict[key]
        val['class'] = 'hide'

        for per in val['children']:
            per['class'] = ''
            per['style'] = ''
            print(per['url'])
            print(request.path_info)
            if per['url'] == request.path_info:
                per['class'] = 'active'
                per['style'] = 'background-color:#ddd'
                val['class'] = ''
        ordered_dict[key] = val
    # return {'menu_dict': ordered_dict}
    print(ordered_dict)
    return HttpResponse(ordered_dict.values)


def test3(request):
    current_url = request.path_info
    user_object = Users.objects.get(id=request.user.id)
    permissions_set = set()
    for item in user_object.groups.all():
        for i in item.permissions.all().values('id'):
            permissions_set.add(i['id'])
    for item in user_object.user_permissions.all().values('id'):
        permissions_set.add(item['id'])
    menu_level_two_queryset = Menu_Level_Two.objects.filter(
        pid__in=list(permissions_set)).values()
    for item in menu_level_two_queryset:
        if re.match(item['url'], current_url):
            url_record = item['title']
            break
    return render(request, 'users/path_navigation.html',
                  {'url_record': url_record})

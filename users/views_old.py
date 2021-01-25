from django import http
from django.db.models.expressions import Value
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views.generic.base import TemplateView, View
from users.forms import UserModelForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission, ContentType, Group

# ? 测试2 
from collections import OrderedDict
from users.models import Menu_Level_Two, Menu_Level_One

# ? 用户Model
Users = get_user_model()
# Create your views here.
class UserListView(ListView):
    """
    用户列表
    """
    template_name = "users/list.html"
    model = Users
    paginate_by = 5
    keyword = ""

    # 数据过滤
    def get_queryset(self):
        queryset = super(UserListView, self).get_queryset()
        queryset = queryset.exclude(username='admin')
        self.keyword = self.request.GET.get("keyword", "")
        if self.keyword:
            queryset = queryset.filter(Q(name__icontains=self.keyword) |
                                       Q(username__icontains=self.keyword) |
                                       Q(phone__icontains=self.keyword))

        return queryset

    # 搜索关键字传给前端
    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context

class UserAddView(CreateView):
    """
    添加用户
    """
    template_name = "users/form.html"
    model = Users
    # fields = ('username', 'name', 'phone','sex')
    form_class = UserModelForm
    # permission_required = 'users.add_userprofile'

    def get_success_url(self):
        print(self.request.POST)
        if "_addanother" in self.request.POST:
            return reverse('users:add')
        return reverse('users:list')

    def form_valid(self, form):
        """
        用户默认密码为其用户名
        """
        # print(form.cleaned_data)
        password = form.cleaned_data['username']
        # print(make_password(password))
        # print(form.instance)  # user = UserProfile.objects.get(pk=1)
        # print(type(form.instance))
        form.instance.password = make_password(password)
        return super().form_valid(form)

# ? AbstractUser(AbstractBaseUser, PermissionsMixin)
# ? Group -> permissions = models.ManyToManyField(Permission)
# ? 这样用户和组都是多对多的

# ? 权限测试函数

# [{"id":id, "title":"con_type_list.name","permission":[{"id":id, "codename":"", "name":name},{"id":id2, "codename":"", "name":name}}]

def test(request):

    print(request.user.id)
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
    user_has_groups_dict = { item.id: None for item in user_groups }

    # ? 选择用户或者组的权限
    if group_object:
        group_permissions = group_object.permissions.all()
        permissions_dict = {item.id: None for item in group_permissions}
    elif user_object:
        # user_permissions
        permissions_set = set()
        for item in user_object.groups.all():
            for i in  item.permissions.all().values('id'):
                permissions_set.add(i['id'])
        for item in user_object.user_permissions.all().values('id'):
            permissions_set.add(item['id'])
        permissions_dict = {item: None  for item in permissions_set}
    else:
        permissions_dict = {}
    
    user_list = Users.objects.all()
    group_list = Group.objects.all()

# [{"id":id, "title":"con_type_list.name","permission":[{"id":id, "codename":"", "name":name},{"id":id2, "codename":"", "name":name}}]
    con_type_list = ContentType.objects.values()
    for item in con_type_list:
        item['title'] = ContentType.objects.get(id=item['id']).name
        permission_list = Permission.objects.filter(content_type_id = item['id']).values()
        item['permission'] = [item for item in permission_list]

    return render(
        request,
        'users/permission.html',
        {
            'user_list': user_list,
            'group_list': group_list,
            'all_menu_list': con_type_list,
            'user_id': user_id,
            'group_id': group_id,
            'user_has_groups_dict': user_has_groups_dict,
            'permissions_dict': permissions_dict,
        }
    )

class PermissionList(TemplateView):

    template_name = 'users/permission.html'

    def get_context_data(self, **kwargs):

        user_id = self.request.GET.get('uid')
        group_id = self.request.GET.get('gid')
        user_list = Users.objects.all()
        group_list = Group.objects.all()
        con_type_list = ContentType.objects.values()
        for item in con_type_list:
            item['title'] = ContentType.objects.get(id=item['id']).name
            permission_list = Permission.objects.filter(content_type_id = item['id']).values()
            item['permission'] = [item for item in permission_list]

        context = super().get_context_data(**kwargs)
        context['all_menu_list'] = con_type_list
        context['user_list'] = user_list
        context['group_list'] = group_list
        context['user_id'] = user_id
        context['group_id'] = group_id
        return context



def test2(request):
    user_object =  Users.objects.get(id=request.user.id)

    con_type_set = set()
    for item in user_object.groups.all():
        for i in item.permissions.all().values('content_type_id'):
            con_type_set.add(i['content_type_id'])
    for item in user_object.user_permissions.all().values('content_type_id'):
        con_type_set.add(item['content_type_id'])

    # ? 获取所有的二级菜单
    con_type_object = ContentType.objects.filter(id__in=list(con_type_set))
    menu_level_two_list = []
    for item in con_type_object:
        menu_level_two = item.menu_level_two_set.all().values('id', 'title', 'url')
        if menu_level_two:
            for i in menu_level_two:
                menu_level_two_list.append(i)

    # ? 获取所有的一级菜单
    menu_level_two_object = Menu_Level_Two.objects.filter(id__in=[ i['id'] for i in menu_level_two_list ])
    menu_level_one_id_set = set()
    for item in menu_level_two_object:
        menu_level_one_id_set.add(item.menu.id)
    
    # ? {menu_level_one:{title:一级菜单,icon:图标,class:XX,menu_level_two:{id:二级菜单的ID,title:二级菜单的名称,class:,style:,}}}
    # ? {menu_level_one:{title:一级菜单,icon:图标,class:XX,menu_level_two:{id:二级菜单的ID,title:二级菜单的名称,class:,style:,}}}
    # ? 拼装ordered_dict = OrderedDict()
    ordered_dict = OrderedDict()
    menu_level_one_list = Menu_Level_One.objects.filter(id__in=list(menu_level_one_id_set)).values()
    for item in menu_level_one_list:
        ordered_dict['menu_level_one'] = item
        ordered_dict['menu_level_one']['class'] = 'hide'
        ordered_dict['menu_level_one']['menu_level_two'] = menu_level_two_list

        for i in ordered_dict['menu_level_one']['menu_level_two']:
            i['class'] = ''
            i['style'] = ''
            # reg = '^{}$'.format(item['url'])
            print(i['url'], request.path_info)
            if i['url'] == request.path_info:
                print('--->')
                i['class'] = 'active'
                i['style'] = 'background-color:#ddd'
        ordered_dict['menu_level_one']['class'] = ''

    print(ordered_dict)
    return HttpResponse(con_type_set)


def test3(request):
    return render(request, 'base/layout.html')


class UserListView(ListView):
    """
    用户列表
    """
    template_name = "users/list.html"
    model = Users
    paginate_by = 5
    keyword = ""

    # 数据过滤
    def get_queryset(self):
        queryset = super(UserListView, self).get_queryset()
        queryset = queryset.exclude(username='admin')
        self.keyword = self.request.GET.get("keyword", "")
        if self.keyword:
            queryset = queryset.filter(Q(name__icontains=self.keyword) |
                                       Q(username__icontains=self.keyword) |
                                       Q(phone__icontains=self.keyword))

        return queryset

    # 搜索关键字传给前端
    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, TemplateView, DeleteView, UpdateView
from users.models import Menu_Level_One, Menu_Level_Two
from users.forms import menu
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required

# ? 获取URL
from django.forms import formset_factory
from users.tools.route import get_all_url_dict
from collections import OrderedDict

# ? 反向生产URL
from users.tools.urls import memory_reverse

class Menu_ListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    菜单列表
    """
    template_name = "users/menu_list.html"
    permission_required = 'users.view_menu_level_one'
    # ?搜索关键字传给前端
    def get_context_data(self, **kwargs):
        context = super(Menu_ListView, self).get_context_data(**kwargs)
        menu_id = self.request.GET.get('mid')
        second_menu_id = self.request.GET.get('sid')
        menu = Menu_Level_One.objects.all()

        # ?增加一个新增展示小功能，需要读取数据库
        # ?展示对应的二级菜单
        if not Menu_Level_One.objects.filter(id=menu_id).exists():
            menu_id = None
        
        # ?根据一级菜单找到二级菜单
        if menu_id:
            second_menu = Menu_Level_Two.objects.filter(menu_id=menu_id)
        else:
            second_menu = []

        context['menus'] = menu
        context['menu_id'] = menu_id
        context['second_menu'] = second_menu
        context['second_menu_id'] = second_menu_id
        return context

class MenuAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    添加一级菜单
    """
    template_name = "base/add.html"
    model = Menu_Level_One
    form_class = menu.MenuModelForm
    permission_required = 'users.add_menu_level_one'

    def get_success_url(self):
        return reverse('users:menu_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'users:menu_list')
        return context

class MenuDelateView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    删除一级菜单
    """
    template_name = 'base/delete.html'
    model = Menu_Level_One
    permission_required = 'users.delete_menu_level_one'

    def get_success_url(self):
        return reverse('users:menu_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'users:menu_list')
        return context

class MenuUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    更新一级菜单
    """
    template_name = "base/change.html"
    model = Menu_Level_One   # object=User.objects.get(pk=pk)
    form_class = menu.MenuModelForm
    success_message = '%(title)s 更新成功！'
    permission_required = 'users.change_menu_level_one'

    def get_success_url(self):
        return reverse('users:menu_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel'] = memory_reverse(self.request, 'users:menu_list')
        return context

@login_required()
@permission_required(perm='users.view_menu_level_two')
def multi_permissions(request):
    """
    批量操作权限
    :param request:
    :return:
    """
    post_type = request.GET.get('type')
    generate_formset_class = formset_factory(menu.MultiAddPermissionForm, extra=0)
    update_formset_class = formset_factory(menu.MultiEditPermissionForm, extra=0)

    generate_formset = None
    update_formset = None
    if request.method == 'POST' and post_type == 'generate':
        # pass # 批量添加
        formset = generate_formset_class(data=request.POST)
        if formset.is_valid():
            object_list = []
            post_row_list = formset.cleaned_data
            has_error = False
            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]
                try:
                    new_object = Menu_Level_Two(**row_dict)
                    new_object.validate_unique()
                    object_list.append(new_object)
                except Exception as e:
                    formset.errors[i].update(e)
                    generate_formset = formset
                    has_error = True
            if not has_error:
                Menu_Level_Two.objects.bulk_create(object_list, batch_size=100)
        else:
            generate_formset = formset

    if request.method == 'POST' and post_type == 'update':
        # pass  # 批量更新
        formset = update_formset_class(data=request.POST)
        if formset.is_valid():
            post_row_list = formset.cleaned_data
            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]
                permission_id = row_dict.pop('id')
                try:
                    row_object = Menu_Level_Two.objects.filter(id=permission_id).first()
                    for k, v in row_dict.items():
                        setattr(row_object, k, v)
                    row_object.validate_unique()
                    row_object.save()
                except Exception as e:
                    formset.errors[i].update(e)
                    update_formset = formset
        else:
            update_formset = formset

    # 1. 获取项目中所有的URL
    all_url_dict = get_all_url_dict()
    router_name_set = set(all_url_dict.keys())

    # 2. 获取数据库中所有的URL
    permissions = Menu_Level_Two.objects.all().values('id', 'title', 'name', 'url', 'menu_id', 'pid_id')
    permission_dict = OrderedDict()
    permission_name_set = set()
    for row in permissions:
        permission_dict[row['name']] = row
        permission_name_set.add(row['name'])


    for name, value in permission_dict.items():
        router_row_dict = all_url_dict.get(name)  # {'name': 'rbac:role_list', 'url': '/rbac/role/list/'},
        if not router_row_dict:
            continue
        if value['url'] != router_row_dict['url']:
            value['url'] = '路由和数据库中不一致'

    # 3. 应该添加、删除、修改的权限有哪些？
    # 3.1 计算出应该增加的name
    if not generate_formset:
        generate_name_list = router_name_set - permission_name_set
        generate_formset = generate_formset_class(
            initial=[row_dict for name, row_dict in all_url_dict.items() if name in generate_name_list])

    # 3.2 计算出应该删除的name
    delete_name_list = permission_name_set - router_name_set
    delete_row_list = [row_dict for name, row_dict in permission_dict.items() if name in delete_name_list]

    # 3.3 计算出应该更新的name
    if not update_formset:
        update_name_list = permission_name_set & router_name_set
        update_formset = update_formset_class(
            initial=[row_dict for name, row_dict in permission_dict.items() if name in update_name_list])

    return render(
        request,
        'users/multi_permissions.html',
        {
            'generate_formset': generate_formset,
            'delete_row_list': delete_row_list,
            'update_formset': update_formset,
        }
    )

@login_required()
@permission_required(perm='users.delete_menu_level_two')
def multi_permissions_del(request, pk):
    """
    批量页面的权限删除
    :param request:
    :param pk:
    :return:
    """
    url = memory_reverse(request, 'users:multi_permissions')
    if request.method == 'GET':
        return render(request, 'users/delete.html', {'cancel': url})
    Menu_Level_Two.objects.filter(id=pk).delete()
    return redirect(url)



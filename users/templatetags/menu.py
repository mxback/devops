from collections import OrderedDict
from django.template import Library
# from django.contrib.auth.models import
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from collections import OrderedDict
from users.models import Menu_Level_Two, Menu_Level_One
from django.forms.models import model_to_dict
import re

Users = get_user_model()
register = Library()
# {}


# ? {menu_id:{title:一级菜单,icon:图标,children:{id:二级菜单的ID,title:二级菜单的名称,}}}
# ? {menu_id:{title:一级菜单,icon:图标,class:XX,children:{id:二级菜单的ID,title:二级菜单的名称,class:,style:,}}
@register.inclusion_tag('users/multi_menu.html')
def multi_menu(request):
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

            if per['url'] == request.path_info:
                per['class'] = 'active'
                per['style'] = 'background-color:#ddd'
                val['class'] = ''
        ordered_dict[key] = val
    return {'menu_dict': ordered_dict}


@register.inclusion_tag('users/path_navigation.html')
def path_navigation(request):
    current_url = request.path_info
    user_object = Users.objects.get(id=request.user.id)
    url_record = "权限不足"
    if user_object:
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
    return {'url_record': url_record}

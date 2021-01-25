import os
from django import template

register = template.Library()

@register.filter()
def get_username(queryset):
    """
    获取manytomanymany name
    :param queryset:
    :return:
    """
    #? 反馈为中文名
    user_names = queryset.values_list('name', flat=True)

    #? 反馈为登录名称
    # user_names = queryset.values_list('username', flat=True)
    return ','.join(user_names)


@register.filter()
def get_permname(queryset):
    """
    获取manytomanymany name
    :param queryset:
    :return:
    """
    perm_names = queryset.values_list('codename', flat=True)
    return ','.join(perm_names)


@register.filter()
def get_host_names2(queryset):
    host_names = [host.instance_name for host in queryset]
    return ','.join(host_names)


@register.filter()
def cut(string, length):
    """
    截取字符串
    :param string:
    :param length:
    :return:
    """
    if len(string) <= length:
        return string
    else:
        s = string[:length] + '......'
    return s

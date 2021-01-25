from django.urls import path, re_path
from django.urls.conf import include
from users.views.user import UserListView, UserAddView, permissions, test2, test3, UserUpdateView, UserDeleteView, PasswordChangeForAdminView
from users.views.menu import Menu_ListView, MenuAddView, MenuDelateView, MenuUpdateView, multi_permissions, multi_permissions_del
from users.views.group import GroupListView, AddUserToGroupView, GroupAddView, GroupDelateView, GroupUpdateView

app_name = 'users'

urlpatterns = [
    #? 用户管理
    path('list/', UserListView.as_view(), name='user_list'),
    path('add/', UserAddView.as_view(), name='user_add'),
    re_path(r'^update/(?P<pk>[0-9]+)?/$', UserUpdateView.as_view(), name='user_update'),
    re_path(r'^del/(?P<pk>[0-9]+)?/$', UserDeleteView.as_view(), name='user_del'),
    re_path(r'^password/reset/(?P<pk>[0-9]+)?/$', PasswordChangeForAdminView.as_view(), name='password_change'),

    #? 权限管理
    path('permissions/', permissions, name='permissions'),

    #? 测试模块
    path('test2/', test2, name='test2'),
    path('test3/', test3, name='test3'),

    #? 菜单管理
    path('menu/list/', Menu_ListView.as_view(), name='menu_list'),
    path('menu/add/', MenuAddView.as_view(), name='menu_add'),
    re_path(r'^menu/del/(?P<pk>[0-9]+)?/$', MenuDelateView.as_view(), name='menu_del'),
    re_path(r'^menu/update/(?P<pk>[0-9]+)?/$', MenuUpdateView.as_view(), name='menu_update'),

    #? 批量修改
    re_path(r'^multi/permissions/$', multi_permissions, name='multi_permissions'),
    re_path(r'^multi/permissions/del/(?P<pk>\d+)/$', multi_permissions_del, name='multi_permissions_del'),

    #? 角色管理
    path('group/list/', GroupListView.as_view(), name='group_list'),
    path('group/add/', GroupAddView.as_view(), name='group_add'),
    re_path(r'^group/del/(?P<pk>[0-9]+)?/$', GroupDelateView.as_view(), name='group_del'),
    re_path(r'^group/update/(?P<pk>[0-9]+)?/$', GroupUpdateView.as_view(), name='group_update'),
    re_path(r'^group_add_user/(?P<pk>[0-9]+)?/$', AddUserToGroupView.as_view(), name='group_add_user'),

]

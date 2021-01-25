from django.urls import path, re_path
from django.urls.conf import include
from cmdb.views.paas import PaasListView, PaasAddView, PaasDelateView, PaasUpdateView
from cmdb.views.region import RegionListView, RegionAddView, RegionUpdateView, RegionDelateView
from cmdb.views.tag import TypeListView, TypeAddView, TypeUpdateView, TypeDelateView, TagListView, TagAddView, \
    TagUpdateView, TagDelateView
from cmdb.views.projectgroup import ProjectGroupListView, ProjectGroupAddView, ProjectGroupUpdateView, \
    ProjectGroupDelateView, AddUserToProjectGroupView
from cmdb.views.host import HostListView, HostAddView, HostUpdateView, HostDelateView, HostUsernameListView, \
    HostUsernameAddView, HostUsernameDelateView, HostUsernameUpdateView, HostUsernameForPasswordView, get_host_list
from cmdb.views.kubernetes import K8SListView, K8SAddView, K8SUpdateView, K8SDelateView

app_name = 'cmdb'

urlpatterns = [
    # ? pass相关u
    path('paas/list/', PaasListView.as_view(), name='paas_list'),
    path('paas/add/', PaasAddView.as_view(), name='paas_add'),
    re_path(r'^pass/update/(?P<pk>[0-9]+)?/$', PaasUpdateView.as_view(), name='pass_update'),
    re_path(r'^pass/delete/(?P<pk>[0-9]+)?/$', PaasDelateView.as_view(), name='pass_delete'),

    # ? region相关
    path('region/list/', RegionListView.as_view(), name='region_list'),
    path('region/add/', RegionAddView.as_view(), name='region_add'),
    re_path(r'^region/update/(?P<pk>[0-9]+)?/$', RegionUpdateView.as_view(), name='region_update'),
    re_path(r'^region/delete/(?P<pk>[0-9]+)?/$', RegionDelateView.as_view(), name='region_delete'),

    # ? tag相关
    path('type/list/', TypeListView.as_view(), name='type_list'),
    path('type/add/', TypeAddView.as_view(), name='type_add'),
    re_path(r'^type/update/(?P<pk>[0-9]+)?/$', TypeUpdateView.as_view(), name='type_update'),
    re_path(r'^type/delete/(?P<pk>[0-9]+)?/$', TypeDelateView.as_view(), name='type_delete'),
    path('tag/list/', TagListView.as_view(), name='tag_list'),
    path('tag/add/', TagAddView.as_view(), name='tag_add'),
    re_path(r'^tag/update/(?P<pk>[0-9]+)?/$', TagUpdateView.as_view(), name='tag_update'),
    re_path(r'^tag/delete/(?P<pk>[0-9]+)?/$', TagDelateView.as_view(), name='tag_delete'),

    # ? project_group相关
    path('project/group/list/', ProjectGroupListView.as_view(), name='project_group_list'),
    path('project/group/add/', ProjectGroupAddView.as_view(), name='project_group_add'),
    re_path(r'^project/group/update/(?P<pk>[0-9]+)?/$', ProjectGroupUpdateView.as_view(), name='project_group_update'),
    re_path(r'^project/group/delete/(?P<pk>[0-9]+)?/$', ProjectGroupDelateView.as_view(), name='project_group_delete'),
    re_path(r'^project/group/add_user/(?P<pk>[0-9]+)?/$', AddUserToProjectGroupView.as_view(),
            name='project_group_add_user'),

    # ? host相关
    path('host/list/', HostListView.as_view(), name='host_list'),
    path('host/add/', HostAddView.as_view(), name='host_add'),
    re_path(r'^host/update/(?P<pk>[0-9]+)?/$', HostUpdateView.as_view(), name='host_update'),
    re_path(r'^host/delete/(?P<pk>[0-9]+)?/$', HostDelateView.as_view(), name='host_delete'),
    path('host/username/list/', HostUsernameListView.as_view(), name='host_username_list'),
    path('host/username/add/', HostUsernameAddView.as_view(), name='host_username_add'),
    re_path(r'^host/username/update/(?P<pk>[0-9]+)?/$', HostUsernameUpdateView.as_view(), name='host_username_update'),
    re_path(r'^host/username/delete/(?P<pk>[0-9]+)?/$', HostUsernameDelateView.as_view(), name='host_username_delete'),
    re_path(r'^host/password/(?P<pk>[0-9]+)?/$', HostUsernameForPasswordView.as_view(), name='host_password'),
    path('get_host_list/', get_host_list, name='get-host-list'),

    # ? k8s相关
    path('k8s/list/', K8SListView.as_view(), name='k8s_list'),
    path('k8s/add/', K8SAddView.as_view(), name='k8s_add'),
    re_path(r'^k8s/update/(?P<pk>[0-9]+)?/$', K8SUpdateView.as_view(), name='k8s_update'),
    re_path(r'^k8s/delete/(?P<pk>[0-9]+)?/$', K8SDelateView.as_view(), name='k8s_delete'),
]

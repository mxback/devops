from django.urls import path, re_path
from task.views import TaskAddView, TaskListView, TaskDetailView, TaskEditView, TaskHistoryListView, get_playbook, \
    task_publish, get_task_result

app_name = "task"

urlpatterns = [
    path('generaltask_add/', TaskAddView.as_view(), name='task_add'),
    path('list/', TaskListView.as_view(), name='task_list'),
    path('history/', TaskHistoryListView.as_view(), name='history'),
    re_path('detail/(?P<pk>[0-9]+)?/', TaskDetailView.as_view(), name='task_detail'),
    re_path('edit/(?P<pk>[0-9]+)?/', TaskEditView.as_view(), name='task_edit'),
    re_path('publish/(?P<pk>[0-9]+)?/', task_publish, name='task_publish'),
    path('get_task_result/', get_task_result, name='get_task_result'),
    path('get_playbook/', get_playbook, name='get_playbook'),

]

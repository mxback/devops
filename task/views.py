import json, traceback
import os
from django.utils import timezone

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from pure_pagination.mixins import PaginationMixin

from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt

from django.template import loader
from devops.settings import BASE_DIR
from users.tools.urls import memory_reverse
# Create your views here.

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.generic.base import View

from cmdb.models import Host, Tag
from task.models import Task
from django_redis import get_redis_connection

from .util import task_execute

from system.utils import ModelUtils

# ? 获取User
from django.contrib.auth import get_user_model

User = get_user_model()


redis_cli = get_redis_connection('default')


class TaskAddView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    添加通用任务
    """
    permission_required = 'task.add_task'

    def get(self, request):
        user = self.request.user
        host_set = set()
        for item in user.projectgroup_set.all():
            for i in item.host_set.all():
                host_set.add(i.id)
        hosts = Host.objects.filter(id__in=host_set)
        tag_model = ModelUtils(model=Host, user=request.user)
        tags = tag_model.get_tag(model=Tag)
        cancel = memory_reverse(request, 'task:task_list')
        context = {'hosts': hosts, 'tags': tags, 'cancel': cancel}
        return render(request, 'task/generaltask_add.html', context=context)

    # @csrf_exempt
    def post(self, request):
        try:
            ids = request.POST.get('ids')
            # print(ids)
            # 将前端传过来的json串转为list
            ids = json.loads(ids)
            content = request.POST.get('content')
            name = request.POST.get('name')
            task = Task()
            task.name = name
            task.content = content
            task.applicant = request.user
            task.status = 0
            task.save()
            task.dest_hosts.set(ids)
            msg = {"code": 0, "msg": "添加用户成功"}
        except:
            msg = {"code": 1, "msg": "添加用户失败: %s" % traceback.format_exc()}
        return JsonResponse(msg)


class TaskListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    任务列表
    """
    template_name = 'task/task_list.html'
    model = Task
    paginate_by = 10
    permission_required = 'task.view_task'
    keyword = None

    def get_keyword(self):
        self.keyword = self.request.GET.get('keyword')
        return self.keyword

    def get_queryset(self):
        user = self.request.user
        host_set = set()
        for item in user.projectgroup_set.all():
            for i in item.host_set.all():
                host_set.add(i.id)
        queryset = super().get_queryset()
        queryset = queryset.filter(status__in=[0, 2], dest_hosts__id__in=host_set).order_by("-created_at").distinct()
        keyword = self.get_keyword()
        if keyword:
            queryset = queryset.filter(Q(name__icontains=keyword) |
                                       Q(dest_hosts__instance_name=keyword) |
                                       Q(content__icontains=keyword) |
                                       Q(applicant__username__icontains=keyword) |
                                       Q(applicant__name__icontains=keyword) |
                                       Q(reviewer__username__icontains=keyword) |
                                       Q(reviewer__name__icontains=keyword) |
                                       Q(review_notes__icontains=keyword) |
                                       Q(publisher__username__icontains=keyword) |
                                       Q(publisher__name__icontains=keyword) |
                                       Q(result__icontains=keyword)).distinct()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['keyword'] = self.keyword
        return context


class TaskDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    任务详情页
    """
    template_name = 'task/task_detail.html'
    model = Task
    permission_required = 'task.view_history'

    def post(self, request, pk):
        status = request.POST.get('status')
        review_notes = request.POST.get('review_notes')
        task = Task.objects.filter(id=pk).get()
        task.status = status
        task.review_notes = review_notes
        task.reviewer = request.user
        task.review_at = timezone.now()
        task.save()
        # status = int(status)
        # if status == 1:
        #     # email_send.delay(task.apply_user.email, send_type='audit_task_refuse', task=task.task.name, id=task.id)
        # elif status == 2:
        #     # email_send.delay(task.apply_user.email, send_type='task_publish', task=task.task.name, id=task.id)
        return JsonResponse({'code': 0, 'msg': '审核成功!'})


class TaskEditView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    编辑通用任务
    """
    permission_required = 'task.change_task'

    def get(self, request, pk):
        hosts = Host.objects.all()
        tags = Tag.objects.all()
        task = Task.objects.get(pk=pk)
        cancel = memory_reverse(request, 'task:task_list')
        context = {'hosts': hosts, 'tags': tags, 'task': task, 'cancel': cancel}
        return render(request, 'task/generaltask_edit.html', context=context)

    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            task.content = request.POST.get('content')
            task.name = request.POST.get('name')
            task.dest_hosts.set(json.loads(request.POST.get('ids')))
            # 如果被退回之后修改，状态又回到待检查状态
            if task.status == 1:
                task.status = 0
            task.save()
            msg = {"code": 0, "msg": "更新任务成功"}
        except:
            msg = {"code": 1, "msg": "更新任务失败: %s" % traceback.format_exc()}
        return JsonResponse(msg)


class TaskHistoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    任务历史列表
    """
    template_name = 'task/task_history_list.html'
    model = Task
    paginate_by = 10
    keyword = None
    permission_required = 'task.view_history'

    def get_keyword(self):
        self.keyword = self.request.GET.get('keyword')
        return self.keyword

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        host_set = set()
        for item in user.projectgroup_set.all():
            for i in item.host_set.all():
                host_set.add(i.id)
        queryset = queryset.filter(status__in=[-1, 1, 3]).filter(dest_hosts__id__in=host_set).order_by("-created_at").distinct()
        keyword = self.get_keyword()
        if keyword:
            queryset = queryset.filter(Q(name__icontains=keyword) | Q(dest_hosts__instance_name=keyword) |
                                       Q(dest_dir__icontains=keyword) | Q(content__icontains=keyword) |
                                       Q(version__icontains=keyword) | Q(apply_user__username__icontains=keyword) |
                                       Q(apply_user__name__icontains=keyword) | Q(
                reviewer__username__icontains=keyword) |
                                       Q(reviewer__name__icontains=keyword) | Q(review_notes__icontains=keyword) |
                                       Q(publisher__username__icontains=keyword) | Q(
                publisher__name__icontains=keyword) |
                                       Q(result__icontains=keyword)).distinct()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['keyword'] = self.keyword
        return context


@require_POST
@login_required
@csrf_exempt
def get_playbook(request):
    """
    返回playbook
    :param request:
    :return:
    """
    ids = request.POST.get('ids', '')
    # print(type(ids))
    content = request.POST.get('content', '')
    print(content)
    ids = json.loads(ids)
    print(type(ids))
    # values_list方法加个参数flat=True返回单个值的QuerySet
    hosts = Host.objects.filter(id__in=ids).values_list('private_ip', flat=True)
    # print(hosts)
    # 判断前端传来的脚本是否为空，为空则返回模板，不为空则写入临时文件
    if content:
        with open(os.path.join(BASE_DIR, 'tmp', 'tmp_playbook.yml'), 'w') as f:
            f.write(content)
        with open(os.path.join(BASE_DIR, 'tmp', 'tmp_playbook.yml'), 'r') as f:
            content = ''
            for line in f:
                if line.startswith('- hosts'):
                    content += '- hosts: {}\n'.format(','.join(hosts))
                else:
                    content += line
    else:
        content = loader.render_to_string('task/playbook_demo.yml.templage', {'dest_hosts': ','.join(hosts)})
    return JsonResponse({'code': 0, 'msg': '获取Playbook demo成功!', 'content': content})


@login_required
@permission_required('task.publish_task')
@require_POST
def task_publish(request, pk):
    """
    发布任务
    :param request:
    :param pk
    :return:
    """
    # 发布任务  状态流转
    historic_task = Task.objects.get(id=pk)
    historic_task.status = 3
    historic_task.publisher = request.user
    historic_task.publish_at = timezone.now()
    historic_task.save()
    # 同步执行
    task_execute(pk)
    return JsonResponse({'code': 0, 'msg': '已将任务放到后台执行，请稍后！'})

@require_GET
def get_task_result(request):
    """
    发布配置文件结果
    :param request:
    :return:
    """
    task_id = request.GET.get('task_id')
    redis_key_prefix = 'ark::task'
    data = redis_cli.get('{}::{}'.format(redis_key_prefix, task_id))
    if not data:
        data = "任务开始执行，请稍作等待！"
    else:
        data = str(data, encoding='utf8')
        # historic_task = Task.objects.get(id=pk)
    # print(data)
    return JsonResponse({'code': 0, 'data': data})

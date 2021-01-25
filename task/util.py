import json
import os
from datetime import datetime

from django.utils import timezone

from devops.settings import BASE_DIR
from cmdb.models import Host
from task.models import Task
from utils.ansible_api import AnsibleClient
from django_redis import get_redis_connection
from utils.email import SendMail

redis_cli = get_redis_connection('default')


def get_inventory():
    """
    获取主机清单
    :return:
    """
    hosts = Host.objects.all().values_list('private_ip', flat=True)
    inventory = ','.join(hosts)
    return inventory


def exec_playbook(redis_key_prefix, task_id):
    """
    执行playbook
    :param redis_key_prefix: Redis Key前缀
    :param task_id 任务id
    :return:
    """
    redis_cli.delete('{}::{}'.format(redis_key_prefix, task_id))
    task = Task.objects.get(id=task_id)
    hosts = task.dest_hosts.all().values_list('private_ip', flat=True)

    # todo https://blog.csdn.net/weixin_45032957/article/details/107815430
    # ? 解决部分bug
    sources = ','.join(hosts) + ','
    client = AnsibleClient(sources)
    file_name = str(task.id) + '_' + datetime.now().strftime('%Y%m%d%H%M') + '.yml'
    pb_path = os.path.join(BASE_DIR, 'tmp', file_name)
    with open(pb_path, 'w') as f:
        f.write(task.content)
    # print(pb_path)
    client.ansible_playbook(redis_key_prefix, task_id, pb_path, extra_vars=None)
    # 任务已经完成，并且任务结果已经存入redis, 我们再把redis的结果 拿出来 存入数据库
    result = redis_cli.get('{}::{}'.format(redis_key_prefix, task_id))
    task.result = str(result, encoding='utf8')
    task.publish_at = timezone.now()
    task.save()
    return True


def task_execute(task_id):
    """
    执行任务
    :param task_id:
    :return:
    """
    # print(task_id)
    redis_key_prefix = "ark::task"
    exec_playbook(redis_key_prefix, task_id)
    task = Task.objects.get(id=task_id)

    # 直接发送,和主线程同步
    # res = send_mail(subject, message, 'mxback@163.com',
    #                 [task.applicant.email, task.reviewer.email, task.publisher.email], fail_silently=True)
    # if res == 1:
    #     print('邮件发送成功, ok')
    # else:
    #     print('邮件发送失败, fail')

    # 异步发送
    subject = "{}({})发布任务成功".format(task.name, task.id)
    message = task.result
    send_mail = SendMail(subject, message, [task.applicant.email, task.reviewer.email, task.publisher.email])
    send_mail.start()

    return '任务发布成功!'

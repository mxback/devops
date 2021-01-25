import json
from ansible import constants
from ansible import context
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from django_redis import get_redis_connection

redis_cli = get_redis_connection("default")
# paramiko_ssh
context.CLIARGS = ImmutableDict(connection='smart', module_path=[], verbosity=5, forks=10, become=None,
                                become_method=None, become_user=None, check=False, diff=False, syntax=False,
                                start_at_task=None)


class PlayResultCallback(CallbackBase):
    """
    执行ansible命令的回调类，用来显示或保存执行结果
    """

    def __init__(self, *args, **kwargs):
        super(PlayResultCallback, self).__init__(*args, **kwargs)

    def v2_runner_on_unreachable(self, result):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_ok(self, result, *args, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))


class PlayBookResultCallback(CallbackBase):
    """
    Playbook回调类，用来显示或保存playbook执行结果
    """

    def __init__(self, redis_key_prefix, task_id, *args, **kwargs):
        super(PlayBookResultCallback, self).__init__(*args, **kwargs)
        self.task_name = ''
        self.key = "{}::{}".format(redis_key_prefix, task_id)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        if not self.task_name:
            self.task_name = result._task_fields['name']
            redis_cli.append(self.key, "TASK [{}]{}\n".format(result._task_fields['name'], '*' * 80))
        if self.task_name != result._task_fields['name']:
            self.task_name = result._task_fields['name']
            redis_cli.append(self.key, "\nTASK [{}]{}\n".format(result._task_fields['name'], '*' * 80))
        if result._result.get('changed'):
            stat = 'changed'
        else:
            stat = 'ok'
        redis_cli.append(self.key, '{}: [{}]\n'.format(stat, result._host.get_name()))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        if not self.task_name or self.task_name != result._task_fields['name']:
            self.task_name = result._task_fields['name']
            redis_cli.append(self.key, "TASK [{}]{}\n".format(result._task_fields['name'], '*' * 80))
        redis_cli.append(self.key, 'fatal: [{}]: FAILED! => {}\n\n'.format(result._host.get_name(), result._result))

    def v2_runner_on_unreachable(self, result):
        if not self.task_name or self.task_name != result._task_fields['name']:
            self.task_name = result._task_fields['name']
            redis_cli.append(self.key, "TASK [{}]\n".format(result._task_fields['name']))
        redis_cli.append(self.key, 'unreachable: [{}]\n'.format(result._host.get_name()))

    def v2_runner_on_skipped(self, result):
        if not self.task_name or self.task_name != result._task_fields['name']:
            self.task_name = result._task_fields['name']
            redis_cli.append(self.key, "TASK [{}]\n".format(result._task_fields['name']))
        redis_cli.append(self.key, 'skipped: [{}]\n'.format(result._host.get_name()))

    def v2_playbook_on_stats(self, stats):
        redis_cli.append(self.key, '\nPLAY RECAP{}\n'.format('*' * 80))
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)
            redis_cli.append(self.key, '{:15s}: {}\n'.format(h, t))


class AnsibleClient:
    def __init__(self, source):
        self.source = source  # 字符串类型，主机名或IP之间用逗号分隔.例如：'192.168.1.1,192.168.1.2' 相当于inventory
        self.loader = DataLoader()  # 解析yaml,json或ini格式文件
        self.inventory = InventoryManager(loader=self.loader, sources=self.source)  # inventory 管理
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)  # 变量管理
        self.passwords = dict(vault_pass='secret')
        # self.passwords = dict(conn_pass='vagrant')
        # self.passwords = None
        self.callback = None

    def ansible(self, hosts, module_name, module_args):
        """
        执行ansible命令
        :param hosts: host-pattern
        :param module_name: ansible模块名称
        :param module_args: ansible模块参数
        :return:
        """
        self.callback = PlayResultCallback()
        play_source = dict(
            name="Ansible Play",
            hosts=hosts,
            gather_facts='no',
            tasks=[
                dict(action=dict(module=module_name, args=module_args)),
            ]
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
                stdout_callback=self.callback,
            )
            tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()

    def ansible_playbook(self, redis_key_prefix, task_id, playbook_path, extra_vars=None):
        """
        执行playbook,相当于ansible-playbook命令
        :param redis_key_prefix: playbook执行结果保存在redis中, redis_key_prifix + task_id 即为key
        :param task_id: 是数据库中保存此次任务执行的自增id
        :param playbook_path: 脚本路径
        :param extra_vars: 额外变量
        :return:
        """
        self.callback = PlayBookResultCallback(redis_key_prefix, task_id)
        if extra_vars:
            self.variable_manager._extra_vars = extra_vars
        executor = PlaybookExecutor(
            playbooks=[playbook_path], inventory=self.inventory, variable_manager=self.variable_manager,
            loader=self.loader,
            passwords=self.passwords,
        )
        executor._tqm._stdout_callback = self.callback
        constants.HOST_KEY_CHECKING = False
        result = executor.run()
        return result

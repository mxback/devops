import json
from django_redis import get_redis_connection
from cmdb.models import Host, Paas, ProjectGroup, Tag

redis_cli = get_redis_connection("hosts")


class AutoUpdateHost(object):

    def __init__(self, redis_config="hosts"):
        self.redis_cli = get_redis_connection(redis_config)

    @property
    def get_hosts_ips(self):
        return self.redis_cli.keys()

    @property
    def update_hosts(self):
        ips = self.get_hosts_ips
        for ip in ips:
            host = Host.objects.filter(private_ip=ip.decode()).first()
            redis_host_data = json.loads(self.redis_cli.get(ip.decode()).decode())
            default_paas = Paas.objects.get(id=5)
            default_project_group = ProjectGroup.objects.get(id=4)
            # default_tags = Tag.objects.get(id=3)
            if host:
                if host.cpu != int(redis_host_data['cpu']['count']) or host.memory != int(
                        redis_host_data['memory']['total']):  # 需要加上磁盘的判断
                    host.cpu = int(redis_host_data['cpu']['count'])
                    host.memory = int(redis_host_data['memory']['total'])
                    host.save()
                else:
                    pass
                    # host.send_time = redis_host_data['send_time']
                    # host.save()
            else:
                host_obj = Host()
                host_obj.paas = default_paas
                host_obj.instance_name = redis_host_data['ip_address']
                host_obj.cpu = int(redis_host_data['cpu']['count'])
                host_obj.memory = int(redis_host_data['memory']['total'])
                # host_obj.disk
                host_obj.private_ip = redis_host_data['ip_address']
                host_obj.os_type = redis_host_data['system']
                host_obj.os_name = redis_host_data['system']  # 可获取的更详细
                host_obj.update_time = redis_host_data['send_time']  #
                host_obj.save()
                host_new = Host.objects.filter(private_ip=redis_host_data['ip_address']).first()
                host_new.project_group.add(default_project_group)
                # host_new.tags.add(default_tags)


class HostUsageInfo(object):

    def __init__(self):
        self.columns = []
        self.cpu_usage_data = []
        self.memory_usage_data = []

    def host_usage_data(self, rds, key):
        for i in range(rds.llen(key)):
            self.columns.append(json.loads(rds.lrange(key, i, i)[0].decode())[2])
            self.cpu_usage_data.append(json.loads(rds.lrange(key, i, i)[0].decode())[0])
            self.memory_usage_data.append(json.loads(rds.lrange(key, i, i)[0].decode())[1])
        return self.columns, self.cpu_usage_data, self.memory_usage_data

    @classmethod
    def get_usage_data(cls, rds, key):
        columns, cpu_usage_data, memory_usage_data = cls().host_usage_data(rds, key)
        return list(reversed(columns)), list(reversed(cpu_usage_data)), list(reversed(memory_usage_data))

#a, b, c = HostUsageInfo(rds, key).get_usage_data(rds, key)


class AutoUpdateK8S(object):
    pass

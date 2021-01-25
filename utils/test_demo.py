class ModelUtils(object):
    def __init__(self, model):
        self.model = model

    def get_hosts(self):
        """
        获取主机清单
        :return:
        """
        hosts = self.model.objects.all().values_list('private_ip', flat=True)
        inventory = ','.join(hosts)
        return inventory

print(ModelUtils.__name__)

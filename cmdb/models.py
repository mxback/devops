from django.db import models
from users.models import UserInfo


# Create your models here.
class Paas(models.Model):
    """
    运维平台
    """
    title = models.CharField(max_length=32, verbose_name="平台名称")

    class Meta:
        verbose_name = '运维平台'
        verbose_name_plural = verbose_name
        default_permissions = ()
        permissions = (
            ('view_paas', '查看运维平台'),
            ('add_paas', '添加运维平台'),
            ('change_paas', '编辑运维平台'),
            ('delete_paas', '删除运维平台'),
        )

    def __str__(self):
        return self.title


class Region(models.Model):
    """
    云平台区域
    """
    paas = models.ForeignKey('Paas', verbose_name="平台名称", on_delete=models.CASCADE)
    name = models.CharField(max_length=32, verbose_name="中文名称")
    region = models.CharField(max_length=32, verbose_name="代码名称")
    endpoint = models.CharField(max_length=32, verbose_name="连接")

    class Meta:
        verbose_name = '云平台区域'
        verbose_name_plural = verbose_name
        default_permissions = ()
        permissions = (
            ('view_region', '查看云平台区域'),
            ('add_region', '添加云平台区域'),
            ('change_region', '编辑云平台区域'),
            ('delete_region', '删除云平台区域'),
        )

    def __str__(self):
        return self.name


class Type(models.Model):
    """
    标签类型
    """
    name = models.CharField(max_length=100, verbose_name='类型名称')
    name_cn = models.CharField(max_length=100, verbose_name='中文名称')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '标签类型'
        verbose_name_plural = verbose_name
        default_permissions = ()
        permissions = (
            ('view_type', '查看标签类型'),
            ('add_type', '添加标签类型'),
            ('change_type', '编辑标签类型'),
            ('delete_type', '删除标签类型'),
        )

    def __str__(self):
        return self.name_cn


class Tag(models.Model):
    """
    标签
    """

    type = models.ForeignKey('Type', verbose_name='类型', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='标签名称')
    name_cn = models.CharField(max_length=100, verbose_name='中文名称')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name
        default_permissions = ()
        permissions = (
            ('view_tag', '查看标签'),
            ('add_tag', '添加标签'),
            ('change_tag', '编辑标签'),
            ('delete_tag', '删除标签'),
        )

    def __str__(self):
        return self.name_cn


class ProjectGroup(models.Model):
    """
    项目组
    """
    title = models.CharField(max_length=32, verbose_name="项目组名称")
    name_cn = models.CharField(max_length=32, verbose_name="项目组中文名称")
    userinfo = models.ManyToManyField(UserInfo, verbose_name="项目组成员", null=True, blank=True)

    class Meta:
        verbose_name = '项目组'
        verbose_name_plural = verbose_name
        default_permissions = ()
        permissions = (
            ('view_project_group', '查看项目组'),
            ('add_project_group', '添加项目组'),
            ('change_project_group', '编辑项目组'),
            ('delete_project_group', '删除项目组'),
        )

    def __str__(self):
        return self.name_cn


class Host(models.Model):
    """
    主机包括阿里云的ECS, 腾讯云的CVM,本地主机等
    """

    STATUS = (
        ('Running', '运行中'),
        ('Starting', '启动中'),
        ('Stopping', '停止中'),
        ('Stopped', '已停止')
    )

    CHARGE_TYPE = (
        ('PrePaid', '预付费'),
        ('PostPaid', '后付费'),
        ('local', '本地购买')
    )
    project_group = models.ManyToManyField('ProjectGroup', verbose_name="所属项目组", null=True, blank=True)
    paas = models.ForeignKey('Paas', verbose_name='所属平台', on_delete=models.CASCADE)
    instance_id = models.CharField(max_length=22, verbose_name='实例ID', null=True, blank=True)
    instance_name = models.CharField(max_length=22, verbose_name='显示名称')
    description = models.CharField(max_length=128, null=True, blank=True, verbose_name='实例的描述')
    image_id = models.CharField(max_length=50, verbose_name='镜像ID', null=True, blank=True, )
    region_id = models.CharField(max_length=30, verbose_name='实例所属地域ID', null=True, blank=True)
    zone_id = models.CharField(max_length=30, verbose_name='实例所属可用区', null=True, blank=True, )
    cpu = models.IntegerField(verbose_name='CPU核数')
    memory = models.IntegerField(verbose_name='内存大小，单位: GB')
    # disk = models.IntegerField(verbose_name='磁盘大小，单位: GB')
    instance_type = models.CharField(max_length=30, verbose_name='实例资源规格', null=True, blank=True, )
    status = models.CharField(max_length=8, choices=STATUS, default='Running', verbose_name='主机状态')
    hostname = models.CharField(max_length=23, blank=True, null=True, verbose_name='主机名称')
    public_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='公网IP')
    private_ip = models.GenericIPAddressField(verbose_name='私网IP')
    os_type = models.CharField(max_length=10, default='linux', verbose_name='操作系统类型')
    os_name = models.CharField(max_length=20, default='', verbose_name='操作系统名称')
    instance_charge_type = models.CharField(max_length=8, default='PrePaid', choices=CHARGE_TYPE,
                                            verbose_name='付费方式')
    creation_time = models.DateTimeField(verbose_name='创建时间', null=True, blank=True, )
    expired_time = models.DateTimeField(verbose_name='过期时间', null=True, blank=True, )
    tags = models.ManyToManyField('Tag', blank=True, verbose_name='标签')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='入库时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    # send_time = models.DateTimeField(verbose_name='更新时间')

    class Meta:
        verbose_name = '主机'
        verbose_name_plural = verbose_name
        default_permissions = ()
        permissions = (
            ('view_host', '查看主机信息'),
            ('add_host', '添加主机信息'),
            ('change_host', '更新主机信息'),
            ('delete_host', '删除主机信息'),
        )

    def __str__(self):
        return self.instance_name


class HostUsername(models.Model):
    """
    账号密码表
    """
    host = models.ForeignKey('Host', verbose_name='主机', on_delete=models.CASCADE)
    username = models.CharField(max_length=32, verbose_name='用户名', unique=True)
    password = models.CharField(max_length=32, verbose_name='密码')

    class Meta:
        verbose_name = '主机用户名'
        verbose_name_plural = verbose_name
        default_permissions = ()
        permissions = (
            ('view_host_username', '查看主机用户名'),
            ('add_host_username', '添加主机用户名'),
            ('change_host_username', '更新主机用户名'),
            ('delete_host_username', '删除主机用户名'),
            ('view_host_password', '查看主机密码'),
        )


class Kubernetes(models.Model):
    """
    k8s容器
    """
    KIND = (
        ('Deployment', '无状态'),
        ('StatefulSet', '有状态'),
        ('DaemonSet', '守护进程集'),
        ('Job', '任务'),
        ('CronJob', '定时任务'),
    )

    project_group = models.ManyToManyField('ProjectGroup', verbose_name="所属项目组", null=True, blank=True)
    paas = models.ForeignKey('Paas', verbose_name='所属平台', on_delete=models.CASCADE, null=True, blank=True)
    kind = models.CharField(max_length=32, default='Deployment', choices=KIND, verbose_name='种类')
    name = models.CharField(max_length=32, verbose_name='名称')
    namespace = models.CharField(max_length=32, verbose_name='命名空间', unique=True)
    limits_cpu = models.IntegerField(verbose_name='最小CPU核数-Core')
    limits_memory = models.IntegerField(verbose_name='最小内存-M')
    requests_cpu = models.IntegerField(verbose_name='最大CPU核数-Core')
    requests_memory = models.IntegerField(verbose_name='最大内存-M')
    gitlab = models.CharField(max_length=32, verbose_name='对应的GIT仓库', null=True, blank=True, )
    tags = models.CharField(max_length=32, verbose_name='GITLAB中最后的标签', null=True, blank=True, )

    class Meta:
        verbose_name = '主机用户名'
        verbose_name_plural = verbose_name
        default_permissions = ()
        permissions = (
            ('view_Kubernetes', '查看息K8S的部署信'),
            ('add_Kubernetes', '添加K8S的部署信息'),
            ('change_Kubernetes', '更新K8S的部署信息'),
            ('delete_Kubernetes', '删除K8S的部署信息'),
        )

    def __str__(self):
        return self.namespace + ':' + self.name

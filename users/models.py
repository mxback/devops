from django.db import models
from django.contrib.auth.models import AbstractUser, Permission


class UserInfo(AbstractUser):
    SEX = (
        (0, '男'),
        (1, '女'),
    )
    name = models.CharField('中文名', max_length=30)
    phone = models.CharField('手机', max_length=11, null=True, blank=True)
    sex = models.IntegerField(choices=SEX, null=True, blank=True, verbose_name="性别")

    class Meta:
        verbose_name = '用户信息'

    def __str__(self):
        return self.username


# todo Menu(菜单)栏, 根据权限自动实现
# ? 一级菜单对应左边栏大的
# ? 二级菜单左边栏对应一级下面

# todo 对应关系
# ? 一个model对应一个二级左边栏
# ? 二级左边栏 对应的是 content_type的ID
# ?


class Menu_Level_One(models.Model):
    title = models.CharField(max_length=32, verbose_name='一级菜单名称')
    icon = models.CharField(max_length=32, verbose_name='图标')

    class Meta:
        verbose_name = '一级菜单'

    def __str__(self):
        return self.title


class Menu_Level_Two(models.Model):
    """
    二级菜单表
    """
    title = models.CharField(verbose_name='标题', max_length=32)
    url = models.CharField(verbose_name='含正则的url', max_length=128)
    name = models.CharField(verbose_name='url的名称', max_length=32, unique=True)
    menu = models.ForeignKey(
        to='Menu_Level_One',
        verbose_name='所属菜单',
        null=True, blank=True,
        help_text='null标示不是菜单,非null表示二级菜单',
        on_delete=models.CASCADE
    )
    pid = models.ForeignKey(
        to=Permission,
        verbose_name='关联的权限',
        null=True,
        blank=True,
        related_name='parents',
        help_text='对于非菜单权限需要选择一个可以成为菜单的权限,用户做默认展开和选中菜单',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = '二级菜单'

    def __str__(self):
        return self.title

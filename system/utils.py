import base64
import random
import string
from random import shuffle
from django.db.models import ForeignKey, ManyToManyField


class CreatePassword(object):

    def __init__(self, num=16, sign_num=3):
        self.num = num
        self.sign_num = sign_num
        self.nums = string.digits
        self.sign = string.punctuation
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase

    def shuffle_str(self, str):
        # 将字符串转换成列表
        str_list = list(str)
        # 调用random模块的shuffle函数打乱列表
        shuffle(str_list)
        # 将列表转字符串
        return ''.join(str_list)

    def encryption(self, str):
        return base64.b64encode(str.encode("utf-8"))

    def decryption(self, bytes):
        return base64.b64decode(bytes).decode("utf-8")

    @property
    def getPassword(self):
        password = ""
        # ? 不含特殊符号的字符串
        for i in range(self.num - self.sign_num):
            chars = random.choice(self.nums + self.lowercase + self.uppercase)
            password = password + ''.join(chars)

        # ? 特殊符号的字符串
        for i in range(self.sign_num):
            chars = random.choice(self.sign)
            password = password + ''.join(chars)

        return self.shuffle_str(password)


class SearchGroupRow(object):
    def __init__(self, title, queryset_or_tuple, option, query_dict):
        self.queryset_or_tuple = queryset_or_tuple
        self.option = option
        self.title = title
        self.query_dict = query_dict  # request.GET

    # 可迭代对象
    def __iter__(self):
        # yield '<div class ="col-md-2" >'
        yield '<div class="whole" style="width:80px;">'
        yield self.title
        # yield '</div>'
        yield '</div>'

        yield '<div class="others">'
        total_query_dict = self.query_dict.copy()
        total_query_dict._mutable = True
        origin_value_list = self.query_dict.getlist(self.option.field)
        if not origin_value_list:
            yield '<a class="active" href="?{}" >全部</a>'.format(total_query_dict.urlencode())
        else:
            total_query_dict.pop(self.option.field)
            yield '<a href="?{}" >全部</a>'.format(total_query_dict.urlencode())
        for item in self.queryset_or_tuple:
            text = self.option.get_text(item)
            value = str(self.option.get_value(item))
            query_dict = self.query_dict.copy()
            query_dict._mutable = True

            #
            if not self.option.is_multi:
                query_dict[self.option.field] = value
                if value in origin_value_list:
                    query_dict.pop(self.option.field)
                    yield "<a class='active' href='?{}'>{}</a>".format(query_dict.urlencode(), text)
                else:
                    yield "<a href='?{}'>{}</a>".format(query_dict.urlencode(), text)
            else:
                multi_value_list = query_dict.getlist(self.option.field)
                if value in multi_value_list:
                    multi_value_list.remove(value)
                    query_dict.setlist(self.option.field, multi_value_list)
                    yield "<a class='active' href='?{}'>{}</a>".format(query_dict.urlencode(), text)
                else:
                    multi_value_list.append(value)
                    query_dict.setlist(self.option.field, multi_value_list)
                    yield "<a href='?{}'>{}</a>".format(query_dict.urlencode(), text)
        yield '</div>'


class SearchOption(object):
    def __init__(self, field, db_condition=None, is_multi=False, text_func=None, value_func=None):
        self.field = field
        if not db_condition:
            db_condition = {}
        self.db_condition = db_condition
        self.text_func = text_func
        self.value_func = value_func

        self.is_multi = is_multi
        self.is_choice = False

    def get_db_condition(self, request, *args, **kwargs):
        return self.db_condition

    def get_queryset_or_tuple(self, model_class, request, *args, queryset=None, **kwargs):
        field_obj = model_class._meta.get_field(self.field)
        title = field_obj.verbose_name
        if isinstance(field_obj, ForeignKey) or isinstance(field_obj, ManyToManyField):
            # FK和M2M找到关联表中的数据
            db_condition = self.get_db_condition(request, *args, **kwargs)
            return SearchGroupRow(title, field_obj.remote_field.model.objects.filter(**db_condition), self, request.GET)
        else:
            # 获取choices
            self.is_choice = True
            return SearchGroupRow(title, field_obj.choices, self, request.GET)

    def get_text(self, field_obj):
        if self.text_func:
            return self.text_func(field_obj)

        if self.is_choice:
            return field_obj[1]

        return str(field_obj)

    def get_value(self, field_obj):
        if self.value_func:
            return self.get_value(field_obj)

        if self.is_choice:
            return field_obj[0]

        return field_obj.pk


class SearchGroup(object):
    def __init__(self, model_class):
        self.model_class = model_class

    db_condition = []
    search_group = []

    def get_db_condition(self, request, *args, **kwargs):
        return self.db_condition

    def get_search_group(self):
        return self.search_group

    def get_search_group_row_list(self, request, *args, **kwargs):
        search_group = self.get_search_group()
        search_group_row_list = []
        for option_obj in search_group:
            row = option_obj.get_queryset_or_tuple(self.model_class, request, *args, **kwargs)
            search_group_row_list.append(row)
        return search_group_row_list

    def get_search_group_condition(self, request):
        condition = {}
        for option in self.get_search_group():
            if option.is_multi:
                value_list = request.GET.getlist(option.field)
                if not value_list:
                    continue
                condition['{}__in'.format(option.field)] = value_list
            else:
                value = request.GET.get(option.field)
                if not value:
                    continue
                condition[option.field] = value
        return condition


class ModelUtils(object):
    def __init__(self, model, user=None, task_id=None):
        self.model = model
        self.user = user
        self.task_id = task_id

    def get_hosts(self):
        """
        获取主机清单
        :return:
        """
        if self.model.__name__ == 'Host' and self.user:
            host_set = set()
            for item in self.user.projectgroup_set.all():
                for i in item.host_set.all():
                    host_set.add(i.id)
            hosts = self.model.objects.filter(id__in=host_set)
            return hosts
        elif self.model.__name__ == 'Task' and self.task_id:
            task = self.model.objects.get(id=self.task_id)
            hosts = task.dest_hosts.all()
            return hosts
        return None

    def get_tag(self, model):
        """
        通过主机获取标签
        :param model:  Tags
        :return:
        """
        if self.model.__name__ == 'Host' and self.user:
            hosts = self.get_hosts()
            tag_set = set()
            for item in hosts:
                for i in item.tags.all():
                    tag_set.add(i.id)
            tags = model.objects.filter(id__in=tag_set)
            return tags
        return None


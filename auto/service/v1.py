from django.db.models import Q, ForeignKey, ManyToManyField
from django.urls import re_path, reverse
from django.shortcuts import HttpResponse, render, redirect
from types import FunctionType
from auto.utils.pagination import Pagination
from django.utils.safestring import mark_safe
from django.http import QueryDict
from django import forms
import functools


class StarkSite(object):

    def __init__(self):
        self._registry = []
        self.app_name = 'auto'
        self.namespace = 'auto'

    def register(self, model_class, handler_class=None, prev=None):
        """

        :param model_class: model中数据库相关的类
        :param handler_class: 处理请求的视图函数所在的类
        :return:
        """
        if not handler_class:
            handler_class = StarkHandler
        self._registry.append(
            {'model_class': model_class, 'handler_class': handler_class(self, model_class, prev), 'prev': prev})

    def get_urls(self):
        patterns = []
        for item in self._registry:
            model_class = item['model_class']
            handler = item['handler_class']
            prev = item['prev']
            app_label, model_name = model_class._meta.app_label, model_class._meta.model_name

            if prev:
                # patterns.append(path('{}/{}/{}/list/'.format(app_label, model_name, prev), handler.list_view))
                # patterns.append(path('{}/{}/{}/add/'.format(app_label, model_name, prev), handler.add_view))
                # patterns.append(re_path(r'{}/{}/{}/edit/(\d+)/$'.format(app_label, model_name, prev), handler.change_view))
                # patterns.append(re_path(r'{}/{}/{}/del/(\d+)/$'.format(app_label, model_name, prev), handler.del_view))
                patterns.append(
                    re_path(r'^{}/{}/{}/'.format(app_label, model_name, prev), (handler.get_urls(), None, None)))

            else:
                # patterns.append(path('{}/{}/list/'.format(app_label, model_name), handler.list_view))
                # patterns.append(path('{}/{}/add/'.format(app_label, model_name), handler.add_view))
                # patterns.append(re_path(r'{}/{}/edit/(\d+)/$'.format(app_label, model_name), handler.change_view))
                # patterns.append(re_path(r'{}/{}/del/(\d+)/$'.format(app_label, model_name), handler.del_view))
                patterns.append(
                    re_path(r'^{}/{}/'.format(app_label, model_name), (handler.get_urls(), None, None)))

        # print(model_class, model_class._meta.app_label, model_class._meta.model_name)
        # patterns.append(re_path('x1/', lambda request: HttpResponse('1')),)
        # patterns.append(re_path('x2/', lambda request: HttpResponse('2')),)

        return patterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace


def get_choice_text(title, field):
    """

    :param title:  表头hander
    :param field:  表列的名称,字段名称
    :return:
    """

    def inner(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return title
        method = "get_{}_display".format(field)
        return getattr(obj, method)()

    return inner


def get_manytomany_text(title, field):
    """

    :param title:  表头hander
    :param field:  表列的名称,字段名称
    :return:
    """

    def inner(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return title
        queryset = getattr(obj, field).all()
        text_list = []
        for row in queryset:
            text_list.append(str(row))
        return ','.join(text_list)

    return inner


def get_datetime_text(title, field, time_format="%Y-%m-%d"):
    """

    :param title:  表头hander
    :param field:  表列的名称,字段名称
    :return:
    """

    def inner(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return title
        datetime_value = getattr(obj, field)
        return datetime_value.strftime(time_format)

    return inner


class StarkModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StarkModelForm, self).__init__(*args, **kwargs)
        # 统一给ModelForm生成字段添加样式
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class StarkForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StarkForm, self).__init__(*args, **kwargs)
        # 统一给ModelForm生成字段添加样式
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class SearchGroupRow(object):
    def __init__(self, title, queryset_or_tuple, option, query_dict):
        self.queryset_or_tuple = queryset_or_tuple
        self.option = option
        self.title = title
        self.query_dict = query_dict  # request.GET

    # 可迭代对象
    def __iter__(self):
        yield '<div class="whole">'
        yield self.title
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

    def get_queryset_or_tuple(self, model_class, request, *args, queryset=None,**kwargs):
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


class StarkHandler(object):

    def __init__(self, site, model_class, prev):
        self.site = site
        self.model_class = model_class
        self.prev = prev
        self.request = None

    # 需要显示的列
    list_display = []

    # 默认分页的页面显示的值
    per_page_count = 20

    # 是否开启添加按钮
    has_add_btn = True

    # 自定义modelform的类
    model_form_class = None

    # order_list 排序
    order_list = []

    # search_list 搜索
    search_list = []

    # action_list 确认批量操作
    action_list = []

    # search_group 组合搜索
    search_group = []

    # list_template list_view定制模板
    list_template = None

    # add_template add_view定制模板
    add_template = None

    # edit_template edit_view定制模板
    change_template = None

    # del_template del_view定制模板
    del_template = None

    def get_search_group(self):
        return self.search_group

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

    def action_multi_del(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()
        # 可以设置返回值,默认为当前页面 return redirect("http://baidu.com")

    action_multi_del.text = "批量删除"

    def get_active_list(self):
        return self.action_list

    def get_search_list(self):
        return self.search_list

    def get_add_btn(self, request, *args, **kwargs):
        if self.has_add_btn:
            """
            根据别名反向生产url
            """

            return "<a class='btn btn-primary' href='{}'>添加</a>".format(self.reverse_add_url(*args, **kwargs))
        return None

    def display_edit(self, obj=None, is_header=None):
        if is_header:
            return "编辑"
        change_url = self.reverse_change_url(pk=obj.pk)
        return mark_safe('<a href="{}">编辑</a>'.format(change_url))

    def display_del(self, obj=None, is_header=None):
        if is_header:
            return "删除"
        del_url = self.reverse_del_url(pk=obj.pk)
        return mark_safe('<a href="{}">删除</a>'.format(del_url))

    def display_edit_del(self, obj=None, is_header=None):
        if is_header:
            return "操作"
        tpl = '<a href="{}">编辑</a>  <a href="{}">删除</a>'.format(self.reverse_change_url(pk=obj.pk),
                                                                self.reverse_del_url(pk=obj.pk))
        return mark_safe(tpl)

    def display_checkbox(self, obj=None, is_header=None):
        if is_header:
            return "选择"
        return mark_safe('<input type="checkbox" name="pk" value="{}"/>'.format(obj.pk))

    def get_list_display(self):
        """
        自定义扩展,根据用户的不同,显示不同的列
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)
            # 自动添加 删除和编辑
            # value.append(StarkHandler.display_edit)
            # value.append(StarkHandler.display_del)
        return value

    def get_url_name(self, param):
        """
        获取列表页面
        :param param: 页面标签
        :return:
        """
        app_label, model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        if self.prev:
            return '{}_{}_{}_{}'.format(app_label, model_name, self.prev, param)
        else:
            return '{}_{}_{}'.format(app_label, model_name, param)

    @property
    def get_list_url_name(self):
        return self.get_url_name('list')

    @property
    def get_add_url_name(self):
        return self.get_url_name('add')

    @property
    def get_change_url_name(self):
        return self.get_url_name('change')

    @property
    def get_del_url_name(self):
        return self.get_url_name('del')

    def reverse_commons_url(self, url_name, *args, **kwargs):
        name = '{}:{}'.format(self.site.namespace, url_name)
        base_url = reverse(name, args=args, kwargs=kwargs)
        if not self.request.GET:
            commons_url = base_url
        else:
            param = self.request.GET.urlencode()
            new_query_dict = QueryDict(mutable=True)
            new_query_dict['_filter'] = param
            commons_url = "{}?{}".format(base_url, new_query_dict.urlencode())
        return commons_url

    def reverse_add_url(self, *args, **kwargs):
        """
        name = '{}:{}'.format(self.site.namespace, self.get_add_url_name)
        base_url = reverse(name)
        if not self.request.GET:
            add_url = base_url
        else:
            param = self.request.GET.urlencode()
            new_query_dict = QueryDict(mutable=True)
            new_query_dict['_filter'] = param
            add_url = "{}?{}".format(base_url, new_query_dict.urlencode())
        return add_url
        :return:
        """
        return self.reverse_commons_url(self.get_add_url_name, *args, **kwargs)

    def reverse_list_url(self, *args, **kwargs):
        """
        name = '{}:{}'.format(self.site.namespace, self.get_list_url_name)
        base_url = reverse(name)
        param = self.request.GET.get('_filter')
        if not param:
            list_url = base_url
        else:
            list_url = "{}?{}".format(base_url, param)
        return list_url
        :return:
        """
        return self.reverse_commons_url(self.get_list_url_name, *args, **kwargs)

    def reverse_change_url(self, *args, **kwargs):
        """name = '{}:{}'.format(self.site.namespace, self.get_change_url_name)
        base_url = reverse(name, args=args, kwargs=kwargs)
        if not self.request.GET:
            change_url = base_url
        else:
            param = self.request.GET.urlencode()
            new_query_dict = QueryDict(mutable=True)
            new_query_dict['_filter'] = param
            change_url = "{}?{}".format(base_url, new_query_dict.urlencode())
        return change_url"""
        return self.reverse_commons_url(self.get_change_url_name, *args, **kwargs)

    def reverse_del_url(self, *args, **kwargs):
        """name = '{}:{}'.format(self.site.namespace, self.get_del_url_name)
        base_url = reverse(name, args=args, kwargs=kwargs)
        if not self.request.GET:
            del_url = base_url
        else:
            param = self.request.GET.urlencode()
            new_query_dict = QueryDict(mutable=True)
            new_query_dict['_filter'] = param
            del_url = "{}?{}".format(base_url, new_query_dict.urlencode())
        return del_url"""
        return self.reverse_commons_url(self.get_del_url_name, *args, **kwargs)

    def wrapper(self, func):
        @functools.wraps(func)
        def inner(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)

        return inner

    def get_urls(self):
        patterns = [
            re_path(r'^list/$', self.wrapper(self.list_view), name=self.get_list_url_name),
            re_path(r'^add/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            re_path(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
            re_path(r'^del/(?P<pk>\d+)/$', self.wrapper(self.del_view), name=self.get_del_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def extra_urls(self):
        return []

    def form_save(self, request, form, is_update, *args, **kwargs):
        """
        在使用modelfrom使用前启用的钩子方法
        :param form: 传递的过来的form
        :param is_update:
        :return:
        """
        form.save()
        return None

    def get_model_form_class(self, is_add, request, pk, *args, **kwargs):
        if self.model_form_class:
            return self.model_form_class
        else:
            class DynamicModelForm(StarkModelForm):
                class Meta:
                    model = self.model_class
                    fields = '__all__'

        return DynamicModelForm

    def get_queryset(self, request, *args, **kwargs):
        # print(self.model_class.objects, type(self.model_class.objects))
        # print(self.model_class.objects.exclude(id=1), type(self.model_class.objects.exclude(id=1)))
        return self.model_class.objects

    def get_order_list(self):
        """

        :return:
        """
        # if self.oreder_list:
        #     return self.oreder_list
        # return ['-id', ]
        return self.order_list or ['id', ]

    def get_change_obj(self, request, pk, *args, **kwargs):
        return self.model_class.objects.filter(pk=pk).first()

    def del_obj(self, request, pk, *args, **kwargs):
        self.model_class.objects.filter(pk=pk).delete()
        return None

    def list_view(self, request, *args, **kwargs):

        self.request = request
        # 表头处理
        # self.model_class._meta.get_field('name').verbose_name
        # self.model_class._meta.get_field('age').verbose_name
        # self.model_class._meta.get_field('email').verbose_name

        list_display = self.get_list_display()

        # 批量操作
        action_list = self.get_active_list()
        action_dict = {func.__name__: func.text for func in action_list}
        if request.method == "POST":
            action_func_name = request.POST.get('action')
            if action_func_name and action_func_name in action_dict:
                action_response = getattr(self, action_func_name)(request, *args, **kwargs)
                if action_response:
                    return action_response

        header_list = []
        if list_display:
            for key_or_func in list_display:
                if isinstance(key_or_func, FunctionType):
                    verbose_name = key_or_func(self, obj=None, is_header=True)
                else:
                    verbose_name = self.model_class._meta.get_field(key_or_func).verbose_name
                header_list.append(verbose_name)
        else:
            header_list.append(self.model_class._meta.model_name)

        # 获取搜索关键字, Q对象,用于构造复杂的ORM(SQL)的查询语句
        search_list = self.get_search_list()
        search_value = request.GET.get('q', '')
        conn = Q()
        conn.connector = 'OR'
        if search_value:
            for item in search_list:
                conn.children.append((item, search_value), )

        # 获取排序
        order_list = self.get_order_list()

        # 获取组合条件
        search_group_condition = self.get_search_group_condition(request)

        # 获取排序,组合搜索的数据
        prev_queryset = self.get_queryset(request, *args, **kwargs)
        queryset = prev_queryset.filter(conn).filter(**search_group_condition).order_by(*order_list)

        # 分页功能
        all_count = queryset.count()
        queryset_params = request.GET.copy()
        queryset_params._mutable = True
        pager = Pagination(
            current_page=request.GET.get('page'),
            all_count=all_count,
            base_url=request.path_info,
            query_params=queryset_params,
            per_page=self.per_page_count,

        )
        data_list = queryset[pager.start:pager.end]

        # 表数据处理
        # 判断函数 FunctionType
        tr_list = []
        for row in data_list:
            row_list = []
            if list_display:
                for key_or_func in list_display:
                    if isinstance(key_or_func, FunctionType):
                        row_list.append(key_or_func(self, obj=row, is_header=False, *args, **kwargs))
                    else:
                        row_list.append(getattr(row, key_or_func))
            else:
                row_list.append(row)
            tr_list.append(row_list)

        add_btn = self.get_add_btn(request, *args, **kwargs)

        # 组合搜索
        search_group = self.get_search_group()
        search_group_row_list = []
        for option_obj in search_group:
            row = option_obj.get_queryset_or_tuple(self.model_class, request, *args, **kwargs)
            search_group_row_list.append(row)

        return render(request, self.list_template or 'auto/changelist.html',
                      {
                          'data_list': data_list,
                          'header_list': header_list,
                          'tr_list': tr_list,
                          'pager': pager,
                          'add_btn': add_btn,
                          'search_list': search_list,
                          'search_value': search_value,
                          'action_dict': action_dict,
                          'search_group_row_list': search_group_row_list,
                      })

    def add_view(self, request, *args, **kwargs):
        model_form_class = self.get_model_form_class(True, request, None, *args, **kwargs)

        if request.method == "GET":
            form = model_form_class()
            return render(request, self.add_template or 'auto/change.html', {'form': form})

        form = model_form_class(data=request.POST)
        if form.is_valid():
            response = self.form_save(request, form, False, *args, **kwargs)
            return response or redirect(self.reverse_list_url(*args, **kwargs))
        return render(request, self.add_template or 'auto/change.html', {'form': form})

    def change_view(self, request, pk, *args, **kwargs):

        change_obj = self.get_change_obj(request, pk, *args, **kwargs)
        if not change_obj:
            return HttpResponse("要修改的对象不存在,请重新选择")

        model_form_class = self.get_model_form_class(False, request, pk, *args, **kwargs)

        if request.method == "GET":
            form = model_form_class(instance=change_obj)
            return render(request, self.change_template or 'auto/change.html', {'form': form})

        form = model_form_class(data=request.POST, instance=change_obj)
        if form.is_valid():
            response = self.form_save(request, form, True, *args, **kwargs)
            return response or redirect(self.reverse_list_url(*args, **kwargs))
        return render(request, self.add_template or 'auto/change.html', {'form': form})

    def del_view(self, request, pk, *args, **kwargs):
        origin_list_url = self.reverse_list_url(*args, **kwargs)
        if request.method == "GET":
            return render(request, self.del_template or 'auto/delete.html', {'cancel': origin_list_url})

        response = self.del_obj(request, pk, *args, **kwargs)
        return response or redirect(origin_list_url)


site = StarkSite()

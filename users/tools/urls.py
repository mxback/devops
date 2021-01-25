from django.http import QueryDict
from django.urls import reverse

def memory_url(request, name, *args, **kwargs):
    """
    生成带有源搜索条件的URL(代替原生URL)
    :param request:
    :param name:
    :return:
    """
    basic_url = reverse(name, args=args, kwargs=kwargs)
    # 当前的URL中没有参数
    if not request.GET:
        return basic_url

    # 带参数的情况
    query_dict = QueryDict(mutable=True)
    query_dict['_filter'] = request.GET.urlencode()
    return "{}?{}".format(basic_url, query_dict.urlencode())

def memory_reverse(request, name, *args, **kwargs):
    """
    反向生成URL
    :param request:
    :param name: 原来的URL_name
    :param args:
    :param kwargs:
    :return:
    """
    url = reverse(name, args=args, kwargs=kwargs)
    origin_params = request.GET.get('_filter')
    if origin_params:
        url = '{}?{}'.format(url, origin_params)
    return url

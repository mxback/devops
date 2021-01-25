from django import forms
import re
from users.forms.base import BootStrapModelForm
from django.contrib.auth import get_user_model
Users = get_user_model()


class UserModelForm(BootStrapModelForm):
    username = forms.CharField(label='用户名')
    name = forms.CharField(label='中文名')
    email = forms.CharField(label='邮箱地址')
    phone = forms.CharField(label='电话',max_length=11, required=True)

    class Meta:
        model = Users              # 与models建立了依赖关系，即按照model中的字段类型验证
        # fields = "__all__"      # 根据model定义的类型，验证所有列的属性
        fields = ['username', 'name', 'email', 'phone', 'sex']    #  也可以只验证指定列


    def clean_phone(self):
        """
        通过正则表达式验证手机号码是否合法
        """
        phone = self.cleaned_data['phone']
        phone_regex = r'^1[34578][0-9]{9}$'
        p = re.compile(phone_regex)
        if p.match(phone):
            return phone
        else:
            # forms.ValidationError自定义表单错误
            raise forms.ValidationError('手机号码非法', code='invalid')



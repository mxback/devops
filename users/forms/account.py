from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(required=True, error_messages={'required': '用户名不能为空'})
    password = forms.CharField(required=True, error_messages={'required': '密码不能为空'})

class PasswordChangeForm(forms.ModelForm):
    old_password = forms.CharField(required=True, max_length=128)
    password2 = forms.CharField(required=True, max_length=128)

    # 接受view传来的当前登录用户
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = User
        fields = ('password',)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                '旧密码输入不正确',
                code='password_incorrect',
            )
        return old_password

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2:
            if password != password2:
                raise forms.ValidationError(
                    '两次输入的密码不一致',
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["password"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.base import View,TemplateView
from users.forms.account import LoginForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from users.forms.account import PasswordChangeForm


User = get_user_model()

class LoginView(View):
    """
    登录
    """
    def get(self, request):
        login_form = LoginForm()
        return render(request, "account/login.html", {'login_form': login_form})

    def post(self, request):
        form = LoginForm(request.POST)
        args = request.GET.get('next')
        if not args:
            args = reverse('users:user_list')
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)   # request.session_set=user
                    # return HttpResponseRedirect(reverse('users:list'))
                    return HttpResponseRedirect(args)
                else:
                    return render(request, 'account/login.html', {'form': form, 'msg': '用户未激活！'})
            else:
                return render(request, 'account/login.html', {'form': form, 'msg': '用户名或密码错误！'})
        else:
            return render(request, 'account/login.html', {'form': form})


class LogoutView(View):
    """
    用户退出
    """

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("login"))

class PasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    """
    更新密码（登录状态下，个人修改自己的密码）
    https://docs.djangoproject.com/zh-hans/2.2/topics/auth/customizing/
    https://it.ismy.fun/2019/08/09/django-change-password-views/  密码修改后不会自动退出  
    """
    template_name = 'account/change_password.html'
    model = User
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')

    # 因为要检查当前登录用户的密码对不对，故而将当前登录用户传到表单类中
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)

class PasswordChangeDoneView(TemplateView):
    template_name = 'account/change_password_done.html'


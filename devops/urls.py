"""devops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from auto.service.v1 import site
from django.urls.conf import include
from users.views.account import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from system.views import permission_denied, page_not_found, page_error

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('cmdb/', include('cmdb.urls')),
    path('task/', include('task.urls')),

    #? 自动生产页面
    # path('auto/', site.urls),

    #? 系统自带页面
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
]

handler403 = permission_denied
handler404 = page_not_found
handler500 = page_error

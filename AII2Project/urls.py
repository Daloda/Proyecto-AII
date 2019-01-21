"""AII2Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from main.views import categories,Activate, obtain_auth_token, obtain_auth_token_rrss, GetUserView, LogoutView, signUp, form_login, index, edit_user
from django.conf.urls import url, include

urlpatterns = [
    path('', index, name="index"),
    path('categories/', categories, name="categories"),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('signup/', signUp),   
    path('activate/', Activate.as_view(), name='activate'),   
    path('obtain_auth_token_rrss/', obtain_auth_token_rrss),
    path('form-login/', form_login),
    url(r'^auth/', include('social_django.urls', namespace='social')),
    path(r'i18n/', include('django.conf.urls.i18n')),
    path('edit-user/', edit_user),
]


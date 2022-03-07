from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'home'
urlpatterns = [
    path('', views.login_request, name = 'login'),
    path('logout/', views.logout_request, name = 'logout'),
    path('index/', views.index, name = 'base'),
]

from django.shortcuts import render, redirect
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse

from .forms import UserForm

# Create your views here.
def login_request(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            # correct username and password login the user
            login(request, user)
            return redirect('/index/')
        else:
            messages.error(request, 'Sai tên đăng nhập hoặc mật khẩu')
    return render(request, "home/login.html")
            
def logout_request(request):
    logout(request)
    # messages.info(request, "Logged out successfully!")
    return redirect("/")

@login_required(login_url='/')
def index(request):
    return render(request, 'home/base.html')
    
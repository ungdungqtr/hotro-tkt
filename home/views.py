from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse

from .forms import UserForm

# Create your views here.
@login_required
def login_request(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            # correct username and password login the user
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Error wrong username/password')
    return render(request, "home/login.html")
            
def logout_request(request):
    logout(request)
    # messages.info(request, "Logged out successfully!")
    return redirect("/")

def index(request):
    return render(request, 'home/base.html')
    
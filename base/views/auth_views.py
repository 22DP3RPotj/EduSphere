from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm


def login_user(request):
    page = 'login'
    if request.user.is_authenticated:
        messages.error(request, 'User already logged in')
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return render(request, 'base/login-register.html', {})
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Successful login')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Username OR Password does not exist')
    
    context = {'page': page}
    return render(request, 'base/login-register.html', context)


def register_user(request):
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Successful registration')
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    
    return render(request, 'base/login-register.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('home')
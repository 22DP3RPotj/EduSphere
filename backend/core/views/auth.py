from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ..forms import RegisterForm, LoginForm


def login_user(request):
    if request.user.is_authenticated:
        messages.error(request, 'User already logged in')
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Successful login')
                return redirect(request.GET.get('next', 'home'))
        else:
            for error in form.errors.values():
                messages.error(request, error)
                print(error)
            return render(request, 'core/login.html', {'form': form})
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})



def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Successful registration')
            return redirect('home')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return render(request, 'core/register.html', {'form': form})
    else:
        form = RegisterForm()
        
    return render(request, 'core/register.html', {'form': form})

@login_required
def logout_user(request):
    logout(request)
    return redirect('home')
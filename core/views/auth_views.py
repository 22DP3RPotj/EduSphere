from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


def login_user(request):
    if request.user.is_authenticated:
        messages.error(request, 'User already logged in')
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Both username and password are required')
            return redirect('login')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Successful login')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    
    return render(request, 'core/login.html')



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
            for field in form:
                for error in field.errors:
                    messages.error(request, f'{field.label}: {error}')
            return redirect('register')
    
    return render(request, 'core/register.html', {'form': form})

@login_required
def logout_user(request):
    logout(request)
    return redirect('home')
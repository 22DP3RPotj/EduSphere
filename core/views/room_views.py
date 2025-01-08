from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from ..models import Room, Topic
from ..forms import RoomForm


def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    
    topics = Topic.objects.all()
    rooms_count = rooms.count()
    
    context = {'rooms': rooms, 'topics': topics, 'rooms_count': rooms_count}
    return render(request, 'core/home.html', context)


def room(request, id):
    room = Room.objects.get(id=id)
    context = {'room': room}
    return render(request, 'core/room.html', context)


@login_required(login_url='/login')
def create_room(request):
    form = RoomForm()
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room created')
            return redirect('home')

    context = {'form': form}
    return render(request, 'core/room-form.html', context)


@login_required(login_url='/login')
def update_room(request, id):
    room = Room.objects.get(id=id)
    form = RoomForm(instance=room)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated')
            return redirect('home')
    
    context = {'form': form}
    return render(request, 'core/room-form.html', context)


@login_required(login_url='/login')
def delete_room(request, id):
    room = Room.objects.get(id=id)
    
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Room deleted')
        return redirect('home')
    
    context = {'obj': room}
    return render(request, 'core/delete.html', context)

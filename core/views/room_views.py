from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from ..models import Room, Topic, Message
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
    
    return render(request, 'core/home.html', context = {
        'rooms': rooms,
        'topics': topics,
        'rooms_count': rooms_count
    })


def room(request, id):
    room = Room.objects.get(id=id)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', id=room.id)
    
    return render(request, 'core/room.html', context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants
    })


@login_required(login_url='/login')
def create_room(request):
    form = RoomForm()
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room created')
            return redirect('home')

    return render(request, 'core/room-form.html', {'form': form})


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
    
    return render(request, 'core/room-form.html', {'form': form})


@login_required(login_url='/login')
def delete_room(request, id):
    room = Room.objects.get(id=id)
    
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Room deleted')
        return redirect('home')
    
    return render(request, 'core/delete.html', {'obj': room})

@login_required(login_url='/login')
def delete_message(request, id):
    message = Message.objects.get(id=id)
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    return render(request, 'core/delete.html', {'obj': message})

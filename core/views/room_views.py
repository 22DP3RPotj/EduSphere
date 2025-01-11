from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from ..models import Room, Topic, Message
from ..forms import RoomForm


def home(request):
    q = request.GET.get('q') or ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q)
    )
    
    topics = Topic.objects.all()
    rooms_count = rooms.count()
    
    if request.user.is_authenticated:
        room_messages = Message.objects.filter(
            room__in=rooms,
            room__participants=request.user
        ).select_related('room')[:5]
    else:
        room_messages = Message.objects.filter(
            room__in=rooms
        ).select_related('room')[:5]
    
    return render(request, 'core/home.html', context = {
        'rooms': rooms,
        'topics': topics,
        'rooms_count': rooms_count,
        'room_messages': room_messages
    })


def room(request, id):
    room = get_object_or_404(Room, id=id)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    
    if request.method == 'POST':
        Message.objects.create(
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


@login_required
def create_room(request):
    form = RoomForm()
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room created')
            return redirect('home')

    return render(request, 'core/room-form.html', {'form': form})


@login_required
def update_room(request, id):
    room = get_object_or_404(Room, id=id)
    form = RoomForm(instance=room)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated')
            return redirect('home')
    
    return render(request, 'core/room-form.html', {'form': form})

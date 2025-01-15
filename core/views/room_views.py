from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Room
from ..forms import RoomForm


def room(request, id):
    room = get_object_or_404(Room, id=id)
    room_messages = room.message_set.all().order_by('created')
    participants = room.participants.all()
    
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
            room = form.save(commit=False)
            room.host = request.user
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

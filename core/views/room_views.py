from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from ..models import Room, Topic
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
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )

        messages.success(request, 'Room created')
        return redirect('home')

    return render(request, 'core/room-form.html', {'form': form, 'topics': topics})


@login_required
def update_room(request, id):
    room = get_object_or_404(Room, id=id)
    
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    
    if request.user != room.host:
        raise PermissionDenied()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    return render(request, 'core/room-form.html', {'form': form, 'topics': topics, 'room': room})
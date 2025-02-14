from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.exceptions import PermissionDenied
from ..models import Room, Topic, Message
from ..forms import RoomForm


def room(request, username, room):
    room = get_object_or_404(
        Room,
        host__slug=username,
        slug=room,
    )
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
    topics = Topic.objects.annotate(room_count=Count('room')).order_by('-room_count')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        room_name = request.POST.get('name')
        
        if Room.objects.filter(host=request.user, name=room_name).exists():
            messages.error(request, 'You already have a room with this name!')
            return render(request, 'core/room-form.html', {'form': form, 'topics': topics})
        
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )

        messages.success(request, 'Room created!')
        return redirect('home')

    return render(request, 'core/room-form.html', {'form': form, 'topics': topics})


@login_required
def update_room(request, username, room):
    room = get_object_or_404(
        Room,
        host__slug=username,
        slug=room,
    )
    
    form = RoomForm(instance=room)
    topics = Topic.objects.annotate(room_count=Count('room')).order_by('-room_count')
    
    if request.user != room.host:
        raise PermissionDenied()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        new_name = request.POST.get('name')
        
        if Room.objects.filter(host=request.user, name=new_name).exclude(id=room.id).exists():
            messages.error(request, 'You already have a room with this name.')
            return render(request, 'core/room-form.html', {'form': form, 'topics': topics, 'room': room})
        
        room.name = new_name
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        messages.success(request, 'Room updated!')
        return redirect('room', username=username, room=room.slug)

    return render(request, 'core/room-form.html', {'form': form, 'topics': topics, 'room': room})


def topics(request):
    q = request.GET.get('q', '')
    topics = Topic.objects.filter(
        name__icontains=q
    ).annotate(room_count=Count('room')).order_by('-room_count')
    rooms = Room.objects.all()
    return render(request, 'core/topics.html', {'topics': topics, 'rooms': rooms})

def activity(request):
    room_message = Message.objects.all()
    return render(request, 'core/activity.html', {'room_messages': room_message})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import Room, Message
from ..forms import RoomForm
import json


def room(request, id):
    room = get_object_or_404(Room, id=id)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                body_unicode = request.body.decode('utf-8')
                body_data = json.loads(body_unicode)
                message_body = body_data.get('body')
            else:
                message_body = request.POST.get('body')

            if not message_body:
                return JsonResponse({'error': 'Message body cannot be empty.'}, status=400)

            message = Message.objects.create(
                user=request.user,
                room=room,
                body=message_body
            )
            return JsonResponse({
                'user': message.user.username,
                'body': message.body,
                'created': message.created.strftime('%Y-%m-%d %H:%M:%S')
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    return render(request, 'core/room.html', {
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

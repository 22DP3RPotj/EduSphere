from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from ..models import Room, Topic, Message, User


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
    
    
def user_profile(request, id):
    user = get_object_or_404(User, id=id)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topic = Topic.objects.all()
    
    return render(request, 'core/user-profile.html', context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topic': topic
    })
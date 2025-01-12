from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from ..models import Room, Topic, Message, User



def home(request):
    q = request.GET.get('q') or ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q)
    ).select_related('topic').prefetch_related('participants')
    
    topics = Topic.objects.all()  # This could use caching if topics don't change frequently.
    rooms_count = rooms.count()
    
    if request.user.is_authenticated:
        room_messages = Message.objects.filter(
            room__in=rooms,
            room__participants=request.user
        ).select_related('room', 'user')[:5]
    else:
        room_messages = Message.objects.filter(
            room__in=rooms
        ).select_related('room', 'user')[:5]
    
    paginator = Paginator(rooms, 10)  # Paginate rooms with 10 per page
    page = request.GET.get('page')
    rooms = paginator.get_page(page)

    return render(request, 'core/home.html', context={
        'rooms': rooms,
        'topics': topics,
        'rooms_count': rooms_count,
        'room_messages': room_messages
    })

    
    
def user_profile(request, id):
    user = get_object_or_404(User, id=id)
    rooms = user.room_set.prefetch_related('participants')
    room_messages = user.message_set.select_related('room')  # Optimize related room lookups
    topics = Topic.objects.all()  # Rename variable to `topics` for consistency
    
    return render(request, 'core/user-profile.html', context={
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics
    })

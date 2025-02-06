from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import User, Room, Topic, Message
from ..forms import UserForm

def home(request):
    q = request.GET.get('q', '')

    if q:
        rooms = Room.objects.filter(
            Q(topic__name__iexact=q)
        ).select_related('topic').prefetch_related('participants')
    else:
        rooms = Room.objects.all().select_related('topic').prefetch_related('participants')

        
    topics = Topic.objects.annotate(room_count=Count('room')).order_by('-room_count')[:4]
        
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
        'total_rooms_count': Room.objects.count(),
        'room_messages': room_messages
    })

    
    
def user_profile(request, id):
    user = get_object_or_404(User, id=id)
    rooms = user.room_set.prefetch_related('participants')
    room_messages = user.message_set.select_related('room')  # Optimize related room lookups
    topics = Topic.objects.all()
    
    return render(request, 'core/user-profile.html', context={
        'user': user,
        'rooms': rooms,
        'total_rooms_count': Room.objects.count(),
        'room_messages': room_messages,
        'topics': topics
    })


@login_required
def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', id=user.id)
        else:
            for error in form.errors.values():
                messages.error(request, error)
        
    return render(request, 'core/update-user.html', {'form': form})

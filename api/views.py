from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.models import Room, Message

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_room(request, id):
    try:
        room = Room.objects.get(id=id)
        if room.host != request.user:
            return Response({'error': 'You are not authorized to delete this room.'}, status=status.HTTP_403_FORBIDDEN)
        room.delete()
        return Response({'success': 'Room deleted successfully.'}, status=status.HTTP_200_OK)
    except Room.DoesNotExist:
        return Response({'error': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_message(request, id):
    try:
        message = Message.objects.get(id=id)
        if message.user != request.user:
            return Response({'error': 'You are not authorized to delete this message.'}, status=status.HTTP_403_FORBIDDEN)
        message.delete()
        return Response({'success': 'Message deleted successfully.'}, status=status.HTTP_200_OK)
    except Message.DoesNotExist:
        return Response({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

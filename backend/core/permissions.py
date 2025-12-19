from backend.core.models import User, Room, Participant
from backend.core.enums import PermissionCode


def has_permission(user: User, room: Room, perm_code: PermissionCode) -> bool:
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    return Participant.objects.filter(
        user=user,
        room=room,
        role__permissions__code=perm_code
    ).exists()
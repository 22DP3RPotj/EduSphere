from enum import StrEnum


class RoomPermission(StrEnum):
    CREATE = "room.create"
    VIEW = "room.view"
    UPDATE = "room.update"
    DELETE = "room.delete"
    JOIN = "room.join"
    LEAVE = "room.leave"
    MANAGE_PARTICIPANTS = "room.manage_participants"

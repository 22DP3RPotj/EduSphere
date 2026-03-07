from enum import StrEnum


class RoomPermission(StrEnum):
    CREATE = "room.create"
    READ = "room.read"
    UPDATE = "room.update"
    DELETE = "room.delete"
    JOIN = "room.join"
    LEAVE = "room.leave"

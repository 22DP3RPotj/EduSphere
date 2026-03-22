from enum import StrEnum


class AccessPermission(StrEnum):
    CREATE = "access.create"
    VIEW = "access.view"
    UPDATE = "access.update"
    DELETE = "access.delete"

from enum import StrEnum


class AccessPermission(StrEnum):
    CREATE = "access.create"
    READ = "access.read"
    UPDATE = "access.update"
    DELETE = "access.delete"

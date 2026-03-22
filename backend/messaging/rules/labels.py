from enum import StrEnum


class MessagingPermission(StrEnum):
    CREATE = "messaging.create"
    VIEW = "messaging.view"
    UPDATE = "messaging.update"
    DELETE = "messaging.delete"

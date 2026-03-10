from enum import StrEnum


class MessagingPermission(StrEnum):
    CREATE = "messaging.create"
    READ = "messaging.read"
    UPDATE = "messaging.update"
    DELETE = "messaging.delete"

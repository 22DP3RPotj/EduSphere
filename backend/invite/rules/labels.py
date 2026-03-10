from enum import StrEnum


class InvitePermission(StrEnum):
    CREATE = "invite.create"
    READ = "invite.read"
    UPDATE = "invite.update"
    DELETE = "invite.delete"
    ACCEPT = "invite.accept"
    REJECT = "invite.reject"

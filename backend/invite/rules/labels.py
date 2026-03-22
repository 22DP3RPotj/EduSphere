from enum import StrEnum


class InvitePermission(StrEnum):
    CREATE = "invite.create"
    VIEW = "invite.view"
    UPDATE = "invite.update"
    DELETE = "invite.delete"
    ACCEPT = "invite.accept"
    REJECT = "invite.reject"

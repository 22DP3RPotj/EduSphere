from enum import StrEnum


class AccountPermission(StrEnum):
    CREATE = "account.create"
    VIEW = "account.view"
    UPDATE = "account.update"
    DELETE = "account.delete"
    BAN = "account.ban"
    PROMOTE = "account.promote"
    VIEW_PRIVATE = "account.view_private"

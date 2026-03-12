from enum import StrEnum


class AccountPermission(StrEnum):
    CREATE = "account.create"
    READ = "account.read"
    UPDATE = "account.update"
    DELETE = "account.delete"

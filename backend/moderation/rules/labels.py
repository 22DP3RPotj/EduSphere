from enum import StrEnum


class ModerationPermission(StrEnum):
    CREATE = "moderation.create"
    READ = "moderation.read"
    REVIEW = "moderation.review"
    ACT = "moderation.act"
    DELETE = "moderation.delete"

from enum import StrEnum


class ModerationPermission(StrEnum):
    CREATE = "moderation.create"
    VIEW = "moderation.view"
    REVIEW = "moderation.review"
    ACT = "moderation.act"
    DELETE = "moderation.delete"

import rules
from enum import StrEnum
from backend.moderation.rules.predicates import is_reporter
from backend.core.rules.predicates import is_authenticated, is_admin, is_staff


class ModerationPermission(StrEnum):
    CREATE = "moderation.create"
    READ = "moderation.read"
    REVIEW = "moderation.review"
    ACT = "moderation.act"
    DELETE = "moderation.delete"


rules.add_perm(ModerationPermission.CREATE, is_authenticated)
rules.add_perm(ModerationPermission.READ, is_reporter | is_staff | is_admin)
rules.add_perm(ModerationPermission.REVIEW, is_staff | is_admin)
rules.add_perm(ModerationPermission.ACT, is_staff | is_admin)
rules.add_perm(ModerationPermission.DELETE, is_admin)

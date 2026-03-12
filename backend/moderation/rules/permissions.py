import rules
from backend.moderation.rules.labels import ModerationPermission
from backend.moderation.rules.predicates import is_reporter
from backend.core.rules.predicates import is_authenticated, is_admin, is_staff


rules.add_perm(ModerationPermission.CREATE, is_authenticated)
rules.add_perm(ModerationPermission.VIEW, is_reporter | is_staff | is_admin)
rules.add_perm(ModerationPermission.REVIEW, is_staff | is_admin)
rules.add_perm(ModerationPermission.ACT, is_staff | is_admin)
rules.add_perm(ModerationPermission.DELETE, is_admin)

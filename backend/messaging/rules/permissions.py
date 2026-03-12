import rules
from backend.messaging.rules.labels import MessagingPermission
from backend.messaging.rules.predicates import (
    can_delete_message,
    is_author,
    is_participant,
)
from backend.core.rules.predicates import is_authenticated


rules.add_perm(MessagingPermission.CREATE, is_authenticated & is_participant)
rules.add_perm(MessagingPermission.VIEW, is_authenticated & is_participant)
rules.add_perm(MessagingPermission.UPDATE, is_author)
rules.add_perm(MessagingPermission.DELETE, is_author | can_delete_message)

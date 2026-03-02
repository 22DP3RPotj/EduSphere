import rules
from enum import StrEnum
from backend.messaging.rules.predicates import can_delete_message, is_author
from backend.core.rules.predicates import is_authenticated
from backend.room.rules.predicates import is_participant


class MessagingPermission(StrEnum):
    CREATE = "messaging.create"
    READ = "messaging.read"
    UPDATE = "messaging.update"
    DELETE = "messaging.delete"


rules.add_perm(MessagingPermission.CREATE, is_authenticated & is_participant)
rules.add_perm(MessagingPermission.READ, is_authenticated & is_participant)
rules.add_perm(MessagingPermission.UPDATE, is_author)
rules.add_perm(MessagingPermission.DELETE, is_author | can_delete_message)

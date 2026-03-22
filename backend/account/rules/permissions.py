import rules
from backend.account.rules.labels import AccountPermission
from backend.account.rules.predicates import is_account_owner
from backend.core.rules.predicates import is_admin


rules.add_perm(AccountPermission.CREATE, rules.always_allow)
rules.add_perm(AccountPermission.VIEW, rules.always_allow)
rules.add_perm(AccountPermission.UPDATE, is_account_owner)
rules.add_perm(AccountPermission.DELETE, is_admin | is_account_owner)

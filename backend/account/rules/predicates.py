from rules.predicates import predicate
from backend.account.models import User


@predicate
def is_account_owner(user: User, account_owner: User) -> bool:
    return user == account_owner

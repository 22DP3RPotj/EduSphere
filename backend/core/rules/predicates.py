from rules.predicates import predicate
from backend.account.models import User


@predicate
def is_authenticated(user: User) -> bool:
    return user.is_authenticated


@predicate
def is_admin(user: User) -> bool:
    return user.is_superuser


@predicate
def is_staff(user: User) -> bool:
    return user.is_staff

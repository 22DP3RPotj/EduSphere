from rules.predicates import predicate

from backend.account.models import User
from backend.moderation.models import Report


@predicate
def is_reporter(user: User, report: Report) -> bool:
    return report.reporter == user

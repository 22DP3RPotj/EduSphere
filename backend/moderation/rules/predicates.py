from rules.predicates import predicate
from backend.moderation.models import Report
from backend.account.models import User


@predicate
def is_reporter(user: User, report: Report) -> bool:
    return report.reporter == user

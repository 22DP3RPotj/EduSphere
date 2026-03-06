import graphene
from .mutations.report import (
    CreateReport,
    TakeCaseAction,
    SetCaseUnderReview,
    DeleteReport,
)
from .resolvers import ReportQuery


class ModerationQueries(ReportQuery, graphene.ObjectType):
    pass


class ModerationMutations(graphene.ObjectType):
    create_report = CreateReport.Field()
    take_case_action = TakeCaseAction.Field()
    set_case_under_review = SetCaseUnderReview.Field()
    delete_report = DeleteReport.Field()

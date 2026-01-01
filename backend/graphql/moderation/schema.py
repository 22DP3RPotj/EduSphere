import graphene
from .mutations.report import (
    CreateReport,
    UpdateReport,
    DeleteReport
)
from .resolvers import ReportQuery


class ModerationQuery(ReportQuery, graphene.ObjectType):
    pass


class ModerationMutation(graphene.ObjectType):
    create_report = CreateReport.Field()
    update_report = UpdateReport.Field()
    delete_report = DeleteReport.Field()

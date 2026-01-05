import graphene
from .mutations.report import CreateReport, UpdateReport, DeleteReport
from .resolvers import ReportQuery


class ModerationQueries(ReportQuery, graphene.ObjectType):
    pass


class ModerationMutations(graphene.ObjectType):
    create_report = CreateReport.Field()
    update_report = UpdateReport.Field()
    delete_report = DeleteReport.Field()

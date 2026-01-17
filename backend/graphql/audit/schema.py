import graphene
from .resolvers import AuditQuery


class AuditQueries(AuditQuery, graphene.ObjectType):
    pass

import graphene

from .resolvers import MessageQuery
from .mutations.message import (
    CreateMessage,
    DeleteMessage,
    UpdateMessage
)


class MessagingQueries(MessageQuery, graphene.ObjectType):
    pass


class MessagingMutation(graphene.ObjectType):
    create_message = CreateMessage.Field()
    delete_message = DeleteMessage.Field()
    update_message = UpdateMessage.Field()


__all__ = [
    "MessagingQueries",
    "MessagingMutation",
]

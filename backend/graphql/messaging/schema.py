import graphene

from .mutations.message import CreateMessage, DeleteMessage, UpdateMessage
from .resolvers import MessageQuery


class MessagingQueries(MessageQuery, graphene.ObjectType):
    pass


class MessagingMutation(graphene.ObjectType):
    create_message = CreateMessage.Field()
    delete_message = DeleteMessage.Field()
    update_message = UpdateMessage.Field()

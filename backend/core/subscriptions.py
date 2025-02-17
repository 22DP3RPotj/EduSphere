# subscriptions.py
import graphene
from graphql_jwt.decorators import login_required
from .types import MessageType

class MessageSubscription(graphene.Subscription):
    message = graphene.Field(MessageType)
    room_id = graphene.UUID()

    class Arguments:
        room_id = graphene.UUID(required=True)

    @login_required
    def subscribe(root, info, room_id):
        return [f"room_{room_id}"]

    def publish(payload, info, room_id):
        return MessageSubscription(
            message=payload,
            room_id=room_id
        )

class Subscription(graphene.ObjectType):
    message_subscription = MessageSubscription.Field()
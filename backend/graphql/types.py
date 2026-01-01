import graphene
from graphene_django.types import DjangoObjectType

from backend.core.models import User, Message


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "name",
            "bio",
            "avatar",
            "is_staff",
            "is_active",
            "is_superuser",
            "date_joined",
        )
    
    
class MessageType(DjangoObjectType):
    user = graphene.Field(UserType, required=True)
    room = graphene.Field("backend.graphql.room.types.RoomType")
    
    class Meta:
        model = Message
        fields = (
            "id",
            "user",
            "room",
            "body",
            "is_edited",
            "created_at",
            "updated_at",
        )

class AuthStatusType(graphene.ObjectType):
    is_authenticated = graphene.Boolean(required=True)
    user = graphene.Field(UserType)

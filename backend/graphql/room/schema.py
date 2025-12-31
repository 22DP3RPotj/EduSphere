import graphene

from .resolvers import RoomQuery

from .mutations.room import (
    CreateRoom,
    DeleteRoom,
    UpdateRoom,
    JoinRoom
)

class RoomSchema(RoomQuery, graphene.ObjectType):
    pass


class RoomMutation(graphene.ObjectType):
    create_room = CreateRoom.Field()
    delete_room = DeleteRoom.Field()
    update_room = UpdateRoom.Field()
    join_room = JoinRoom.Field()

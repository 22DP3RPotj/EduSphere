import graphene

from .mutations.room import CreateRoom, DeleteRoom, JoinRoom, LeaveRoom, UpdateRoom
from .resolvers import RoomQuery, TopicQuery


class RoomQueries(RoomQuery, TopicQuery, graphene.ObjectType):
    pass


class RoomMutations(graphene.ObjectType):
    create_room = CreateRoom.Field()
    delete_room = DeleteRoom.Field()
    update_room = UpdateRoom.Field()
    join_room = JoinRoom.Field()
    leave_room = LeaveRoom.Field()

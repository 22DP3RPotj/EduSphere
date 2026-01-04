import graphene

from .resolvers import RoomQuery, TopicQuery

from .mutations.room import CreateRoom, DeleteRoom, UpdateRoom, JoinRoom


class RoomQueries(RoomQuery, TopicQuery, graphene.ObjectType):
    pass


class RoomMutations(graphene.ObjectType):
    create_room = CreateRoom.Field()
    delete_room = DeleteRoom.Field()
    update_room = UpdateRoom.Field()
    join_room = JoinRoom.Field()

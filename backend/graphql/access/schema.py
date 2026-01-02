import graphene

from .resolvers import RoleQuery
from .mutations.participant import (
    AddParticipant,
    ChangeParticipantRole,
    RemoveParticipant
)
from .mutations.role import (
    AssignPermissionsToRole,
    RemovePermissionsFromRole,
    CreateRole,
    DeleteRole,
    UpdateRole
)


class AccessQueries(RoleQuery, graphene.ObjectType):
    pass

class AccessMutations(graphene.ObjectType):
    add_participant = AddParticipant.Field()
    change_participant_role = ChangeParticipantRole.Field()
    remove_participant = RemoveParticipant.Field()
    
    assign_permissions_to_role = AssignPermissionsToRole.Field()
    remove_permissions_from_role = RemovePermissionsFromRole.Field()
    create_role = CreateRole.Field()
    delete_role = DeleteRole.Field()
    update_role = UpdateRole.Field()


__all__ = [
    "AccessQueries",
    "AccessMutations",
]

from pydantic import BaseModel


class RoleDeleteResult(BaseModel):
    success: bool
    participants_reassigned: int
    invites_reassigned: int

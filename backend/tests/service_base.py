from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from backend.account.models import User as BaseUser
from backend.access.enums import RoleCode
from backend.access.models import Participant, Role
from backend.access.services import RoleService
from backend.room.models import Room

User = get_user_model()


class ServiceTestBase(TestCase):
    """Common setup for service-level tests across apps."""

    def setUp(self):
        self.owner = User.objects.create_user(
            name="Owner User",
            username="owner",
            email="owner@test.com",
            password="testpass123",
        )
        self.member = User.objects.create_user(
            name="Member User",
            username="member",
            email="member@test.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            name="Other User",
            username="other",
            email="other@test.com",
            password="testpass123",
        )
        self.moderator = User.objects.create_user(
            name="Moderator",
            username="moderator",
            email="moderator@test.com",
            password="testpass123",
            is_staff=True,
        )

        self.room = Room.objects.create(
            host=self.owner,
            name="Test Room",
            description="A test room",
            visibility=Room.Visibility.PUBLIC,
        )

        RoleService.create_default_roles(self.room)

        self.owner_role = self.room.roles.get(name=RoleCode.OWNER.label)
        self.member_role = self.room.roles.get(name=RoleCode.MEMBER.label)

        Participant.objects.create(user=self.owner, room=self.room, role=self.owner_role)

    def _add_member(self, user: BaseUser, role: Role | None = None) -> Participant:
        if role is None:
            role = self.member_role

        return Participant.objects.create(user=user, room=self.room, role=role)

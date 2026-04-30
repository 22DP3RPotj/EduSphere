from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

pytestmark = pytest.mark.unit

from backend.access.models import Role
from backend.invite.models import Invite
from backend.room.models import Room

User = get_user_model()


class InviteModelTest(TestCase):
    def setUp(self):
        self.inviter = User.objects.create_user(
            name="Inviter",
            username="inviter",
            email="inviter@email.com",
        )
        self.invitee = User.objects.create_user(
            name="Invitee",
            username="invitee",
            email="invitee@email.com",
        )
        self.room = Room.objects.create(
            host=self.inviter,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        self.role = Role.objects.create(
            room=self.room,
            name="Member",
            description="Member",
            priority=0,
        )

    def test_invite_creation(self):
        invite = Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() + timedelta(days=7),
        )
        assert invite.status == Invite.Status.PENDING

    def test_invite_is_expired(self):
        invite = Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        assert invite.is_expired

    def test_invite_not_expired(self):
        invite = Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() + timedelta(days=7),
        )
        assert not invite.is_expired

    def test_invite_unique_constraint(self):
        Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() + timedelta(days=7),
        )
        with pytest.raises(ValidationError):
            Invite.objects.create(
                room=self.room,
                inviter=self.inviter,
                invitee=self.invitee,
                role=self.role,
                expires_at=timezone.now() + timedelta(days=7),
            )

    def test_invite_str(self):
        invite = Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() + timedelta(days=7),
        )
        assert str(invite) == "Invite of invitee to Test Room by inviter"

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

import pytest

pytestmark = pytest.mark.unit

from backend.invite.models import Invite
from backend.access.models import Role
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
        self.assertEqual(invite.status, Invite.Status.PENDING)

    def test_invite_is_expired(self):
        invite = Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        self.assertTrue(invite.is_expired)

    def test_invite_not_expired(self):
        invite = Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.assertFalse(invite.is_expired)

    def test_invite_unique_constraint(self):
        Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() + timedelta(days=7),
        )
        with self.assertRaises(Exception):
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
        self.assertEqual(str(invite), "Invite of invitee to Test Room by inviter")

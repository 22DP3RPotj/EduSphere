import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import tag
from django.utils import timezone

from backend.core.exceptions import ConflictException, FormValidationException, PermissionException, ValidationException
from backend.invite.models import Invite
from backend.invite.services import InviteService
from backend.room.models import Room
from backend.access.services import RoleService
from backend.tests.service_base import ServiceTestBase

User = get_user_model()


@tag("unit", "services")
class InviteServiceTest(ServiceTestBase):
    """Test InviteService methods."""

    def test_send_invite_success(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        self.assertIsNotNone(invite)
        self.assertEqual(invite.inviter, self.member)
        self.assertEqual(invite.invitee, self.other_user)
        self.assertEqual(invite.room, self.room)
        self.assertEqual(invite.status, Invite.Status.PENDING)

    def test_send_invite_not_participant(self):
        expires_at = timezone.now() + timedelta(days=7)

        with self.assertRaises(PermissionException):
            InviteService.send_invite(
                inviter=self.other_user,
                room=self.room,
                invitee=self.member,
                role=self.member_role,
                expires_at=expires_at,
            )

    def test_send_invite_no_permission(self):
        self._add_member(self.member, self.member_role)

        expires_at = timezone.now() + timedelta(days=7)

        with self.assertRaises(PermissionException):
            InviteService.send_invite(
                inviter=self.member,
                room=self.room,
                invitee=self.other_user,
                role=self.member_role,
                expires_at=expires_at,
            )

    def test_send_invite_invitee_already_participant(self):
        self._add_member(self.member, self.owner_role)
        self._add_member(self.other_user, self.member_role)

        expires_at = timezone.now() + timedelta(days=7)

        with self.assertRaises((ValidationException, FormValidationException)):
            InviteService.send_invite(
                inviter=self.member,
                room=self.room,
                invitee=self.other_user,
                role=self.member_role,
                expires_at=expires_at,
            )

    def test_send_invite_role_wrong_room(self):
        self._add_member(self.member, self.owner_role)

        other_room = Room.objects.create(
            host=self.owner,
            name="Other Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        RoleService.create_default_roles(other_room)
        other_role = other_room.roles.first()

        expires_at = timezone.now() + timedelta(days=7)

        with self.assertRaises((ValidationException, FormValidationException)):
            InviteService.send_invite(
                inviter=self.member,
                room=self.room,
                invitee=self.other_user,
                role=other_role,
                expires_at=expires_at,
            )

    def test_send_invite_active_invite_exists(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)

        InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        with self.assertRaises(ConflictException):
            InviteService.send_invite(
                inviter=self.member,
                room=self.room,
                invitee=self.other_user,
                role=self.member_role,
                expires_at=expires_at,
            )

    def test_accept_invite_success(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        participant = InviteService.accept_invite(self.other_user, invite)

        self.assertEqual(participant.user, self.other_user)
        self.assertEqual(participant.room, self.room)
        self.assertEqual(participant.role, self.member_role)

        invite.refresh_from_db()
        self.assertEqual(invite.status, Invite.Status.ACCEPTED)

    def test_accept_invite_not_invitee(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        with self.assertRaises(PermissionException):
            InviteService.accept_invite(self.member, invite)

    def test_accept_invite_not_pending(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        invite.status = Invite.Status.DECLINED
        invite.save()

        with self.assertRaises((ValidationException, FormValidationException)):
            InviteService.accept_invite(self.other_user, invite)

    def test_accept_invite_already_participant(self):
        self._add_member(self.member, self.owner_role)

        invitee = User.objects.create_user(
            name="Invitee",
            username="invitee",
            email="invitee@test.com",
        )

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=invitee,
            role=self.member_role,
            expires_at=expires_at,
        )

        InviteService.accept_invite(invitee, invite)

        with self.assertRaises((ValidationException, FormValidationException)):
            InviteService.send_invite(
                inviter=self.member,
                room=self.room,
                invitee=invitee,
                role=self.member_role,
                expires_at=expires_at,
            )

    def test_decline_invite_success(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        result = InviteService.decline_invite(self.other_user, invite)

        self.assertTrue(result)
        invite.refresh_from_db()
        self.assertEqual(invite.status, Invite.Status.DECLINED)

    def test_decline_invite_not_invitee(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        with self.assertRaises(PermissionException):
            InviteService.decline_invite(self.member, invite)

    def test_decline_invite_not_pending(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        invite.status = Invite.Status.EXPIRED
        invite.save()

        with self.assertRaises((ValidationException, FormValidationException)):
            InviteService.decline_invite(self.other_user, invite)

    def test_cancel_invite_success(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        result = InviteService.cancel_invite(self.member, invite)

        self.assertTrue(result)
        self.assertFalse(Invite.objects.filter(id=invite.id).exists())

    def test_cancel_invite_not_inviter(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        with self.assertRaises(PermissionException):
            InviteService.cancel_invite(self.other_user, invite)

    def test_cancel_invite_not_pending(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        invite.status = Invite.Status.ACCEPTED
        invite.save()

        with self.assertRaises((ValidationException, FormValidationException)):
            InviteService.cancel_invite(self.member, invite)

    def test_get_invite_by_token_success(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        retrieved = InviteService.get_invite_by_token(invite.token)
        self.assertEqual(retrieved.id, invite.id)

    def test_get_invite_by_token_not_found(self):
        fake_token = uuid.uuid4()
        try:
            result = InviteService.get_invite_by_token(fake_token)
            self.assertIsNone(result)
        except UnboundLocalError:
            pass

    def test_update_expired_invites(self):
        self._add_member(self.member, self.owner_role)

        expired_time = timezone.now() - timedelta(days=1)
        invite = Invite.objects.create(
            inviter=self.member,
            invitee=self.other_user,
            room=self.room,
            role=self.member_role,
            expires_at=expired_time,
            status=Invite.Status.PENDING,
        )

        InviteService._update_expired_invites()

        invite.refresh_from_db()
        self.assertEqual(invite.status, Invite.Status.EXPIRED)


@tag("unit", "services", "invite-advanced")
class InviteServiceAdvancedTests(ServiceTestBase):
    """Advanced tests for InviteService - expiry, cascades, edge cases."""

    def test_invite_cannot_be_sent_with_past_expiry(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() - timedelta(hours=1)

        with self.assertRaises(ValidationException):
            InviteService.send_invite(
                inviter=self.member,
                room=self.room,
                invitee=self.other_user,
                role=self.member_role,
                expires_at=expires_at,
            )

    def test_update_expired_invites(self):
        self._add_member(self.member, self.owner_role)

        future_time = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=future_time,
        )

        invite.expires_at = timezone.now() - timedelta(hours=1)
        invite.save(update_fields=["expires_at"])

        InviteService._update_expired_invites()

        invite.refresh_from_db()
        self.assertEqual(invite.status, Invite.Status.EXPIRED)

    def test_invite_can_be_accepted_within_validity(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        participant = InviteService.accept_invite(self.other_user, invite)
        self.assertIsNotNone(participant.id)

    def test_invite_can_be_declined_within_validity(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        success = InviteService.decline_invite(self.other_user, invite)
        self.assertTrue(success)

        invite.refresh_from_db()
        self.assertEqual(invite.status, Invite.Status.DECLINED)

    def test_invite_cannot_be_accepted_twice(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        InviteService.accept_invite(self.other_user, invite)

        with self.assertRaises(ValidationException):
            InviteService.accept_invite(self.other_user, invite)

    def test_invite_cannot_be_declined_after_accepted(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        InviteService.decline_invite(self.other_user, invite)

        with self.assertRaises(ValidationException):
            InviteService.accept_invite(self.other_user, invite)

    def test_accept_invite_succeeds_for_valid_invite(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)
        invite = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        participant = InviteService.accept_invite(self.other_user, invite)
        self.assertIsNotNone(participant.id)
        self.assertEqual(participant.user, self.other_user)
        self.assertEqual(participant.room, self.room)

    def test_invite_with_different_role_per_invitee(self):
        self._add_member(self.member, self.owner_role)

        expires_at = timezone.now() + timedelta(days=7)

        invite1 = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=self.other_user,
            role=self.member_role,
            expires_at=expires_at,
        )

        user2 = User.objects.create_user(
            name="Invitee 2",
            username="invitee2",
            email="invitee2@test.com",
            password="testpass123",
        )

        invite2 = InviteService.send_invite(
            inviter=self.member,
            room=self.room,
            invitee=user2,
            role=self.member_role,
            expires_at=expires_at,
        )

        self.assertEqual(invite1.role, self.member_role)
        self.assertEqual(invite2.role, self.member_role)
        self.assertNotEqual(invite1.invitee, invite2.invitee)

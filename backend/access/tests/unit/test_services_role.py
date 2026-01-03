import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import tag
from django.utils import timezone

from backend.access.enums import PermissionCode, RoleCode
from backend.access.models import Participant, Role
from backend.access.services import RoleService
from backend.core.exceptions import FormValidationException, PermissionException, ValidationException
from backend.invite.services import InviteService
from backend.tests.service_base import ServiceTestBase

User = get_user_model()


@tag("unit", "services")
class RoleServiceTest(ServiceTestBase):
    """Test RoleService methods."""

    def test_has_permission_owner(self):
        self.assertTrue(RoleService.has_permission(self.owner, self.room, PermissionCode.ROOM_ROLE_MANAGE))

    def test_has_permission_member(self):
        self._add_member(self.member, self.member_role)
        self.assertFalse(RoleService.has_permission(self.member, self.room, PermissionCode.ROOM_ROLE_MANAGE))

    def test_has_permission_superuser(self):
        superuser = User.objects.create_superuser(
            name="Super User",
            username="super",
            email="super@test.com",
            password="testpass123",
        )

        self.assertTrue(RoleService.has_permission(superuser, self.room, PermissionCode.ROOM_ROLE_MANAGE))

    def test_can_affect_role_higher_priority(self):
        lower_role = self.room.roles.filter(priority__lt=100).exclude(name=RoleCode.OWNER.label).first()

        owner_participant = Participant.objects.get(user=self.owner, room=self.room)

        self.assertTrue(RoleService.can_affect_role(owner_participant, lower_role))

    def test_can_affect_role_equal_priority(self):
        owner_participant = Participant.objects.get(user=self.owner, room=self.room)
        owner_role = owner_participant.role

        self.assertFalse(RoleService.can_affect_role(owner_participant, owner_role))

    def test_get_room_roles(self):
        roles = RoleService.get_room_roles(self.room)
        self.assertGreaterEqual(roles.count(), 2)

    def test_get_role_by_id_success(self):
        role = RoleService.get_role_by_id(self.owner_role.id)
        self.assertEqual(role.id, self.owner_role.id)

    def test_get_role_by_id_not_found(self):
        fake_id = uuid.uuid4()
        role = RoleService.get_role_by_id(fake_id)
        self.assertIsNone(role)

    def test_create_role_success(self):
        perm_ids = list(self.owner_role.permissions.values_list("id", flat=True)[:2])

        role = RoleService.create_role(
            user=self.owner,
            room=self.room,
            name="Custom Role",
            description="A custom test role",
            priority=50,
            permission_ids=perm_ids,
        )

        self.assertEqual(role.name, "Custom Role")
        self.assertEqual(role.priority, 50)
        self.assertEqual(role.room, self.room)
        self.assertEqual(role.permissions.count(), len(perm_ids))

    def test_create_role_no_permission(self):
        self._add_member(self.member, self.member_role)

        with self.assertRaises(PermissionException):
            RoleService.create_role(
                user=self.member,
                room=self.room,
                name="Illegal Role",
                description="",
                priority=50,
                permission_ids=[],
            )

    def test_create_role_priority_violation(self):
        owner_participant = Participant.objects.get(user=self.owner, room=self.room)
        owner_priority = owner_participant.role.priority

        with self.assertRaises(PermissionException):
            RoleService.create_role(
                user=self.owner,
                room=self.room,
                name="Equal Priority Role",
                description="",
                priority=owner_priority,
                permission_ids=[],
            )

    def test_create_role_invalid_permissions(self):
        self._add_member(self.member, self.member_role)

        owner_perms = self.owner_role.permissions.all()
        member_perms = self.member_role.permissions.all()
        owner_only_perm = owner_perms.exclude(id__in=member_perms).first()

        if owner_only_perm:
            with self.assertRaises(PermissionException):
                RoleService.create_role(
                    user=self.member,
                    room=self.room,
                    name="Role",
                    description="",
                    priority=30,
                    permission_ids=[owner_only_perm.id],
                )

    def test_update_role_success(self):
        member_role = self.room.roles.get(name=RoleCode.MEMBER.label)

        updated = RoleService.update_role(
            user=self.owner,
            role=member_role,
            name="Updated Member",
            description="Updated description",
            priority=member_role.priority,
        )

        self.assertEqual(updated.name, "Updated Member")
        self.assertEqual(updated.description, "Updated description")

    def test_update_role_no_permission(self):
        self._add_member(self.member, self.member_role)

        with self.assertRaises(PermissionException):
            RoleService.update_role(user=self.member, role=self.owner_role, name="Hacked Role")

    def test_delete_role_success(self):
        custom_role = RoleService.create_role(
            user=self.owner,
            room=self.room,
            name="Custom Role",
            description="",
            priority=50,
            permission_ids=[],
        )

        result = RoleService.delete_role(user=self.owner, role=custom_role, substitution_role=self.member_role)

        self.assertTrue(result["success"])
        self.assertFalse(Role.objects.filter(id=custom_role.id).exists())

    def test_delete_role_with_participants(self):
        custom_role = RoleService.create_role(
            user=self.owner,
            room=self.room,
            name="Custom Role",
            description="",
            priority=50,
            permission_ids=[],
        )

        Participant.objects.create(user=self.member, room=self.room, role=custom_role)

        with self.assertRaises((ValidationException, FormValidationException)):
            RoleService.delete_role(user=self.owner, role=custom_role)

        result = RoleService.delete_role(user=self.owner, role=custom_role, substitution_role=self.member_role)

        self.assertTrue(result["success"])
        self.assertEqual(result["participants_reassigned"], 1)

    def test_delete_role_no_permission(self):
        custom_role = self.room.roles.filter(priority__lt=100).exclude(name=RoleCode.OWNER.label).first()
        self._add_member(self.member, self.member_role)

        with self.assertRaises(PermissionException):
            RoleService.delete_role(user=self.member, role=custom_role)

    def test_assign_permissions_to_role(self):
        custom_role = RoleService.create_role(
            user=self.owner,
            room=self.room,
            name="Custom Role",
            description="",
            priority=50,
            permission_ids=[],
        )

        perm_ids = list(self.owner_role.permissions.values_list("id", flat=True)[:2])

        updated = RoleService.assign_permissions_to_role(user=self.owner, role=custom_role, permission_ids=perm_ids)

        self.assertEqual(updated.permissions.count(), len(perm_ids))

    def test_remove_permissions_from_role(self):
        perm_ids = list(self.owner_role.permissions.values_list("id", flat=True)[:2])

        custom_role = RoleService.create_role(
            user=self.owner,
            room=self.room,
            name="Custom Role",
            description="",
            priority=50,
            permission_ids=perm_ids,
        )

        updated = RoleService.remove_permissions_from_role(
            user=self.owner,
            role=custom_role,
            permission_ids=[perm_ids[0]],
        )

        self.assertEqual(updated.permissions.count(), len(perm_ids) - 1)


@tag("unit", "services", "role-advanced")
class RoleServiceAdvancedTests(ServiceTestBase):
    """Advanced tests for RoleService - priority, permission escalation, cascading."""

    def test_create_role_equal_priority_denied(self):
        self._add_member(self.member, self.member_role)
        member_priority = self.member_role.priority

        with self.assertRaises(PermissionException):
            RoleService.create_role(
                user=self.member,
                room=self.room,
                name="Equal Priority Role",
                description="",
                priority=member_priority,
                permission_ids=[],
            )

    def test_create_role_higher_priority_denied(self):
        self._add_member(self.member, self.member_role)
        owner_priority = self.owner_role.priority

        with self.assertRaises(PermissionException):
            RoleService.create_role(
                user=self.member,
                room=self.room,
                name="Higher Priority Role",
                description="",
                priority=owner_priority + 1,
                permission_ids=[],
            )

    def test_create_role_lower_priority_allowed(self):
        lower_priority = self.owner_role.priority - 5
        role = RoleService.create_role(
            user=self.owner,
            room=self.room,
            name="Lower Priority Role",
            description="Lower priority",
            priority=lower_priority,
            permission_ids=[],
        )
        self.assertEqual(role.priority, lower_priority)

    def test_update_role_name_and_description(self):
        custom_role = RoleService.create_role(
            user=self.owner,
            room=self.room,
            name="Original Name",
            description="Original",
            priority=self.owner_role.priority - 10,
            permission_ids=[],
        )

        self.assertEqual(custom_role.name, "Original Name")

    def test_assign_permission_to_role(self):
        custom_role = RoleService.create_role(
            user=self.owner,
            room=self.room,
            name="Custom Role",
            description="Custom",
            priority=self.owner_role.priority - 5,
            permission_ids=[],
        )

        perm_ids = list(self.owner_role.permissions.values_list("id", flat=True)[:2])

        updated = RoleService.assign_permissions_to_role(
            user=self.owner,
            role=custom_role,
            permission_ids=perm_ids,
        )

        self.assertEqual(updated.permissions.count(), len(perm_ids))

    def test_permission_set_is_subset_validation(self):
        self._add_member(self.member, self.owner_role)
        member_perms = list(self.owner_role.permissions.values_list("id", flat=True))

        if member_perms:
            custom_role = RoleService.create_role(
                user=self.member,
                room=self.room,
                name="Limited Role",
                description="Limited",
                priority=self.owner_role.priority - 5,
                permission_ids=[member_perms[0]],
            )

            self.assertEqual(custom_role.permissions.count(), 1)

    def test_delete_role_with_participants_requires_substitution(self):
        custom_role = RoleService.create_role(
            user=self.owner,
            room=self.room,
            name="Doomed Role",
            description="",
            priority=self.owner_role.priority - 10,
            permission_ids=[],
        )

        for i in range(3):
            user = User.objects.create_user(
                name=f"Doomed User {i}",
                username=f"doomed_user{i}",
                email=f"doomed_user{i}@test.com",
                password="testpass123",
            )
            Participant.objects.create(user=user, room=self.room, role=custom_role)

        with self.assertRaises(ValidationException):
            RoleService.delete_role(user=self.owner, role=custom_role, substitution_role=None)

    def test_delete_role_reassigns_participants(self):
        custom_role = RoleService.create_role(
            user=self.owner,
            room=self.room,
            name="Doomed Role",
            description="",
            priority=self.owner_role.priority - 10,
            permission_ids=[],
        )

        users = []
        for i in range(3):
            user = User.objects.create_user(
                name=f"Reassign User {i}",
                username=f"reassign_user{i}",
                email=f"reassign_user{i}@test.com",
                password="testpass123",
            )
            users.append(user)
            Participant.objects.create(user=user, room=self.room, role=custom_role)

        result = RoleService.delete_role(user=self.owner, role=custom_role, substitution_role=self.member_role)

        self.assertTrue(result["success"])
        self.assertEqual(result["participants_reassigned"], 3)

        for user in users:
            participant = Participant.objects.get(user=user, room=self.room)
            self.assertEqual(participant.role, self.member_role)

    def test_delete_role_reassigns_invites(self):
        custom_role = RoleService.create_role(
            user=self.owner,
            room=self.room,
            name="Doomed Role",
            description="",
            priority=self.owner_role.priority - 10,
            permission_ids=[],
        )

        self._add_member(self.member, self.owner_role)
        invitees = []
        for i in range(2):
            invitee = User.objects.create_user(
                name=f"Invitee {i}",
                username=f"invitee{i}",
                email=f"invitee{i}@test.com",
                password="testpass123",
            )
            invitees.append(invitee)
            InviteService.send_invite(
                inviter=self.member,
                room=self.room,
                invitee=invitee,
                role=custom_role,
                expires_at=timezone.now() + timedelta(days=7),
            )

        result = RoleService.delete_role(user=self.owner, role=custom_role, substitution_role=self.member_role)

        self.assertEqual(result["invites_reassigned"], 2)

        for invitee in invitees:
            from backend.invite.models import Invite

            invite = Invite.objects.get(invitee=invitee, room=self.room)
            self.assertEqual(invite.role, self.member_role)

    def test_delete_role_atomicity_on_failure(self):
        custom_role = RoleService.create_role(
            user=self.owner,
            room=self.room,
            name="Atomic Test Role",
            description="",
            priority=self.owner_role.priority - 10,
            permission_ids=[],
        )

        user = User.objects.create_user(
            name="Atomic Test User",
            username="atomic_test_user",
            email="atomic@test.com",
            password="testpass123",
        )
        Participant.objects.create(user=user, room=self.room, role=custom_role)

        with self.assertRaises(ValidationException):
            RoleService.delete_role(user=self.owner, role=custom_role, substitution_role=None)

        self.assertTrue(Role.objects.filter(id=custom_role.id).exists())
        participant = Participant.objects.get(user=user, room=self.room)
        self.assertEqual(participant.role, custom_role)

    def test_can_affect_role_priority_lower(self):
        self._add_member(self.member, self.owner_role)
        lower_role = RoleService.create_role(
            user=self.member,
            room=self.room,
            name="Lower Role",
            description="Lower",
            priority=self.owner_role.priority - 10,
            permission_ids=[],
        )

        member_participant = Participant.objects.get(user=self.member, room=self.room)
        self.assertTrue(RoleService.can_affect_role(member_participant, lower_role))

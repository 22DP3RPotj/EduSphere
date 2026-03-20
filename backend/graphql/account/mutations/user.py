import graphene
import uuid
from datetime import datetime
from typing import Any, Optional, Self, cast
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from django.utils.datastructures import MultiValueDict

from backend.core.exceptions import ErrorCode
from backend.graphql.account.types import UserType
from backend.graphql.mutations import BaseMutation
from backend.graphql.utils import format_form_errors
from backend.account.models import User
from backend.account.services import RestrictionService
from backend.account.forms import UserForm


class UpdateUser(BaseMutation):
    class Arguments:
        name = graphene.String(required=False)
        username = graphene.String(required=False)
        bio = graphene.String(required=False)
        avatar = Upload(required=False)

    user = graphene.Field(UserType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        name: Optional[str] = None,
        username: Optional[str] = None,
        bio: Optional[str] = None,
        avatar: Optional[Upload] = None,
    ) -> Self:
        user = info.context.user

        data = {
            "username": username or user.username,
            "name": name or user.name,
            "bio": bio or user.bio,
        }

        files = None
        if avatar is not None:
            files = MultiValueDict({"avatar": [cast(UploadedFile, avatar)]})

        form = UserForm(data=data, files=files, instance=user)

        if not form.is_valid():
            raise GraphQLError(
                "Invalid data",
                extensions={
                    "code": ErrorCode.VALIDATION_ERROR,
                    "errors": format_form_errors(form.errors),
                },
            )

        form.save()
        return cls(user=user)


# TODO: Separate into BanUser and UnbanUser mutations
class UpdateUserActiveStatus(BaseMutation):
    class Arguments:
        user_ids = graphene.List(graphene.UUID, required=True)
        is_active = graphene.Boolean(required=True)
        reason = graphene.String(required=False)
        expires_at = graphene.DateTime(required=False)

    success = graphene.Boolean()
    updated_count = graphene.Int()

    @classmethod
    @superuser_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        user_ids: list[uuid.UUID],
        is_active: bool,
        reason: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Self:
        users = User.objects.filter(id__in=user_ids)

        with transaction.atomic():
            for user in users:
                if is_active:
                    RestrictionService.unban_user(user)
                else:
                    RestrictionService.ban_user(
                        user=user,
                        banned_by=info.context.user,
                        reason=reason,
                        expires_at=expires_at,
                    )

        return cls(success=True, updated_count=len(users))


class UpdateUserStaffStatus(BaseMutation):
    class Arguments:
        user_ids = graphene.List(graphene.UUID, required=True)
        is_staff = graphene.Boolean(required=True)

    success = graphene.Boolean()
    updated_count = graphene.Int()

    @classmethod
    @superuser_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        user_ids: list[uuid.UUID],
        is_staff: bool,
    ) -> Self:
        updated_count = User.objects.filter(id__in=user_ids).update(is_staff=is_staff)

        return cls(success=True, updated_count=updated_count)

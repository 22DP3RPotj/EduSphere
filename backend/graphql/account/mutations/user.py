import graphene
import uuid
from typing import Optional, cast
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError

from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from django.utils.datastructures import MultiValueDict

from backend.graphql.account.types import UserType
from backend.graphql.utils import format_form_errors
from backend.account.models import User
from backend.core.forms import UserForm, RegisterForm


class RegisterUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)

    user = graphene.Field(UserType)
    success = graphene.Boolean()

    def mutate(self, info: graphene.ResolveInfo, **kwargs):
        form = RegisterForm(kwargs)

        if not form.is_valid():
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form.errors)})
        
        user = form.save()
        return RegisterUser(user=user, success=True)

# TODO: rework argument types
class UpdateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=False)
        bio = graphene.String(required=False)
        avatar = Upload(required=False)

    user = graphene.Field(UserType)

    @login_required
    def mutate(
        self,
        info: graphene.ResolveInfo,
        name: Optional[str] = None,
        username: Optional[str] = None,
        bio: Optional[str] = None,
        avatar: Optional[Upload] = None,
    ):
        user = info.context.user
        
        data = {
            "username": username or user.username,
            "name": name or user.name,
            "bio": bio or user.bio,
        }
        
        files = None
        if avatar is not None:
            files = MultiValueDict({"avatar": [cast(UploadedFile, avatar)]})

        form = UserForm(
            data=data,
            files=files,
            instance=user
        )

        if not form.is_valid():
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form.errors)})
        
        form.save()
        return UpdateUser(user=user)
        
        
class UpdateUserActiveStatus(graphene.Mutation):
    class Arguments:
        user_ids = graphene.List(graphene.UUID, required=True)
        is_active = graphene.Boolean(required=True)

    success = graphene.Boolean()
    updated_count = graphene.Int()

    @superuser_required
    def mutate(self, info: graphene.ResolveInfo, user_ids: list[uuid.UUID], is_active: bool):
        with transaction.atomic():
            updated_count = User.objects.filter(
                id__in=user_ids
            ).update(is_active=is_active)
            
        return UpdateUserActiveStatus(
            success=True, 
            updated_count=updated_count
        )


class UpdateUserStaffStatus(graphene.Mutation):
    class Arguments:
        user_ids = graphene.List(graphene.UUID, required=True)
        is_staff = graphene.Boolean(required=True)

    success = graphene.Boolean()
    updated_count = graphene.Int()

    @superuser_required
    def mutate(self, info: graphene.ResolveInfo, user_ids: list[uuid.UUID], is_staff: bool):
        with transaction.atomic():
            updated_count = User.objects.filter(
                id__in=user_ids
            ).update(is_staff=is_staff)
            
        return UpdateUserStaffStatus(
            success=True, 
            updated_count=updated_count
        )

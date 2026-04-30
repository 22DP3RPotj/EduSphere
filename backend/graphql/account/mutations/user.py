from typing import TYPE_CHECKING, Any, Self, cast

import graphene
from django.utils.datastructures import MultiValueDict
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from backend.account.choices import LanguageChoices
from backend.account.forms import UserForm
from backend.account.services import AccountService
from backend.core.exceptions import ErrorCode, format_form_errors
from backend.graphql.account.types import UserType
from backend.graphql.mutations import BaseMutation

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile


class Register(BaseMutation):
    class Arguments:
        username = graphene.String(required=True)
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)

    success = graphene.Boolean()

    @classmethod
    def resolve(  # type: ignore[override]
        cls,
        root: Any | None,
        info: graphene.ResolveInfo,
        username: str,
        name: str,
        email: str,
        password1: str,
        password2: str,
    ) -> Self:
        AccountService.register_user(
            username=username,
            name=name,
            email=email,
            password1=password1,
            password2=password2,
        )
        return cls(success=True)


class UpdateUser(BaseMutation):
    class Arguments:
        name = graphene.String(required=False)
        username = graphene.String(required=False)
        bio = graphene.String(required=False)
        language = graphene.String(required=False)
        avatar = Upload(required=False)

    user = graphene.Field(UserType)

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Any | None,
        info: graphene.ResolveInfo,
        name: str | None = None,
        username: str | None = None,
        bio: str | None = None,
        language: str | None = None,
        avatar: Upload | None = None,
    ) -> Self:
        user = info.context.user

        data = {
            "username": username if username is not None else user.username,
            "name": name if name is not None else user.name,
            "bio": bio if bio is not None else user.bio,
        }

        files = None
        if avatar is not None:
            files = MultiValueDict({"avatar": [cast("UploadedFile", avatar)]})

        form = UserForm(data=data, files=files, instance=user)

        if not form.is_valid():
            raise GraphQLError(
                "Invalid data",
                extensions={
                    "code": ErrorCode.VALIDATION_ERROR,
                    "errors": format_form_errors(form.errors),
                },
            )

        user = form.save(commit=False)
        if language is not None:
            valid = {c.value for c in LanguageChoices}
            if language not in valid:
                raise GraphQLError(
                    "Invalid language", extensions={"code": ErrorCode.VALIDATION_ERROR}
                )
            user.language = language
        user.save()

        return cls(user=user)

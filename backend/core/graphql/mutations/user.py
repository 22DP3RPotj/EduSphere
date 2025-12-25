import graphene
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required, superuser_required
from graphql import GraphQLError
from django.db import transaction

from backend.core.graphql.types import UserType
from backend.core.graphql.utils import format_form_errors
from backend.core.models import User
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

    def mutate(self, info, **kwargs):
        form = RegisterForm(kwargs)

        if form.is_valid():
            user = form.save()
            return RegisterUser(user=user, success=True)
        else:
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form)})
     

class UpdateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=False)
        bio = graphene.String(required=False)
        avatar = Upload(required=False)
        language = graphene.String(required=False)

    user = graphene.Field(UserType)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        
        data = {
            "username": user.username,
            "name": kwargs.get("name", user.name),
            "bio": kwargs.get("bio", user.bio),
            "language": kwargs.get("language", user.language),
        }
        
        avatar = kwargs.pop("avatar", None)
        
        form = UserForm(
            data=data,
            files={"avatar": avatar} if avatar else None,
            instance=user
        )

        if form.is_valid():
            form.save()
            return UpdateUser(user=user)
        else:
            raise GraphQLError("Invalid data", extensions={"errors": format_form_errors(form)})
        
        
class UpdateUserActiveStatus(graphene.Mutation):
    class Arguments:
        user_ids = graphene.List(graphene.UUID, required=True)
        is_active = graphene.Boolean(required=True)

    success = graphene.Boolean()
    updated_count = graphene.Int()

    @superuser_required
    def mutate(self, info, user_ids, is_active):
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
    def mutate(self, info, user_ids, is_staff):
        with transaction.atomic():
            updated_count = User.objects.filter(
                id__in=user_ids
            ).update(is_staff=is_staff)
            
        return UpdateUserStaffStatus(
            success=True, 
            updated_count=updated_count
        )

class UserMutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    update_user = UpdateUser.Field()
    update_user_active_status = UpdateUserActiveStatus.Field()
    update_user_staff_status = UpdateUserStaffStatus.Field()

import graphene
import graphql_jwt
from typing import Any, Optional, Self
from graphql_jwt.decorators import login_required

from backend.graphql.mutations import BaseMutation
from backend.account.services import AccountService


class VerifyAccount(BaseMutation):
    """
    Mark the authenticated user's email as verified.
    The verification link should direct the user to a page that calls
    this mutation while authenticated.
    """

    class Arguments:
        token = graphene.String(required=True)

    success = graphene.Boolean()

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        token: str,
    ) -> Self:
        AccountService.verify_email(token=token)
        return cls(success=True)


class ResendActivationEmail(BaseMutation):
    """
    Re-send the verification email to the currently authenticated user.
    """

    success = graphene.Boolean()

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
    ) -> Self:
        AccountService.resend_verification_email(user=info.context.user)
        return cls(success=True)


class SendPasswordResetEmail(BaseMutation):
    """
    Send a password-reset email.
    Unauthenticated — user has forgotten their password.
    Always returns success=True to prevent email enumeration.
    """

    class Arguments:
        email = graphene.String(required=True)

    success = graphene.Boolean()

    @classmethod
    def resolve(  # type: ignore[override]
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        email: str,
    ) -> Self:
        AccountService.send_password_reset_email(email=email)
        return cls(success=True)


class PasswordReset(BaseMutation):
    """
    Reset a user's password using the uid + token from the reset email.
    Unauthenticated — user is locked out.
    """

    class Arguments:
        token = graphene.String(required=True)
        new_password = graphene.String(required=True)

    success = graphene.Boolean()

    @classmethod
    def resolve(  # type: ignore[override]
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        token: str,
        new_password: str,
    ) -> Self:
        AccountService.reset_password(token=token, new_password=new_password)
        return cls(success=True)


class PasswordChange(BaseMutation):
    """
    Change password for the currently authenticated user.
    Requires the current password to be supplied.
    """

    class Arguments:
        old_password = graphene.String(required=True)
        new_password = graphene.String(required=True)

    success = graphene.Boolean()

    @classmethod
    @login_required
    def resolve(
        cls,
        root: Optional[Any],
        info: graphene.ResolveInfo,
        old_password: str,
        new_password: str,
    ) -> Self:
        AccountService.change_password(
            user=info.context.user,
            old_password=old_password,
            new_password=new_password,
        )
        return cls(success=True)


class AuthMutation(graphene.ObjectType):
    # --- JWT token lifecycle ---
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    delete_token = graphql_jwt.DeleteJSONWebTokenCookie.Field()
    delete_refresh_token = graphql_jwt.DeleteRefreshTokenCookie.Field()

    # --- Email verification ---
    verify_account = VerifyAccount.Field()
    resend_activation_email = ResendActivationEmail.Field()

    # --- Password management ---
    send_password_reset_email = SendPasswordResetEmail.Field()
    password_reset = PasswordReset.Field()
    password_change = PasswordChange.Field()

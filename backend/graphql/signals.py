from django.contrib.auth.models import update_last_login
from django.dispatch import receiver
from graphql_jwt.signals import token_issued
from graphql_jwt.refresh_token.signals import refresh_token_rotated


@receiver(token_issued)
def update_jwt_last_login(sender, request, user, **kwargs):
    update_last_login(sender, user)

@receiver(refresh_token_rotated)
def revoke_refresh_token(sender, request, refresh_token, **kwargs):
    refresh_token.revoke(request)

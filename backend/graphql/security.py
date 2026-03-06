from django.conf import settings
from graphene.validation import depth_limit_validator


def get_validation_rules():
    """
    Returns a list of validation rules based on the environment.
    """
    rules = [depth_limit_validator(max_depth=settings.GRAPHQL_MAX_DEPTH)]

    # TODO: Breaks frontend
    # if not settings.DEBUG:
    #     rules.append(DisableIntrospection)

    return rules

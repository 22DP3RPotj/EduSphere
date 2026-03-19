import logging

from django.conf import settings
from graphene_file_upload.django import FileUploadGraphQLView
from backend.graphql.security import get_validation_rules

logger = logging.getLogger(__name__)


class GraphqlView(FileUploadGraphQLView):
    """Custom GraphQL view to handle multipart/form-data requests"""

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            graphiql=settings.DEBUG,
            validation_rules=get_validation_rules(),
            **kwargs,
        )

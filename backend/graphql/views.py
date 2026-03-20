from django.conf import settings
from graphene_file_upload.django import FileUploadGraphQLView
from backend.graphql.security import get_validation_rules
from graphql_sync_dataloaders import DeferredExecutionContext

class GraphqlView(FileUploadGraphQLView):
    """Custom GraphQL view to handle multipart/form-data requests"""

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            graphiql=settings.DEBUG,
            validation_rules=get_validation_rules(),
            execution_context_class=DeferredExecutionContext,
            **kwargs,
        )

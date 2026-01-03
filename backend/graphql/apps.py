from django.apps import AppConfig


class GraphQLConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.graphql"
    label = "graphql"

    def ready(self):
        import backend.graphql.signals as _

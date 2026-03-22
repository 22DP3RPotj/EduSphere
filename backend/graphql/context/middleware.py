from backend.graphql.context.registry import GQLDataLoaderRegistry


class GQLDataLoaderMiddleware:
    """
    Django WSGI middleware that attaches a fresh GQLDataLoaderRegistry to
    every request so resolvers can access loaders via info.context.loaders.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.loaders = GQLDataLoaderRegistry()
        return self.get_response(request)

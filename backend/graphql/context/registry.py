from backend.graphql.account.dataloaders import UserLoader


class GQLDataLoaderRegistry:
    """
    Holds per-request loader instances.

    A new registry (and therefore new loader instances) is created for every
    request by GQLDataLoaderMiddleware. This ensures the per-request cache
    built into SyncDataLoader is never shared across requests.
    """

    def __init__(self):
        self._cache = {}

    @property
    def user(self):
        if "user" not in self._cache:
            self._cache["user"] = UserLoader()
        return self._cache["user"]

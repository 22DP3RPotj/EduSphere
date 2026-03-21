from typing import Generic, Optional, Type, TypeVar
from django.db import models
from graphql_sync_dataloaders import SyncDataLoader

T = TypeVar("T", bound=models.Model)


class BaseModelLoader(Generic[T]):
    """
    Per-request batching loader backed by graphql-sync-dataloaders.

    graphql-core 3 dropped support for the `promise` library, so the old
    `promise.dataloader.DataLoader` base class returns Promise objects that
    graphql-core 3 cannot resolve, causing "Received incompatible instance"
    errors at runtime. SyncDataLoader + DeferredExecutionContext is the
    canonical replacement for synchronous Django stacks.

    Subclasses only need to declare `model`:

        class UserLoader(BaseModelLoader):
            model = User
    """

    model: Type[T]

    def __init__(self):
        self._loader = SyncDataLoader(self._batch_load)

    def _batch_load(self, keys) -> list[Optional[T]]:
        key_strings = [str(k) for k in keys]

        manager: models.Manager = self.model._default_manager

        instance_map = {str(obj.id): obj for obj in manager.filter(id__in=key_strings)}

        return [instance_map.get(str(k)) for k in key_strings]

    def load(self, key) -> Optional[T]:
        return self._loader.load(key)

from graphql_sync_dataloaders import SyncDataLoader 

class BaseModelLoader:
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
    model = None

    def __init__(self):
        self._loader = SyncDataLoader(self._batch_load)

    def _batch_load(self, keys):
        key_strings = [str(k) for k in keys]
        
        instance_map = {
            str(obj.id): obj
            for obj in self.model.objects.filter(id__in=key_strings)
        }

        return [instance_map.get(str(k)) for k in key_strings]
    
    def load(self, key):
        return self._loader.load(key)

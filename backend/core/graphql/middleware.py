import logging
import time
import inspect
from graphql import GraphQLResolveInfo


logger = logging.getLogger(__name__)

class DebugLoggingMiddleware:
    def resolve(self, next_, root, info: GraphQLResolveInfo, **kwargs):
        if info.field_name.startswith("__"):
            return next_(root, info, **kwargs)

        if info.path.prev is not None:
            return next_(root, info, **kwargs)

        safe_args = {
            k: v for k, v in kwargs.items() if v is not None
        }
        
        logger.info(f"⇒ {info.parent_type.name}.{info.field_name} args={safe_args}")

        start = time.time()
        try:
            result = next_(root, info, **kwargs)
            if inspect.isawaitable(result):
                return result
            return result
        finally:
            dur = time.time() - start
            logger.info(f"⇐ {info.parent_type.name}.{info.field_name} done in {dur:.3f}s")

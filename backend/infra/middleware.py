import inspect
import graphene
from typing import Any, Callable
from prometheus_client import Counter, Histogram


GRAPHQL_RESOLVER_LATENCY_SECONDS = Histogram(
    "graphql_resolver_latency_seconds",
    "Time taken for a GraphQL resolver to complete.",
    ["operation_type", "field"],
)

GRAPHQL_RESOLVER_EXCEPTIONS_TOTAL = Counter(
    "graphql_resolver_exceptions_total",
    "Total exceptions raised by a GraphQL resolver.",
    ["operation_type", "field"],
)

GRAPHQL_RESOLVER_COMPLETED_TOTAL = Counter(
    "graphql_resolver_completed_total",
    "Total GraphQL resolver executions.",
    ["operation_type", "field"],
)


class PrometheusMiddleware:
    def resolve(
        self,
        next_: Callable,
        root: Any,
        info: graphene.ResolveInfo,
        **kwargs: Any,
    ) -> Any:
        labels = {
            "operation_type": info.operation.operation.value,
            "field": f"{info.parent_type.name}.{info.field_name}",
        }

        try:
            # If the resolver is SYNC, this times the actual work.
            # If the resolver is ASYNC, this times only the creation of the coroutine (near 0s).
            with GRAPHQL_RESOLVER_EXCEPTIONS_TOTAL.labels(**labels).count_exceptions():
                with GRAPHQL_RESOLVER_LATENCY_SECONDS.labels(**labels).time():
                    result = next_(root, info, **kwargs)
        except Exception:
            GRAPHQL_RESOLVER_COMPLETED_TOTAL.labels(**labels).inc()
            raise

        if inspect.isawaitable(result):

            async def wrapper():
                with GRAPHQL_RESOLVER_EXCEPTIONS_TOTAL.labels(
                    **labels
                ).count_exceptions():
                    with GRAPHQL_RESOLVER_LATENCY_SECONDS.labels(**labels).time():
                        try:
                            return await result
                        finally:
                            GRAPHQL_RESOLVER_COMPLETED_TOTAL.labels(**labels).inc()

            return wrapper()

        GRAPHQL_RESOLVER_COMPLETED_TOTAL.labels(**labels).inc()
        return result

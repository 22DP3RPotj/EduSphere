import inspect
import graphene
from typing import Any, Callable, Optional
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
        next: Callable,
        root: Optional[graphene.Schema],
        info: graphene.ResolveInfo,
        **kwargs: Any,
    ) -> Any:
        operation_type = info.operation.operation.value
        field = f"{info.parent_type.name}.{info.field_name}"

        with GRAPHQL_RESOLVER_LATENCY_SECONDS.labels(
            operation_type=operation_type,
            field=field,
        ).time():
            with GRAPHQL_RESOLVER_EXCEPTIONS_TOTAL.labels(
                operation_type=operation_type,
                field=field,
            ).count_exceptions():
                result = next(root, info, **kwargs)

        if inspect.isawaitable(result):

            async def _await():
                try:
                    return await result
                finally:
                    GRAPHQL_RESOLVER_COMPLETED_TOTAL.labels(
                        operation_type=operation_type,
                        field=field,
                    ).inc()

            return _await()

        GRAPHQL_RESOLVER_COMPLETED_TOTAL.labels(
            operation_type=operation_type,
            field=field,
        ).inc()
        return result

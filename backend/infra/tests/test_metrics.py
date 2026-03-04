import json
import pytest
from prometheus_client import REGISTRY


@pytest.mark.django_db
def test_prometheus_metrics_endpoint_accessible(client):
    """Verify that the metrics endpoint is reachable and returns 200."""

    url = "/infra/metrics/"
    response = client.get(url)

    assert response.status_code == 200
    assert "text/plain" in response["Content-Type"]
    # Verify standard django metrics are present
    assert (
        b"django_http_requests_before_middlewares_total" in response.content
        or b"django_http_requests_total_by_method_total" in response.content
    )


@pytest.mark.django_db
def test_graphql_middleware_updates_metrics(client):
    """Verify that GraphQL queries increment our custom prometheus metrics."""
    # Note: GraphQL queries hit the /graphql/ endpoint.
    # The middleware is in backend.infra.middleware.PrometheusMiddleware

    query = """
    query TestQuery {
        __schema {
            queryType {
                name
            }
        }
    }
    """

    # Label format from backend/infra/middleware.py:
    # field = f"{info.parent_type.name}.{info.field_name}"
    # For __schema on Query, it should be Query.__schema

    # Get initial value of the counter if it exists
    before = (
        REGISTRY.get_sample_value(
            "graphql_resolver_completed_total",
            {"operation_type": "query", "field": "Query.__schema"},
        )
        or 0.0
    )

    response = client.post(
        "/graphql/",
        data=json.dumps({"query": query}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert "errors" not in response.json()

    after = REGISTRY.get_sample_value(
        "graphql_resolver_completed_total",
        {"operation_type": "query", "field": "Query.__schema"},
    )

    assert after is not None
    assert after > before

import json
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit


def _make_info(*, body: bytes | None):
    return SimpleNamespace(
        context=SimpleNamespace(body=body),
        schema=object(),
    )


def test_validation_middleware_skips_when_no_body():
    from backend.graphql.middleware import ValidationMiddleware

    middleware = ValidationMiddleware()

    def next_(root, info, **kwargs):
        return "ok"

    info = _make_info(body=None)
    assert middleware.resolve(next_, None, info) == "ok"


def test_validation_middleware_ignores_bad_json():
    from backend.graphql.middleware import ValidationMiddleware

    middleware = ValidationMiddleware()

    def next_(root, info, **kwargs):
        return "ok"

    info = _make_info(body=b"not-json")
    assert middleware.resolve(next_, None, info) == "ok"


def test_validation_middleware_skips_when_query_missing():
    from backend.graphql.middleware import ValidationMiddleware

    middleware = ValidationMiddleware()

    def next_(root, info, **kwargs):
        return "ok"

    info = _make_info(body=json.dumps({"variables": {}}).encode())
    assert middleware.resolve(next_, None, info) == "ok"


def test_validation_middleware_validates_query(monkeypatch):
    import backend.graphql.middleware as mw

    middleware = mw.ValidationMiddleware()

    captured: dict[str, object] = {}

    def next_(root, info, **kwargs):
        return "ok"

    def fake_parse(query_str):
        captured["query_str"] = query_str
        return "AST"

    def fake_depth_limit_validator(limit):
        captured["limit"] = limit
        return "DEPTH_RULE"

    def fake_validate(*, schema, document_ast, rules):
        captured["schema"] = schema
        captured["document_ast"] = document_ast
        captured["rules"] = rules
        return []

    monkeypatch.setattr(mw, "parse", fake_parse)
    monkeypatch.setattr(mw, "depth_limit_validator", fake_depth_limit_validator)
    monkeypatch.setattr(mw, "validate", fake_validate)

    query = "query { __typename }"
    info = _make_info(body=json.dumps({"query": query}).encode())

    assert middleware.resolve(next_, None, info) == "ok"
    assert captured["query_str"] == query
    assert captured["limit"] == 10
    assert captured["document_ast"] == "AST"
    rules = captured["rules"]
    assert rules[0] is mw.DisableIntrospection
    assert rules[1] == "DEPTH_RULE"


def test_validation_middleware_swallow_validation_exceptions(monkeypatch):
    import backend.graphql.middleware as mw

    middleware = mw.ValidationMiddleware()

    def next_(root, info, **kwargs):
        return "ok"

    monkeypatch.setattr(mw, "parse", lambda _: "AST")
    monkeypatch.setattr(mw, "validate", lambda **_: (_ for _ in ()).throw(ValueError("boom")))

    info = _make_info(body=json.dumps({"query": "query { x }"}).encode())
    assert middleware.resolve(next_, None, info) == "ok"


def test_validation_middleware_handles_validation_errors(monkeypatch):
    import backend.graphql.middleware as mw

    middleware = mw.ValidationMiddleware()

    def next_(root, info, **kwargs):
        return "ok"

    monkeypatch.setattr(mw, "parse", lambda _: "AST")

    class FakeErr(Exception):
        def __str__(self):
            return "bad"

    monkeypatch.setattr(mw, "validate", lambda **_: [FakeErr()])

    info = _make_info(body=json.dumps({"query": "query { x }"}).encode())
    assert middleware.resolve(next_, None, info) == "ok"

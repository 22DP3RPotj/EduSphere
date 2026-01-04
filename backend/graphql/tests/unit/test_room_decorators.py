from types import SimpleNamespace

import pytest
from graphql import GraphQLError

from backend.core.exceptions import ErrorCode

pytestmark = pytest.mark.unit


def _make_info(*, user):
    return SimpleNamespace(context=SimpleNamespace(user=user))


def test_require_room_permission_missing_room_id_raises():
    from backend.graphql.room.decorators import require_room_permission

    @require_room_permission("ANY")
    def resolver(self, info, **kwargs):
        return "ok"

    with pytest.raises(GraphQLError) as exc:
        resolver(None, _make_info(user=SimpleNamespace(is_authenticated=True)))

    assert exc.value.extensions["code"] == ErrorCode.BAD_REQUEST


def test_require_room_permission_requires_authentication():
    from backend.graphql.room.decorators import require_room_permission

    @require_room_permission("ANY")
    def resolver(self, info, **kwargs):
        return "ok"

    with pytest.raises(GraphQLError) as exc:
        resolver(None, _make_info(user=SimpleNamespace(is_authenticated=False)), room_id="1")

    assert exc.value.extensions["code"] == ErrorCode.PERMISSION_DENIED


def test_require_room_permission_room_not_found(monkeypatch):
    import backend.graphql.room.decorators as dec

    @dec.require_room_permission("ANY")
    def resolver(self, info, **kwargs):
        return "ok"

    def fake_get(**kwargs):
        raise dec.Room.DoesNotExist()

    monkeypatch.setattr(dec.Room.objects, "get", fake_get)

    with pytest.raises(GraphQLError) as exc:
        resolver(None, _make_info(user=SimpleNamespace(is_authenticated=True)), room_id="1")

    assert exc.value.extensions["code"] == ErrorCode.NOT_FOUND


def test_require_room_permission_permission_denied(monkeypatch):
    import backend.graphql.room.decorators as dec

    @dec.require_room_permission("PERM")
    def resolver(self, info, **kwargs):
        return "ok"

    room = object()
    monkeypatch.setattr(dec.Room.objects, "get", lambda **_: room)
    monkeypatch.setattr(dec.RoleService, "has_permission", lambda *args, **kwargs: False)

    with pytest.raises(GraphQLError) as exc:
        resolver(None, _make_info(user=SimpleNamespace(is_authenticated=True)), room_id="1")

    assert exc.value.extensions["code"] == ErrorCode.PERMISSION_DENIED


def test_require_room_permission_success_injects_room(monkeypatch):
    import backend.graphql.room.decorators as dec

    captured = {}

    @dec.require_room_permission("PERM")
    def resolver(self, info, **kwargs):
        captured["room"] = kwargs.get("room")
        return "ok"

    room = object()
    monkeypatch.setattr(dec.Room.objects, "get", lambda **_: room)
    monkeypatch.setattr(dec.RoleService, "has_permission", lambda *args, **kwargs: True)

    result = resolver(None, _make_info(user=SimpleNamespace(is_authenticated=True)), room_id="1")
    assert result == "ok"
    assert captured["room"] is room

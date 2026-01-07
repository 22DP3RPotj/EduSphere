import pytest
from asgiref.sync import async_to_sync
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser

from backend.messaging.chat.routing import websocket_urlpatterns


class FakeRedis:
    """Minimal async Redis fake for incr/expire/xadd/xrange/aclose used by ChatConsumer."""

    last_instance = None

    def __init__(self, *args, **kwargs):
        FakeRedis.last_instance = self
        self._kv: dict[str, int] = {}
        self._streams: dict[str, list[tuple[str, dict[str, str]]]] = {}
        self._stream_seq: dict[str, int] = {}

    async def incr(self, key: str) -> int:
        self._kv[key] = self._kv.get(key, 0) + 1
        return self._kv[key]

    async def expire(self, key: str, seconds: int) -> bool:
        # TTL isn't simulated; good enough for functional tests.
        return True

    async def xadd(self, stream: str, fields: dict[str, str]) -> str:
        seq = self._stream_seq.get(stream, 0) + 1
        self._stream_seq[stream] = seq
        msg_id = f"{seq}-0"
        self._streams.setdefault(stream, []).append((msg_id, dict(fields)))
        return msg_id

    async def xrange(self, stream: str, start: str, end: str, count: int = 50):
        # Very small subset: return up to `count` entries.
        return list(self._streams.get(stream, []))[:count]

    async def aclose(self, *args, **kwargs) -> None:
        return None


@pytest.fixture(autouse=True)
def _patch_redis(monkeypatch):
    # Ensure ChatConsumer uses FakeRedis instead of real redis.
    import backend.messaging.chat.consumers as consumers

    FakeRedis.last_instance = None

    monkeypatch.setattr(consumers.aioredis, "Redis", FakeRedis)


@pytest.fixture(autouse=True)
def _in_memory_channel_layer(settings):
    # Keep this active for the entire test, not just while building the ASGI app.
    settings.CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
    }


@pytest.fixture
def asgi_app():
    # URLRouter is needed so `scope["url_route"]["kwargs"]["room_id"]` is populated.
    return URLRouter(websocket_urlpatterns)


@pytest.fixture
def users(django_user_model):
    host = django_user_model.objects.create_user(
        email="host@example.com", username="host", name="Host", password="pass"
    )
    member = django_user_model.objects.create_user(
        email="member@example.com", username="member", name="Member", password="pass"
    )
    other = django_user_model.objects.create_user(
        email="other@example.com", username="other", name="Other", password="pass"
    )
    return host, member, other


@pytest.fixture
def room_and_participant(users):
    from backend.room.models import Room, Topic
    from backend.access.models import Role, Participant

    host, member, _other = users

    topic = Topic.objects.create(name="General")
    room = Room.objects.create(host=host, name="Test Room")
    room.topics.add(topic)

    role = Role.objects.create(name="Member", room=room)
    Participant.objects.create(user=member, room=room, role=role)

    return room, member


@pytest.mark.django_db(transaction=True)
def test_connect_requires_auth(asgi_app, room_and_participant):
    room, _member = room_and_participant

    async def run():
        communicator = WebsocketCommunicator(asgi_app, f"/ws/chat/{room.id}")
        communicator.scope["user"] = AnonymousUser()

        connected, _ = await communicator.connect()
        assert connected is False

    async_to_sync(run)()


@pytest.mark.django_db(transaction=True)
def test_connect_requires_participant(asgi_app, users):
    from backend.room.models import Room, Topic

    host, _member, other = users

    topic = Topic.objects.create(name="General")
    room = Room.objects.create(host=host, name="Test Room")
    room.topics.add(topic)

    async def run():
        communicator = WebsocketCommunicator(asgi_app, f"/ws/chat/{room.id}")
        communicator.scope["user"] = other

        connected, _ = await communicator.connect()
        assert connected is False

    async_to_sync(run)()


@pytest.mark.django_db(transaction=True)
def test_invalid_json_returns_error(asgi_app, room_and_participant):
    room, member = room_and_participant

    async def run():
        communicator = WebsocketCommunicator(asgi_app, f"/ws/chat/{room.id}")
        communicator.scope["user"] = member

        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_to(text_data="not-json")
        payload = await communicator.receive_json_from()
        assert payload == {"error": "Invalid JSON."}

        await communicator.disconnect()

    async_to_sync(run)()


@pytest.mark.django_db(transaction=True)
def test_unknown_message_type_returns_error(asgi_app, room_and_participant):
    room, member = room_and_participant

    async def run():
        communicator = WebsocketCommunicator(asgi_app, f"/ws/chat/{room.id}")
        communicator.scope["user"] = member

        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to({"type": "bogus"})
        payload = await communicator.receive_json_from()
        assert payload == {"error": "Unknown message type."}

        await communicator.disconnect()

    async_to_sync(run)()


@pytest.mark.django_db(transaction=True)
def test_text_message_broadcasts_and_persists_history(asgi_app, room_and_participant):
    room, member = room_and_participant

    async def run():
        communicator = WebsocketCommunicator(asgi_app, f"/ws/chat/{room.id}")
        communicator.scope["user"] = member

        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to({"type": "text", "message": "hi"})
        payload = await communicator.receive_json_from()

        assert payload["type"] == "chat_message"
        assert payload["action"] == "new"
        assert payload["body"] == "hi"
        assert payload["author"] == member.username

        await communicator.disconnect()

    async_to_sync(run)()

    # Ensure redis stream received a history entry
    fake = FakeRedis.last_instance
    assert fake is not None
    stream_key = f"chat_stream:{room.id}"
    assert stream_key in fake._streams
    assert len(fake._streams[stream_key]) == 1


@pytest.mark.django_db(transaction=True)
def test_rate_limit_blocks_excess_messages(settings, asgi_app, room_and_participant):
    settings.MAX_MESSAGES_PER_SEC = 1
    room, member = room_and_participant

    async def run():
        communicator = WebsocketCommunicator(asgi_app, f"/ws/chat/{room.id}")
        communicator.scope["user"] = member

        connected, _ = await communicator.connect()
        assert connected is True

        # First message should go through
        await communicator.send_json_to({"type": "text", "message": "one"})
        payload1 = await communicator.receive_json_from()
        assert payload1["action"] == "new"

        # Second message should be rate-limited
        await communicator.send_json_to({"type": "text", "message": "two"})
        payload2 = await communicator.receive_json_from()
        assert payload2 == {"error": "Too many messages. Please slow down."}

        await communicator.disconnect()

    async_to_sync(run)()

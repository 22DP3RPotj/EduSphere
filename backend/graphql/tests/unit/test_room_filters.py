import pytest

pytestmark = pytest.mark.unit


def test_room_filter_search_calls_queryset_filter():
    from backend.graphql.room.filters import RoomFilter

    class DummyQuerySet:
        def __init__(self):
            self.args = None

        def filter(self, *args, **kwargs):
            self.args = (args, kwargs)
            return "filtered"

    qs = DummyQuerySet()
    # Avoid instantiating the django-filter FilterSet (it expects a real QuerySet
    # with a model). The method itself only needs a queryset-like object.
    rf = RoomFilter.__new__(RoomFilter)

    result = RoomFilter.filter_search(rf, qs, "search", "abc")

    assert result == "filtered"
    assert qs.args is not None

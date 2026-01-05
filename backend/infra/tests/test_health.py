import pytest
from django.test import Client


@pytest.mark.django_db
def test_health_live():
    client = Client()
    resp = client.get("/infra/live")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.django_db
def test_health_ready():
    client = Client()
    resp = client.get("/infra/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

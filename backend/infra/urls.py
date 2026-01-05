from django.urls import path

from backend.infra.views import health, info


urlpatterns = [
    path("live", health.live, name="health-live"),
    path("ready", health.ready, name="health-ready"),
    path("info", info.version, name="info-version"),
]

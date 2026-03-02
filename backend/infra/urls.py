from django.urls import path, include

from backend.infra.views import health, info


urlpatterns = [
    path("live", health.live, name="health-live"),
    path("ready", health.ready, name="health-ready"),
    path("info", info.version, name="info-version"),
    path("", include("django_prometheus.urls")),
]

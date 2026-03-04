from django.urls import path
from django_prometheus import exports
from backend.infra.views import health, info


urlpatterns = [
    path("live/", health.live, name="health-live"),
    path("ready/", health.ready, name="health-ready"),
    path("info/", info.version, name="info-version"),
    path("metrics/", exports.ExportToDjangoView, name="prometheus-django-metrics"),
]

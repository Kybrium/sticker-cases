import os

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from router import router
from wallet.views import tonconsole_webhook

from .health import healthz

webhook_uuid = os.getenv("TONCONSOLE_WEBHOOK_UUID")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz),
    path("api/", include(router.urls)),
    path(f"webhook/tonconsole/{webhook_uuid}", tonconsole_webhook),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

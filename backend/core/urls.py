from django.contrib import admin
from django.urls import path, include
from .health import healthz
from router import router, get_manifest
from django.conf.urls.static import static
from .settings import MEDIA_URL, MEDIA_ROOT
from wallet.views import tonconsole_webhook

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path("healthz/", healthz),
                  path('api/', include(router.urls)),
                  path('tonconnect-manifest.json', get_manifest),
                  path('webhook/tonconsole/6ecad084-35fb-43bb-a805-77a2a4291232', tonconsole_webhook)
              ] + static(MEDIA_URL, document_root=MEDIA_ROOT)

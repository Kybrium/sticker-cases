from django.contrib import admin
from django.urls import path, include
from .health import healthz
from router import router
from django.conf.urls.static import static
from .settings import MEDIA_URL, MEDIA_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    path("healthz/", healthz),
    path('api/', include(router.urls))
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
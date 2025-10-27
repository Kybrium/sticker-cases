from packs.views import PackAPIViewSet
from cases.views import CaseAPIViewSet
from rest_framework import routers
from wallet.views import WalletAPIViewSet
from users.views import UserAPIViewSet
from upgrade.views import UpgradeAPIViewSet
from django.urls import path
from consumers import WSConsumer

ws_urlpatterns = [
    path('ws/rolls/', WSConsumer.as_asgi())
]

router = routers.DefaultRouter()
router.register(
    prefix="packs",
    viewset=PackAPIViewSet,
    basename="packs"
)
router.register(
    prefix="cases",
    viewset=CaseAPIViewSet,
    basename="cases"
)
router.register(
    prefix="wallet",
    viewset=WalletAPIViewSet,
    basename="wallet"
)
router.register(
    prefix="users",
    viewset=UserAPIViewSet,
    basename="users"
)
router.register(
    prefix="upgrade",
    viewset=UpgradeAPIViewSet,
    basename="upgrade"
)

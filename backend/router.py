from packs.views import PackAPIViewSet
from cases.views import CaseAPIViewSet
from rest_framework import routers
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status as drf_status
from rest_framework.decorators import api_view
from wallet.views import WalletAPIViewSet
from users.views import UserAPIViewSet

manifest = {
    "url": "http://localhost:8080",
    "name": "TON Connect Demo"
}


@api_view(["GET"])
def get_manifest(request: Request):
    return Response(manifest, status=drf_status.HTTP_200_OK)


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

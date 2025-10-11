from rest_framework import status as drf_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from .models import Upgrade
from .serializers import UpgradeLiquiditySerializer
from packs.models import Liquidity, Pack
from users.models import CustomUser, UserInventory
import random
from packs.serializers import ResponseLiquiditySerializer, RequestLiquiditySerializer
from shared.calculations import get_upgrade_liquidity
from django.utils import timezone
from django.db import transaction


class UpgradeAPIViewSet(viewsets.GenericViewSet):
    queryset = Upgrade.objects.all()
    serializer_class = UpgradeLiquiditySerializer

    @action(detail=False, methods=["GET"], url_path="check")
    def check_upgrade(self, request: Request) -> Response:
        serializer = RequestLiquiditySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        liquidity = serializer.validated_data["liquidity"]

        result = get_upgrade_liquidity(liquidity)

        data = [
            {
                "id": liq.id,
                "liq_name": liq.pack.pack_name,
                "liq_collection": liq.pack.collection_name,
                "liq_contributor": liq.pack.contributor,
                "liq_number": liq.number,
                "floor_price": liq.pack.floor_price,
                "image_url": liq.pack.image_url or "",
                "chance": chance
            }
            for liq, chance in result
        ]

        return Response({
            "status": "success",
            "message": "Получена ликвидность доступная для апгрейда",
            "liquidity": data
        }, status=drf_status.HTTP_200_OK)

    @action(detail=False, methods=["POST"], url_path="upgrade")
    def upgrade_pack(self, request: Request) -> Response:
        serializer = UpgradeLiquiditySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        roll = random.random()

        user = serializer.validated_data["user"]
        user_liq = serializer.validated_data["user_liq"]
        upgrade_liq = serializer.validated_data["upgrade_liq"]
        chance = serializer.validated_data["chance"]
        bet = serializer.validated_data["user_pack"]
        drop = serializer.validated_data["upgrade_pack"]

        if roll <= chance:
            with transaction.atomic():
                Upgrade.objects.create(user=user, bet=bet, success=True, drop=drop, date=timezone.now())
                user_liq.free = True
                user_liq.save()
                try:
                    liq_to_delete: UserInventory = UserInventory.objects.get(user=user, liquidity=user_liq)
                    liq_to_delete.delete()
                except UserInventory.DoesNotExist:
                    return Response({"status": "error", "message": "Не удалось удалить ликвидность из инвентаря"})
                upgrade_liq.free = False
                upgrade_liq.save()
                CustomUser.objects.create(user=user, liquidity=upgrade_liq)
            return Response({"status": "Test", "message": "Апгрейд успешен"}, drf_status.HTTP_200_OK)

        with transaction.atomic():
            user_liq.free = True
            user_liq.save()
            try:
                liq_to_delete: UserInventory = UserInventory.objects.get(user=user, liquidity=user_liq)
                liq_to_delete.delete()
            except UserInventory.DoesNotExist:
                return Response({"status": "error", "message": "Не удалось удалить ликвидность из инвентаря"})
            Upgrade.objects.create(user=user, bet=bet, success=False, drop=drop, date=timezone.now())
        return Response({"status": "Test", "message": "Апгрейд не случился"}, drf_status.HTTP_200_OK)

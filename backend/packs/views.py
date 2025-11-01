from typing import cast

from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from packs.serializers import PackSerializer
from rest_framework import status as drf_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from users.models import CustomUser
from packs.serializers import RequestLiquiditySerializer
from packs.models import UserInventory

from .models import Pack, PackSell


class PackAPIViewSet(viewsets.GenericViewSet):
    queryset = Pack.objects.all()
    serializer_class = PackSerializer

    def list(self, request: Request) -> Response:
        pack_id = request.GET.get("id")

        if pack_id:
            serializer = PackSerializer(data={"id": pack_id})
            serializer.is_valid(raise_exception=True)
            pack = serializer.save()
            return Response(
                {"status": "success", "pack": serializer.to_representation(pack)},
                status=drf_status.HTTP_200_OK,
            )

        all_packs = self.get_queryset()

        if not all_packs.exists():
            return Response({"status": "success", "items": []}, status=drf_status.HTTP_200_OK)

        serializer = self.get_serializer(all_packs, many=True)
        return Response(
            {"status": "success", "items": serializer.data},
            status=drf_status.HTTP_200_OK,
        )

    @method_decorator(cache_page(70))
    @action(detail=False, methods=["get"], url_path="contributor/(?P<contributor>[^/.]+)")
    def list_by_contributor(self, request: Request, contributor: str | None = None) -> Response:
        if not contributor:
            return Response(
                {"status": "error", "message": "URL param 'contributor' is required"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        packs = Pack.objects.filter(contributor=contributor)
        serializer = PackSerializer(packs, many=True)
        return Response(
            {"status": "success", "items": serializer.data},
            status=drf_status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="pack/(?P<collection_name>[^/.]+)/(?P<pack_name>[^/.]+)",
    )
    def get_pack(self, request: Request, pack_name: str, collection_name: str) -> Response:
        serializer = PackSerializer(data={"collection_name": collection_name, "pack_name": pack_name})
        serializer.is_valid(raise_exception=True)
        pack = serializer.save()

        return Response(
            {"status": "success", "item": serializer.to_representation(pack)},
            status=drf_status.HTTP_200_OK,
        )

    @action(detail=False, methods=["patch"], url_path="update-stickers-price")
    def update_stickers_price(self, request: Request) -> Response:
        data = request.data.get("packs_data")

        if not data or not isinstance(data, dict):
            return Response(
                {
                    "status": "error",
                    "message": "Поле 'packs_data' обязательно и должно быть словарём",
                },
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        packs_to_update = []
        try:
            with transaction.atomic():
                for collection, pack in data.items():
                    for pack_name, price in pack.items():
                        try:
                            obj = Pack.objects.get(collection_name=collection, pack_name=pack_name)
                            obj.price = price
                            packs_to_update.append(obj)
                        except Pack.DoesNotExist:
                            continue

                if packs_to_update:
                    Pack.objects.bulk_update(packs_to_update, ["price"])

        except Exception as e:
            return Response(
                {"status": "error", "message": f"Ошибка обновления: {str(e)}"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"status": "success", "updated": len(packs_to_update)},
            status=drf_status.HTTP_200_OK,
        )

    @action(detail=False, methods=["POST"], url_path="sell")
    def sell_liquidity(self, request: Request) -> Response:  # noqa: C901

        serializer = RequestLiquiditySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        liquidity = serializer.validated_data["liquidity"]
        pack = serializer.validated_data["pack"]
        user = serializer.validated_data["user"]

        if not UserInventory.objects.filter(user=user, liquidity=liquidity).exists():
            return Response(
                {"status": "error", "message": "Стикер не принадлежит пользователю"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                user.balance = cast(float, user.balance) + cast(float, pack.price)
                user.save()
                UserInventory.objects.filter(user=user, liquidity=liquidity).delete()
                liquidity.free = True
                liquidity.save()
                PackSell.objects.create(liquidity=liquidity, user=user, date=timezone.now())
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": f"Ошибка во время продажи стикера: {e}. Стикер не был продан.",
                },
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": "success",
                "message": "Стикер был продан",
                "amount_added": pack.price,
            },
            status=drf_status.HTTP_200_OK,
        )

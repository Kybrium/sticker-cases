from itertools import chain
from operator import attrgetter

from cases.models import CaseOpen
from django.db.models import QuerySet
from packs.models import Liquidity, PackSell
from packs.serializers import LiquiditySerializer
from rest_framework import status as drf_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from wallet.models import Deposit, Withdrawal

from .models import CustomUser
from .serializers import TransactionSerializer, UserSerializer


class UserAPIViewSet(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["POST"], url_path="user")
    def create_user(self, request: Request) -> Response:
        telegram_id = request.data.get("telegram_id")

        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
            if user:
                return Response({"status": "error", "message": "Пользователь уже был создан"}, drf_status.HTTP_200_OK)
        except Exception:
            pass

        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        username = request.data.get("username")
        language = request.data.get("language")
        is_bot = request.data.get("is_bot")
        image_url = request.data.get("image_url")

        try:
            CustomUser.objects.create_user(telegram_id=telegram_id, username=username, first_name=first_name,
                                           last_name=last_name, language=language, is_bot=is_bot,
                                           password="plug", image_url=image_url)
        except Exception as e:
            print("Ошибка при создании пользователя", e)
            return Response({"status": "error", "message": f"Ошибка при создании пользователя: {e}"},
                            drf_status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"status": "success", "message": "Новый пользователь создан"}, drf_status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="user/(?P<telegram_id>[^/.]+)")
    def get_user(self, request: Request, telegram_id: int | None) -> Response:
        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"status": "error", "message": "Пользователь не найден"},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        serialized = UserSerializer(user)
        return Response(
            {"status": "success", "user": serialized.data},
            status=drf_status.HTTP_200_OK,
        )

    @action(detail=False, methods=["GET"], url_path="user/(?P<telegram_id>[^/.]+)/inventory")
    def get_user_inventory(self, request: Request, telegram_id: int) -> Response:
        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"status": "error", "message": "Пользователь не найден"},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        liqs: QuerySet[Liquidity, Liquidity] | list[Liquidity] = user.get_liquidity or []
        serialized = LiquiditySerializer(liqs, many=True)
        return Response(
            {
                "status": "success",
                "inventory_count": len(liqs),
                "inventory": serialized.data,
            },
            status=drf_status.HTTP_200_OK,
        )

    @action(detail=False, methods=["GET"], url_path="(?P<telegram_id>[^/.]+)/transactions")
    def get_all_user_transactions(self, request: Request, telegram_id: int) -> Response:
        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"status": "error", "message": "Пользователь не найден"},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        all_case_opens = CaseOpen.objects.filter(user=user)
        all_pack_sell = PackSell.objects.filter(user=user)
        all_deposits = Deposit.objects.filter(user=user)
        all_withdrawals = Withdrawal.objects.filter(user=user)

        all_transactions = list(chain(all_withdrawals, all_deposits, all_case_opens, all_pack_sell))
        sorted_transactions = sorted(all_transactions, key=attrgetter("date"), reverse=True)

        serialized = TransactionSerializer(sorted_transactions, many=True)

        return Response(
            {
                "status": "success",
                "transaction_count": len(serialized.data),
                "transactions": serialized.data,
            },
            status=drf_status.HTTP_200_OK,
        )

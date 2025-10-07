import json
import os
from itertools import chain
from operator import attrgetter

from cases.models import CaseOpen
from django.contrib.auth import login, logout
from django.db.models import QuerySet
from django.utils import timezone
from packs.models import Liquidity, PackSell
from packs.serializers import LiquiditySerializer
from rest_framework import permissions
from rest_framework import status
from rest_framework import status as drf_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from wallet.models import Deposit, Withdrawal

from .models import CustomUser
from .serializers import TransactionSerializer, UserSerializer
from .telegram_wbapp import parse_init_data, verify_webapp_init_data


class TelegramWebAppLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        init_data = (request.data or {}).get("initData", "")
        if not bot_token or not init_data:
            return Response(
                {"ok": False, "error": "bad request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not verify_webapp_init_data(init_data, bot_token):
            return Response(
                {"ok": False, "error": "verification failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        items = parse_init_data(init_data)
        try:
            user_json = json.loads(items.get("user", "{}"))
            tg_id = int(user_json["id"])
        except Exception:
            return Response(
                {"ok": False, "error": "invalid user data"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = CustomUser.objects.get(telegram_id=tg_id)
        if user is None:
            user = CustomUser.objects.create(
                telegram_id=tg_id,
                username=user_json.get("username") or "",
                first_name=user_json.get("first_name") or "",
                last_name=user_json.get("last_name") or "",
                image_url=user_json.get("photo_url") or "",
                date_joined=timezone.now(),
            )
        else:
            user.username = user_json.get("username") or user.username
            user.first_name = user_json.get("first_name") or user.first_name
            user.last_name = user_json.get("last_name") or user.last_name
            user.image_url = user_json.get("image_url") or user.image_url
            user.date_joined = timezone.now()
            user.save()

        login(request, user)

        return Response(
            {
                "ok": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "telegram_id": user.telegram_id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "image_url": user.image_url,
                },
            },
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        user = getattr(request.user, "telegram", None)
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "telegram": {
                    "id": user.telegram_id if user else None,
                    "username": user.username if user else None,
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        logout(request)
        return Response({"ok": True}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------------
class UserAPIViewSet(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["GET"], url_path="(?P<telegram_id>[^/.]+)")
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

    @action(detail=False, methods=["GET"], url_path="(?P<telegram_id>[^/.]+)/inventory")
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

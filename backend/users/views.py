import os, json
from .serializers import UserSerializer
from django.contrib.auth import login, logout
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework import status as drf_status
from packs.serializers import LiquiditySerializer
from packs.models import Liquidity, PackSell
from cases.models import CaseOpen
from wallet.models import Withdrawal, Deposit
from itertools import chain
from operator import attrgetter
from .models import CustomUser
from .telegram_wbapp import verify_webapp_init_data, parse_init_data
from .serializers import TransactionSerializer


class TelegramWebAppLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        init_data = (request.data or {}).get("initData", "")
        if not bot_token or not init_data:
            return Response({"ok": False, "error": "bad request"}, status=status.HTTP_400_BAD_REQUEST)

        if not verify_webapp_init_data(init_data, bot_token):
            return Response({"ok": False, "error": "verification failed"}, status=status.HTTP_400_BAD_REQUEST)

        items = parse_init_data(init_data)
        try:
            user_json = json.loads(items.get("user", "{}"))
            tg_id = int(user_json["id"])
        except Exception:
            return Response({"ok": False, "error": "invalid user data"}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(telegram_id=tg_id)
        if user is None:
            user = CustomUser.objects.create(
                telegram_id=tg_id,
                username=user_json.get("username") or "",
                first_name=user_json.get("first_name") or "",
                last_name=user_json.get("last_name") or "",
                photo_url=user_json.get("photo_url") or "",
                auth_date=timezone.now(),
            )
        else:
            user.username = user_json.get("username") or acc.username
            user.first_name = user_json.get("first_name") or acc.first_name
            user.last_name = user_json.get("last_name") or acc.last_name
            user.photo_url = user_json.get("photo_url") or acc.photo_url
            user.auth_date = timezone.now()
            user.save()

        login(request, user)

        return Response({
            "ok": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "telegram_id": user.telegram_id,
                "telegram_username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "photo_url": user.photo_url,
            }
        }, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = getattr(request.user, "telegram", None)
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "telegram": {
                "id": acc.telegram_id if acc else None,
                "username": acc.username if acc else None,
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"ok": True}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------------
class UserAPIViewSet(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["GET"], url_path="(?P<telegram_id>[^/.]+)")
    def get_user(self, request: Request, telegram_id=None):
        user = get_object_or_404(CustomUser, telegram_id=telegram_id)
        serialized = UserSerializer(user)
        return Response({"message": "Пользователь найден", "user": serialized.data}, drf_status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="(?P<telegram_id>[^/.]+)/inventory")
    def get_user_inventory(self, request: Request, telegram_id=None):
        user: CustomUser = get_object_or_404(CustomUser, telegram_id=telegram_id)
        liqs: list[Liquidity] = user.get_liquidity
        if not liqs:
            return Response({"error": "Инвентарь пуст"}, drf_status.HTTP_400_BAD_REQUEST)

        serialized = LiquiditySerializer(liqs, many=True)
        return Response({"message": f"Возвращено {len(liqs)} объектов", "inventory": serialized.data},
                        drf_status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="(?P<telegram_id>[^/.]+)/transactions")
    def get_all_user_transactions(self, request: Request, telegram_id=None):
        user = get_object_or_404(CustomUser, telegram_id=telegram_id)
        all_case_opens = CaseOpen.objects.filter(user=user)
        all_pack_sell = PackSell.objects.filter(user=user)
        all_deposits = Deposit.objects.filter(user=user)
        all_withdrawals = Withdrawal.objects.filter(user=user)

        all_transactions = list(chain(all_withdrawals, all_deposits, all_case_opens, all_pack_sell))
        if not all_transactions:
            return Response({"error": "У пользователя нет транзакций"}, drf_status.HTTP_400_BAD_REQUEST)

        sorted_transactions = sorted(all_transactions, key=attrgetter("date"), reverse=True)

        serialized = TransactionSerializer(sorted_transactions, many=True)

        return Response({"transactions": serialized.data}, drf_status.HTTP_200_OK)

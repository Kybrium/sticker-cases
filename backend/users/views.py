from itertools import chain
from operator import attrgetter

from cases.models import CaseOpen
from django.db.models import QuerySet
from packs.models import Liquidity, PackSell
from packs.serializers import ResponseLiquiditySerializer
from rest_framework import status as drf_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from wallet.models import Deposit, Withdrawal
from upgrade.models import Upgrade

from .models import CustomUser
from .serializers import TransactionSerializer, UserSerializer


class UserAPIViewSet(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["GET"], url_path="(?P<telegram_id>[^/.]+)")
    def get_user(self, request: Request, telegram_id: int | None) -> Response:
        serializer = UserSerializer(data={"telegram_id": telegram_id})
        serializer.is_valid(raise_exception=True)

        user = CustomUser.objects.get(telegram_id=telegram_id)
        serialized = UserSerializer(user)
        return Response({"status": "success", "user": serialized.data})

    @action(detail=False, methods=["GET"], url_path="(?P<telegram_id>[^/.]+)/inventory")
    def get_user_inventory(self, request: Request, telegram_id: int | None = None) -> Response:
        serializer = UserSerializer(data={"telegram_id": telegram_id})
        serializer.is_valid(raise_exception=True)

        user = CustomUser.objects.get(telegram_id=telegram_id)

        liqs: QuerySet[Liquidity, Liquidity] | list[Liquidity] = user.get_liquidity or []
        serialized = ResponseLiquiditySerializer(liqs, many=True)
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
        serializer = UserSerializer(data={"telegram_id": telegram_id})
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(telegram_id=telegram_id)

        all_case_opens = CaseOpen.objects.filter(user=user)
        all_pack_sell = PackSell.objects.filter(user=user)
        all_deposits = Deposit.objects.filter(user=user)
        all_withdrawals = Withdrawal.objects.filter(user=user)
        all_upgrades = Upgrade.objects.filter(user=user)

        all_transactions = list(chain(all_withdrawals, all_deposits, all_case_opens, all_pack_sell, all_upgrades))
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

import random
from typing import Any, cast

from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from packs.models import Liquidity, Pack
from packs.serializers import CaseItemSerializer, PackSerializer
from rest_framework import status as drf_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response
from users.models import CustomUser, UserInventory

from .models import Case, CaseItem, CaseOpen, CaseStatus
from .serializers import CaseSerializer


def open_case(case: Case) -> tuple[dict, int]:
    case_packs = CaseItem.objects.filter(case=case)
    if not case_packs.exists():
        return {"error": "Стикеры в кейсе отсутствуют"}, 400

    rand_value = random.random()
    cumulative: float = 0
    selected_pack: Any | None = None

    for cp in case_packs:
        cumulative += cp.chance
        if rand_value <= cumulative:
            selected_pack = cp.pack
            break

    if selected_pack is None:
        last_cp = case_packs.last()
        if last_cp is None:
            return {"error": "Стикеры в кейсе отсутствуют"}, 400
        selected_pack = last_cp.pack

    serializer = PackSerializer(selected_pack)
    return {"serialized_pack": serializer.data, "raw_pack": selected_pack}, 200


class CaseAPIViewSet(viewsets.GenericViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    def list(self, request: Request) -> Response:
        active_cases = self.get_queryset().filter(status=CaseStatus.ACTIVE)
        pagination = request.GET.get("pagination")

        if not active_cases.exists():
            return Response(
                {
                    "status": "success",
                    "message": "Нету доступных кейсов",
                },
                status=drf_status.HTTP_200_OK,
            )

        if pagination:
            paginator = LimitOffsetPagination()
            paginator.default_limit = 2
            paginator.max_limit = 10
            page = paginator.paginate_queryset(active_cases, request, view=self)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return Response(
                    {
                        "status": "success",
                        "count": paginator.count,
                        "next": paginator.get_next_link(),
                        "previous": paginator.get_previous_link(),
                        "items": serializer.data,
                    }
                )

        serializer = CaseSerializer(active_cases, many=True)
        return Response({"status": "success", "items": serializer.data}, drf_status.HTTP_200_OK)

    @action(detail=False, methods=["patch"], url_path="update-chances")
    def update_chances(self, request: Request) -> Response:
        data = request.data.get("data")

        if not data or not isinstance(data, dict):
            return Response(
                {
                    "status": "error",
                    "message": "Поле 'data' обязательно и должно быть словарём",
                },
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        chances_to_update = []
        try:
            with transaction.atomic():
                for case, pack_data in data.items():
                    print(case, pack_data)
                    for pack_info in pack_data:
                        try:
                            pack = Pack.objects.get(
                                pack_name=pack_info["pack_name"],
                                collection_name=pack_info["collection_name"],
                            )
                            obj = CaseItem.objects.get(pack=pack)
                            obj.chance = pack_info["chance"]
                            chances_to_update.append(obj)
                        except (Pack.DoesNotExist, CaseItem.DoesNotExist):
                            continue
                if chances_to_update:
                    CaseItem.objects.bulk_update(chances_to_update, ["chance"])
        except Exception as e:
            return Response(
                {"status": "error", "message": f"Ошибка обновления: {str(e)}"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"status": "success", "updated": len(chances_to_update)},
            status=drf_status.HTTP_200_OK,
        )

    @action(detail=False, methods=["patch"], url_path="update-cases")
    def update_cases(self, request: Request) -> Response:
        data = request.data.get("data")

        if not data or not isinstance(data, dict):
            return Response(
                {
                    "status": "error",
                    "message": "Поле 'data' обязательно и должно быть словарём",
                },
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        cases_to_update = []
        try:
            with transaction.atomic():
                for case_name, value in data.items():
                    try:
                        obj = Case.objects.get(name=case_name)
                        obj.current_fee = value.get("fee", obj.current_fee)
                        obj.price = value.get("price", obj.price)
                        cases_to_update.append(obj)
                    except Case.DoesNotExist:
                        continue
                if cases_to_update:
                    Case.objects.bulk_update(cases_to_update, ["current_fee", "price"])
        except Exception as e:
            return Response(
                {"status": "error", "message": f"Ошибка обновления: {str(e)}"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"status": "success", "updated": len(cases_to_update)},
            status=drf_status.HTTP_200_OK,
        )

    @method_decorator(cache_page(300))
    @action(detail=False, methods=["get"], url_path="case/(?P<case_name>[^/.]+)")
    def list_case_items(self, request: Request, case_name: str) -> Response:
        try:
            case = Case.objects.get(name=case_name)
        except Case.DoesNotExist:
            return Response(
                {"status": "error", "message": "Кейс не найден"},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        case_items = CaseItem.objects.filter(case=case)
        serializer = CaseItemSerializer(case_items, many=True)
        return Response(
            {"status": "success", "case": case.name, "items": serializer.data},
            status=drf_status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["POST", "GET"],
        url_path="case/(?P<case_name>[^/.]+)/open",
    )
    def open_case_view(self, request: Request, case_name: str | None = None) -> Response:  # noqa: C901
        telegram_id = request.data.get("telegram_id")

        if not telegram_id:
            return Response(
                {"status": "error", "message": "Telegram ID не предоставлен"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        try:
            case = Case.objects.get(name=case_name)
        except Case.DoesNotExist:
            return Response(
                {"status": "error", "message": "Кейс не найден"},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        user = None
        if telegram_id:
            try:
                user = CustomUser.objects.get(telegram_id=telegram_id)
            except CustomUser.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Пользователь не найден"},
                    status=drf_status.HTTP_404_NOT_FOUND,
                )
            if cast(float, case.price) > cast(float, user.balance):
                return Response(
                    {
                        "status": "error",
                        "message": "Недостаточно денег на балансе",
                        "case_price": case.price,
                        "user_balance": user.balance,
                    },
                    status=drf_status.HTTP_400_BAD_REQUEST,
                )

        message, status_code = open_case(case)
        if status_code != 200:
            return Response({"status": "error", "message": message}, status=status_code)

        pack: Pack = message["raw_pack"]

        if user:
            if case.status == CaseStatus.OUT_OF_STICKERS:
                return Response(
                    {"status": "error", "message": "Кейс не доступен для открытий"},
                    status=drf_status.HTTP_400_BAD_REQUEST,
                )

            if pack.liquidity_count <= 0:
                case.status = CaseStatus.OUT_OF_STICKERS
                case.save()
                return Response(
                    {
                        "status": "error",
                        "message": "В кейсе закончились стикеры. Баланс не был списан",
                    },
                    status=drf_status.HTTP_409_CONFLICT,
                )

            try:
                with transaction.atomic():
                    drop: Liquidity | None = Liquidity.objects.filter(pack=pack, in_case=True).first()
                    if not drop:
                        case.status = CaseStatus.OUT_OF_STICKERS
                        case.save()
                        return Response(
                            {"error": "Не найден дроп для кейса. Баланс не был списан."},
                            drf_status.HTTP_400_BAD_REQUEST,
                        )
                    drop.in_case = False
                    drop.save()

                    user.balance = cast(float, user.balance) - cast(float, case.price)
                    user.save()

                    UserInventory.objects.create(user=user, liquidity=drop)
                    CaseOpen.objects.create(user=user, case=case, drop=drop, date=timezone.now())
            except Exception as e:
                return Response(
                    {
                        "status": "error",
                        "message": f"Ошибка во время распределения дропа: {e}. Баланс не был списан",
                    },
                    status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {
                    "status": "success",
                    "drop": message["serialized_pack"],
                    "drop_number": drop.number,
                },
                status=drf_status.HTTP_200_OK,
            )

        return Response(
            {"status": "success", "drop": message["serialized_pack"]},
            status=drf_status.HTTP_200_OK,
        )

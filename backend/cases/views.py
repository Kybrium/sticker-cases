from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from .models import Case, CaseStatus, CaseItems
from rest_framework import status as drf_status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from packs.models import Pack
from packs.serializers import PackSerializer, CaseItemsSerializer
from .serializers import CaseSerializer
import random
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.celery import celery_app
from rest_framework.pagination import LimitOffsetPagination


class CaseAPIViewSet(viewsets.GenericViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    def list(self, request: Request) -> Response:
        active_cases = self.get_queryset().filter(status=CaseStatus.ACTIVE)

        if not active_cases.exists():
            return Response(
                {"error": "Нету доступных кейсов."},
                status=drf_status.HTTP_404_NOT_FOUND
            )

        paginator = LimitOffsetPagination()
        page = paginator.paginate_queryset(active_cases, request, view=self)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = CaseSerializer(active_cases, many=True)
        return Response(serializer.data, drf_status.HTTP_200_OK)





    @method_decorator(cache_page(300))
    @action(detail=False, methods=["get"], url_path="(?P<case_name>[^/.]+)")
    def list_case_items(self, request: Request, case_name=None):
        try:
            case = Case.objects.get(name=case_name)
        except Case.DoesNotExist:
            return Response({"error": "Кейс не найден."}, status=drf_status.HTTP_404_NOT_FOUND)

        case_items = CaseItems.objects.filter(case=case)
        serializer = CaseItemsSerializer(case_items, many=True)
        return Response(serializer.data, status=drf_status.HTTP_200_OK)


    @action(detail=False, methods=["get"], url_path="(?P<case_name>[^/.]+)/demo-open")
    def demo_open_case(self, request, case_name=None):
        """
        октрытие кейса в демо режиме. Данные никуда не записываются, токен не нужен
        """
        try:
            case = Case.objects.get(name=case_name)
        except Case.DoesNotExist:
            return Response({"error": "Кейс не найден"}, status=drf_status.HTTP_404_NOT_FOUND)

        case_packs = CaseItems.objects.filter(case=case)
        if not case_packs.exists():
            return Response({"error": "Пакеты в кейсе отсутствуют"}, status=drf_status.HTTP_404_NOT_FOUND)

        rand_value = random.random()
        cumulative = 0
        for cp in case_packs:
            cumulative += cp.chance
            if rand_value <= cumulative:
                selected_pack = cp.pack
                break
        else:
            selected_pack = case_packs.last().pack

        serializer = PackSerializer(selected_pack)

        return Response({
            "pack": serializer.data,
        }, status=drf_status.HTTP_200_OK)

    @action(detail=False, methods=["patch"], url_path="(?P<case_name>[^/.]+)/update-chance/(?P<pack_name>[^/.]+)")
    def update_chance(self, request, pack_name=None, case_name=None):
        pack = get_object_or_404(Pack, pack_name=pack_name)
        case = get_object_or_404(Case, name=case_name)
        new_chance = request.data.get("chance")
        if new_chance is None:
            return Response(
                {"error": "Поле 'chance' обязательно."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        try:
            new_chance = float(new_chance)
        except ValueError:
            return Response(
                {"error": "chance должно быть числом."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        case_item = get_object_or_404(CaseItems, case=case, pack=pack)
        case_item.chance = new_chance
        case_item.save()

        return Response(
            {"message": f"Шанс для стикерпака {pack.pack_name} в кейсе {case.name} обновлен на {new_chance}.", "chance": new_chance},
            status=drf_status.HTTP_200_OK
        )


    @action(detail=False, methods=["patch"], url_path="(?P<case_name>[^/.]+)/update-current-fee")
    def update_current_case_fee(self, request, case_name=None):
        case = get_object_or_404(Case, name=case_name)
        new_fee = request.data.get("fee")
        if new_fee is None:
            return Response(
                {"error": "Поле 'fee' обязательно."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        try:
            new_fee = float(new_fee)  # или Decimal(new_chance)
        except ValueError:
            return Response(
                {"error": "Fee должно быть числом."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        case = get_object_or_404(Case, name=case_name)
        case.current_fee = new_fee
        case.save()

        return Response(
            {"message": f"Текущее fee для кейса {case.name} обновлено на {new_fee}."},
            status=drf_status.HTTP_200_OK
        )

    @action(detail=False, methods=["patch"], url_path="(?P<case_name>[^/.]+)/update-price")
    def update_case_price(self, request: Request, case_name=None):
        case = get_object_or_404(Case, name=case_name)
        new_price = request.data.get("price")
        if new_price is None:
            return Response(
                {"error": "Поле 'price' обязательно."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        try:
            new_price = float(new_price)
        except ValueError:
            return Response(
                {"error": "Price должно быть числом."},
                status=drf_status.HTTP_400_BAD_REQUEST
            )

        case = get_object_or_404(Case, name=case_name)
        case.price = new_price
        case.save()

        return Response(
            {"message": f"Текущая цена для кейса {case.name} обновлена на {new_price}."},
            status=drf_status.HTTP_200_OK
        )

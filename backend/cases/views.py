from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from .models import Case, CaseStatus, CaseItems
from rest_framework import status as drf_status
from rest_framework.decorators import action
from packs.models import Pack
from packs.serializers import PackSerializer, CaseItemsSerializer
from .serializers import CaseSerializer
import random
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.celery import celery_app
from rest_framework.pagination import LimitOffsetPagination
from django.db import transaction


class CaseAPIViewSet(viewsets.GenericViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer

    def list(self, request: Request) -> Response:
        active_cases = self.get_queryset().filter(status=CaseStatus.ACTIVE)
        pagination = request.GET.get("pagination")

        if not active_cases.exists():
            return Response(
                {"error": "Нету доступных кейсов."},
                status=drf_status.HTTP_404_NOT_FOUND
            )

        if pagination:
            paginator = LimitOffsetPagination()
            page = paginator.paginate_queryset(active_cases, request, view=self)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

        serializer = CaseSerializer(active_cases, many=True)
        return Response(serializer.data, drf_status.HTTP_200_OK)


    @action(detail=False, methods=["patch"], url_path="update-chances")
    def update_chances(self, request: Request):
        print("До получения даты в update_chances")
        data = request.data.get("data")
        print("После получения даты в update_chances", data)
        chances_to_update = []
        try:
            with transaction.atomic():
                for case, pack_data in data.items():
                    print(case, pack_data)
                    for pack_info in pack_data:
                        try:
                            pack = Pack.objects.get(pack_name=pack_info["pack_name"], collection_name=pack_info["collection_name"])
                            obj = CaseItems.objects.get(pack=pack)
                            obj.chance = pack_info["chance"]
                            chances_to_update.append(obj)
                        except [Pack.DoesNotExist, CaseItems.DoesNotExist]:
                            continue
                if chances_to_update:
                    CaseItems.objects.bulk_update(chances_to_update, ["chance"])
        except Exception as e:
            return Response(
                {"detail": f"Ошибка обновления: {str(e)}"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        return Response({"info": len(chances_to_update)}, status=drf_status.HTTP_200_OK)

    @action(detail=False, methods=["patch"], url_path="update-cases")
    def update_cases(self, request: Request):
        print("До получения данных в update_cases")
        data = request.data.get("data")
        print("После получения данных в update_cases", data)
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
                {"detail": f"Ошибка обновления: {str(e)}"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        return Response({"info": len(cases_to_update)}, status=drf_status.HTTP_200_OK)


    @method_decorator(cache_page(300))
    @action(detail=False, methods=["get"], url_path="case/(?P<case_name>[^/.]+)")
    def list_case_items(self, request: Request, case_name=None):
        try:
            case = Case.objects.get(name=case_name)
        except Case.DoesNotExist:
            return Response({"error": "Кейс не найден."}, status=drf_status.HTTP_404_NOT_FOUND)

        case_items = CaseItems.objects.filter(case=case)
        serializer = CaseItemsSerializer(case_items, many=True)
        return Response(serializer.data, status=drf_status.HTTP_200_OK)


    @action(detail=False, methods=["get"], url_path="case/(?P<case_name>[^/.]+)/demo-open")
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

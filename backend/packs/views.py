from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from .models import Pack
from rest_framework import status as drf_status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from packs.serializers import PackSerializer
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db import transaction



class PackAPIViewSet(viewsets.GenericViewSet):
    queryset = Pack.objects.all()
    serializer_class = PackSerializer

    def list(self, request: Request) -> Response:
        all_packs = self.get_queryset()

        if not all_packs.exists():
            return Response(
                {"error": "Нету паков в бд."},
                status=drf_status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(all_packs, many=True)
        return Response(serializer.data, status=drf_status.HTTP_200_OK)

    # @method_decorator(cache_page(70))
    @action(detail=False, methods=["get"], url_path="contributor/(?P<contributor>[^/.]+)")
    def list_by_contributor(self, request: Request, contributor=None):
        """
        контрибьютор это стикер пак, fuse, зеленый слон маркет и прочее
        """
        packs = Pack.objects.filter(contributor=contributor)
        serializer = PackSerializer(packs, many=True)
        return Response(serializer.data, status=drf_status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="(?P<collection_name>[^/.]+)/(?P<pack_name>[^/.]+)")
    def get_pack(self, request: Request, pack_name=None, collection_name=None):
        pack = get_object_or_404(Pack, pack_name=pack_name, collection_name=collection_name)
        serializer = PackSerializer(pack)
        return Response(serializer.data, status=drf_status.HTTP_200_OK)

    @action(detail=False, methods=["patch"], url_path="update-stickers-price")
    def update_stickers_price(self, request: Request):
        data = request.data.get("packs_data")
        packs_to_update = []
        try:
            with transaction.atomic():
                for collection, pack in data.items():
                    print(collection, pack)
                    for pack_name, price in pack.items():
                        try:
                            obj = Pack.objects.get(
                                collection_name=collection,
                                pack_name=pack_name
                            )
                            obj.floor_price = price
                            packs_to_update.append(obj)
                        except Pack.DoesNotExist:
                            continue

                if packs_to_update:
                    Pack.objects.bulk_update(packs_to_update, ["floor_price"])

        except Exception as e:
            return Response(
                {"detail": f"Ошибка обновления: {str(e)}"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        return Response({"info": len(packs_to_update)}, status=drf_status.HTTP_200_OK)

from rest_framework import serializers
from .models import Pack
from cases.serializers import CaseItemsSerializer


class PackSerializer(serializers.ModelSerializer):
    cases = CaseItemsSerializer(source="pack_items", many=True, read_only=True)

    class Meta:
        model = Pack
        fields = [
            "pack_name",
            "collection_name",
            "contributor",
            "floor_price",
            "status",
            "in_stock_count",
            "image_url",
            "cases"
        ]

from rest_framework import serializers
from .models import Pack
from cases.serializers import CaseItemSerializer


class PackSerializer(serializers.ModelSerializer):
    cases = CaseItemSerializer(source="pack_items", many=True, read_only=True)

    class Meta:
        model = Pack
        fields = [
            "pack_name",
            "collection_name",
            "contributor",
            "floor_price",
            "status",
            "image_url",
            "cases"
        ]

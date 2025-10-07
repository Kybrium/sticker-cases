from cases.serializers import CaseItemSerializer
from rest_framework import serializers

from .models import Liquidity, Pack


class PackSerializer(serializers.ModelSerializer):
    cases = CaseItemSerializer(source="pack_item", many=True, read_only=True)

    class Meta:
        model = Pack
        fields = [
            "pack_name",
            "collection_name",
            "contributor",
            "floor_price",
            "image_url",
            "cases",
        ]


class LiquiditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Liquidity
        fields = ["pack", "number"]

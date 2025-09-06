from rest_framework import serializers
from .models import Case, CaseItems


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ["name", "price", "image_url", "base_fee"]


class CaseItemsSerializer(serializers.ModelSerializer):
    pack_name = serializers.CharField(source="pack.pack_name")
    pack_floor_price = serializers.DecimalField(source="pack.floor_price", max_digits=20, decimal_places=3)
    pack_image = serializers.CharField(source="pack.image_url")
    chance = serializers.FloatField()
    case_name = serializers.CharField(source="case.name")

    class Meta:
        model = CaseItems
        fields = ["pack_name", "pack_image", "chance", "case_name", "pack_floor_price"]

from cases.serializers import CaseItemSerializer
from rest_framework import serializers
from users.models import CustomUser, UserInventory

from .models import Liquidity, Pack


class PackSerializer(serializers.Serializer):
    collection_name = serializers.CharField()
    pack_name = serializers.CharField()

    def validate(self, attrs):
        collection_name = attrs.get("collection_name")
        pack_name = attrs.get("pack_name")

        try:
            pack = Pack.objects.get(
                collection_name=collection_name,
                pack_name=pack_name,
            )
        except Pack.DoesNotExist:
            raise serializers.ValidationError("Пак не найден")

        attrs["pack"] = pack
        return attrs

    def create(self, validated_data):
        return validated_data["pack"]

    def to_representation(self, instance):
        """instance — это уже объект Pack"""
        return {
            "pack_name": instance.pack_name,
            "collection_name": instance.collection_name,
            "contributor": instance.contributor,
            "floor_price": instance.floor_price,
            "image_url": instance.image_url,
            "cases": CaseItemSerializer(instance.cases.all(), many=True).data,
        }


class ResponseLiquiditySerializer(serializers.ModelSerializer):
    pack = PackSerializer()

    class Meta:
        model = Liquidity
        fields = ["pack", "number", "id"]


class RequestLiquiditySerializer(serializers.Serializer):
    pack_name = serializers.CharField(required=False)
    collection_name = serializers.CharField(required=False)
    contributor = serializers.CharField(required=False)
    number = serializers.IntegerField(required=False)

    id = serializers.IntegerField(required=False)

    telegram_id = serializers.IntegerField()

    def validate(self, attrs):
        liquidity = None
        pack = None

        if attrs.get("id"):
            try:
                liquidity = Liquidity.objects.get(id=attrs["id"])
                pack = liquidity.pack
            except Liquidity.DoesNotExist:
                raise serializers.ValidationError({"id": "Ликвидность с таким id не найдена"})

        else:
            try:
                pack = Pack.objects.get(
                    pack_name=attrs["pack_name"],
                    collection_name=attrs["collection_name"],
                    contributor=attrs["contributor"]
                )
            except Pack.DoesNotExist:
                raise serializers.ValidationError({"pack_name": "Пак не найден"})

            try:
                liquidity = Liquidity.objects.get(pack=pack, number=attrs["number"])
            except Liquidity.DoesNotExist:
                raise serializers.ValidationError({"number": "Ликвидность не найдена"})

        try:
            user = CustomUser.objects.get(telegram_id=attrs["telegram_id"])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"telegram_id": "Пользователь не найден"})

        attrs["pack"] = pack
        attrs["liquidity"] = liquidity
        attrs["user"] = user

        return attrs

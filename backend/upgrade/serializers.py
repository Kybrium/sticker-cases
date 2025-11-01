from rest_framework import serializers
from users.models import CustomUser
from packs.models import Pack, Liquidity, UserInventory
from shared.utils import get_upgrade_liquidity


class UpgradeLiquiditySerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()

    user_liq_id = serializers.IntegerField(required=False)
    user_liq_name = serializers.CharField(required=False)
    user_liq_collection = serializers.CharField(required=False)
    user_liq_contributor = serializers.CharField(required=False)
    user_liq_number = serializers.IntegerField(required=False)

    upgrade_liq_id = serializers.IntegerField(required=False)
    liq_upgrade_name = serializers.CharField(required=False)
    liq_upgrade_collection = serializers.CharField(required=False)
    liq_upgrade_contributor = serializers.CharField(required=False)
    liq_upgrade_number = serializers.IntegerField(required=False)

    def validate(self, attrs):
        try:
            user = CustomUser.objects.get(telegram_id=attrs["telegram_id"])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"telegram_id": "Пользователь не найден"})

        user_liq = None
        user_pack = None

        if attrs.get("user_liq_id"):
            try:
                user_liq = Liquidity.objects.get(id=attrs["user_liq_id"])
                user_pack = user_liq.pack
            except Liquidity.DoesNotExist:
                raise serializers.ValidationError({"user_liq_id": "Ликвидность не найдена"})
        else:
            try:
                user_pack = Pack.objects.get(
                    pack_name=attrs.get("user_liq_name"),
                    collection_name=attrs.get("user_liq_collection"),
                    contributor=attrs.get("user_liq_contributor"),
                )
            except Pack.DoesNotExist:
                raise serializers.ValidationError({"user_liq": "Пак не найден"})

            try:
                user_liq = Liquidity.objects.get(
                    pack=user_pack, number=attrs.get("user_liq_number")
                )
            except Liquidity.DoesNotExist:
                raise serializers.ValidationError({"user_liq_number": "Ликвидность не найдена"})

        if not UserInventory.objects.filter(user=user, liquidity=user_liq).exists():
            raise serializers.ValidationError({"user_liq": "Стикер не принадлежит пользователю"})

        upgrade_liq = None
        upgrade_pack = None

        if attrs.get("upgrade_liq_id"):
            try:
                upgrade_liq = Liquidity.objects.get(id=attrs["upgrade_liq_id"])
                upgrade_pack = upgrade_liq.pack
            except Liquidity.DoesNotExist:
                raise serializers.ValidationError({"upgrade_liq_id": "Ликвидность не найдена"})
        else:
            try:
                upgrade_pack = Pack.objects.get(
                    pack_name=attrs.get("liq_upgrade_name"),
                    collection_name=attrs.get("liq_upgrade_collection"),
                    contributor=attrs.get("liq_upgrade_contributor"),
                )
            except Pack.DoesNotExist:
                raise serializers.ValidationError({"upgrade_liq": "Пак не найден"})

            upgrade_liq = Liquidity.objects.filter(
                pack=upgrade_pack, number=attrs.get("liq_upgrade_number")
            ).first()

            if not upgrade_liq:
                raise serializers.ValidationError({"upgrade_liq": "Ликвидность не найдена"})

        upgrade_chance = None
        result = get_upgrade_liquidity(user_liq)
        for liq, chance in result:
            if liq == upgrade_liq:
                upgrade_chance = chance
                break

        if upgrade_chance is None:
            raise serializers.ValidationError({"upgrade_liq": "Нельзя улучшить на эту ликвидность"})

        attrs.update({
            "user": user,
            "user_liq": user_liq,
            "upgrade_liq": upgrade_liq,
            "chance": upgrade_chance,
            "user_pack": user_pack,
            "upgrade_pack": upgrade_pack,
        })
        return attrs

from cases.models import CaseOpen
from packs.models import PackSell
from rest_framework import serializers
from wallet.models import Deposit, Withdrawal
from upgrade.models import Upgrade

from .models import CustomUser


class UserSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()

    def validate_telegram_id(self, value):
        if not CustomUser.objects.filter(telegram_id=value).exists():
            raise serializers.ValidationError("Пользователь с таким telegram_id не найден")
        return value

    def to_representation(self, instance):
        """Преобразование пользователя в JSON при успешной валидации"""
        return {
            "telegram_id": instance.telegram_id,
            "username": instance.username,
            "balance": instance.balance,
            "image_url": instance.image_url,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "language": instance.language,
            "is_bot": instance.is_bot,
        }


class TransactionSerializer(serializers.ModelSerializer):
    def to_representation(self, instance: str) -> dict:  # type: ignore[return]
        if isinstance(instance, PackSell):
            return {
                "type": "Sticker sell",
                "data": {
                    "price": instance.price,
                    "date": instance.date,
                    "sticker_image_url": instance.liquidity.pack.image_url
                },
            }
        elif isinstance(instance, CaseOpen):
            return {
                "type": "Case open",
                "data": {
                    "price": instance.price,
                    "date": instance.date,
                    "drop_image_url": instance.image_url
                },
            }
        elif isinstance(instance, Upgrade):
            return {
                "type": "Upgrade",
                "data": {
                    "success": instance.success,
                    "date": instance.date,
                    "bet_image_url": instance.bet.image_url,
                    "drop_image_url": instance.drop.image_url,
                    "price": instance.price,
                },
            }
        elif isinstance(instance, Deposit):
            return {
                "type": "Deposit",
                "data": {
                    "sum": instance.sum,
                    "date": instance.date,
                },
            }
        elif isinstance(instance, Withdrawal):
            return {
                "type": "Withdrawal",
                "data": {
                    "sum": instance.sum,
                    "date": instance.date,
                    "pack": instance.pack.image_url
                },
            }

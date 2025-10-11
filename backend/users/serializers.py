from cases.models import CaseOpen
from packs.models import PackSell
from rest_framework import serializers
from wallet.models import Deposit, Withdrawal

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["telegram_id", "username", "balance", "image_url", "first_name", "last_name", "language", "is_bot"]


class TransactionSerializer(serializers.ModelSerializer):
    def to_representation(self, instance: str) -> dict:  # type: ignore[return]
        if isinstance(instance, PackSell):
            return {
                "type": "Sticker sell",
                "data": {
                    "price": instance.price,
                    "date": instance.date,
                },
            }
        elif isinstance(instance, CaseOpen):
            return {
                "type": "Case open",
                "data": {
                    "price": instance.price,
                    "date": instance.date,
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
                },
            }

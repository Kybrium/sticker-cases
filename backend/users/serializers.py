from rest_framework import serializers
from .models import CustomUser
from packs.models import PackSell
from cases.models import CaseOpen
from wallet.models import Withdrawal, Deposit


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "telegram_id",
            "username",
            "balance",
            "image_url"
        ]


class TransactionSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        if isinstance(instance, PackSell):
            return {
                "type": "Sticker sell",
                "data": {
                    "price": instance.price,
                    "date": instance.date,
                }
            }
        elif isinstance(instance, CaseOpen):
            return {
                "type": "Case open",
                "data": {
                    "price": instance.price,
                    "date": instance.date,
                }
            }
        elif isinstance(instance, Deposit):
            return {
                "type": "Deposit",
                "data": {
                    "sum": instance.sum,
                    "date": instance.date,
                }
            }
        elif isinstance(instance, Withdrawal):
            return {
                "type": "Withdrawal",
                "data": {
                    "sum": instance.price,
                    "date": instance.date,
                }
            }

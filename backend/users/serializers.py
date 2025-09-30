from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "telegram_id",
            "username",
            "balance",
            "image_url",
            "first_name"
        ]

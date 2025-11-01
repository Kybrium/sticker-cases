from rest_framework import serializers
from .models import Roulette


class RouletteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseItem
        fields = "__all__"


class WinningsSerializer(serializers.Serializer):
    pass

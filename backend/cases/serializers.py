from rest_framework import serializers

from .models import Case, CaseItem


class CaseSerializer(serializers.Serializer):
    name = serializers.CharField()

    def validate_name(self, value):
        try:
            case = Case.objects.get(name=value)
        except Case.DoesNotExist:
            raise serializers.ValidationError("Кейс не найден")
        self.case = case
        return value

    def create(self, validated_data):
        return self.case

    def to_representation(self, instance):
        return {
            "name": instance.name,
            "price": instance.price,
            "image_url": instance.image_url,
            "base_fee": instance.base_fee,
            "status": instance.status,
            "current_fee": instance.current_fee
        }


class CaseItemSerializer(serializers.ModelSerializer):
    pack_name = serializers.CharField(source="pack.pack_name")
    collection_name = serializers.CharField(source="pack.collection_name")
    pack_floor_price = serializers.DecimalField(source="pack.floor_price", max_digits=20, decimal_places=3)
    pack_image = serializers.CharField(source="pack.image_url")
    chance = serializers.FloatField()
    case_name = serializers.CharField(source="case.name")

    class Meta:
        model = CaseItem
        fields = [
            "pack_name",
            "collection_name",
            "pack_image",
            "chance",
            "case_name",
            "pack_floor_price",
        ]

    def __init__(self, *args, **kwargs):
        # Позволяет передавать кастомный список полей при инициализации
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            for field_name in set(self.fields) - allowed:
                self.fields.pop(field_name)

from rest_framework import serializers
from urllib.parse import parse_qs


class SignatureValidationSerializer(serializers.Serializer):
    signature = serializers.CharField(required=True)
    message = serializers.CharField(required=True)
    public = serializers.CharField(required=True)

    def validate_message(self, value):
        parsed = parse_qs(value)

        telegram_id = parsed.get("telegram_id", [None])[0]
        wallet = parsed.get("wallet", [None])[0]
        timestamp = parsed.get("timestamp", [None])[0]
        nonce = parsed.get("nonce", [None])[0]

        if not all([telegram_id, wallet, timestamp, nonce]):
            raise serializers.ValidationError("Message is missing required fields")

        try:
            int(timestamp)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Invalid timestamp")

        self.context["parsed_message"] = {
            "telegram_id": telegram_id,
            "wallet": wallet,
            "timestamp": int(timestamp),
            "nonce": nonce,
        }

        return value
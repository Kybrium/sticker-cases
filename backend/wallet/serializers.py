from urllib.parse import parse_qs

from rest_framework import serializers

from .models import Deposit, Withdrawal


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = "__all__"


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = "__all__"


class WalletSerializer(serializers.Serializer):
    deposits = DepositSerializer(many=True)
    withdrawals = WithdrawalSerializer(many=True)


class SignatureValidationSerializer(serializers.Serializer):
    signature = serializers.CharField(required=True)
    message = serializers.CharField(required=True)
    public = serializers.CharField(required=True)

    def validate_message(self, value: str) -> str:
        parsed: dict[str, list[str]] = parse_qs(value)

        telegram_id: str | None = parsed.get("telegram_id", [None])[0]
        wallet: str | None = parsed.get("wallet", [None])[0]
        timestamp: str | None = parsed.get("timestamp", [None])[0]
        nonce: str | None = parsed.get("nonce", [None])[0]

        if not all([telegram_id, wallet, timestamp, nonce]):
            raise serializers.ValidationError("Message is missing required fields")

        try:
            int(timestamp)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            raise serializers.ValidationError("Invalid timestamp")

        self.context["parsed_message"] = {
            "telegram_id": telegram_id,
            "wallet": wallet,
            "timestamp": int(timestamp),  # type: ignore[arg-type]
            "nonce": nonce,
        }
        return value

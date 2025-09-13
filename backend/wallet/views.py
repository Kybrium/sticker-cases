import secrets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets
from rest_framework import status as drf_status
from rest_framework.decorators import action
from core.celery import celery_app
import base64
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from users.models import CustomUser
from django.shortcuts import get_object_or_404
import datetime
from django.utils import timezone
from shared.cache import CacheService
from .serializers import SignatureValidationSerializer
from rest_framework.serializers import Serializer

class PlugSerializer(Serializer):
    pass

def verify_signature(public_key: str, message: str, signature: str) -> bool:
    try:
        pub_key_bytes = base64.b64decode(public_key)
        sig_bytes = base64.b64decode(signature)
        verify_key = VerifyKey(pub_key_bytes)
        verify_key.verify(message.encode(), sig_bytes)
        return True
    except BadSignatureError:
        return False


class WalletAPIViewSet(viewsets.GenericViewSet):
    serializer_class = PlugSerializer

    def get_serializer_class(self):
        if self.action == "validate_signature":
            return SignatureValidationSerializer
        return super().get_serializer_class()


    @action(methods=["POST"], detail=False, url_path="get-nonce")
    def get_nonce(self, request: Request):
        telegram_id  = request.data.get("telegram_id")
        if not telegram_id:
            return Response({"error": "Telegram id is not provided"}, drf_status.HTTP_400_BAD_REQUEST)
        get_object_or_404(CustomUser, telegram_id=telegram_id)
        cache = CacheService()
        if cache.is_active_key(telegram_id):
            return Response({"error": "Nonce is already created"}, drf_status.HTTP_400_BAD_REQUEST)

        nonce = secrets.token_urlsafe(24)
        cache.add_active_nonce(telegram_id, nonce)
        cache.set(f"nonce:{telegram_id}:{nonce}", {"used": False}, 300)
        return Response({"nonce": nonce}, drf_status.HTTP_200_OK)


    @action(methods=["POST"], detail=False, url_path="connect-wallet")
    def validate_signature(self, request: Request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        signature = serializer.validated_data["signature"]
        message = serializer.validated_data["message"]
        public_key = serializer.validated_data["public"]

        parsed_message = serializer.context["parsed_message"]
        telegram_id = parsed_message["telegram_id"]
        wallet = parsed_message["wallet"]
        timestamp = parsed_message["timestamp"]
        nonce = parsed_message["nonce"]

        cache = CacheService()
        key = f"nonce:{telegram_id}:{nonce}"

        cached_nonce = cache.get(key)
        if not cached_nonce:
            return Response({"error": "Wrong telegram id or nonce is used"}, drf_status.HTTP_400_BAD_REQUEST)

        if not cached_nonce.get("used"):
            user = get_object_or_404(CustomUser, telegram_id=telegram_id)
            is_valid = verify_signature(public_key, message, signature)
            if not is_valid:
                return Response({"error": "Signature is not valid"}, drf_status.HTTP_400_BAD_REQUEST)

            ts = int(timestamp)
            naive_dt = datetime.datetime.fromtimestamp(ts)
            aware_dt = timezone.make_aware(naive_dt)

            user.wallet_connection_date = aware_dt
            user.wallet = wallet
            user.save()

            cache.set(key, {"used": True}, 86400)
            return Response({"message": "Wallet connected successfully"}, drf_status.HTTP_200_OK)
        else:
            return Response({"error": "Signature is already used"}, drf_status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=False, url_path="deposit")
    def deposit(self, request: Request):
        invoice_status = request.data.get("status")
        if invoice_status == "pending":
            telegram_id = request.data.get("telegram_id")
            invoice_id = request.data.get("invoice_id")
            invoice_data_expire = request.data.get("invoice_data_expire")

        elif invoice_status == "cancelled" or "expired":
            pass
        elif invoice_status == "paid":
            pass




        





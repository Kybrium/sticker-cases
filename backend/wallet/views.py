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
from enum import StrEnum
from .models import Deposit
from django.db.models import F
import requests
from tonsdk.utils import Address
import time
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt

AUTHORIZATION_TOKEN = "TC-INVOICE_a93fb0f16272e1a51f50c154489810927cdfbe20d03ffa9a825c48df53758fbe91"
MAX_MESSAGE_AGE = 300


class InvoiceStatus(StrEnum):
    PENDING = "pending"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAID = "paid"


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
        telegram_id = request.data.get("telegram_id")
        if not telegram_id:
            return Response({"error": "Telegram id is not provided"}, drf_status.HTTP_400_BAD_REQUEST)
        get_object_or_404(CustomUser, telegram_id=telegram_id)
        cache = CacheService()

        is_active = cache.get("active_nonces:{telegram_id}")
        if is_active:
            return Response({"error": "Nonce is already created"}, drf_status.HTTP_400_BAD_REQUEST)

        nonce = secrets.token_urlsafe(24)
        cache.set(f"active_nonces:{telegram_id}", {"nonce": nonce}, 300)
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

        if cached_nonce.get("used"):
            return Response({"error": "Signature has already been used"}, drf_status.HTTP_400_BAD_REQUEST)

        try:
            ts = int(timestamp)
        except (ValueError, TypeError):
            return Response({"error": "Invalid timestamp format"}, drf_status.HTTP_400_BAD_REQUEST)

        current_ts = int(time.time())
        if abs(current_ts - ts) > MAX_MESSAGE_AGE:
            return Response({"error": "Message timestamp is expired"}, drf_status.HTTP_400_BAD_REQUEST)

        is_valid = verify_signature(public_key, message, signature)
        if not is_valid:
            return Response({"error": "Signature is not valid"}, drf_status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, telegram_id=telegram_id)
        naive_dt = datetime.datetime.fromtimestamp(ts)
        aware_dt = timezone.make_aware(naive_dt)

        user.wallet_connection_date = aware_dt
        user.wallet = wallet
        user.save()

        cache.set(key, {"used": True}, 86400)
        return Response({"message": "Wallet connected successfully"}, drf_status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="create-invoice")
    def create_invoice(self, request: Request):
        telegram_id = request.data.get("telegram_id")
        get_object_or_404(CustomUser, telegram_id=telegram_id)

        cache = CacheService()
        active_invoice = cache.get(f"active_invoices:{telegram_id}")

        if active_invoice:
            invoice_key = active_invoice["key"]
            invoice_data = cache.get(invoice_key)
            return Response(
                {
                    "message": "Invoice already exists",
                    "address_to_pay": invoice_data.get("address"),
                    "invoice_id": invoice_data.get("invoice_id"),
                    "status": invoice_data.get("status"),
                },
                drf_status.HTTP_400_BAD_REQUEST
            )
        payload = {
            "amount": "100000000",
            "life_time": 86400,
            "description": str(telegram_id),
            "currency": "TON"
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {AUTHORIZATION_TOKEN}"}

        response = requests.post(
            "https://tonconsole.com/api/v1/services/invoices/invoice",
            json=payload,
            headers=headers
        )

        if response.status_code != 201:
            return Response(
                {"error": "Something went wrong with ton console API", "detail": response.text},
                drf_status.HTTP_400_BAD_REQUEST
            )

        data = response.json()

        address_obj = Address(data["pay_to_address"])
        address = address_obj.to_string(is_user_friendly=True, is_bounceable=True, is_url_safe=True)

        invoice_id = data["id"]
        invoice_data_expire = data["date_expire"]

        key = f"invoice:{telegram_id}:{invoice_id}"

        now_ts = int(time.time())
        ttl = invoice_data_expire - now_ts
        if ttl < 0:
            ttl = 0

        cache.set(f"active_invoices:{telegram_id}", {"key": key}, 86400)
        cache.set(key, {"status": InvoiceStatus.PENDING, "invoice_id": invoice_id, "address": address}, ttl)

        return Response(
            {"message": "Invoice created", "address_to_pay": address, "invoice_id": invoice_id},
            drf_status.HTTP_200_OK
        )

    @action(detail=False, methods=["POST"], url_path="check-deposit")
    def check_deposit(self, request: Request):
        telegram_id = str(request.data.get("telegram_id"))
        cache = CacheService()
        active_invoice_key = f"active_invoices:{str(telegram_id)}"
        key = cache.get(active_invoice_key)["key"]
        user_invoice = cache.get(key)
        if not user_invoice:
            return Response({"error": "Invoice is expired"}, drf_status.HTTP_400_BAD_REQUEST)

        invoice_id = user_invoice["invoice_id"]
        invoice_status = user_invoice["status"]

        if invoice_status == InvoiceStatus.PENDING:
            return Response({"message": "Invoice is pending", "status": InvoiceStatus.PENDING,
                             "invoice_id": invoice_id}, drf_status.HTTP_400_BAD_REQUEST)

        elif invoice_status == InvoiceStatus.CANCELLED:
            cache.delete(key)
            cache.delete(active_invoice_key)
            return Response({"error": "Invoice is cancelled", "status": InvoiceStatus.CANCELLED},
                            drf_status.HTTP_400_BAD_REQUEST)

        elif invoice_status == InvoiceStatus.PAID:
            user = get_object_or_404(CustomUser, telegram_id=telegram_id)
            balance = user.balance
            cache.delete(key)
            cache.delete(active_invoice_key)
            return Response({"message": "Invoice is paid", "status": InvoiceStatus.PAID, "new_balance": balance},
                            drf_status.HTTP_200_OK)

        return Response({"error": "Unknown invoice status", "status": invoice_status, "invoice_id": invoice_id},
                        drf_status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def tonconsole_webhook(request: Request):
    if request.method != "POST":
        return Response({"error": "Only POST allowed"}, status=405)
    if request.content_type == "application/json":
        data = json.loads(request.body)
    else:
        data = request.POST.dict()

    invoice_status = data.get("status")
    telegram_id = str(data.get("description"))
    invoice_id = data.get("id")
    cache = CacheService()
    key = f"invoice:{str(telegram_id)}:{invoice_id}"

    if invoice_status == InvoiceStatus.CANCELLED:
        ttl = cache.get_ttl(key)
        if not ttl:
            return Response({"error": "Invoice is not exist", "invoice_id": invoice_id},
                            status=drf_status.HTTP_400_BAD_REQUEST)
        cache.set(key, {"status": InvoiceStatus.CANCELLED, "invoice_id": invoice_id}, ttl)
        return Response({"message": "Invoice is cancelled"}, status=drf_status.HTTP_200_OK)

    elif invoice_status == InvoiceStatus.EXPIRED:
        cache.delete(key)
        return Response({"message": "Invoice is expired"}, status=drf_status.HTTP_200_OK)

    elif invoice_status == InvoiceStatus.PAID:
        try:
            amount = Decimal(str(data.get("amount", "0")))
            overpayment = Decimal(str(data.get("overpayment", "0")))
            deposit_sum = amount + overpayment
            wallet = data.get("paid_by_address")
        except (ValueError, TypeError) as e:
            return Response({"error": "Error while extracting values", "detail": e},
                            status=drf_status.HTTP_400_BAD_REQUEST)

        is_active = cache.get(key)
        if not is_active:
            return Response({"error": "Invoice is not exist"}, status=drf_status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, telegram_id=int(telegram_id))
        user.balance = F("balance") + deposit_sum
        user.save(update_fields=["balance"])
        user.refresh_from_db()

        Deposit.objects.create(
            user=user,
            sum=deposit_sum,
            date=timezone.now(),
            wallet=wallet
        )
        ttl = cache.get_ttl(key)
        if not ttl:
            return Response({"error": "Invoice is not exist", "invoice_id": invoice_id},
                            status=drf_status.HTTP_400_BAD_REQUEST)
        cache.set(key, {"status": InvoiceStatus.PAID, "invoice_id": invoice_id}, ttl)
        return Response({"message": "Invoice successfully paid"}, status=drf_status.HTTP_200_OK)

    return Response({"error": "Wrong invoice status provided"}, status=drf_status.HTTP_400_BAD_REQUEST)

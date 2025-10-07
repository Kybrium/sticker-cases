import asyncio
import base64
import datetime
import json
import os
import secrets
import time
from decimal import Decimal
from enum import StrEnum
from typing import Any

import aiohttp
import requests
from asgiref.sync import async_to_sync
from django.db import transaction
from django.db.models import F
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from packs.models import Liquidity, Pack
from rest_framework import status as drf_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from shared.cache import CacheService
from tonsdk.utils import Address  # type: ignore
from tonutils.client import TonapiClient
from tonutils.wallet import WalletV5R1
from tonutils.wallet.messages import TransferNFTMessage
from users.models import CustomUser, UserInventory

from .models import Deposit, Withdrawal
from .serializers import SignatureValidationSerializer, WalletSerializer

PLUG = "plug"
MAX_MESSAGE_AGE = 300
IS_TESTNET: Any | None = os.getenv("IS_TESNET", PLUG)
INVOICE_AUTHORIZATION_TOKEN: str | None = os.getenv("INVOICE_AUTHORIZATION_TOKEN", PLUG)
MNEMONIC: str | None = os.getenv(
    "MNEMONIC", PLUG
)
TONAPI_KEY: str | None = os.getenv("TONAPI_KEY", PLUG)

if TONAPI_KEY is None:
    raise ValueError("TONAPI_KEY переменная окружения обязательна")
if MNEMONIC is None:
    raise ValueError("MNEMONIC переменная окружения обязательна")
if INVOICE_AUTHORIZATION_TOKEN is None:
    raise ValueError("INVOICE_AUTHORIZATION_TOKEN переменная окружения обязательна")

client = TonapiClient(api_key=TONAPI_KEY, is_testnet=IS_TESTNET, rps=1)  # type: ignore[arg-type]
wallet, public_key, private_key, mnemonic = WalletV5R1.from_mnemonic(client, MNEMONIC)


class InvoiceStatus(StrEnum):
    PENDING = "pending"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAID = "paid"


def verify_signature(public_key: str, message: str, signature: str) -> bool:
    try:
        pub_key_bytes = base64.b64decode(public_key)
        sig_bytes = base64.b64decode(signature)
        verify_key = VerifyKey(pub_key_bytes)
        verify_key.verify(message.encode(), sig_bytes)
        return True
    except BadSignatureError:
        return False


async def transfer_nft(
        nft_address: str | None, new_owner_address: str | None
) -> tuple[bool, str] | tuple[bool, Exception] | tuple[bool, None]:
    # TODO: сделать проверку существует ли аддресс нфт
    if not nft_address:
        return False, "Переменная nft_address пуста"
    if not new_owner_address:
        return False, "Переменная new_owner_address пуста"

    try:
        sender_address = wallet.address.to_str(is_user_friendly=False)
        tx_hash = await wallet.transfer_message(
            message=TransferNFTMessage(destination=new_owner_address, nft_address=nft_address, amount=0.005),
        )
        async with aiohttp.ClientSession() as session:
            while True:
                response = await session.get(f"https://tonapi.io/v2/blockchain/transactions/{tx_hash}")
                tx = await response.json()

                try:
                    if tx["error"]:
                        await asyncio.sleep(5)
                        continue
                    break
                except KeyError:
                    break

            success = (
                    tx["success"] and not tx["aborted"] and tx["compute_phase"]["success"] and tx["action_phase"][
                "success"]
            )

            if not success:
                return False, "Транзакция отменена или не прошла"

            out_msgs = tx.get("out_msgs", [])
            nft_received = False
            for msg in out_msgs:
                if msg.get("decoded_op_name") == "nft_transfer":
                    new_owner = msg["decoded_body"]["new_owner"]
                    if new_owner == new_owner_address:
                        nft_received = True
                        break

            if not nft_received:
                return False, "NFT не дошла до адреса получателя"

            response = await session.get(f"https://tonapi.io/v2/nfts/{nft_address}")
            data = await response.json()

            owner_address = data["owner"]["address"]
            if owner_address == sender_address:
                return False, "NFT не было отправлено"

            return True, None

    except Exception as e:
        return False, e


class WalletAPIViewSet(viewsets.GenericViewSet):
    serializer_class = WalletSerializer

    def get_serializer_class(self) -> type[BaseSerializer[Any]]:
        if self.action == "validate_signature":
            return SignatureValidationSerializer
        return super().get_serializer_class()

    @action(methods=["POST"], detail=False, url_path="get-nonce")
    def get_nonce(self, request: Request) -> Response:
        telegram_id = request.data.get("telegram_id")
        if not telegram_id:
            return Response(
                {"status": "error", "message": "Telegram id is not provided"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        try:
            CustomUser.objects.get(telegram_id=telegram_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"status": "error", "message": "Пользователь не найден"},
                status=drf_status.HTTP_404_NOT_FOUND,
            )
        cache = CacheService()

        if cache.get(f"active_nonces:{telegram_id}"):
            return Response(
                {"status": "error", "message": "Nonce is already created"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        nonce = secrets.token_urlsafe(24)
        cache.set(f"active_nonces:{telegram_id}", {"nonce": nonce}, 300)
        cache.set(f"nonce:{telegram_id}:{nonce}", {"used": False}, 300)
        return Response({"status": "success", "nonce": nonce}, status=drf_status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="connect-wallet")
    def validate_signature(self, request: Request) -> Response:
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
            return Response(
                {"status": "error", "message": "Неверный Telegram ID или nonce"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        if cached_nonce.get("used"):
            return Response(
                {"status": "error", "message": "Эта подпись уже использована"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        try:
            ts = int(timestamp)
        except (ValueError, TypeError):
            return Response(
                {"status": "error", "message": "Неверный формат timestamp"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        current_ts = int(time.time())
        if abs(current_ts - ts) > MAX_MESSAGE_AGE:
            return Response(
                {"status": "error", "message": "Timestamp в сообщении истек"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        if not verify_signature(public_key, message, signature):
            return Response(
                {"status": "error", "message": "Подпись недействительна"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"status": "error", "message": "Пользователь не найден"},
                status=drf_status.HTTP_404_NOT_FOUND,
            )
        naive_dt = datetime.datetime.fromtimestamp(ts)
        aware_dt = timezone.make_aware(naive_dt)

        user.wallet_connection_date = aware_dt
        user.wallet = wallet
        user.save()

        cache.set(key, {"used": True}, 86400)
        return Response(
            {"status": "success", "message": "Кошелек успешно подключен"},
            status=drf_status.HTTP_200_OK,
        )

    @action(methods=["POST"], detail=False, url_path="create-invoice")
    def create_invoice(self, request: Request) -> Response:
        telegram_id = request.data.get("telegram_id")
        if not telegram_id:
            return Response(
                {"status": "error", "message": "Telegram ID не предоставлен"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        try:
            CustomUser.objects.get(telegram_id=telegram_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"status": "error", "message": "Пользователь не найден"},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        cache = CacheService()
        active_invoice = cache.get(f"active_invoices:{telegram_id}")

        if active_invoice:
            invoice_key = active_invoice["key"]
            invoice_data = cache.get(invoice_key)
            return Response(
                {
                    "status": "success",
                    "message": "Инвойс уже существует",
                    "address_to_pay": invoice_data.get("address"),
                    "invoice_id": invoice_data.get("invoice_id"),
                    "status_invoice": invoice_data.get("status"),
                },
                status=drf_status.HTTP_200_OK,
            )
        payload = {
            "amount": "100000000",
            "life_time": 86400,
            "description": str(telegram_id),
            "currency": "TON",
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {INVOICE_AUTHORIZATION_TOKEN}",
        }

        response = requests.post(
            "https://tonconsole.com/api/v1/services/invoices/invoice",
            json=payload,
            headers=headers,
        )

        if response.status_code != 201:
            return Response(
                {
                    "status": "error",
                    "message": "Ошибка при создании инвойса через Tonconsole API",
                    "detail": response.text,
                },
                status=drf_status.HTTP_400_BAD_REQUEST,
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
        cache.set(
            key,
            {
                "status": InvoiceStatus.PENDING,
                "invoice_id": invoice_id,
                "address": address,
            },
            ttl,
        )

        return Response(
            {
                "status": "success",
                "message": "Инвойс создан",
                "address_to_pay": address,
                "invoice_id": invoice_id,
            },
            status=drf_status.HTTP_200_OK,
        )

    @action(detail=False, methods=["POST"], url_path="check-deposit")
    def check_deposit(self, request: Request) -> Response:
        telegram_id = str(request.data.get("telegram_id"))
        if not telegram_id:
            return Response(
                {"status": "error", "message": "Telegram ID не предоставлен"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        cache = CacheService()
        active_invoice_key = f"active_invoices:{str(telegram_id)}"
        try:
            key = cache.get(active_invoice_key)["key"]
        except TypeError:
            return Response(
                {"status": "error", "message": "Инвойс не существует"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        user_invoice = cache.get(key)
        if not user_invoice:
            return Response(
                {"status": "error", "message": "Инвойс истёк"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        invoice_id = user_invoice["invoice_id"]
        invoice_status = user_invoice["status"]

        if invoice_status == InvoiceStatus.PENDING:
            return Response(
                {
                    "status": "success",
                    "message": "Инвойс ожидает оплаты",
                    "invoice_status": InvoiceStatus.PENDING,
                    "invoice_id": invoice_id,
                },
                status=drf_status.HTTP_200_OK,
            )

        elif invoice_status == InvoiceStatus.CANCELLED:
            cache.delete(key)
            cache.delete(active_invoice_key)
            return Response(
                {
                    "status": "error",
                    "message": "Инвойс отменён",
                    "invoice_status": InvoiceStatus.CANCELLED,
                },
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        elif invoice_status == InvoiceStatus.PAID:
            try:
                user = CustomUser.objects.get(telegram_id=telegram_id)
            except CustomUser.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Пользователь не найден"},
                    status=drf_status.HTTP_404_NOT_FOUND,
                )
            cache.delete(key)
            cache.delete(active_invoice_key)
            return Response(
                {
                    "status": "success",
                    "message": "Инвойс оплачен",
                    "invoice_status": InvoiceStatus.PAID,
                    "new_balance": user.balance,
                },
                status=drf_status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "error",
                "message": "Неизвестный статус инвойса",
                "invoice_status": invoice_status,
                "invoice_id": invoice_id,
            },
            status=drf_status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["POST"], url_path="withdrawal")
    def withdrawal_nft(self, request: Request) -> Response:  # noqa: C901
        required_fields = [
            "telegram_id",
            "pack_name",
            "collection_name",
            "contributor",
            "number",
        ]
        for field in required_fields:
            if not request.data.get(field):
                return Response(
                    {"status": "error", "message": f"Поле '{field}' обязательно"},
                    status=drf_status.HTTP_400_BAD_REQUEST,
                )
        telegram_id = request.data.get("telegram_id")
        pack_name = request.data.get("pack_name")
        collection_name = request.data.get("collection_name")
        contributor = request.data.get("contributor")
        number: Any = request.data.get("number")

        try:
            pack = Pack.objects.get(
                pack_name=pack_name,
                collection_name=collection_name,
                contributor=contributor,
            )
        except Pack.DoesNotExist:
            return Response(
                {"status": "error", "message": "Пак не найден"},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        try:
            liquidity = Liquidity.objects.get(pack=pack, number=number)
        except Liquidity.DoesNotExist:
            return Response(
                {"status": "error", "message": "Ликвидность не найдена"},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"status": "error", "message": "Пользователь не найден"},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        if not UserInventory.objects.filter(user=user, liquidity=liquidity).exists():
            return Response(
                {"status": "error", "message": "Стикер не принадлежит пользователю"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        transfered, e = async_to_sync(transfer_nft)(liquidity.nft_address, user.wallet)
        if not transfered:
            return Response(
                {"status": "error", "message": f"Не удалось вывести NFT: {e}"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            try:
                Withdrawal.objects.create(user=user, pack=pack, date=timezone.now(), sum=pack.floor_price)
                liquidity.delete()
            except Exception as e:
                return Response(
                    {"status": "error", "message": f"Ошибка при выводе: {e}"},
                    status=drf_status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"status": "success", "message": "NFT выведено успешно"},
            status=drf_status.HTTP_200_OK,
        )


@csrf_exempt
def tonconsole_webhook(request: HttpRequest) -> JsonResponse:  # noqa: C901
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Разрешён только POST"}, status=405)
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
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Инвойс не существует",
                    "invoice_id": invoice_id,
                },
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        cache.set(key, {"status": InvoiceStatus.CANCELLED, "invoice_id": invoice_id}, ttl)
        return JsonResponse({"status": "success", "message": "Инвойс отменён"}, status=200)

    elif invoice_status == InvoiceStatus.EXPIRED:
        cache.delete(key)
        return JsonResponse({"status": "success", "message": "Инвойс истёк"}, status=200)

    elif invoice_status == InvoiceStatus.PAID:
        try:
            amount = Decimal(str(data.get("amount", "0")))
            overpayment = Decimal(str(data.get("overpayment", "0")))
            deposit_sum = amount + overpayment
        except (ValueError, TypeError) as e:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Ошибка при обработке депозита",
                    "detail": str(e),
                },
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        if not cache.get(key):
            return JsonResponse(
                {"status": "error", "message": "Инвойс не существует"},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
        except CustomUser.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Пользователь не найден"},
                status=drf_status.HTTP_404_NOT_FOUND,
            )
        user.balance = F("balance") + deposit_sum
        user.save(update_fields=["balance"])
        user.refresh_from_db()

        Deposit.objects.create(user=user, sum=deposit_sum, date=timezone.now())

        ttl = cache.get_ttl(key)
        if not ttl:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Инвойс не существует",
                    "invoice_id": invoice_id,
                },
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        cache.set(key, {"status": InvoiceStatus.PAID, "invoice_id": invoice_id}, ttl)
        return JsonResponse({"status": "success", "message": "Инвойс успешно оплачен"}, status=200)

    return JsonResponse(
        {"status": "error", "message": "Неверный статус инвойса"},
        status=drf_status.HTTP_400_BAD_REQUEST,
    )

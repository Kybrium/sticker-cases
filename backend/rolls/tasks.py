from .models import Round, RoundResult, TonBet, NFTBet, Roulette

import hashlib
from decimal import Decimal, getcontext
from typing import Dict, Tuple
from core import settings
import os
from django.db.utils import timezone
import asyncio
from consumers import WSConsumer
from users.models import CustomUser
from .models import RoundResult, TonBet, NFTBet
import aiohttp
from packs.models import Pack, Liquidity

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

getcontext().prec = 50

fernet = Fernet(settings.SECRET_ENCRYPTION_KEY)


def get_round_secret(round: Round) -> str:
    """Расшифровывает secret из модели."""
    encrypted_secret = round.secret.encode()
    return fernet.decrypt(encrypted_secret).decode()


def seed_from(round: Round, block_hash: str) -> str:
    secret = get_round_secret(round)
    inp = f"{secret}{round.id}{block_hash}".encode()
    return hashlib.sha256(inp).hexdigest()


def deterministic_random_fraction(seed_hex: str) -> Decimal:
    H = int(seed_hex, 16)
    denom = Decimal(2) ** Decimal(256)
    return Decimal(H) / denom


def weighted_winner(storage: Dict[int, Decimal], seed_hex: str) -> int:
    if not storage:
        raise ValueError("No bets")

    total = sum(storage.values())
    if total <= 0:
        raise ValueError("Total must be > 0")

    u = deterministic_random_fraction(seed_hex)
    r = u * total  # r - точка на диапазоне ставок которая определит победителя

    cumulative = Decimal(0)
    for user_id, weight in storage.items():
        cumulative += Decimal(weight)
        if r < cumulative:
            return user_id

    return list(storage.keys())[-1]


def create_round(roulette: Roulette):
    secret_plain = os.urandom(32).hex()  # рандом число

    # шифруем его
    encrypted_secret = fernet.encrypt(secret_plain.encode()).decode()

    # создаём хэш для публичности
    secret_hash = hashlib.sha256(secret_plain.encode()).hexdigest()

    return Round.objects.create(
        roulette=roulette,
        secret_hash=secret_hash,
        secret=encrypted_secret,  # хранится зашифрованным
        is_active=True
    )


async def finish_round_task(round: Round):
    time_to_bet = round.roulette.time_to_bet
    seconds_last = time_to_bet

    for sec in time_to_bet:
        WSConsumer.send_json({"time_to_bet": seconds_last})
        if seconds_last == 0:
            break
        await asyncio.sleep(sec)
        seconds_last -= sec

    bets = list(NFTBet.objects.filter(round=round)) + list(TonBet.objects.filter(round=round))
    storage = {}

    for bet in bets:
        user_id = bet.user.telegram_id
        value = bet.amount if isinstance(bet, TonBet) else bet.liquidity.pack.floor_price
        storage[user_id] = storage.get(user_id, 0) + value

    block_hash = somefunc()

    seed_hex = seed_from(round, block_hash)
    winner_id = weighted_winner(storage, seed_hex)

    round.is_active = False
    round.executed_at = timezone.now()

    win_payload = {"ton": TonBet.objects.filter(round=round).aggregate(total=Sum("amount"))["total"] or 0,
                   "nfts": NFTBet.objects.filter(round=round).values_list("liquidity_id", flat=True),
                   "winner_id": winner_id, "winner_username": user.username if not None else "Anonymous"}

    async with aiohttp.ClientSession() as session:
        response = await session.post(f"{BASE_URL}/api/rolls/{winner_id}/winnings/")

    ws_pack_winning = []
    for nft_id in win_payload.get("nft") or []:
        liquidity = Liquidity.objects.get(id=nft_id)
        pack_name, image_url, pack_collection, number, price = (liquidity.pack.pack_name, liquidity.pack.image_url,
                                                                liquidity.pack.collection_name, liquidity.number,
                                                                liquidity.pack.floor_price)
        ws_pack_winning.append({"pack_name": pack_name, "pack_image_url": image_url, "pack_collection": pack_collection,
                                "number": number, "price": price})

    round_meta_data = win_payload["nfts"] = ws_pack_winning

    # TODO: создать запись RoundResult

    await create_round(round.roulette)

    user = CustomUser.objects.get(telegram_id=winner_id)

    ws_payload = {"winner": user.username if not None else "Anonymous"}

    WSConsumer.send_json({"time_to_bet": seconds_last})

    # TODO: вернуть по вебсокету че он там выйграл

from packs.models import Liquidity
import hashlib
import hmac
import urllib.parse
import json
import time
import os

BOT_API_TOKEN = os.getenv("BOT_API_TOKEN", "plug")


def get_upgrade_liquidity(liquidity: Liquidity, fee: float = 0.2, min_multiplier: float = 1.5, x: float = 1.186,
                          limit: int = 30):
    liqs = Liquidity.objects.filter(free=True).order_by("pack__price")
    """
    ---- Конфигурация апгрейда через параметры ----
    fee = 0.20  # на сколько процентов уменьшить шанс
    min_multiplier = 1.5  # будет выбрана ликвидность с иксом не меньше min_multiplier
    x = 1.186  # во сколько минимум раз будет дороже следующий стикер. Последний из 30 дает 100 иксов
    limit = 30  # сколько максимум стикеров вывести
    """

    result = []
    base_price = float(liquidity.pack.price)
    current_price = base_price * min_multiplier

    for liq in liqs:
        if liq.pack.price >= current_price:
            chance = (base_price / float(liq.pack.price)) * (1 - fee)
            chance = min(chance, 1.0)

            result.append((liq, chance))
            current_price *= x
        if len(result) >= limit:
            break

    return result


def verify_telegram_init_data(init_data: str):
    if not init_data:
        return None

    try:
        parsed = urllib.parse.parse_qs(init_data, strict_parsing=True)
        params = {k: v[0] for k, v in parsed.items()}
    except Exception:
        return None

    given_hash = params.pop("hash", None)
    if not given_hash:
        return None

    auth_date = int(params.get("auth_date", 0))
    if time.time() - auth_date > 86400:
        return None

    data_check = "\n".join(f"{k}={params[k]}" for k in sorted(params.keys()))
    secret_key = hashlib.sha256(BOT_API_TOKEN.encode()).digest()
    calc_hash = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()

    if calc_hash != given_hash:
        return None

    try:
        return json.loads(params["user"])
    except Exception:
        return None

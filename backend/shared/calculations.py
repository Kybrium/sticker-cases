from packs.models import Liquidity


def get_upgrade_liquidity(liquidity: Liquidity, fee: float = 0.2, min_multiplier: float = 1.5, x: float = 1.186,
                          limit: int = 30):
    liqs = Liquidity.objects.filter(free=True).order_by("pack__floor_price")
    """
    ---- Конфигурация апгрейда через параметры ----
    fee = 0.20  # на сколько процентов уменьшить шанс
    min_multiplier = 1.5  # будет выбрана ликвидность с иксом не меньше min_multiplier
    x = 1.186  # во сколько минимум раз будет дороже следующий стикер. Последний из 30 дает 100 иксов
    limit = 30  # сколько максимум стикеров вывести
    """

    result = []
    base_price = float(liquidity.pack.floor_price)
    current_price = base_price * min_multiplier

    for liq in liqs:
        if liq.pack.floor_price >= current_price:
            chance = (base_price / float(liq.pack.floor_price)) * (1 - fee)
            chance = min(chance, 1.0)

            result.append((liq, chance))
            current_price *= x
        if len(result) >= limit:
            break

    return result

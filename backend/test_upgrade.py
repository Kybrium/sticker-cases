import random


def upgrade(item_price: float, target_price: float, fee: float) -> bool:
    """
    Апгрейд предмета с учетом комиссии (фи).

    :param item_price: цена текущего предмета
    :param target_price: цена желаемого предмета
    :param fee: комиссия (0.05 = 5%)
    """
    if target_price <= item_price:
        return True  # если цель дешевле или равна — успех гарантирован

    # базовый честный шанс
    chance = item_price / target_price

    # уменьшение шанса из-за комиссии
    chance *= (1 - fee)

    roll = random.random()
    return roll <= chance


# пример
item = 10
target = 50
fee = 0.2  # 10% комиссия

if upgrade(item, target, fee):
    print("✅ Апгрейд успешен!")
else:
    print("❌ Неудача, предмет сгорел.")

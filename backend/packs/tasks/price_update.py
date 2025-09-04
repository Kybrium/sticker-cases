import asyncio
import aiohttp
from core.celery import celery_app
from urllib.parse import quote

# логика обновления цен на стикеры, изменение их шансов в кейсах, изменение фи кейса и цены кейса
# лишний раз сюда не лезть

@celery_app.task(name="packs.tasks.update_packs_prices_sticker_bot_task")
def update_packs_prices_sticker_bot_task():
    asyncio.run(update_packs_prices_sticker_bot())

async def update_packs_prices_sticker_bot():
    """
    Обновляет цены на стикеры из коллекций выпущенных @sticker_bot
    :return:
    """
    async with aiohttp.ClientSession() as client:
        response = await client.get("https://stickers.tools/api/stats-new")
        data = await response.json()
        collections = data.get("collections")
        response = await client.get("http://localhost:8000/api/packs/contributor/Sticker Pack/")
        packs = await response.json()
        pack_names = [p["pack_name"] for p in packs]

        for col_data in collections.values():
            for pack_data in col_data["stickers"].values():
                pack_name = pack_data["name"]
                # TODO: собрать все в один запрос и отправить
                if pack_name in pack_names:
                    await client.patch(f"http://localhost:8000/api/packs/{pack_name}/update-floor-price/",
                                                 json={"floor_price": pack_data["current"]["price"]["floor"]["ton"]})

        await calculate_cases_price()

async def adjust_case_price(items_dict, base_fee, percent=5):
    EV = sum(v["price"] * v["chance"] for v in items_dict.values())
    min_fee = base_fee - base_fee * percent / 100
    max_fee = base_fee + base_fee * percent / 100

    case_price_min = EV / (1 - max_fee / 100)
    case_price_max = EV / (1 - min_fee / 100)

    case_price_new = (case_price_min + case_price_max) / 2
    case_price_new = round(case_price_new * 2) / 2  # округление до 0.5

    new_fee = (case_price_new - EV) / case_price_new * 100

    # TODO: сделать в будущем чтобы администратор получал понятные логи на изменение цены кейса в админке вручную
    return case_price_new, new_fee


"""
Формула фи:
Для айтема:
Цена айтема * шанс / 100к
Фи кейса:
Цена кейса - Сума айтемов/ цена кейса
"""

def _rebalance_probs_greedy(prices, probs, target_ev, min_p, max_p, eps=1e-9):
    """
    Greedy redistribution: переносим вероятность между парой (дорогой <-> дешёвый),
    чтобы EV приблизить к target_ev. Возвращает (new_probs, new_ev).
    """
    n = len(prices)
    p = probs[:]  # копия
    ev = sum(prices[i] * p[i] for i in range(n))
    if abs(ev - target_ev) <= eps:
        return p, ev

    # индексы: дешёвые -> дорогие
    asc = sorted(range(n), key=lambda i: prices[i])
    desc = asc[::-1]

    if ev > target_ev:
        # EV слишком большой -> перекладываем массу с дорогих на дешёвые
        i_ptr, j_ptr = 0, 0
        while ev - target_ev > eps and i_ptr < n and j_ptr < n:
            i = asc[i_ptr]   # дешёвый (получатель)
            j = desc[j_ptr]  # дорогой (донор)
            if prices[j] <= prices[i]:
                break

            room_i = max_p - p[i]         # сколько можно добавить дешёвому
            avail_j = p[j] - min_p        # сколько можно взять у дорогого
            if room_i <= eps:
                i_ptr += 1
                continue
            if avail_j <= eps:
                j_ptr += 1
                continue

            need = (ev - target_ev) / (prices[j] - prices[i])
            delta = min(room_i, avail_j, need)
            if delta <= eps:
                break

            p[i] += delta
            p[j] -= delta
            ev -= delta * (prices[j] - prices[i])
    else:
        # EV слишком мал -> перекладываем массу с дешёвых на дорогие
        i_ptr, j_ptr = 0, 0
        while target_ev - ev > eps and i_ptr < n and j_ptr < n:
            i = asc[i_ptr]   # дешёвый (донор)
            j = desc[j_ptr]  # дорогой (получатель)
            if prices[j] <= prices[i]:
                break

            avail_i = p[i] - min_p
            room_j  = max_p - p[j]
            if avail_i <= eps:
                i_ptr += 1
                continue
            if room_j <= eps:
                j_ptr += 1
                continue

            need = (target_ev - ev) / (prices[j] - prices[i])
            delta = min(avail_i, room_j, need)
            if delta <= eps:
                break

            p[i] -= delta
            p[j] += delta
            ev += delta * (prices[j] - prices[i])

    return p, ev


async def rebalance_chances(items, case_price, base_fee, case_name, client_session, percent=5, max_iter=100):
    names = list(items.keys())
    prices = [items[n]["price"] for n in names]
    chances = [items[n]["chance"] for n in names]
    print(f"Старые шансы {chances}")

    def fee_from_ev(ev, price):
        return (price - ev) / price * 100

    MIN_CHANCE = 0.01
    MAX_CHANCE = 0.5
    tol = base_fee * percent / 100
    target_ev = case_price * (1 - base_fee / 100)

    # Текущее EV и fee
    EV0 = sum(p * c for p, c in zip(prices, chances))
    fee0 = fee_from_ev(EV0, case_price)

    # Если уже в пределах — обновить current fee и выйти
    if abs(fee0 - base_fee) <= tol:
        await client_session.patch(
            f"http://localhost:8000/api/cases/{quote(case_name)}/update-current-fee/",
            json={"fee": fee0}
        )
        print(f"[rebalance] case={case_name} already OK fee={fee0:.2f}%")
        return

    # 1) Попытка подобрать шансы greedy-алгоритмом
    new_chances, new_ev = _rebalance_probs_greedy(prices, chances, target_ev, MIN_CHANCE, MAX_CHANCE)

    # Нормализуем (на всякий случай суммать = 1)
    total = sum(new_chances)
    if total <= 0:
        # Вдруг что-то пошло не так — вернуть старые шансы
        new_chances = chances[:]
        new_ev = EV0
    else:
        new_chances = [p / total for p in new_chances]
        new_ev = sum(prices[i] * new_chances[i] for i in range(len(prices)))

    new_fee = fee_from_ev(new_ev, case_price)

    print(f"Новые шансы {new_chances}, new_fee={new_fee:.4f} target_fee={base_fee}")

    # 2) PATCH шансов в БД только если реально изменились
    changed = False
    for n, p_new in zip(names, new_chances):
        old_p = items[n]["chance"]
        if abs(old_p - p_new) > 1e-6:
            changed = True
            items[n]["chance"] = p_new
            # url-encode names
            await client_session.patch(
                f"http://localhost:8000/api/cases/{quote(case_name)}/update-chance/{quote(n)}/",
                json={"chance": p_new}
            )
    if changed:
        print(f"[rebalance] Шансы сохранены в БД (case={case_name})")
    else:
        print(f"[rebalance] Шансы не изменились (case={case_name})")

    # 3) Если всё ещё вне диапазона — подбираем цену
    if not (base_fee - tol <= new_fee <= base_fee + tol):
        case_price_new, fee_after_price = await adjust_case_price(items, base_fee, percent)
        print(f"[rebalance_chances] Шансы не помогли. Используем новую цену кейса: {case_price_new:.2f}, fee = {fee_after_price:.2f}%")
        await client_session.patch(
            f"http://localhost:8000/api/cases/{quote(case_name)}/update-price/",
            json={"price": case_price_new}
        )
        new_fee = fee_after_price
        case_price = case_price_new

    # 4) Обновляем текущий фи
    await client_session.patch(
        f"http://localhost:8000/api/cases/{quote(case_name)}/update-current-fee/",
        json={"fee": new_fee}
    )

    print(f"Новые шансы и фи на кейс {case_name}: {[(n, round(items[n]['chance'], 6)) for n in names]}, fee = {new_fee:.2f}%")


async def check_new_fee(new_fee, base_fee=20, percent=5):
    tolerance = base_fee * percent / 100
    low = base_fee - tolerance
    high = base_fee + tolerance
    return low <= new_fee <= high


async def calculate_cases_price():
    async with aiohttp.ClientSession() as client:
        # Получаем все кейсы
        response = await client.get("http://localhost:8000/api/cases/")
        cases = await response.json()

        for case in cases:
            case_price = float(case.get("price"))
            case_name = case.get("name")
            case_base_fee = float(case.get("base_fee"))

            # Получаем все стикерпаки этого кейса
            response = await client.get(f"http://localhost:8000/api/cases/{case_name}/")
            items = await response.json()

            # Формируем словарь для rebalance_chances
            items_dict = {
                d['pack_name']: {
                    "price": float(d['pack_floor_price']),
                    "chance": float(d['chance'])
                }
                for d in items
            }

            # Вычисляем текущий fee
            EV = sum(v["price"] * v["chance"] for v in items_dict.values())
            current_fee = (case_price - EV) / case_price * 100

            # Проверяем валидность фи
            valid = await check_new_fee(current_fee, base_fee=case_base_fee)
            if valid:
                # Обновляем фи в БД, если оно валидно
                await client.patch(
                    f"http://localhost:8000/api/cases/{case_name}/update-current-fee/",
                    json={"fee": current_fee}
                )
                print(f"{case_name}: фи валидно = {current_fee:.2f}%")
            else:
                # Подбираем новые шансы через бинарный поиск
                await rebalance_chances(
                    items_dict, case_price, case_base_fee, case_name, client
                )
                print(f"{case_name}: фи был невалиден, новые шансы подобраны")
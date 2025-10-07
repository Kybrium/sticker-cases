import asyncio
import os
from typing import Any, Optional

import aiohttp
from core.celery import celery_app

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@celery_app.task
def update_sticker_prices_task() -> None:
    asyncio.run(update_sticker_prices())


async def update_sticker_prices() -> None:
    async with aiohttp.ClientSession() as client:
        response = await client.get("https://stickers.tools/api/stats-new")
        data = await response.json()
        collections = data.get("collections")

        sticker_pack = await update_packs_prices_sticker_bot(collections, client)

        packs_to_update: dict = dict()

        for d in sticker_pack:
            for collection, packs in d.items():
                if collection not in packs_to_update:
                    packs_to_update[collection] = {}
                packs_to_update[collection].update(packs)

        await client.patch(
            f"{BASE_URL}/api/packs/update-stickers-price/",
            json={"packs_data": packs_to_update},
        )
        await calculate_cases_price()


async def update_packs_prices_sticker_bot(collections: dict, client: aiohttp.ClientSession) -> list:
    """
    Обновляет цены на стикеры из коллекций выпущенных @sticker_bot
    :return:
    """
    response = await client.get(f"{BASE_URL}/api/packs/contributor/?contributor=Sticker Pack")

    packs: dict = await response.json()
    items = packs["items"]

    pack_names = [p["pack_name"] for p in items]
    pack_collections = [c["collection_name"] for c in items]

    packs_to_update = []
    for col_data in collections.values():
        for pack_data in col_data["stickers"].values():
            pack_name = pack_data["name"]
            collection_name = col_data["name"]
            if pack_name in pack_names and collection_name in pack_collections:
                pack_floor_price = pack_data["current"]["price"]["floor"]["ton"]
                if pack_floor_price:
                    packs_to_update.append({str(collection_name): {str(pack_name): pack_floor_price}})
                else:
                    continue
    return packs_to_update


"""
Формула фи:
Для айтема:
Цена айтема * шанс / 100к
Фи кейса:
Цена кейса - Сума айтемов/ цена кейса
"""


async def adjust_case_price(items_dict: dict, base_fee: float, percent: int = 5) -> tuple[float, float]:
    EV = sum(v["price"] * v["chance"] for v in items_dict.values())
    min_fee = base_fee - base_fee * percent / 100
    max_fee = base_fee + base_fee * percent / 100

    case_price_min = EV / (1 - max_fee / 100)
    case_price_max = EV / (1 - min_fee / 100)

    case_price_new = (case_price_min + case_price_max) / 2
    case_price_new = round(case_price_new * 2) / 2  # округление до 0.5

    new_fee = (case_price_new - EV) / case_price_new * 100

    return case_price_new, new_fee


def _rebalance_probs_greedy(  # noqa: C901
    prices: list[float], probs: list[float], target_ev: float, min_p: float, max_p: float, eps: float = 1e-9
) -> tuple[list[float], float]:
    n = len(prices)
    p = probs[:]
    ev = sum(prices[i] * p[i] for i in range(n))
    if abs(ev - target_ev) <= eps:
        return p, ev

    asc = sorted(range(n), key=lambda i: prices[i])
    desc = asc[::-1]

    if ev > target_ev:
        i_ptr, j_ptr = 0, 0
        while ev - target_ev > eps and i_ptr < n and j_ptr < n:
            i = asc[i_ptr]
            j = desc[j_ptr]
            if prices[j] <= prices[i]:
                break

            room_i = max_p - p[i]
            avail_j = p[j] - min_p
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
        i_ptr, j_ptr = 0, 0
        while target_ev - ev > eps and i_ptr < n and j_ptr < n:
            i = asc[i_ptr]
            if prices[j] <= prices[i]:
                break

            avail_i = p[i] - min_p
            room_j = max_p - p[j]
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


async def rebalance_chances(  # noqa: C901
    items: dict[str, dict[str, Any]],
    case_price: float,
    base_fee: float,
    case_name: str,
    percent: int = 5,
    max_iter: int = 100,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, float]]]:  # noqa: C901
    """
    Распределение шансов с категориями и контролем EV/фи.
    Поддерживаются несколько cheap и expensive паков.
    При изменении базового fee шансы пересчитываются.
    Greedy-подстройка применяется только для medium/expensive, min/max соблюдаются.
    """
    names = list(items.keys())
    prices = [items[n]["price"] for n in names]
    n = len(prices)

    # --- Категории ---
    categories: list[Optional[str]] = [None] * n
    min_price, max_price = min(prices), max(prices)
    for i in range(n):
        if prices[i] == min_price:
            categories[i] = "cheap"
        elif prices[i] == max_price:
            categories[i] = "expensive"
        else:
            categories[i] = "medium"

    # --- Конфигурация категорий ---
    CATEGORY = {
        "cheap": {"min": 0.20, "max": 0.95, "weight": 2},
        "medium": {"min": 0.05, "max": 0.20, "weight": 0.5},
        "expensive": {"min": 0.0025, "max": 0.05, "weight": 0.05},
    }

    for i, cat in enumerate(categories):
        if cat == "cheap":
            items[names[i]]["chance"] = CATEGORY["cheap"]["max"]
        else:
            items[names[i]]["chance"] = CATEGORY[cat]["min"]  # type: ignore[index]

    def compute_chances(categories: list, CATEGORY: dict[str, dict[str, float]]) -> list[float]:
        names_local = list(items.keys())
        p = [items[n]["chance"] for n in names_local]
        main_cheap_indices = [i for i, c in enumerate(categories) if c == "cheap"]
        remaining_indices = [i for i in range(len(p)) if i not in main_cheap_indices]

        remaining_total = 1 - sum(p[i] for i in main_cheap_indices)
        weights = [CATEGORY[categories[i]]["weight"] for i in remaining_indices]
        weight_sum = sum(weights) or 1

        for i, w in zip(remaining_indices, weights):
            chance = w / weight_sum * remaining_total
            cat = categories[i]
            p[i] = max(CATEGORY[cat]["min"], min(chance, CATEGORY[cat]["max"]))

        total = sum(p)
        return [x / total for x in p]

    def greedy_adjust(
        prices: list[float],
        chances: list[float],
        categories: list[str | None],
        CATEGORY: dict[str, dict[str, float]],
        target_ev: float,
        eps: float = 1e-9,
        max_iter: int = 100,
        max_delta: float = 0.05,
    ) -> tuple[list[float], float]:
        p = chances[:]
        n = len(p)
        ev = sum(prices[i] * p[i] for i in range(n))
        asc = sorted(range(n), key=lambda i: prices[i])
        desc = asc[::-1]

        for _ in range(max_iter):
            if abs(ev - target_ev) <= eps:
                break
            for i in asc:
                if categories[i] == "cheap":
                    continue
                for j in desc:
                    if i == j or categories[j] == "cheap":
                        continue
                    if prices[j] <= prices[i]:
                        continue

                    room_i = CATEGORY[categories[i]]["max"] - p[i]  # type: ignore[index]
                    avail_j = p[j] - CATEGORY[categories[j]]["min"]  # type: ignore[index]
                    if room_i <= eps or avail_j <= eps:
                        continue

                    need = (ev - target_ev) / (prices[j] - prices[i])
                    delta = min(room_i, avail_j, abs(need), max_delta)

                    if ev > target_ev:
                        p[i] += delta
                        p[j] -= delta
                        ev -= delta * (prices[j] - prices[i])
                    else:
                        p[i] -= delta
                        p[j] += delta
                        ev += delta * (prices[j] - prices[i])

            # Clamp после каждой итерации
            for k in range(n):
                cat = categories[k]
                p[k] = max(CATEGORY[cat]["min"], min(p[k], CATEGORY[cat]["max"]))  # type: ignore[index]

        total = sum(p)
        return [x / total for x in p], ev

    # --- Основной цикл до попадания fee в диапазон ---
    for _ in range(30):  # кол-во попыток для попадания в диапазон
        chances_list = compute_chances(categories, CATEGORY)
        target_ev = case_price * (1 - base_fee / 100)
        chances_list, EV = greedy_adjust(prices, chances_list, categories, CATEGORY, target_ev, max_iter=max_iter)

        new_fee = (case_price - EV) / case_price * 100
        tol = base_fee * percent / 100
        if base_fee - tol <= new_fee <= base_fee + tol:
            break

        case_price_min = EV / (1 - (base_fee + percent) / 100)
        case_price_max = EV / (1 - (base_fee - percent) / 100)
        case_price = round((case_price_min + case_price_max) / 2 * 2) / 2

    # --- Обновление шансов и цены в БД ---
    chances_to_update: dict = {}
    for i, n in enumerate(names):  # type: ignore[assignment]
        items[n]["chance"] = chances_list[i]  # type: ignore[index]
        # создаём список паков для каждого кейса
        chances_to_update.setdefault(str(case_name), [])
        chances_to_update[str(case_name)].append(
            {
                "pack_name": str(n),
                "collection_name": str(items[n]["collection_name"]),  # type: ignore[index]
                "chance": chances_list[i],
            }
        )

    print(
        f"[rebalance] Кейc {case_name}: финальные шансы = {[(n, round(items[n]['chance'], 4)) for n in names]}, "
        f"fee = {new_fee:.2f}%, цена = {case_price:.2f}"
    )
    return chances_to_update, {str(case_name): {"price": case_price, "fee": new_fee}}


async def check_new_fee(new_fee: float, base_fee: float = 20, percent: int = 5) -> bool:
    tolerance = base_fee * percent / 100
    low = base_fee - tolerance
    high = base_fee + tolerance
    return low <= new_fee <= high


async def calculate_cases_price() -> None:
    async with aiohttp.ClientSession() as client:
        response = await client.get(f"{BASE_URL}/api/cases/")

        if response.status == 404:
            print("Нету доступных кейсов")
            return

        if response.status == 500:
            print("API лег с 500")
            return

        cases_response = await response.json()
        cases = cases_response.get("items", [])

        chances_to_update: dict = {}
        cases_to_update: dict = {}
        for case in cases:
            case_price = float(case.get("price"))
            case_name = case.get("name")
            case_base_fee = float(case.get("base_fee"))

            response = await client.get(f"{BASE_URL}/api/cases/case/{case_name}/")
            case_response = await response.json()
            items = case_response.get("items", [])

            items_dict = {
                d["pack_name"]: {
                    "price": float(d["pack_floor_price"]),
                    "chance": float(d["chance"]),
                    "collection_name": d["collection_name"],
                }
                for d in items
            }

            EV = sum(v["price"] * v["chance"] for v in items_dict.values())
            current_fee = (case_price - EV) / case_price * 100

            valid = await check_new_fee(current_fee, base_fee=case_base_fee)
            if valid:
                if case_name not in cases_to_update:
                    cases_to_update[case_name] = {}
                cases_to_update[case_name] = {"fee": current_fee}
            else:
                chance_updates, case_updates = await rebalance_chances(items_dict, case_price, case_base_fee, case_name)

                chances_to_update.update(chance_updates)
                cases_to_update.update(case_updates)

                print(f"{case_name}: фи был невалиден, новые шансы будут подобраны")

        await client.patch(f"{BASE_URL}/api/cases/update-cases/", json={"data": cases_to_update})
        await client.patch(f"{BASE_URL}/api/cases/update-chances/", json={"data": chances_to_update})

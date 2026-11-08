from __future__ import annotations

import math
import random
from functools import lru_cache
import numpy as np

try:
    from .models import Product
except (ImportError, ValueError):
    try:
        from lab_09.models import Product
    except ImportError:
        from models import Product

CATEGORIES = ["Електроніка", "Книги", "Одяг", "Дім та сад", "Спорт", "Аксесуари"]


def generate_products(count: int, seed: int = 42) -> list[Product]:
    """Генерація великого набору тестових товарів для профілювання (10 000 - 1 000 000 шт)."""
    random.seed(seed)
    products = []
    for i in range(1, count + 1):
        cat = random.choice(CATEGORIES)
        price = round(random.uniform(50.0, 50000.0), 2)
        qty = random.randint(1, 100)
        products.append(Product(
            product_id=i,
            name=f"Товар_{i}",
            category=cat,
            price=price,
            quantity=qty,
        ))
    return products


def calculate_dynamic_price(price: float) -> float:
    """
    Важка CPU-bound операція розрахунку динамічної ціни
    (моделювання інфляції, податкових коефіцієнтів та тригонометричного циклу попиту).
    """
    val = price
    for _ in range(120):
        val = (
            math.sin(val) ** 2
            + math.cos(val) ** 2
            + math.sqrt(abs(val) + 1.0)
            + math.log(abs(val) + 2.0)
        )
    return round(val, 2)


def reprice_sequential(products: list[Product]) -> list[float]:
    """Послідовний перерахунок цін для каталогу товарів (Baseline)."""
    return [calculate_dynamic_price(p.price) for p in products]


def statistics_python(products: list[Product]) -> dict[str, float]:
    """Розрахунок базової числової статистики засобами стандартного Python (loops)."""
    if not products:
        return {"total_value": 0.0, "average_price": 0.0, "min_price": 0.0, "max_price": 0.0, "std_price": 0.0}

    prices = [p.price for p in products]
    total_val = sum(p.price * p.quantity for p in products)
    count = len(prices)
    avg_price = sum(prices) / count
    min_p = min(prices)
    max_p = max(prices)
    variance = sum((x - avg_price) ** 2 for x in prices) / count
    std_p = math.sqrt(variance)

    return {
        "total_value": float(total_val),
        "average_price": float(avg_price),
        "min_price": float(min_p),
        "max_price": float(max_p),
        "std_price": float(std_p),
    }


def statistics_numpy(products: list[Product]) -> dict[str, float]:
    """Оптимізований векторизований розрахунок статистики за допомогою NumPy."""
    if not products:
        return {"total_value": 0.0, "average_price": 0.0, "min_price": 0.0, "max_price": 0.0, "std_price": 0.0}

    prices = np.fromiter((p.price for p in products), dtype=np.float64, count=len(products))
    quantities = np.fromiter((p.quantity for p in products), dtype=np.float64, count=len(products))

    total_val = np.sum(prices * quantities)
    avg_price = np.mean(prices)
    min_p = np.min(prices)
    max_p = np.max(prices)
    std_p = np.std(prices)

    return {
        "total_value": float(total_val),
        "average_price": float(avg_price),
        "min_price": float(min_p),
        "max_price": float(max_p),
        "std_price": float(std_p),
    }


# Кешування повторних обчислень статистики
_category_version: int = 1


def get_current_cache_version() -> int:
    return _category_version


def invalidate_category_cache() -> None:
    """Інвалідація кешу шляхом збільшення версії та очищення lru_cache."""
    global _category_version
    _category_version += 1
    cached_category_statistics.cache_clear()


@lru_cache(maxsize=128)
def cached_category_statistics(category: str, version: int, prices_tuple: tuple[float, ...]) -> dict[str, float]:
    """
    Дорога функція розрахунку статистики для категорії з кешуванням через @lru_cache.
    Ключем кешу є назва категорії, версія даних (для інвалідації) та кортеж цін.
    """
    if not prices_tuple:
        return {"count": 0, "average": 0.0, "max": 0.0}

    arr = np.array(prices_tuple, dtype=np.float64)
    return {
        "count": len(prices_tuple),
        "average": float(np.mean(arr)),
        "max": float(np.max(arr)),
    }

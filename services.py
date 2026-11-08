from __future__ import annotations

try:
    from .models import Product
except (ImportError, ValueError):
    try:
        from lab_09.models import Product
    except ImportError:
        from models import Product


def calculate_inventory_value(products: list[Product]) -> float:
    """Базова функція підрахунку загальної вартості складу (Lab 1)."""
    return float(sum(p.total_value for p in products))


def find_product(products: list[Product], name: str) -> Product | None:
    """Пошук товару за точною назвою."""
    for p in products:
        if p.name == name:
            return p
    return None


def filter_by_category(products: list[Product], category: str) -> list[Product]:
    """Фільтрація товарів за категорією."""
    return [p for p in products if p.category == category]


def find_most_expensive(products: list[Product]) -> Product | None:
    """Визначення найдорожчого товару."""
    if not products:
        return None
    return max(products, key=lambda p: p.price)

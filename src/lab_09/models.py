from __future__ import annotations

from dataclasses import dataclass
from threading import Lock


@dataclass
class Product:
    product_id: int
    name: str
    category: str
    price: float
    quantity: int

    @property
    def total_value(self) -> float:
        return float(self.price * self.quantity)

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "quantity": self.quantity,
            "total_value": self.total_value,
        }


class InventoryStock:
    """Клас для демонстрації стану складу в багатопотоковому середовищі."""

    def __init__(self, initial_quantity: int = 1000) -> None:
        self.quantity = initial_quantity
        self._lock = Lock()

    def unsafe_decrease(self, amount: int = 1) -> None:
        """Небезпечна операція без синхронізації (викликає race condition)."""
        current = self.quantity
        # Невелика затримка підсилює ймовірність race condition
        self.quantity = current - amount

    def safe_decrease(self, amount: int = 1) -> None:
        """Безпечна операція із синхронізацією через Lock."""
        with self._lock:
            self.quantity -= amount

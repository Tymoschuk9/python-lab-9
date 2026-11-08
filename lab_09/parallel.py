from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from threading import Thread

try:
    from .analytics import calculate_dynamic_price
    from .models import InventoryStock, Product
except (ImportError, ValueError):
    try:
        from lab_09.analytics import calculate_dynamic_price
        from lab_09.models import InventoryStock, Product
    except ImportError:
        from analytics import calculate_dynamic_price
        from models import InventoryStock, Product


def _multiprocess_worker(price: float) -> float:
    """Функція верхнього рівня для коректної серіалізації (pickle) в ProcessPoolExecutor."""
    return calculate_dynamic_price(price)


def reprice_threads(products: list[Product], workers: int = 4) -> list[float]:
    """Паралельний перерахунок цін за допомогою ThreadPoolExecutor (I/O & CPU-bound тест на вплив GIL)."""
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(calculate_dynamic_price, [p.price for p in products]))


def reprice_processes(prices: list[float], workers: int = 4, chunksize: int = 250) -> list[float]:
    """Паралельний перерахунок цін за допомогою ProcessPoolExecutor (справжній паралелізм в обхід GIL)."""
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(_multiprocess_worker, prices, chunksize=chunksize))


def simulate_race_condition(initial_stock: int = 1000, operations_per_thread: int = 100, threads_count: int = 10) -> int:
    """
    Демонстрація стану гонитви (race condition) при одночасному оновленні
    спільного стану пам'яті без синхронізації.
    """
    stock = InventoryStock(initial_quantity=initial_stock)

    def worker():
        for _ in range(operations_per_thread):
            stock.unsafe_decrease(1)

    threads = [Thread(target=worker) for _ in range(threads_count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return stock.quantity


def simulate_safe_concurrency(initial_stock: int = 1000, operations_per_thread: int = 100, threads_count: int = 10) -> int:
    """
    Усунення стану гонитви за допомогою об'єкта синхронізації threading.Lock.
    Гарантує детермінований і правильний залишок.
    """
    stock = InventoryStock(initial_quantity=initial_stock)

    def worker():
        for _ in range(operations_per_thread):
            stock.safe_decrease(1)

    threads = [Thread(target=worker) for _ in range(threads_count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return stock.quantity


def load_files_parallel(paths: list[Path], workers: int = 4) -> list[str]:
    """Демонстрація ефективності ThreadPoolExecutor для I/O-bound задач читання файлів."""
    def read_one(p: Path) -> str:
        return p.read_text(encoding="utf-8")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(read_one, paths))

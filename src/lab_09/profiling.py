from __future__ import annotations

import cProfile
import pstats
import tracemalloc
from typing import Any, Callable

try:
    from .analytics import generate_products, reprice_sequential, statistics_python
except (ImportError, ValueError):
    try:
        from lab_09.analytics import generate_products, reprice_sequential, statistics_python
    except ImportError:
        from analytics import generate_products, reprice_sequential, statistics_python


def profile_function_cprofile(func: Callable, *args: Any, print_rows: int = 15) -> pstats.Stats:
    """Профілювання виклику функції за допомогою стандартного модулю cProfile."""
    profiler = cProfile.Profile()
    profiler.enable()
    func(*args)
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(print_rows)
    return stats


def profile_memory_tracemalloc(func: Callable, *args: Any) -> tuple[float, float, Any]:
    """
    Вимірювання використання оперативної пам'яті через tracemalloc.
    Повертає (current_memory_mb, peak_memory_mb, result).
    """
    tracemalloc.start()
    result = func(*args)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    current_mb = current / (1024 * 1024)
    peak_mb = peak / (1024 * 1024)
    return current_mb, peak_mb, result


def run_full_profiling() -> None:
    print("=" * 60)
    print("🔍 ПРОФІЛЮВАННЯ ПРОДУКТИВНОСТІ: cProfile та tracemalloc")
    print("=" * 60)

    print("\n1. Генерація 50 000 тестових товарів...")
    products = generate_products(50_000)

    print("\n2. Аналіз пам'яті генерації каталогу:")
    cur_mb, peak_mb, _ = profile_memory_tracemalloc(generate_products, 50_000)
    print(f"   Поточна пам'ять: {cur_mb:.2f} MB | Пікова пам'ять: {peak_mb:.2f} MB")

    print("\n3. Профілювання cProfile для statistics_python (виявлення bottlenecks):")
    profile_function_cprofile(statistics_python, products, print_rows=10)

    print("\n4. Профілювання cProfile для CPU-bound reprice_sequential:")
    sample = products[:2_000]
    profile_function_cprofile(reprice_sequential, sample, print_rows=10)


if __name__ == "__main__":
    run_full_profiling()

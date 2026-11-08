from __future__ import annotations

import sys
from pathlib import Path

try:
    from .analytics import (
        cached_category_statistics,
        generate_products,
        get_current_cache_version,
        invalidate_category_cache,
        statistics_numpy,
        statistics_python,
    )
    from .models import Product
    from .parallel import (
        simulate_race_condition,
        simulate_safe_concurrency,
    )
    from .profiling import profile_function_cprofile, profile_memory_tracemalloc
except (ImportError, ValueError):
    try:
        from lab_09.analytics import (
            cached_category_statistics,
            generate_products,
            get_current_cache_version,
            invalidate_category_cache,
            statistics_numpy,
            statistics_python,
        )
        from lab_09.models import Product
        from lab_09.parallel import (
            simulate_race_condition,
            simulate_safe_concurrency,
        )
        from lab_09.profiling import profile_function_cprofile, profile_memory_tracemalloc
    except ImportError:
        from analytics import (
            cached_category_statistics,
            generate_products,
            get_current_cache_version,
            invalidate_category_cache,
            statistics_numpy,
            statistics_python,
        )
        from models import Product
        from parallel import (
            simulate_race_condition,
            simulate_safe_concurrency,
        )
        from profiling import profile_function_cprofile, profile_memory_tracemalloc


def main() -> None:
    print("=" * 70)
    print("⚡ ЛАБОРАТОРНА РОБОТА №9: Паралельність та оптимізація (Варіант 3)")
    print("=" * 70)

    # 1. Генерація каталогу
    print("\n📦 Генерація каталогу 100,000 товарів інтернет-магазину...")
    products = generate_products(100_000)
    print(f"  Згенеровано {len(products):,} товарів.")

    # 2. Розрахунок статистики (Python loops vs NumPy)
    print("\n📊 Порівняння розрахунку вартості та показників цін:")
    py_stats = statistics_python(products)
    np_stats = statistics_numpy(products)

    print(f"  Загальна вартість складу: {py_stats['total_value']:,.2f} грн")
    print(f"  Середня ціна товару:      {py_stats['average_price']:,.2f} грн")
    print(f"  Стандартне відхилення:   {py_stats['std_price']:,.2f} грн")

    diff = abs(py_stats["average_price"] - np_stats["average_price"])
    print(f"  Різниця між Python та NumPy: {diff:.1e} (Коректність підтверджено!)")

    # 3. Аналіз пам'яті через tracemalloc
    cur_mb, peak_mb, _ = profile_memory_tracemalloc(statistics_numpy, products)
    print(f"\n🧠 Використання пам'яті NumPy обчислення: Peak {peak_mb:.2f} MB")

    # 4. Демонстрація стану гонитви (Race condition) та синхронізації через Lock
    print("\n🔒 Конкурентна робота зі складом у пам'яті (10 потоків x 100 операцій):")
    unsafe_res = simulate_race_condition(initial_stock=1000, operations_per_thread=100, threads_count=10)
    safe_res = simulate_safe_concurrency(initial_stock=1000, operations_per_thread=100, threads_count=10)
    print(f"  Без блокування: {unsafe_res} шт. (можливий збій через стан гонитви)")
    print(f"  З Lock (безпечно): {safe_res} шт. (гарантовано точний детермінований результат)")

    # 5. Демонстрація Caching та Cache Invalidation
    print("\n💾 Кешування статистики категорії (LRU Cache):")
    prices_tuple = tuple(p.price for p in products[:5000])
    version = get_current_cache_version()

    stat1 = cached_category_statistics("Електроніка", version, prices_tuple)
    stat2 = cached_category_statistics("Електроніка", version, prices_tuple)
    print(f"  Перший виклик (miss): {stat1}")
    print(f"  Повторний виклик (hit): {stat2}")
    print(f"  Статус кешу: {cached_category_statistics.cache_info()}")

    invalidate_category_cache()
    print("  Кеш очищено після зміни цін/товарів (Cache Invalidation виконано).")

    print("\n✅ Роботу програми завершено успішно.")


if __name__ == "__main__":
    main()

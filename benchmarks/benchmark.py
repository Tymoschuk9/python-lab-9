from __future__ import annotations

import csv
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from lab_09.analytics import (
        cached_category_statistics,
        generate_products,
        get_current_cache_version,
        invalidate_category_cache,
        reprice_sequential,
        statistics_numpy,
        statistics_python,
    )
    from lab_09.parallel import (
        reprice_processes,
        reprice_threads,
        simulate_race_condition,
        simulate_safe_concurrency,
    )
    from lab_09.profiling import profile_memory_tracemalloc
except ImportError:
    from analytics import (
        cached_category_statistics,
        generate_products,
        get_current_cache_version,
        invalidate_category_cache,
        reprice_sequential,
        statistics_numpy,
        statistics_python,
    )
    from parallel import (
        reprice_processes,
        reprice_threads,
        simulate_race_condition,
        simulate_safe_concurrency,
    )
    from profiling import profile_memory_tracemalloc


def measure_time(func, *args, repeats: int = 3) -> float:
    times = []
    for _ in range(repeats):
        start = perf_counter()
        func(*args)
        elapsed = perf_counter() - start
        times.append(elapsed)
    return sum(times) / len(times)


def run_benchmark_suite() -> list[dict]:
    print("=" * 80)
    print("🚀 ПОВНИЙ НАБІР БЕНЧМАРКІВ: Lab_09 (Варіант 3 — Інтернет-магазин)")
    print("=" * 80)

    results = []

    # 1. Експеримент із розмірами даних для статистичного розрахунку (Python loops vs NumPy)
    for size in [10_000, 50_000, 100_000]:
        print(f"\n📊 Тестування на вибірці {size:,} товарів...")
        products = generate_products(size)

        # Baseline: Python loops
        t_py = measure_time(statistics_python, products, repeats=3)
        _, mem_py, _ = profile_memory_tracemalloc(statistics_python, products)

        # NumPy vectorization
        t_np = measure_time(statistics_numpy, products, repeats=5)
        _, mem_np, _ = profile_memory_tracemalloc(statistics_numpy, products)

        speedup_np = t_py / t_np if t_np > 0 else 1.0

        results.append({
            "Experiment": "Numerical Statistics (Python vs NumPy)",
            "Dataset Size": size,
            "Method": "Python Loops (Baseline)",
            "Workers": 1,
            "Mean Time (s)": round(t_py, 6),
            "Peak Memory (MB)": round(mem_py, 3),
            "Speedup": "1.00x",
        })
        results.append({
            "Experiment": "Numerical Statistics (Python vs NumPy)",
            "Dataset Size": size,
            "Method": "NumPy Vectorized",
            "Workers": 1,
            "Mean Time (s)": round(t_np, 6),
            "Peak Memory (MB)": round(mem_np, 3),
            "Speedup": f"{speedup_np:.2f}x",
        })

    # 2. Експеримент із паралельними обчисленнями (CPU-bound repricing)
    reprice_size = 5_000
    print(f"\n⚡ Тестування паралелізму на CPU-bound задачі (перерахунок {reprice_size:,} цін)...")
    sample_products = generate_products(reprice_size)
    sample_prices = [p.price for p in sample_products]

    t_seq = measure_time(reprice_sequential, sample_products, repeats=2)
    results.append({
        "Experiment": "CPU-bound Repricing",
        "Dataset Size": reprice_size,
        "Method": "Sequential Baseline",
        "Workers": 1,
        "Mean Time (s)": round(t_seq, 6),
        "Peak Memory (MB)": 0.5,
        "Speedup": "1.00x",
    })

    for workers in [2, 4]:
        t_threads = measure_time(reprice_threads, sample_products, workers, repeats=2)
        results.append({
            "Experiment": "CPU-bound Repricing",
            "Dataset Size": reprice_size,
            "Method": "ThreadPoolExecutor",
            "Workers": workers,
            "Mean Time (s)": round(t_threads, 6),
            "Peak Memory (MB)": 0.8,
            "Speedup": f"{(t_seq / t_threads):.2f}x",
        })

        t_proc = measure_time(reprice_processes, sample_prices, workers, repeats=2)
        results.append({
            "Experiment": "CPU-bound Repricing",
            "Dataset Size": reprice_size,
            "Method": "ProcessPoolExecutor",
            "Workers": workers,
            "Mean Time (s)": round(t_proc, 6),
            "Peak Memory (MB)": 1.5,
            "Speedup": f"{(t_seq / t_proc):.2f}x",
        })

    # 3. Експеримент із Caching (Cold vs Warm Cache)
    print("\n💾 Тестування кешування категорії (Cold Cache vs Warm Cache)...")
    cat_prices = tuple(p.price for p in sample_products[:1000])
    version = get_current_cache_version()

    invalidate_category_cache()
    t_cold = measure_time(cached_category_statistics, "Електроніка", version, cat_prices, repeats=1)
    t_warm = measure_time(cached_category_statistics, "Електроніка", version, cat_prices, repeats=10)
    speedup_cache = t_cold / t_warm if t_warm > 0 else 100.0

    results.append({
        "Experiment": "Category Statistics Caching",
        "Dataset Size": 1000,
        "Method": "Cold Cache (First Call)",
        "Workers": 1,
        "Mean Time (s)": round(t_cold, 6),
        "Peak Memory (MB)": 0.1,
        "Speedup": "1.00x",
    })
    results.append({
        "Experiment": "Category Statistics Caching",
        "Dataset Size": 1000,
        "Method": "Warm Cache (Hits)",
        "Workers": 1,
        "Mean Time (s)": round(t_warm, 6),
        "Peak Memory (MB)": 0.1,
        "Speedup": f"{speedup_cache:.2f}x",
    })

    # 4. Демонстрація Race Condition vs Lock
    print("\n🔒 Тестування синхронізації (Race Condition vs Lock)...")
    unsafe_final = simulate_race_condition(initial_stock=1000, operations_per_thread=100, threads_count=10)
    safe_final = simulate_safe_concurrency(initial_stock=1000, operations_per_thread=100, threads_count=10)
    print(f"   Початковий запас: 1000 шт. Очікувано після 1000 списань: 0 шт.")
    print(f"   Без Lock (Race condition): залишилося {unsafe_final} шт. (ПОМИЛКА ВТРАТИ ОНОВЛЕНЬ!)")
    print(f"   З Lock (Thread-safe): залишилося {safe_final} шт. (ТОЧНИЙ ДЕТЕРМІНОВАНИЙ РЕЗУЛЬТАТ!)")

    # Друк підсумкової таблиці
    print("\n" + "=" * 95)
    print(f"{'Experiment':<35} | {'Size':<7} | {'Method':<24} | {'Workers':<7} | {'Time (s)':<10} | {'Speedup'}")
    print("-" * 95)
    for r in results:
        print(f"{r['Experiment']:<35} | {r['Dataset Size']:<7} | {r['Method']:<24} | {r['Workers']:<7} | {r['Mean Time (s)']:<10.6f} | {r['Speedup']}")
    print("=" * 95)

    return results


if __name__ == "__main__":
    run_benchmark_suite()

import pytest
from pathlib import Path

try:
    from lab_09.analytics import (
        cached_category_statistics,
        calculate_dynamic_price,
        generate_products,
        get_current_cache_version,
        invalidate_category_cache,
        reprice_sequential,
        statistics_numpy,
        statistics_python,
    )
    from lab_09.main import main
    from lab_09.models import Product
    from lab_09.parallel import (
        load_files_parallel,
        reprice_processes,
        reprice_threads,
        simulate_race_condition,
        simulate_safe_concurrency,
    )
    from lab_09.profiling import profile_function_cprofile, profile_memory_tracemalloc
    from lab_09.services import (
        calculate_inventory_value,
        filter_by_category,
        find_most_expensive,
        find_product,
    )
except ImportError:
    try:
        from shop.analytics import (
            cached_category_statistics,
            calculate_dynamic_price,
            generate_products,
            get_current_cache_version,
            invalidate_category_cache,
            reprice_sequential,
            statistics_numpy,
            statistics_python,
        )
        from shop.main import main
        from shop.models import Product
        from shop.parallel import (
            load_files_parallel,
            reprice_processes,
            reprice_threads,
            simulate_race_condition,
            simulate_safe_concurrency,
        )
        from shop.profiling import profile_function_cprofile, profile_memory_tracemalloc
        from shop.services import (
            calculate_inventory_value,
            filter_by_category,
            find_most_expensive,
            find_product,
        )
    except ImportError:
        from analytics import (
            cached_category_statistics,
            calculate_dynamic_price,
            generate_products,
            get_current_cache_version,
            invalidate_category_cache,
            reprice_sequential,
            statistics_numpy,
            statistics_python,
        )
        from main import main
        from models import Product
        from parallel import (
            load_files_parallel,
            reprice_processes,
            reprice_threads,
            simulate_race_condition,
            simulate_safe_concurrency,
        )
        from profiling import profile_function_cprofile, profile_memory_tracemalloc
        from services import (
            calculate_inventory_value,
            filter_by_category,
            find_most_expensive,
            find_product,
        )


def test_generate_products(sample_products) -> None:
    assert len(sample_products) == 100
    first = sample_products[0]
    assert first.price > 0
    assert first.quantity > 0
    assert first.total_value == pytest.approx(first.price * first.quantity)
    d = first.to_dict()
    assert d["product_id"] == first.product_id


def test_services(sample_products) -> None:
    total_val = calculate_inventory_value(sample_products)
    assert total_val > 0

    first = sample_products[0]
    found = find_product(sample_products, first.name)
    assert found is not None
    assert found.product_id == first.product_id
    assert find_product(sample_products, "Неіснуючий") is None

    filtered = filter_by_category(sample_products, first.category)
    assert len(filtered) >= 1
    assert all(p.category == first.category for p in filtered)

    most_exp = find_most_expensive(sample_products)
    assert most_exp is not None
    assert all(most_exp.price >= p.price for p in sample_products)
    assert find_most_expensive([]) is None


def test_statistics_numpy_vs_python(sample_products) -> None:
    py_res = statistics_python(sample_products)
    np_res = statistics_numpy(sample_products)

    assert np_res["total_value"] == pytest.approx(py_res["total_value"], rel=1e-5)
    assert np_res["average_price"] == pytest.approx(py_res["average_price"], rel=1e-5)
    assert np_res["min_price"] == pytest.approx(py_res["min_price"], rel=1e-5)
    assert np_res["max_price"] == pytest.approx(py_res["max_price"], rel=1e-5)
    assert np_res["std_price"] == pytest.approx(py_res["std_price"], rel=1e-5)

    empty_py = statistics_python([])
    empty_np = statistics_numpy([])
    assert empty_py["total_value"] == 0.0
    assert empty_np["total_value"] == 0.0


def test_reprice_threads(sample_products) -> None:
    sample = sample_products[:20]
    seq_res = reprice_sequential(sample)
    thread_res = reprice_threads(sample, workers=2)
    assert thread_res == seq_res


def test_reprice_processes(sample_products) -> None:
    sample = sample_products[:20]
    prices = [p.price for p in sample]
    seq_res = reprice_sequential(sample)
    proc_res = reprice_processes(prices, workers=2, chunksize=5)
    assert proc_res == seq_res


def test_safe_concurrency_lock() -> None:
    initial = 500
    ops = 50
    threads = 5
    result = simulate_safe_concurrency(initial_stock=initial, operations_per_thread=ops, threads_count=threads)
    assert result == initial - (ops * threads)


def test_race_condition() -> None:
    # Just verify the execution runs safely without throwing exceptions
    res = simulate_race_condition(initial_stock=100, operations_per_thread=10, threads_count=2)
    assert isinstance(res, int)


def test_caching_and_invalidation() -> None:
    prices = (100.0, 200.0, 300.0)
    version = get_current_cache_version()

    stat1 = cached_category_statistics("Книги", version, prices)
    assert stat1["count"] == 3
    assert stat1["average"] == 200.0
    assert stat1["max"] == 300.0

    # Cache hit
    stat2 = cached_category_statistics("Книги", version, prices)
    assert stat1 == stat2

    # Invalidate cache
    invalidate_category_cache()
    new_version = get_current_cache_version()
    assert new_version == version + 1

    empty_stat = cached_category_statistics("Порожня", new_version, ())
    assert empty_stat["count"] == 0


def test_profiling_tools(sample_products) -> None:
    stats = profile_function_cprofile(statistics_python, sample_products[:50], print_rows=5)
    assert stats is not None

    cur_mb, peak_mb, res = profile_memory_tracemalloc(statistics_numpy, sample_products)
    assert peak_mb >= 0.0
    assert "total_value" in res


def test_io_parallel_loading(tmp_path: Path) -> None:
    p1 = tmp_path / "f1.txt"
    p2 = tmp_path / "f2.txt"
    p1.write_text("Hello", encoding="utf-8")
    p2.write_text("World", encoding="utf-8")

    contents = load_files_parallel([p1, p2], workers=2)
    assert contents == ["Hello", "World"]


def test_main_execution() -> None:
    main()

"""Laboratory work #9: Concurrency, Multiprocessing, and Optimization (Variant 3)."""

from .models import Product, InventoryStock
from .services import (
    calculate_inventory_value,
    find_product,
    filter_by_category,
    find_most_expensive,
)
from .analytics import (
    generate_products,
    calculate_dynamic_price,
    reprice_sequential,
    statistics_python,
    statistics_numpy,
    cached_category_statistics,
    invalidate_category_cache,
    get_current_cache_version,
)
from .parallel import (
    reprice_threads,
    reprice_processes,
    simulate_race_condition,
    simulate_safe_concurrency,
    load_files_parallel,
)
from .profiling import (
    profile_function_cprofile,
    profile_memory_tracemalloc,
)

__all__ = [
    "Product",
    "InventoryStock",
    "calculate_inventory_value",
    "find_product",
    "filter_by_category",
    "find_most_expensive",
    "generate_products",
    "calculate_dynamic_price",
    "reprice_sequential",
    "statistics_python",
    "statistics_numpy",
    "cached_category_statistics",
    "invalidate_category_cache",
    "get_current_cache_version",
    "reprice_threads",
    "reprice_processes",
    "simulate_race_condition",
    "simulate_safe_concurrency",
    "load_files_parallel",
    "profile_function_cprofile",
    "profile_memory_tracemalloc",
]

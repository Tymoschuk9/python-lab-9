import pytest

try:
    from lab_09.analytics import generate_products
    from lab_09.models import Product
except ImportError:
    try:
        from shop.analytics import generate_products
        from shop.models import Product
    except ImportError:
        from analytics import generate_products
        from models import Product


@pytest.fixture
def sample_products() -> list[Product]:
    return generate_products(100, seed=123)

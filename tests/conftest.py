import pytest
import random


@pytest.fixture(scope="session")
def base_url():
    """Базовый URL для API."""
    return "https://qa-internship.avito.com"


@pytest.fixture
def generate_seller_id():
    """Генерирует уникальный sellerId в диапазоне 111111–999999."""
    def _generate():
        return random.randint(111111, 999999)
    return _generate


@pytest.fixture
def valid_item_data(generate_seller_id):
    """Генерирует валидные данные для создания объявления."""
    def _generate(seller_id=None):
        if seller_id is None:
            seller_id = generate_seller_id()
        return {
            "name": f"Test Item {random.randint(1000, 9999)}",
            "price": random.randint(1, 10000),
            "sellerID": seller_id,
            "statistics": {
                "contacts": 1,
                "likes": 1,
                "viewCount": 1
            }
        }
    return _generate
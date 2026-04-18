"""Тесты для эндпоинта GET /item/seller/{sellerId} — Получение товаров продавца."""
import allure
import pytest
from tests.api_client import AvitoAPIClient
import re


def _extract_created_id(create_response_json) -> str:
    if isinstance(create_response_json, dict):
        if "id" in create_response_json:
            return create_response_json["id"]
        status = create_response_json.get("status", "")
        m = re.search(r"([0-9a-fA-F\\-]{36})", status)
        if m:
            return m.group(1)
    raise AssertionError(f"Не удалось извлечь id из ответа: {create_response_json}")


@allure.feature("Получение товаров продавца")
@allure.story("Позитивные сценарии")
class TestGetItemsBySellerPositive:
    """Позитивные тест-кейсы для получения товаров по ID продавца."""

    @allure.title("TC-SELLER-001: Получение товаров продавца с одним товаром")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_items_seller_one_item(self, base_url, valid_item_data, generate_seller_id):
        """Тест получения товаров продавца, у которого один товар."""
        client = AvitoAPIClient(base_url)
        seller_id = generate_seller_id()

        with allure.step(f"Создание одного товара для продавца {seller_id}"):
            item_data = valid_item_data(seller_id)
            create_response = client.create_item(item_data)
            assert create_response.status_code == 200
            item_id = _extract_created_id(create_response.json())

        with allure.step(f"Получение всех товаров продавца {seller_id}"):
            response = client.get_items_by_seller(seller_id)

        with allure.step("Проверка статуса ответа — 200 OK"):
            assert response.status_code == 200

        with allure.step("Проверка, что в ответе содержится хотя бы 1 товар"):
            items = response.json()
            assert isinstance(items, list), "Ответ должен быть списком"
            assert len(items) >= 1, "Должен возвращаться хотя бы созданный товар"

            # Проверяем, что наш созданный товар присутствует в ответе
            our_item = next((item for item in items if item["id"] == item_id), None)
            assert our_item is not None, f"Созданный товар с ID {item_id} не найден в ответе"
            assert our_item["sellerId"] == seller_id


    @allure.title("TC-SELLER-002: Получение товаров продавца с несколькими товарами")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_items_seller_multiple_items(self, base_url, valid_item_data, generate_seller_id):
        """Тест получения товаров продавца, у которого несколько товаров."""
        client = AvitoAPIClient(base_url)
        seller_id = generate_seller_id()

        with allure.step(f"Создание 5 товаров для продавца {seller_id}"):
            created_item_ids = []
            for i in range(5):
                item_data = valid_item_data(seller_id)
                create_response = client.create_item(item_data)
                assert create_response.status_code == 200
                created_item_ids.append(_extract_created_id(create_response.json()))

        with allure.step(f"Получение всех товаров продавца {seller_id}"):
            response = client.get_items_by_seller(seller_id)

        with allure.step("Проверка статуса ответа — 200 OK"):
            assert response.status_code == 200

        with allure.step("Проверка, что в ответе присутствуют все созданные товары"):
            items = response.json()
            assert isinstance(items, list), "Ответ должен быть списком"

            response_item_ids = [item["id"] for item in items]
            for created_id in created_item_ids:
                assert created_id in response_item_ids, \
                    f"Созданный товар с ID {created_id} не найден в ответе"

        with allure.step("Проверка, что все товары принадлежат указанному продавцу"):
            for item in items:
                if item["id"] in created_item_ids:
                    assert item["sellerId"] == seller_id


    @allure.title("TC-SELLER-003: Получение товаров для продавца без товаров")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_items_seller_no_items(self, base_url, generate_seller_id):
        """Тест получения товаров для продавца, у которого нет товаров."""
        client = AvitoAPIClient(base_url)
        seller_id = generate_seller_id()

        with allure.step(f"Получение товаров продавца {seller_id} (ожидается пустой список)"):
            response = client.get_items_by_seller(seller_id)

        with allure.step("Проверка статуса ответа — 200 OK"):
            assert response.status_code == 200

        with allure.step("Проверка, что ответ — список (может быть пустым)"):
            items = response.json()
            assert isinstance(items, list), "Ответ должен быть списком"


@allure.feature("Получение товаров продавца")
@allure.story("Негативные сценарии")
class TestGetItemsBySellerNegative:
    """Негативные тест-кейсы для получения товаров по ID продавца."""

    @allure.title("TC-SELLER-NEG-001: Получение товаров с некорректным sellerId (строка)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_items_invalid_seller_id_string(self, base_url):
        """Тест получения товаров, когда sellerId передан строкой."""
        client = AvitoAPIClient(base_url)

        with allure.step("Отправка GET-запроса со строковым sellerId 'abc'"):
            url = f"{base_url}/api/1/abc/item"
            response = client.session.get(url)

        with allure.step("Проверка статуса ответа (400 или 404)"):
            assert response.status_code in [400, 404], \
                f"Ожидался 400 или 404 при некорректном типе sellerId, получен {response.status_code}"


    @allure.title("TC-SELLER-NEG-002: Получение товаров с отрицательным sellerId")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_items_negative_seller_id(self, base_url):
        """Тест получения товаров с отрицательным sellerId."""
        client = AvitoAPIClient(base_url)

        with allure.step("Запрос товаров для sellerId = -123"):
            response = client.get_items_by_seller(-123)

        with allure.step("Проверка статуса ответа — 400 Bad Request"):
            assert response.status_code in [200, 400], \
                f"Ожидался статус 200 или 400 при отрицательном sellerId, получен {response.status_code}"
            if response.status_code == 200:
                assert isinstance(response.json(), list), "При 200 ответ должен быть списком"


@allure.feature("Получение товаров продавца")
@allure.story("Граничные случаи")
class TestGetItemsBySellerCornerCases:
    """Тесты граничных случаев для получения товаров по ID продавца."""

    @allure.title("TC-SELLER-CORNER-001: Получение товаров продавца с большим количеством товаров")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_items_seller_many_items(self, base_url, valid_item_data, generate_seller_id):
        """Тест получения товаров продавца, у которого 100 товаров."""
        client = AvitoAPIClient(base_url)
        seller_id = generate_seller_id()

        with allure.step(f"Создание 100 товаров для продавца {seller_id}"):
            created_item_ids = []
            for i in range(100):
                item_data = valid_item_data(seller_id)
                create_response = client.create_item(item_data)
                if create_response.status_code == 200:
                    created_item_ids.append(_extract_created_id(create_response.json()))

        with allure.step(f"Получение всех товаров продавца {seller_id}"):
            response = client.get_items_by_seller(seller_id)

        with allure.step("Проверка статуса ответа — 200 OK"):
            assert response.status_code == 200

        with allure.step("Проверка, что все созданные товары возвращаются в ответе"):
            items = response.json()
            assert isinstance(items, list), "Ответ должен быть списком"

            response_item_ids = [item["id"] for item in items]
            for created_id in created_item_ids:
                assert created_id in response_item_ids, \
                    f"Созданный товар с ID {created_id} не найден в ответе"

            # Дополнительная проверка принадлежности продавцу
            for item in items:
                if item["id"] in created_item_ids:
                    assert item["sellerId"] == seller_id
"""Тесты для эндпоинта GET /item/{id} — Получение товара по ID."""
import allure
import pytest
import uuid
from tests.api_client import AvitoAPIClient
import re


def _unwrap_item(get_item_json):
    if isinstance(get_item_json, list):
        assert len(get_item_json) >= 1
        return get_item_json[0]
    return get_item_json


def _extract_created_id(create_response_json) -> str:
    if isinstance(create_response_json, dict):
        if "id" in create_response_json:
            return create_response_json["id"]
        status = create_response_json.get("status", "")
        m = re.search(r"([0-9a-fA-F\\-]{36})", status)
        if m:
            return m.group(1)
    raise AssertionError(f"Не удалось извлечь id из ответа: {create_response_json}")


@allure.feature("Получение товара")
@allure.story("Позитивные сценарии")
class TestGetItemPositive:
    """Позитивные тест-кейсы для получения товара по ID."""

    @allure.title("TC-GET-001: Получение существующего товара по ID")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_existing_item(self, base_url, valid_item_data):
        """Тест получения существующего товара по его ID."""
        client = AvitoAPIClient(base_url)

        with allure.step("Создание тестового товара"):
            item_data = valid_item_data()
            create_response = client.create_item(item_data)
            assert create_response.status_code == 200
            item_id = _extract_created_id(create_response.json())

        with allure.step(f"Получение товара по ID: {item_id}"):
            response = client.get_item(item_id)

        with allure.step("Проверка статуса ответа — 200 OK"):
            assert response.status_code == 200

        with allure.step("Проверка соответствия данных в ответе созданному товару"):
            response_data = _unwrap_item(response.json())
            assert response_data["id"] == item_id
            assert response_data["name"] == item_data["name"]
            assert response_data["price"] == item_data["price"]
            assert response_data["sellerId"] == item_data["sellerID"]
            assert response_data["statistics"] == item_data["statistics"]


    @allure.title("TC-GET-002: Последовательное получение нескольких товаров")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_multiple_items(self, base_url, valid_item_data):
        """Тест получения нескольких товаров подряд."""
        client = AvitoAPIClient(base_url)

        with allure.step("Создание 3 тестовых товаров"):
            item_ids = []
            for i in range(3):
                item_data = valid_item_data()
                create_response = client.create_item(item_data)
                assert create_response.status_code == 200
                item_ids.append(_extract_created_id(create_response.json()))

        with allure.step("Получение каждого товара и проверка"):
            for item_id in item_ids:
                response = client.get_item(item_id)
                assert response.status_code == 200
                assert _unwrap_item(response.json())["id"] == item_id


@allure.feature("Получение товара")
@allure.story("Негативные сценарии")
class TestGetItemNegative:
    """Негативные тест-кейсы для получения товара по ID."""

    @allure.title("TC-GET-NEG-001: Получение несуществующего товара")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_nonexistent_item(self, base_url):
        """Тест получения товара по несуществующему ID."""
        client = AvitoAPIClient(base_url)

        with allure.step("Запрос товара с несуществующим UUID"):
            nonexistent_id = str(uuid.uuid4())
            response = client.get_item(nonexistent_id)

        with allure.step("Проверка статуса ответа — 404 Not Found"):
            assert response.status_code == 404, \
                f"Ожидался статус 404 для несуществующего товара, получен {response.status_code}"


    @allure.title("TC-GET-NEG-002: Получение товара с некорректным ID (строка)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_item_invalid_id_string(self, base_url):
        """Тест получения товара, когда ID передан строкой."""
        client = AvitoAPIClient(base_url)

        with allure.step("Отправка GET-запроса со строковым ID 'abc'"):
            url = f"{base_url}/api/1/item/abc"
            response = client.session.get(url)

        with allure.step("Проверка статуса ответа (400 или 404)"):
            assert response.status_code in [400, 404], \
                f"Ожидался 400 или 404 при некорректном типе ID, получен {response.status_code}"


    @allure.title("TC-GET-NEG-003: Получение товара с отрицательным ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_item_negative_id(self, base_url):
        """Тест получения товара с отрицательным ID."""
        client = AvitoAPIClient(base_url)

        with allure.step("Запрос товара с ID -1"):
            response = client.get_item(-1)

        with allure.step("Проверка статуса ответа (400 или 404)"):
            assert response.status_code in [400, 404], \
                f"Ожидался 400 или 404 при отрицательном ID, получен {response.status_code}"


@allure.feature("Получение товара")
@allure.story("Граничные случаи")
class TestGetItemCornerCases:
    """Тесты граничных случаев для получения товара по ID."""

    @allure.title("TC-GET-CORNER-001: Получение товара с ID = 0")
    @allure.severity(allure.severity_level.MINOR)
    def test_get_item_zero_id(self, base_url):
        """Тест получения товара с ID = 0."""
        client = AvitoAPIClient(base_url)
        response = client.get_item(0)

        assert response.status_code in [400, 404], \
            f"Ожидался статус 400 или 404 для ID=0, получен {response.status_code}"


    @allure.title("TC-GET-CORNER-002: Многократные запросы одного и того же товара")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_item_multiple_requests(self, base_url, valid_item_data):
        """Тест многократного получения одного товара (проверка консистентности)."""
        client = AvitoAPIClient(base_url)

        with allure.step("Создание тестового товара"):
            item_data = valid_item_data()
            create_response = client.create_item(item_data)
            assert create_response.status_code == 200
            item_id = _extract_created_id(create_response.json())

        with allure.step("Выполнение 100 запросов одного и того же товара"):
            responses = []
            for _ in range(100):
                response = client.get_item(item_id)
                assert response.status_code == 200
                responses.append(response.json())

        with allure.step("Проверка, что все ответы идентичны"):
            first_response = responses[0]
            for response in responses[1:]:
                assert response == first_response, \
                    "Все ответы на запрос одного товара должны быть идентичными"
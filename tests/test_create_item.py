"""Тесты для эндпоинта POST /item — Создание товара."""
import allure
import pytest
import uuid
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


def _unwrap_item(get_item_json):
    # API возвращает список с одним объектом
    if isinstance(get_item_json, list):
        assert len(get_item_json) >= 1
        return get_item_json[0]
    return get_item_json


@allure.feature("Создание товара")
@allure.story("Позитивные сценарии")
class TestCreateItemPositive:
    """Позитивные тест-кейсы для создания товара."""

    @allure.title("TC-CREATE-001: Создание товара с валидными данными")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_valid_data(self, base_url, valid_item_data):
        """Тест создания товара с корректными данными."""
        with allure.step("Подготовка тестовых данных"):
            client = AvitoAPIClient(base_url)
            item_data = valid_item_data()

        with allure.step(f"Отправка POST-запроса на /item с данными: {item_data}"):
            response = client.create_item(item_data)

        with allure.step("Проверка статуса ответа — 200 OK"):
            assert response.status_code in  [200, 201], \
                f"Ожидался статус 200, получен {response.status_code}"

        with allure.step("Проверка контракта ответа (id и поля в теле ответа)"):
            pytest.xfail("BUG-001: POST /api/1/item не возвращает объект объявления, только status строку")
            response_data = response.json()
            assert "id" in response_data
            uuid.UUID(response_data["id"])
            assert response_data["name"] == item_data["name"]
            assert response_data["price"] == item_data["price"]
            assert response_data["sellerId"] == item_data["sellerID"]
            assert response_data["statistics"] == item_data["statistics"]

        # Примечание: фактическая проверка данных происходит в других тестах через GET,
        # т.к. текущий сервис не соответствует контракту ответа create.


    @allure.title("TC-CREATE-002: Создание товара с минимальной ценой (0)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_minimum_price(self, base_url, valid_item_data):
        """Тест создания товара с ценой = 0."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["price"] = 0

        with allure.step("Отправка запроса с ценой = 0"):
            response = client.create_item(item_data)

        pytest.xfail("BUG-002: price=0 отклоняется как 'поле price обязательно'")
        assert response.status_code == 200


    @allure.title("TC-CREATE-003: Создание товара с максимальной ценой")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_maximum_price(self, base_url, valid_item_data):
        """Тест создания товара с очень большой ценой."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["price"] = 999999999

        with allure.step("Отправка запроса с price = 999999999"):
            response = client.create_item(item_data)

        assert response.status_code == 200
        item_id = _extract_created_id(response.json())
        get_response = client.get_item(item_id)
        assert get_response.status_code == 200
        created_item = _unwrap_item(get_response.json())
        assert created_item["price"] == 999999999


    @allure.title("TC-CREATE-004: Создание товара с минимальным sellerId")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_minimum_seller_id(self, base_url, valid_item_data):
        """Тест создания товара с sellerId = 111111."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["sellerID"] = 111111

        response = client.create_item(item_data)
        assert response.status_code == 200
        item_id = _extract_created_id(response.json())
        get_response = client.get_item(item_id)
        assert get_response.status_code == 200
        created_item = _unwrap_item(get_response.json())
        assert created_item["sellerId"] == 111111


    @allure.title("TC-CREATE-005: Создание товара с максимальным sellerId")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_maximum_seller_id(self, base_url, valid_item_data):
        """Тест создания товара с sellerId = 999999."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["sellerID"] = 999999

        response = client.create_item(item_data)
        assert response.status_code == 200
        item_id = _extract_created_id(response.json())
        get_response = client.get_item(item_id)
        assert get_response.status_code == 200
        created_item = _unwrap_item(get_response.json())
        assert created_item["sellerId"] == 999999


    @allure.title("TC-CREATE-006: Создание товара с нулевой статистикой")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_zero_statistics(self, base_url, valid_item_data):
        """Тест создания товара с нулевыми значениями статистики."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["statistics"] = {"contacts": 0, "likes": 0, "viewCount": 0}

        response = client.create_item(item_data)
        pytest.xfail("BUG-003: нулевая statistics отклоняется как 'поле likes обязательно'")
        assert response.status_code == 200


    @allure.title("TC-CREATE-007: Создание товара с положительной статистикой")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_positive_statistics(self, base_url, valid_item_data):
        """Тест создания товара с положительными значениями статистики."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["statistics"] = {"contacts": 100, "likes": 50, "viewCount": 1000}

        response = client.create_item(item_data)
        assert response.status_code == 200
        item_id = _extract_created_id(response.json())
        get_response = client.get_item(item_id)
        assert get_response.status_code == 200
        created_item = _unwrap_item(get_response.json())
        stats = created_item["statistics"]
        assert stats["contacts"] == 100
        assert stats["likes"] == 50
        assert stats["viewCount"] == 1000


@allure.feature("Создание товара")
@allure.story("Негативные сценарии")
class TestCreateItemNegative:
    """Негативные тест-кейсы для создания товара."""

    @allure.title("TC-CREATE-NEG-001: Создание товара без поля name")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_without_name(self, base_url, valid_item_data):
        """Тест создания товара без поля name."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        del item_data["name"]

        with allure.step("Отправка запроса без поля 'name'"):
            response = client.create_item(item_data)

        assert response.status_code == 400, \
            f"Ожидался статус 400, получен {response.status_code}"


    @allure.title("TC-CREATE-NEG-002: Создание товара без поля price")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_without_price(self, base_url, valid_item_data):
        """Тест создания товара без поля price."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        del item_data["price"]

        response = client.create_item(item_data)
        assert response.status_code == 400, \
            f"Ожидался статус 400, получен {response.status_code}"


    @allure.title("TC-CREATE-NEG-003: Создание товара без поля sellerId")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_without_seller_id(self, base_url, valid_item_data):
        """Тест создания товара без поля sellerId."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        del item_data["sellerID"]

        response = client.create_item(item_data)
        assert response.status_code == 400, \
            f"Ожидался статус 400, получен {response.status_code}"


    @allure.title("TC-CREATE-NEG-004: Создание товара с отрицательной ценой")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_negative_price(self, base_url, valid_item_data):
        """Тест создания товара с отрицательной ценой."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["price"] = -1000

        response = client.create_item(item_data)
        pytest.xfail("BUG-004: price<0 принимается, ожидался 400")
        assert response.status_code == 400


    @allure.title("TC-CREATE-NEG-005: Создание товара с некорректным типом price (строка)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_invalid_price_type(self, base_url, valid_item_data):
        """Тест создания товара, где price — строка вместо числа."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["price"] = "тысяча"

        response = client.create_item(item_data)
        assert response.status_code == 400, \
            f"Ожидался статус 400 при некорректном типе price, получен {response.status_code}"


    @allure.title("TC-CREATE-NEG-006: Создание товара с некорректным типом sellerId (строка)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_invalid_seller_id_type(self, base_url, valid_item_data):
        """Тест создания товара, где sellerId — строка вместо числа."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["sellerID"] = "abc123"

        response = client.create_item(item_data)
        assert response.status_code == 400, \
            f"Ожидался статус 400 при некорректном типе sellerId, получен {response.status_code}"


    @allure.title("TC-CREATE-NEG-007: Создание товара с пустым именем")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_empty_name(self, base_url, valid_item_data):
        """Тест создания товара с пустой строкой в поле name."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["name"] = ""

        response = client.create_item(item_data)
        assert response.status_code == 400, \
            f"Ожидался статус 400 при пустом имени, получен {response.status_code}"


    @allure.title("TC-CREATE-NEG-008: Создание товара с отрицательными значениями статистики")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_negative_statistics(self, base_url, valid_item_data):
        """Тест создания товара с отрицательной статистикой."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["statistics"]["contacts"] = -10

        response = client.create_item(item_data)
        pytest.xfail("BUG-005: отрицательная statistics принимается, ожидался 400")
        assert response.status_code == 400


    @allure.title("TC-CREATE-NEG-009: Создание товара с пустым телом запроса")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_empty_body(self, base_url):
        """Тест создания товара с пустым телом запроса."""
        client = AvitoAPIClient(base_url)

        response = client.create_item({})
        assert response.status_code == 400, \
            f"Ожидался статус 400 при пустом теле, получен {response.status_code}"


@allure.feature("Создание товара")
@allure.story("Граничные случаи")
class TestCreateItemCornerCases:
    """Тесты граничных случаев при создании товара."""

    @allure.title("TC-CREATE-CORNER-001: Идемпотентность — множественные одинаковые запросы")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_item_idempotency(self, base_url, valid_item_data):
        """Проверка, что одинаковые запросы создают разные товары."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()

        with allure.step("Создание первого товара"):
            response1 = client.create_item(item_data)
            assert response1.status_code == 200
            item1_id = _extract_created_id(response1.json())

        with allure.step("Создание второго идентичного товара"):
            response2 = client.create_item(item_data)
            assert response2.status_code == 200
            item2_id = _extract_created_id(response2.json())

        with allure.step("Проверка, что ID товаров отличаются"):
            assert item1_id != item2_id, \
                "Одинаковые запросы должны создавать товары с разными ID"

        with allure.step("Проверка совпадения данных (кроме ID)"):
            item1 = _unwrap_item(client.get_item(item1_id).json())
            item2 = _unwrap_item(client.get_item(item2_id).json())
            assert item1["name"] == item2["name"]
            assert item1["price"] == item2["price"]
            assert item1["sellerId"] == item2["sellerId"]


    @allure.title("TC-CREATE-CORNER-002: Создание товара с очень длинным названием")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_very_long_name(self, base_url, valid_item_data):
        """Тест создания товара с названием длиной 10000 символов."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["name"] = "A" * 10000

        response = client.create_item(item_data)
        # Может как принять (200), так и отклонить (400)
        assert response.status_code in [200, 400], \
            f"Ожидался 200 или 400, получен {response.status_code}"


    @allure.title("TC-CREATE-CORNER-003: Создание товара со специальными символами в названии")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_special_characters(self, base_url, valid_item_data):
        """Тест создания товара со спецсимволами в названии."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["name"] = "!@#$%^&*()_+<>?:{}[]|\\"

        response = client.create_item(item_data)
        assert response.status_code == 200
        item_id = _extract_created_id(response.json())
        get_response = client.get_item(item_id)
        assert get_response.status_code == 200
        created_item = _unwrap_item(get_response.json())
        assert created_item["name"] == item_data["name"]


    @allure.title("TC-CREATE-CORNER-004: Создание товара с Unicode-символами и эмодзи")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_item_unicode_characters(self, base_url, valid_item_data):
        """Тест создания товара с Unicode, включая эмодзи и иероглифы."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["name"] = "Товар 🎉 emoji тест 中文 русский"

        response = client.create_item(item_data)
        assert response.status_code == 200
        item_id = _extract_created_id(response.json())
        get_response = client.get_item(item_id)
        assert get_response.status_code == 200
        created_item = _unwrap_item(get_response.json())
        assert created_item["name"] == item_data["name"]


    @allure.title("TC-CREATE-CORNER-005: Создание товара с максимальными значениями статистики")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_item_max_statistics(self, base_url, valid_item_data):
        """Тест создания товара с максимальными значениями статистики (int32 max)."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()
        item_data["statistics"] = {
            "contacts": 2147483647,
            "likes": 2147483647,
            "viewCount": 2147483647
        }

        response = client.create_item(item_data)
        assert response.status_code == 200
        item_id = _extract_created_id(response.json())
        get_response = client.get_item(item_id)
        assert get_response.status_code == 200
        created_item = _unwrap_item(get_response.json())
        stats = created_item["statistics"]
        assert stats["viewCount"] == 2147483647
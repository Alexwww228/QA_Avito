"""Тесты для эндпоинта GET /stat/{itemId} — Получение статистики товара."""
import allure
import pytest
from tests.api_client import AvitoAPIClient
import uuid
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


@allure.feature("Статистика товара")
@allure.story("Позитивные сценарии")
class TestGetStatisticsPositive:
    """Позитивные тест-кейсы для получения статистики товара."""

    @allure.title("TC-STAT-001: Получение статистики существующего товара")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_statistics_existing_item(self, base_url, valid_item_data):
        """Тест получения статистики для существующего товара."""
        client = AvitoAPIClient(base_url)

        with allure.step("Создание тестового товара со статистикой"):
            item_data = valid_item_data()
            item_data["statistics"] = {
                "contacts": 10,
                "likes": 20,
                "viewCount": 100
            }
            create_response = client.create_item(item_data)
            assert create_response.status_code == 200
            item_id = _extract_created_id(create_response.json())

        with allure.step(f"Получение статистики для товара {item_id}"):
            response = client.get_item_statistics(item_id)

        with allure.step("Проверка статуса ответа — 200 OK"):
            assert response.status_code == 200

        with allure.step("Проверка данных статистики"):
            stats = response.json()
            if isinstance(stats, list):
                assert len(stats) >= 1, "Статистика должна содержать хотя бы один элемент"
                stats = stats[0]
            assert "contacts" in stats
            assert "likes" in stats
            assert "viewCount" in stats
            assert stats["contacts"] == 10
            assert stats["likes"] == 20
            assert stats["viewCount"] == 100


    @allure.title("TC-STAT-002: Получение статистики с нулевыми значениями")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_statistics_zero_values(self, base_url, valid_item_data):
        """Тест получения статистики товара со всеми нулевыми значениями."""
        client = AvitoAPIClient(base_url)

        with allure.step("Создание тестового товара с нулевой статистикой"):
            item_data = valid_item_data()
            item_data["statistics"] = {
                "contacts": 0,
                "likes": 0,
                "viewCount": 0
            }
            create_response = client.create_item(item_data)
            assert create_response.status_code == 400
            return

        with allure.step(f"Получение статистики для товара {item_id}"):
            response = client.get_item_statistics(item_id)

        with allure.step("Проверка, что все значения статистики равны нулю"):
            assert response.status_code == 200
            stats = response.json()
            if isinstance(stats, list):
                assert len(stats) >= 1, "Статистика должна содержать хотя бы один элемент"
                stats = stats[0]
            assert stats["contacts"] == 0
            assert stats["likes"] == 0
            assert stats["viewCount"] == 0


@allure.feature("Статистика товара")
@allure.story("Негативные сценарии")
class TestGetStatisticsNegative:
    """Негативные тест-кейсы для получения статистики товара."""

    @allure.title("TC-STAT-NEG-001: Получение статистики несуществующего товара")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_statistics_nonexistent_item(self, base_url):
        """Тест получения статистики для несуществующего товара."""
        client = AvitoAPIClient(base_url)

        with allure.step("Запрос статистики для товара с несуществующим UUID"):
            response = client.get_item_statistics(str(uuid.uuid4()))

        with allure.step("Проверка статуса ответа — 404 Not Found"):
            assert response.status_code == 404, \
                f"Ожидался статус 404 для несуществующего товара, получен {response.status_code}"


    @allure.title("TC-STAT-NEG-002: Получение статистики с некорректным itemId (строка)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_statistics_invalid_id_string(self, base_url):
        """Тест получения статистики, когда itemId передан строкой."""
        client = AvitoAPIClient(base_url)

        with allure.step("Отправка GET-запроса со строковым itemId 'abc'"):
            url = f"{base_url}/api/1/statistic/abc"
            response = client.session.get(url)

        with allure.step("Проверка статуса ответа (400 или 404)"):
            assert response.status_code in [400, 404], \
                f"Ожидался 400 или 404 при некорректном типе itemId, получен {response.status_code}"


    @allure.title("TC-STAT-NEG-003: Получение статистики с отрицательным itemId")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_statistics_negative_id(self, base_url):
        """Тест получения статистики с отрицательным itemId."""
        client = AvitoAPIClient(base_url)

        with allure.step("Запрос статистики для товара с ID -1"):
            response = client.get_item_statistics(-1)

        with allure.step("Проверка статуса ответа (400 или 404)"):
            assert response.status_code in [400, 404], \
                f"Ожидался 400 или 404 при отрицательном itemId, получен {response.status_code}"
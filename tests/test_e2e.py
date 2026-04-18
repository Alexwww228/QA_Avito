"""E2E-тесты для Avito API."""
import allure
import pytest
from tests.api_client import AvitoAPIClient
import re


@allure.feature("E2E-сценарии")
@allure.story("Полный жизненный цикл товара")
class TestE2EScenarios:
    """End-to-end тесты сценариев."""

    @allure.title("TC-E2E-001: Полный жизненный цикл товара")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_complete_item_lifecycle(self, base_url, valid_item_data, generate_seller_id):
        """Тест полного жизненного цикла товара: создание → получение → по продавцу → статистика."""
        client = AvitoAPIClient(base_url)
        seller_id = generate_seller_id()

        with allure.step("Шаг 1: Создание нового товара"):
            item_data = valid_item_data(seller_id)
            item_data["statistics"] = {
                "contacts": 5,
                "likes": 10,
                "viewCount": 50
            }
            create_response = client.create_item(item_data)
            assert create_response.status_code == 200, \
                f"Не удалось создать товар: {create_response.status_code}"

            created_item = create_response.json()
            m = re.search(r"([0-9a-fA-F\\-]{36})", created_item.get("status", ""))
            assert m, f"Не удалось извлечь id из ответа: {created_item}"
            item_id = m.group(1)
            allure.attach(str(item_id), name="Созданный ID товара", attachment_type=allure.attachment_type.TEXT)

        with allure.step("Шаг 2: Получение созданного товара по ID"):
            get_response = client.get_item(item_id)
            assert get_response.status_code == 200, \
                f"Не удалось получить товар: {get_response.status_code}"

            retrieved_json = get_response.json()
            retrieved_item = retrieved_json[0] if isinstance(retrieved_json, list) else retrieved_json
            assert retrieved_item["id"] == item_id
            assert retrieved_item["name"] == item_data["name"]
            assert retrieved_item["price"] == item_data["price"]
            assert retrieved_item["sellerId"] == seller_id

        with allure.step("Шаг 3: Получение всех товаров продавца по sellerId"):
            seller_response = client.get_items_by_seller(seller_id)
            assert seller_response.status_code == 200, \
                f"Не удалось получить товары продавца: {seller_response.status_code}"

            seller_items = seller_response.json()
            assert isinstance(seller_items, list)

            # Ищем наш товар в списке
            our_item = next((item for item in seller_items if item["id"] == item_id), None)
            assert our_item is not None, f"Созданный товар {item_id} не найден в списке товаров продавца"
            assert our_item["sellerId"] == seller_id

        with allure.step("Шаг 4: Получение статистики товара"):
            stats_response = client.get_item_statistics(item_id)
            assert stats_response.status_code == 200, \
                f"Не удалось получить статистику: {stats_response.status_code}"

            statistics = stats_response.json()
            if isinstance(statistics, list):
                assert len(statistics) >= 1, "Статистика должна содержать хотя бы один элемент"
                statistics = statistics[0]
            assert statistics["contacts"] == 5
            assert statistics["likes"] == 10
            assert statistics["viewCount"] == 50

        with allure.step("Проверка согласованности данных между всеми эндпоинтами"):
            assert retrieved_item["name"] == our_item["name"]
            assert retrieved_item["price"] == our_item["price"]
            assert retrieved_item["statistics"] == statistics


    @allure.title("TC-E2E-002: Несколько товаров у одного продавца")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_multiple_items_same_seller(self, base_url, valid_item_data, generate_seller_id):
        """Тест создания нескольких товаров у одного продавца и их получение."""
        client = AvitoAPIClient(base_url)
        seller_id = generate_seller_id()
        created_items = []

        with allure.step(f"Создание 3 товаров для продавца {seller_id}"):
            for i in range(3):
                item_data = valid_item_data(seller_id)
                item_data["name"] = f"Товар {i+1} для продавца {seller_id}"
                item_data["price"] = 1000 * (i + 1)

                create_response = client.create_item(item_data)
                assert create_response.status_code == 200

                created_json = create_response.json()
                m = re.search(r"([0-9a-fA-F\\-]{36})", created_json.get("status", ""))
                assert m, f"Не удалось извлечь id из ответа: {created_json}"
                created_item = {"id": m.group(1), "name": item_data["name"], "price": item_data["price"]}
                created_items.append(created_item)
                allure.attach(
                    str(created_item["id"]),
                    name=f"ID товара {i+1}",
                    attachment_type=allure.attachment_type.TEXT
                )

        with allure.step("Проверка уникальности ID товаров"):
            item_ids = [item["id"] for item in created_items]
            assert len(item_ids) == len(set(item_ids)), "Все ID товаров должны быть уникальными"

        with allure.step("Получение всех товаров продавца"):
            seller_response = client.get_items_by_seller(seller_id)
            assert seller_response.status_code == 200

            seller_items = seller_response.json()
            seller_item_ids = [item["id"] for item in seller_items]

        with allure.step("Проверка, что все созданные товары присутствуют в списке продавца"):
            for created_item in created_items:
                assert created_item["id"] in seller_item_ids, \
                    f"Товар {created_item['id']} не найден в списке товаров продавца"

        with allure.step("Проверка каждого товара индивидуально"):
            for created_item in created_items:
                get_response = client.get_item(created_item["id"])
                assert get_response.status_code == 200

                retrieved_json = get_response.json()
                retrieved_item = retrieved_json[0] if isinstance(retrieved_json, list) else retrieved_json
                assert retrieved_item["id"] == created_item["id"]
                assert retrieved_item["name"] == created_item["name"]
                assert retrieved_item["sellerId"] == seller_id


    @allure.title("TC-E2E-003: Товары разных продавцов не пересекаются")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_different_sellers_isolation(self, base_url, valid_item_data, generate_seller_id):
        """Тест изоляции товаров между разными продавцами."""
        client = AvitoAPIClient(base_url)

        seller_id_1 = generate_seller_id()
        seller_id_2 = generate_seller_id()

        # Гарантируем, что seller ID разные
        while seller_id_1 == seller_id_2:
            seller_id_2 = generate_seller_id()

        with allure.step(f"Создание товара для продавца 1 (ID: {seller_id_1})"):
            item_data_1 = valid_item_data(seller_id_1)
            create_response_1 = client.create_item(item_data_1)
            assert create_response_1.status_code == 200
            created_1 = create_response_1.json()
            m1 = re.search(r"([0-9a-fA-F\\-]{36})", created_1.get("status", ""))
            assert m1, f"Не удалось извлечь id из ответа: {created_1}"
            item_id_1 = m1.group(1)

        with allure.step(f"Создание товара для продавца 2 (ID: {seller_id_2})"):
            item_data_2 = valid_item_data(seller_id_2)
            create_response_2 = client.create_item(item_data_2)
            assert create_response_2.status_code == 200
            created_2 = create_response_2.json()
            m2 = re.search(r"([0-9a-fA-F\\-]{36})", created_2.get("status", ""))
            assert m2, f"Не удалось извлечь id из ответа: {created_2}"
            item_id_2 = m2.group(1)

        with allure.step("Получение товаров продавца 1"):
            seller_1_response = client.get_items_by_seller(seller_id_1)
            assert seller_1_response.status_code == 200
            seller_1_items = seller_1_response.json()
            seller_1_item_ids = [item["id"] for item in seller_1_items]

        with allure.step("Получение товаров продавца 2"):
            seller_2_response = client.get_items_by_seller(seller_id_2)
            assert seller_2_response.status_code == 200
            seller_2_items = seller_2_response.json()
            seller_2_item_ids = [item["id"] for item in seller_2_items]

        with allure.step("Проверка, что товар продавца 1 находится в его списке"):
            assert item_id_1 in seller_1_item_ids, \
                f"Товар продавца 1 ({item_id_1}) не найден в его товарах"

        with allure.step("Проверка, что товар продавца 2 находится в его списке"):
            assert item_id_2 in seller_2_item_ids, \
                f"Товар продавца 2 ({item_id_2}) не найден в его товарах"

        with allure.step("Проверка, что товар продавца 1 НЕ попадает в список продавца 2"):
            assert item_id_1 not in seller_2_item_ids, \
                f"Товар продавца 1 ({item_id_1}) ошибочно найден в товарах продавца 2"

        with allure.step("Проверка, что товар продавца 2 НЕ попадает в список продавца 1"):
            assert item_id_2 not in seller_1_item_ids, \
                f"Товар продавца 2 ({item_id_2}) ошибочно найден в товарах продавца 1"


    @allure.title("TC-E2E-004: Создание товара и проверка согласованности статистики")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_statistics_consistency(self, base_url, valid_item_data):
        """Тест согласованности статистики между разными эндпоинтами."""
        client = AvitoAPIClient(base_url)

        with allure.step("Создание товара с заданной статистикой"):
            item_data = valid_item_data()
            item_data["statistics"] = {
                "contacts": 15,
                "likes": 25,
                "viewCount": 150
            }
            create_response = client.create_item(item_data)
            assert create_response.status_code == 200
            created = create_response.json()
            m = re.search(r"([0-9a-fA-F\\-]{36})", created.get("status", ""))
            assert m, f"Не удалось извлечь id из ответа: {created}"
            item_id = m.group(1)

        with allure.step("Получение статистики через /stat эндпоинт"):
            stats_response = client.get_item_statistics(item_id)
            assert stats_response.status_code == 200
            stat_endpoint_data = stats_response.json()
            if isinstance(stat_endpoint_data, list):
                assert len(stat_endpoint_data) >= 1, "Статистика должна содержать хотя бы один элемент"
                stat_endpoint_data = stat_endpoint_data[0]

        with allure.step("Получение статистики через /item эндпоинт"):
            item_response = client.get_item(item_id)
            assert item_response.status_code == 200
            item_json = item_response.json()
            item_data_obj = item_json[0] if isinstance(item_json, list) else item_json
            item_endpoint_data = item_data_obj["statistics"]

        with allure.step("Проверка совпадения статистики из обоих эндпоинтов"):
            assert stat_endpoint_data == item_endpoint_data, \
                "Статистика из /stat и /item эндпоинтов должна совпадать"
            assert stat_endpoint_data["contacts"] == 15
            assert stat_endpoint_data["likes"] == 25
            assert stat_endpoint_data["viewCount"] == 150
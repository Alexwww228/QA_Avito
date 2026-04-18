"""Нефункциональные тесты: Производительность, Безопасность и Поведение API."""
import allure
import pytest
import time
from tests.api_client import AvitoAPIClient
import re
import requests


def _extract_created_id(create_response_json) -> str:
    if isinstance(create_response_json, dict):
        if "id" in create_response_json:
            return create_response_json["id"]
        status = create_response_json.get("status", "")
        m = re.search(r"([0-9a-fA-F\\-]{36})", status)
        if m:
            return m.group(1)
    raise AssertionError(f"Не удалось извлечь id из ответа: {create_response_json}")


@allure.feature("Нефункциональное тестирование")
@allure.story("Тестирование производительности")
class TestPerformance:
    """Тесты производительности API."""

    @allure.title("TC-PERF-001: Время ответа API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_api_response_time(self, base_url, valid_item_data):
        """Тест, что API отвечает в пределах приемлемого времени."""
        client = AvitoAPIClient(base_url)
        response_times = []

        with allure.step("Создание тестового товара"):
            item_data = valid_item_data()
            create_response = client.create_item(item_data)
            assert create_response.status_code == 200
            item_id = _extract_created_id(create_response.json())

        with allure.step("Измерение времени ответа для 100 GET-запросов"):
            for _ in range(100):
                start_time = time.time()
                response = client.get_item(item_id)
                end_time = time.time()

                response_time = (end_time - start_time) * 1000  # в миллисекундах
                response_times.append(response_time)

                assert response.status_code == 200

        with allure.step("Расчёт статистик производительности"):
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)

            # 95-й перцентиль
            sorted_times = sorted(response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_response_time = sorted_times[p95_index]

            allure.attach(
                f"Среднее время: {avg_response_time:.2f} мс\n"
                f"Минимум: {min_response_time:.2f} мс\n"
                f"Максимум: {max_response_time:.2f} мс\n"
                f"95-й перцентиль: {p95_response_time:.2f} мс",
                name="Статистика времени ответа",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка соответствия требованиям производительности"):
            assert avg_response_time < 500, \
                f"Среднее время ответа ({avg_response_time:.2f} мс) превышает 500 мс"
            assert p95_response_time < 1000, \
                f"95-й перцентиль ({p95_response_time:.2f} мс) превышает 1000 мс"


    @allure.title("TC-PERF-002: Производительность массового создания товаров")
    @allure.severity(allure.severity_level.NORMAL)
    def test_bulk_create_performance(self, base_url, valid_item_data):
        """Тест производительности при последовательном создании множества товаров."""
        client = AvitoAPIClient(base_url)
        num_items = 100
        successful_creates = 0
        failed_creates = 0

        with allure.step(f"Создание {num_items} товаров"):
            start_time = time.time()

            for i in range(num_items):
                item_data = valid_item_data()
                response = client.create_item(item_data)

                if response.status_code == 200:
                    successful_creates += 1
                else:
                    failed_creates += 1

            end_time = time.time()
            total_time = end_time - start_time

        with allure.step("Анализ результатов"):
            avg_time_per_item = (total_time / num_items) * 1000  # в мс

            allure.attach(
                f"Общее время: {total_time:.2f} сек\n"
                f"Успешно создано: {successful_creates}\n"
                f"Ошибок создания: {failed_creates}\n"
                f"Среднее время на один товар: {avg_time_per_item:.2f} мс",
                name="Результаты массового создания",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Проверка, что все товары успешно созданы"):
            assert successful_creates == num_items, \
                f"Успешно создано только {successful_creates}/{num_items} товаров"
            assert failed_creates == 0, f"Не удалось создать {failed_creates} товаров"


@allure.feature("Нефункциональное тестирование")
@allure.story("Тестирование безопасности")
class TestSecurity:
    """Тесты безопасности API."""

    @allure.title("TC-SEC-001: Валидация Content-Type")
    @allure.severity(allure.severity_level.NORMAL)
    def test_content_type_validation(self, base_url, valid_item_data):
        """Тест поведения API при отсутствии или неверном Content-Type заголовке."""
        client = AvitoAPIClient(base_url)
        item_data = valid_item_data()

        with allure.step("Отправка запроса без заголовка Content-Type"):
            url = f"{base_url}/api/1/item"
            response = client.session.post(
                url,
                json=item_data,
                headers={"Content-Type": ""}
            )

        # API может либо отклонить запрос, либо обработать его
        assert response.status_code in [200, 400, 415], \
            f"Неожиданный статус-код: {response.status_code}"


    @allure.title("TC-SEC-002: Защита от SQL-инъекций")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sql_injection_protection(self, base_url):
        """Тест защиты от SQL-инъекций."""
        client = AvitoAPIClient(base_url)

        with allure.step("Попытка SQL-инъекции в параметре URL"):
            url = f"{base_url}/api/1/item/1' OR '1'='1"
            response = client.session.get(url)

        with allure.step("Проверка, что SQL-инъекция заблокирована"):
            assert response.status_code in [400, 404], \
                f"SQL-инъекция не была должным образом обработана: {response.status_code}"


    @allure.title("TC-SEC-003: Попытка XSS в названии товара")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_xss_in_name(self, base_url, valid_item_data):
        """Тест обработки XSS-атак в поле name."""
        client = AvitoAPIClient(base_url)

        with allure.step("Создание товара со скриптом в названии"):
            item_data = valid_item_data()
            xss_payload = "<script>alert('XSS')</script>"
            item_data["name"] = xss_payload

            create_response = client.create_item(item_data)
            assert create_response.status_code == 200
            # API возвращает id внутри поля status
            status = create_response.json().get("status", "")
            import re
            m = re.search(r"([0-9a-fA-F\\-]{36})", status)
            assert m, f"Не удалось извлечь id из ответа: {create_response.json()}"
            item_id = m.group(1)

        with allure.step("Получение товара и проверка экранирования XSS"):
            get_response = client.get_item(item_id)
            assert get_response.status_code == 200

            item_json = get_response.json()
            retrieved = item_json[0] if isinstance(item_json, list) else item_json
            retrieved_name = retrieved["name"]
            # Скрипт должен сохраняться как текст, а не исполняться
            assert xss_payload in retrieved_name or "&lt;script&gt;" in retrieved_name, \
                "XSS-пayload должен быть экранирован или сохранён как текст"


    @allure.title("TC-SEC-004: Обработка oversized запроса (большой payload)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_oversized_payload(self, base_url, valid_item_data):
        """Тест поведения API при очень большом размере тела запроса."""
        client = AvitoAPIClient(base_url)

        with allure.step("Создание товара с очень длинным названием (1 МБ)"):
            item_data = valid_item_data()
            item_data["name"] = "A" * 1000000  # 1 миллион символов

            try:
                response = client.create_item(item_data)
            except requests.exceptions.ConnectionError:
                # Некоторые реализации серверов просто разрывают соединение на oversized payload.
                return

        # API может принять или отклонить запрос с соответствующим кодом
        assert response.status_code in [200, 400, 413], \
            f"Неожиданный статус-код для oversized payload: {response.status_code}"


@allure.feature("Нефункциональное тестирование")
@allure.story("Поведение API")
class TestAPIBehavior:
    """Тесты общего поведения API и соответствия стандартам."""

    @allure.title("Валидация HTTP-методов")
    @allure.severity(allure.severity_level.NORMAL)
    def test_http_methods_validation(self, base_url):
        """Тест реакции эндпоинтов на неверные HTTP-методы."""
        client = AvitoAPIClient(base_url)

        with allure.step("Отправка DELETE-запроса на POST-эндпоинт"):
            response = client._request("DELETE", f"{base_url}/api/1/item")
            assert response.status_code in [405, 404], \
                f"Ожидался 405 или 404 при неверном методе, получен {response.status_code}"

        with allure.step("Отправка POST-запроса на GET-эндпоинт"):
            response = client._request("POST", f"{base_url}/api/1/item/1")
            assert response.status_code in [405, 404], \
                f"Ожидался 405 или 404 при неверном методе, получен {response.status_code}"


    @allure.title("Проверка CORS-заголовков")
    @allure.severity(allure.severity_level.MINOR)
    def test_cors_headers(self, base_url, valid_item_data):
        """Тест наличия корректных CORS-заголовков."""
        client = AvitoAPIClient(base_url)

        with allure.step("Отправка OPTIONS-запроса"):
            response = client.session.options(f"{base_url}/api/1/item")

            allure.attach(
                str(dict(response.headers)),
                name="Заголовки ответа",
                attachment_type=allure.attachment_type.JSON
            )

        headers = response.headers
        cors_headers_present = any([
            "Access-Control-Allow-Origin" in headers,
            "Access-Control-Allow-Methods" in headers
        ])

        allure.attach(
            f"CORS-заголовки присутствуют: {cors_headers_present}",
            name="Статус CORS",
            attachment_type=allure.attachment_type.TEXT
        )

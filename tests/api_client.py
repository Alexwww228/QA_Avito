"""API клиент для Avito QA Internship."""
import requests
from typing import Dict, Any, Optional, List
import re
import time


class AvitoAPIClient:
    """Клиент для взаимодействия с Avito API."""

    def __init__(self, base_url: str):
        """Инициализация API клиента.

        Args:
            base_url: Базовый URL для API
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self._timeout_s = 20
        self._max_attempts = 4

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        last_exc = None
        for attempt in range(self._max_attempts):
            try:
                resp = self.session.request(method, url, timeout=self._timeout_s, **kwargs)
                # transient gateway/server issues
                if resp.status_code in {502, 503, 504}:
                    time.sleep(0.3 * (attempt + 1))
                    continue
                return resp
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as exc:
                last_exc = exc
                time.sleep(0.3 * (attempt + 1))
        if last_exc:
            raise last_exc
        return resp

    def create_item(self, item_data: Dict[str, Any]) -> requests.Response:
        """Создать новый товар.

        Args:
            item_data: Данные товара для создания

        Returns:
            Объект ответа
        """
        url = f"{self.base_url}/api/1/item"
        return self._request("POST", url, json=item_data)

    def get_item(self, item_id) -> requests.Response:
        """Получить товар по ID.

        Args:
            item_id: ID товара

        Returns:
            Объект ответа
        """
        url = f"{self.base_url}/api/1/item/{item_id}"
        return self._request("GET", url)

    def get_items_by_seller(self, seller_id: int) -> requests.Response:
        """Получить все товары продавца по ID продавца.

        Args:
            seller_id: ID продавца

        Returns:
            Объект ответа
        """
        url = f"{self.base_url}/api/1/{seller_id}/item"
        return self._request("GET", url)

    def get_item_statistics(self, item_id) -> requests.Response:
        """Получить статистику товара.

        Args:
            item_id: ID товара

        Returns:
            Объект ответа
        """
        url = f"{self.base_url}/api/1/statistic/{item_id}"
        return self._request("GET", url)

    def create_item_and_get_id(self, item_data: Dict[str, Any]) -> Optional[int]:
        """Вспомогательный метод: Создать товар и вернуть его ID.

        Args:
            item_data: Данные товара для создания

        Returns:
            ID товара или None, если создание не удалось
        """
        response = self.create_item(item_data)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                if "id" in data:
                    return data.get("id")
                status = data.get("status", "")
                m = re.search(r"([0-9a-fA-F\\-]{36})", status)
                if m:
                    return m.group(1)
        return None
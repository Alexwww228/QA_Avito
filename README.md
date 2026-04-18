## Структура
```bash
├── TESTCASES.md
├── README.md
├── BUGS.md
├── requirements.txt
├── test_api.py
├── pyproject.toml
├── .flake8
└── allure-results/
```

## Установка
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Линтер + форматтер
```bash
black .
flake8 .
```

## Запуск тестов
```bash
# Обычный
pytest tests/ -v

# С Allure
pytest tests/ --alluredir=allure-results
allure serve allure-results
```
Все тесты независимы, используют уникальный sellerID (111111–999999).

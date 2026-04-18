# Avito QA Internship - API Testing Project

Автоматизированное тестирование API микросервиса объявлений для стажировки QA в Avito.

## 📋 Содержание

- [Описание проекта](#описание-проекта)
- [Структура проекта](#структура-проекта)
- [Требования](#требования)
- [Установка](#установка)
- [Запуск тестов](#запуск-тестов)
- [Отчеты Allure](#отчеты-allure)
- [Линтеры и форматтеры](#линтеры-и-форматтеры)
- [Тест-кейсы](#тест-кейсы)
- [CI/CD](#cicd)

## 📖 Описание проекта

Проект содержит полный набор автоматизированных тестов для API микросервиса объявлений Avito, включающий:

- ✅ Позитивные сценарии
- ❌ Негативные сценарии
- 🔄 Корнер-кейсы (граничные значения, идемпотентность)
- 🔗 E2E тесты
- ⚡ Нефункциональные тесты (производительность, безопасность)

**API Endpoints:**
- `POST /item` - Создание объявления
- `GET /item/{id}` - Получение объявления по ID
- `GET /item/seller/{sellerId}` - Получение всех объявлений продавца
- `GET /stat/{itemId}` - Получение статистики объявления

**Host:** `https://qa-internship.avito.com`

## 📁 Структура проекта

```
.
├── tests/                          # Директория с тестами
│   ├── conftest.py                # Фикстуры pytest
│   ├── api_client.py              # API клиент
│   ├── test_create_item.py        # Тесты создания объявлений
│   ├── test_get_item.py           # Тесты получения объявления
│   ├── test_get_seller_items.py   # Тесты получения объявлений продавца
│   ├── test_statistics.py         # Тесты статистики
│   ├── test_e2e.py                # E2E тесты
│   └── test_nonfunctional.py      # Нефункциональные тесты
├── TESTCASES.md                   # Описание тест-кейсов
├── BUGS.md                        # Обнаруженные дефекты
├── README.md                      # Этот файл
├── requirements.txt               # Python зависимости
├── pytest.ini                     # Конфигурация pytest
├── pyproject.toml                 # Конфигурация black
├── .flake8                        # Конфигурация flake8
├── .pylintrc                      # Конфигурация pylint
└── .isort.cfg                     # Конфигурация isort
```

## 🛠 Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Доступ к интернету (для выполнения API запросов)

## 🚀 Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd avito-qa-internship
```

### 2. Создание виртуального окружения (рекомендуется)

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 🧪 Запуск тестов

### Запуск всех тестов

```bash
pytest
```

### Запуск с подробным выводом

```bash
pytest -v
```

### Запуск конкретного файла с тестами

```bash
pytest tests/test_create_item.py
```

### Запуск конкретного теста

```bash
pytest tests/test_create_item.py::TestCreateItemPositive::test_create_item_valid_data
```

### Запуск тестов по маркерам

```bash
# Только E2E тесты
pytest -m e2e

# Только тесты производительности
pytest -m performance

# Все тесты кроме медленных
pytest -m "not slow"
```

### Запуск с генерацией Allure отчета

```bash
pytest --alluredir=allure-results
```

### Параллельный запуск (ускоренный)

```bash
pip install pytest-xdist
pytest -n auto
```

## 📊 Отчеты Allure

### Установка Allure (если еще не установлен)

**macOS:**
```bash
brew install allure
```

**Linux:**
```bash
sudo apt-add-repository ppa:qameta/allure
sudo apt-get update
sudo apt-get install allure
```

**Windows:**
Скачайте с [GitHub Releases](https://github.com/allure-framework/allure2/releases)

### Генерация и открытие отчета

```bash
# Запуск тестов с сохранением результатов
pytest --alluredir=allure-results

# Генерация и открытие отчета
allure serve allure-results
```

### Генерация статического отчета

```bash
# Генерация отчета в директорию allure-report
allure generate allure-results -o allure-report --clean

# Открытие отчета
allure open allure-report
```

### Особенности Allure отчетов

- 📈 **Графики и статистика** - визуализация результатов
- 🏷️ **Группировка тестов** - по фичам и сторис
- 📝 **Шаги тестов** - детальная информация о каждом шаге
- 🔗 **История выполнения** - тренды и история
- 📎 **Вложения** - логи, скриншоты, JSON данные

## 🎨 Линтеры и форматтеры

Проект использует следующие инструменты для обеспечения качества кода:

### Black (форматтер кода)

```bash
# Проверка форматирования (без изменений)
black --check tests/

# Автоматическое форматирование
black tests/
```

### Flake8 (проверка стиля кода)

```bash
# Проверка всего проекта
flake8 tests/

# Проверка конкретного файла
flake8 tests/test_create_item.py
```

### Pylint (статический анализ)

```bash
# Анализ всего проекта
pylint tests/

# Анализ конкретного файла
pylint tests/test_create_item.py

# С оценкой (0-10)
pylint tests/ --score=y
```

### isort (сортировка импортов)

```bash
# Проверка порядка импортов
isort --check-only tests/

# Автоматическая сортировка
isort tests/
```

### Запуск всех проверок одной командой

```bash
# Создайте скрипт lint.sh
#!/bin/bash
echo "Running Black..."
black --check tests/

echo "Running isort..."
isort --check-only tests/

echo "Running Flake8..."
flake8 tests/

echo "Running Pylint..."
pylint tests/ --score=y

echo "All checks completed!"
```

```bash
chmod +x lint.sh
./lint.sh
```

### Автоматическое исправление проблем форматирования

```bash
# Автоматически исправить форматирование и импорты
black tests/ && isort tests/
```

## 📝 Тест-кейсы

Полное описание всех тест-кейсов находится в файле [TESTCASES.md](TESTCASES.md).

### Покрытие тестами:

- **Создание объявлений**: 25+ тест-кейсов
  - Позитивные: 7 тестов
  - Негативные: 10 тестов
  - Корнер-кейсы: 5 тестов

- **Получение объявления**: 10+ тест-кейсов
  - Позитивные: 2 теста
  - Негативные: 4 теста
  - Корнер-кейсы: 3 теста

- **Получение по продавцу**: 8+ тест-кейсов
  - Позитивные: 3 теста
  - Негативные: 3 теста
  - Корнер-кейсы: 1 тест

- **Статистика**: 6+ тест-кейсов
  - Позитивные: 2 теста
  - Негативные: 3 теста

- **E2E сценарии**: 4 теста
- **Нефункциональные**: 9 тестов (производительность, безопасность)

## 🐛 Обнаруженные дефекты

Все обнаруженные дефекты описаны в файле [BUGS.md](BUGS.md) со следующей информацией:

- Краткое описание
- Шаги воспроизведения
- Фактический результат
- Ожидаемый результат
- Серьезность (Critical/Major/Minor)
- Окружение

## 🔄 CI/CD

### GitHub Actions (пример конфигурации)

Создайте файл `.github/workflows/tests.yml`:

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run linters
      run: |
        black --check tests/
        flake8 tests/
        pylint tests/
    
    - name: Run tests
      run: |
        pytest --alluredir=allure-results
    
    - name: Generate Allure report
      uses: simple-elf/allure-report-action@master
      if: always()
      with:
        allure_results: allure-results
        allure_history: allure-history
```

## 📞 Контакты

При возникновении вопросов или обнаружении проблем, пожалуйста, создайте issue в репозитории.

## 📄 Лицензия

Этот проект создан в образовательных целях для стажировки QA в Avito.

---

**Автор:** QA Intern Candidate  
**Дата:** 2024  
**Версия:** 1.0.0
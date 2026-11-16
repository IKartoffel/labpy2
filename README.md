# Потоковый анализатор логов

# Перед началом
Нужен python 3.10 и выше

Сделайте клон из репозитория гита

Запустите виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

Довать пакет для разработки
pip install -e ".[dev]"

# Для запуска
Справка для команд
python -m streamstats --help

Пример запуска:
python -m streamstats analyze logs.csv --format csv
Режим пропуска работает через --skip-invalid
Пример:
python -m streamstats analyze broken_data.jsonl --format jsonl --skip-invalid

# Тесты
pytest

# Прооверка

ruff check .
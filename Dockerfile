FROM python:3.10-slim

# рабочая директория
WORKDIR /app

# системные зависимости
RUN apt-get update && apt-get install -y tk

# установка SQLite
RUN apt-get install -y sqlite3

# копирование файлов в контейнер
COPY . /app

# установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# путь к бд
ENV SQLITE_DB_PATH=/app/cargo_tracking.db

# запуск
CMD ["python", "main.py"]

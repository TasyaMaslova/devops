# Базовый Образ
FROM python:3.10-slim

# Рабочая директория
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY ./app .

# Команда для запуска приложения
CMD ["flask", "run", "--host=0.0.0.0"] 

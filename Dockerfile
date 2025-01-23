# Используем официальный образ Python 3.11
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем системные зависимости и утилиты


# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Команда по умолчанию для запуска сервера разработки
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]

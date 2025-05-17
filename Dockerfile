# Используем официальный Python-образ
FROM python:3.11-slim


# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем всё приложение
COPY . .

# Команда по умолчанию
CMD ["gunicorn", "materials_api.wsgi:application", "--bind", "0.0.0.0:8000"]

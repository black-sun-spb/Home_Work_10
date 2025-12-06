FROM python:3.12

WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Переменная окружения для Django
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=home_work_7.settings

# Команда по умолчанию
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

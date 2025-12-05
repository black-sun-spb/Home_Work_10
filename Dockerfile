# Используем Python 3.12 slim
FROM python:3.12-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Устанавливаем рабочую директорию для Gunicorn
WORKDIR /app/home_work_7

# Команда запуска Gunicorn
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8000"]


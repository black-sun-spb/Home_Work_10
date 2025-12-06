# LMS API — Система управления обучением

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Описание

LMS API — это серверная часть системы управления обучением (Learning Management System), реализованная на **Django** и **Django REST Framework**.

**Основные возможности:**
- управление пользователями и их ролями;
- работа с учебным контентом (курсы, уроки);
- обработка платежей через Stripe;
- асинхронные задачи (Celery);
- API для интеграции с фронтендом;
- автоматизированный деплой через GitHub Actions.

## Требования к окружению

- Python 3.10+;
- PostgreSQL 14+;
- Redis 7+ (для Celery);
- Docker 24+ и Docker Compose v2;
- Stripe API key (для платёжных операций).

## Структура проекта

```
Home_work_10/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── .venv/
├── home_work_7/
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── settings_test.py
│   ├── urls.py
│   └── wsgi.py
├── lms/
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_initial.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── paginators.py
│   ├── serializers.py
│   ├── stripe_service.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   ├── validators.py
│   └── views.py
├── users/
│   ├── fixtures/
│   │   └── groups.json
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── .env
├── .env.example
├── .flake8
├── .gitignore
├── celerybeat-schedule
├── celerybeat-schedule-shm
├── celerybeat-schedule-wal
├── docker-compose.yml
├── Dockerfile
├── manage.py
└── requirements.txt
```

## Установка и запуск

### 1. Клонируйте репозиторий
```bash
git clone <URL_репозитория>
cd Home_work_10
```

### 2. Настройте виртуальное окружение
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate    # Windows
```

### 3. Установите зависимости
```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения
- Скопируйте .env.example в .env.
- Заполните параметры:
  - SECRET_KEY — секретный ключ Django;
  - DEBUG — режим отладки (True/False);
  - ALLOWED_HOSTS — разрешённые хосты;
  - DATABASE_URL — строка подключения к PostgreSQL;
  - REDIS_URL — URL Redis-сервера;
  - STRIPE_SECRET_KEY — API-ключ Stripe;
  - STRIPE_WEBHOOK_SECRET — секрет вебхука Stripe.

### 5. Настройте БД и выполните миграции
```bash
python manage.py migrate
```

### 6. Загрузите фикстуры (опционально)
```bash
python manage.py loaddata users/fixtures/groups.json
```

### 7. Запустите сервер
```bash
python manage.py runserver 0.0.0.0:8000
```
Сервер будет доступен по адресу: http://localhost:8000/.

### 8. Запустите Celery (отдельно)
```bash
celery -A home_work_7 worker -l info
```

### 9. Запустите Celery Beat (отдельно)
```bash
celery -A home_work_7 beat -l info
```

## Запуск через Docker

1. Соберите контейнеры:
```bash
docker-compose build
```

2. Запустите сервисы:
```bash
docker-compose up -d
```

3. Выполните миграции внутри контейнера:
```bash
docker-compose exec web python manage.py migrate
```

4. Загрузите фикстуры:
```bash
docker-compose exec web python manage.py loaddata users/fixtures/groups.json
```

## Доступные эндпоинты

### Пользователи (/users/)
- GET /users/ — список пользователей;
- GET /users/{id}/ — профиль пользователя;
- POST /users/ — создание пользователя;
- PUT /users/{id}/ — обновление профиля;
- DELETE /users/{id}/ — удаление.

### Курсы и уроки (/lms/)
- GET /lms/courses/ — список курсов;
- GET /lms/courses/{id}/ — детали курса;
- GET /lms/lessons/ — список уроков;
- GET /lms/lessons/{id}/ — детали урока.

### Платежи (Stripe)
- POST /lms/create-payment/ — создание платёжной сессии;
- POST /lms/stripe-webhook/ — вебхук Stripe (обработка событий).

### Сервисные эндпоинты
- GET /health/ — проверка работоспособности;
- GET /admin/ — панель администратора Django;
- GET /api-docs/ — документация API (Swagger/Redoc).

## Настройка Celery

1. Убедитесь, что Redis запущен.
2. В .env укажите REDIS_URL=redis://redis:6379/0.
3. Запускайте worker и beat отдельно (см. выше).

## Тестирование

Запустите тесты:
```
python manage.py test
```

Или для конкретного приложения:
```
python manage.py test lms
python manage.py test users
```

## Документация API

После запуска сервера откройте:
- http://localhost:8000/api-docs/ — интерактивная документация (Swagger);
- http://localhost:8000/redoc/ — документация (Redoc).

## CI/CD

Пайплайн деплоя настроен в .github/workflows/deploy.yml. Он:
- проверяет код (flake8);
- запускает тесты;
- собирает Docker-образ;
- деплоит на сервер (при пуше в main).

## Логирование

Логи пишутся в:
- консоль (при запуске runserver);
- файлы celerybeat-schedule* (для Celery Beat);
- Docker-контейнеры (смотрите через docker-compose logs).

## Рекомендации для продакшена
1. Установите DEBUG=False в .env.
2. Настройте HTTPS (например, через Nginx).
3. Используйте надёжный SECRET_KEY.
4. Ограничьте ALLOWED_HOSTS.
5. Настройте резервное копирование БД и Redis.
6. Запускайте Celery worker/beat как системные сервисы (например, через systemd).


## Переменные окружения (.env)

Пример:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:password@db:5432/lmsdb
REDIS_URL=redis://redis:6379/0
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```
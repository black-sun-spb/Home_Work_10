"""
Настройки для запуска тестов в Django.
"""

from .settings import *  # Импортируем все настройки из основного settings.py


# Переопределяем базу данных для тестов
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_db',                  # Имя тестовой БД
        'USER': 'postgres',                # Пользователь PostgreSQL
        'PASSWORD': 'postgres',            # Пароль пользователя
        'HOST': 'db',                     # Имя сервиса в Docker (не localhost!)
        'PORT': '5432',                   # Порт PostgreSQL
    }
}

# Отключаем DEBUG в тестах (для безопасности)
DEBUG = False

# Для тестов можно отключить секретный ключ (но не в продакшене!)
SECRET_KEY = 'test-secret-key-for-tests'


# Отключаем статические файлы в тестах
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Дополнительные настройки для тестов
TEST_RUNNER = 'django.test.runner.DiscoverRunner'


# Если используете кэширование — отключаем его в тестах
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

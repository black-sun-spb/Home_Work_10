# home_work_7/settings_test.py
from .settings import *  # noqa

# Тестовые переопределения
DEBUG = False
SECRET_KEY = 'test-secret-key-for-ci'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}

# Статические файлы для тестов не собираем
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

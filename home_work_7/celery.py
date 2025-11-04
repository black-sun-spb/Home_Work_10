import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_work_7.settings')

app = Celery('home_work_7')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

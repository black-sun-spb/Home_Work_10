from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

@shared_task
def deactivate_inactive_users():
    """
    Деактивировать пользователей, не заходивших более 30 дней.
    """
    User = get_user_model()
    one_month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=one_month_ago, is_active=True)
    count = inactive_users.update(is_active=False)
    print(f'Деактивировано пользователей: {count}')

from celery import shared_task
from django.core.mail import send_mail
from .models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    """
    Асинхронная рассылка уведомлений подписчикам курса.
    """
    course = Course.objects.get(id=course_id)
    subscribers = Subscription.objects.filter(course=course).select_related('user')

    for sub in subscribers:
        send_mail(
            subject=f'Обновление курса: {course.title}',
            message=f'Здравствуйте, {sub.user.username}! Курс "{course.title}" был обновлён.',
            from_email='noreply@lms.com',
            recipient_list=[sub.user.email],
            fail_silently=True,
        )

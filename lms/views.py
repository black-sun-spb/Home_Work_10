from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .paginators import StandardResultsSetPagination
from .stripe_service import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_checkout_session,
    retrieve_checkout_session
)
from .tasks import send_course_update_email  # Celery-задача уведомления подписчиков


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        # Для Swagger и анонимов возвращаем пустой QuerySet
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Course.objects.none()
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        if self.request.user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут создавать курсы.")
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """
        Обновление курса с уведомлением подписчиков (если курс не обновлялся > 4 часов).
        """
        course = serializer.save()
        last_updated = getattr(course, 'updated_at', None)

        if not last_updated or timezone.now() - last_updated > timedelta(hours=4):
            # Асинхронно запускаем рассылку уведомлений
            send_course_update_email.delay(course.id)

    def perform_destroy(self, instance):
        if self.request.user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут удалять курсы.")
        if instance.owner != self.request.user:
            raise PermissionDenied("Удалять можно только свои курсы.")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """
        POST-эндпоинт для подписки / отписки на курс.
        """
        course = self.get_object()
        user = request.user

        subscription, created = Subscription.objects.get_or_create(user=user, course=course)
        if created:
            return Response({"detail": "Подписка оформлена."}, status=status.HTTP_201_CREATED)
        else:
            subscription.delete()
            return Response({"detail": "Подписка отменена."}, status=status.HTTP_200_OK)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Lesson.objects.none()
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(course__owner=user)

    def perform_create(self, serializer):
        if self.request.user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут создавать уроки.")
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут удалять уроки.")
        instance.delete()


class PaymentViewSet(viewsets.ViewSet):
    """
    Эндпоинты для оплаты курса через Stripe.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def create_checkout_session(self, request, pk=None):
        """
        Создание сессии оплаты курса.
        """
        course = Course.objects.get(pk=pk)
        product = create_stripe_product(course.title, course.description)
        price = create_stripe_price(product['id'], amount=course.price if hasattr(course, 'price') else 1000)
        session = create_stripe_checkout_session(
            price_id=price['id'],
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel'
        )
        return Response({'checkout_url': session.url})

    @action(detail=False, methods=['get'])
    def retrieve_session(self, request):
        """
        Получение информации о сессии оплаты по её ID.
        """
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({"error": "session_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        session = retrieve_checkout_session(session_id)
        return Response(session)

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .paginators import StandardResultsSetPagination


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            qs = Course.objects.all()
        else:
            qs = Course.objects.filter(owner=user)
        return qs.order_by('id')  # Добавлено явное упорядочивание

    def perform_create(self, serializer):
        if self.request.user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут создавать курсы.")
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут удалять курсы.")
        if instance.owner != self.request.user:
            raise PermissionDenied("Удалять можно только свои курсы.")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
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
        if user.groups.filter(name='moderators').exists():
            qs = Lesson.objects.all()
        else:
            qs = Lesson.objects.filter(course__owner=user)
        return qs.order_by('id')  # Добавлено явное упорядочивание

    def perform_create(self, serializer):
        if self.request.user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут создавать уроки.")
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут удалять уроки.")
        instance.delete()

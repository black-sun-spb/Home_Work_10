# lms/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer
from .paginators import StandardResultsSetPagination
from users.permissions import IsModer

class CourseViewSet(viewsets.ModelViewSet):
    """
    Courses:
    - обычный пользователь видит/управляет только своими курсами;
    - модератор видит все, может редактировать, но не создавать и не удалять.
    Дополнительно: actions subscribe (POST) и unsubscribe (DELETE)
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.action in ['retrieve', 'subscribe', 'unsubscribe']:
            return Course.objects.all()
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

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
        sub, created = Subscription.objects.get_or_create(user=request.user, course=course)
        if created:
            serializer = SubscriptionSerializer(sub, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Already subscribed'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def unsubscribe(self, request, pk=None):
        course = self.get_object()
        deleted, _ = Subscription.objects.filter(user=request.user, course=course).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)


class LessonViewSet(viewsets.ModelViewSet):
    """
    LessonViewSet:
    - модератор видит и может редактировать любой урок, но не создавать/удалять
    - обычный пользователь — работает только со своими уроками
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        if self.request.user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут создавать уроки.")
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут удалять уроки.")
        if instance.owner != self.request.user:
            raise PermissionDenied("Удалять можно только свои уроки.")
        instance.delete()

from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModer, IsOwner

class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD для курсов.
    Модераторы могут только смотреть и редактировать.
    Обычные пользователи могут работать только со своими курсами.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Разделяем права по action
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated()]  # object-level проверка ниже
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated()]  # object-level проверка в IsOwner | IsModer
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()  # модератор видит все
        return Course.objects.filter(owner=user)  # обычный пользователь — только свои

    def perform_create(self, serializer):
        if self.request.user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут создавать курсы.")
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут удалять курсы.")
        instance.delete()

class LessonViewSet(viewsets.ModelViewSet):
    """
    CRUD для уроков.
    Модераторы могут только смотреть и редактировать.
    Обычные пользователи могут работать только со своими уроками.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

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
        instance.delete()

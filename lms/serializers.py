# lms/serializers.py
from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_video_url


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для уроков"""
    video_url = serializers.URLField(allow_null=True, allow_blank=True, required=False,
                                     validators=[validate_video_url])

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_url', 'course', 'owner']
        read_only_fields = ['owner']


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курсов, с подсчётом количества уроков и флагом подписки текущего пользователя"""
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.IntegerField(source='lessons.count', read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'preview', 'lessons_count', 'lessons', 'owner', 'is_subscribed']
        read_only_fields = ['owner', 'lessons_count', 'lessons', 'is_subscribed']

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return obj.subscriptions.filter(user=request.user).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'course', 'created']
        read_only_fields = ['user', 'created']

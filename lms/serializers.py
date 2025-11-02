# lms/serializers.py
from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_video_url


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(
        allow_null=True,
        allow_blank=True,
        required=False,
        validators=[validate_video_url]
    )

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'course', 'owner', 'video_url']
        read_only_fields = ['owner']


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.IntegerField(source='lessons.count', read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'owner', 'lessons', 'lessons_count', 'is_subscribed']

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, course=obj).exists()
        return False

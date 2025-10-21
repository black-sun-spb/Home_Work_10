from rest_framework import serializers
from .models import User, Payment
from lms.models import Course, Lesson

class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    """Платежи с гиперссылками на пользователя, курс и урок"""
    user = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        read_only=True
    )
    course = serializers.HyperlinkedRelatedField(
        view_name='course-detail',
        queryset=Course.objects.all(),
        allow_null=True,
        required=False
    )
    lesson = serializers.HyperlinkedRelatedField(
        view_name='lesson-detail',
        queryset=Lesson.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = Payment
        fields = ['id', 'user', 'course', 'lesson', 'date', 'amount', 'payment_method', 'url']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Пользователь с историей платежей"""
    payments = PaymentSerializer(many=True, read_only=True)  # source не нужен

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'payments', 'url']
        extra_kwargs = {
            'url': {'view_name': 'user-detail', 'lookup_field': 'pk'}
        }


class RegisterSerializer(serializers.ModelSerializer):
    """Регистрация нового пользователя"""
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = ('email', 'password', 'phone', 'city', 'avatar')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
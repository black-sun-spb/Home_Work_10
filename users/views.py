from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD для пользователей.
    Каждый пользователь при выводе включает историю своих платежей.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD для платежей.
    Поддерживает фильтрацию по курсу, уроку и способу оплаты,
    а также сортировку по дате.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['date']
    ordering = ['-date']  # по умолчанию последние платежи сверху

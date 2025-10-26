from rest_framework import viewsets, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer, RegisterSerializer
from .permissions import IsModer, IsOwner
from rest_framework_simplejwt.tokens import RefreshToken


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD для пользователей.
    Каждый пользователь при выводе включает историю своих платежей.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Регистрация нового пользователя доступна без авторизации через отдельный эндпоинт
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # создаём пользователя (через админку или регистрацию)
        serializer.save()


class PaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD для платежей.
    Поддерживает фильтрацию по курсу, уроку и способу оплаты,
    а также сортировку по дате.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['date']
    ordering = ['-date']  # по умолчанию последние платежи сверху


class RegisterAPIView(APIView):
    """
    Эндпоинт для регистрации пользователей.
    Доступен без авторизации.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # возвращаем JWT-токены сразу после регистрации
        refresh = RefreshToken.for_user(user)
        data = {
            'user': UserSerializer(user, context={'request': request}).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_201_CREATED)

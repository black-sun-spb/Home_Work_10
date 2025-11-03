from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PaymentViewSet, RegisterAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'payments', PaymentViewSet, basename='payment')  # добавляем платежи

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterAPIView.as_view(), name='register'),      # доступно всем
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # доступно всем
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

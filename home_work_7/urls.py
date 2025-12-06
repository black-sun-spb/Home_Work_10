from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse
from django.utils import timezone

# Схема API
schema_view = get_schema_view(
    openapi.Info(
        title="LMS API",
        default_version='v1',
        description="Документация для учебного LMS проекта",
        contact=openapi.Contact(email="admin@example.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Healthcheck
def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "timestamp": timezone.now().isoformat(),
        "service": "LMS API"
    })

# Корневой URL (опционально)
def home(request):
    return JsonResponse({"message": "Добро пожаловать в LMS API!"})

urlpatterns = [
    # Админка Django
    path('admin/', admin.site.urls),

    # Корень сайта (можно заменить на TemplateView)
    path('', home, name='home'),

    # API для LMS
    path('api/lms/', include(('lms.urls', 'lms'), namespace='lms')),

    # API для пользователей
    path('api/users/', include(('users.urls', 'users'), namespace='users')),

    # JWT-токены
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Документация API
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Healthcheck
    path('health/', health_check, name='health'),
]

# Home_Work_7/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # namespace 'api' нужен для reverse('api:lesson-list') и course-detail/subscription
    path('api/', include(('lms.urls', 'lms'), namespace='api')),
    path('api/', include(('users.urls', 'users'), namespace='users')),

    # JWT токены
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

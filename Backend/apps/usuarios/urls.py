from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView

urlpatterns = [
    # Endpoint principal de Login (Retorna tokens y datos del usuario)
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Endpoint para renovar el Access Token usando el Refresh Token
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
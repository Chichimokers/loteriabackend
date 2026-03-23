from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UsuarioViewSet, TarjetaSistemaViewSet,
    SolicitudAcreditacionViewSet, ExtraccionViewSet
)

router = DefaultRouter()
router.register(r'', UsuarioViewSet, basename='usuarios')
router.register(r'tarjetas', TarjetaSistemaViewSet, basename='tarjetas')
router.register(r'acreditaciones', SolicitudAcreditacionViewSet, basename='acreditaciones')
router.register(r'extracciones', ExtraccionViewSet, basename='extracciones')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

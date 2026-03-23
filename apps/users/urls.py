from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet, TarjetaSistemaViewSet,
    SolicitudAcreditacionViewSet, ExtraccionViewSet
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')
router.register(r'tarjetas', TarjetaSistemaViewSet, basename='tarjetas')
router.register(r'acreditaciones', SolicitudAcreditacionViewSet, basename='acreditaciones')
router.register(r'extracciones', ExtraccionViewSet, basename='extracciones')

urlpatterns = [
    path('', include(router.urls)),
]

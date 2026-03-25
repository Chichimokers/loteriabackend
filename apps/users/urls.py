from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UsuarioViewSet, TarjetaSistemaViewSet,
    SolicitudAcreditacionViewSet, ExtraccionViewSet, usuario_me
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Usuario endpoints - me/ debe ir antes de <int:pk>/
    path('me/', usuario_me, name='usuarios-me'),
    path('', UsuarioViewSet.as_view({'get': 'list', 'post': 'create'}), name='usuarios-list'),
    path('<int:pk>/', UsuarioViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='usuarios-detail'),
    path('<int:pk>/ajustar_saldo/', UsuarioViewSet.as_view({'patch': 'ajustar_saldo'}), name='usuarios-ajustar-saldo'),
    
    # Tarjetas
    path('tarjetas/', TarjetaSistemaViewSet.as_view({'get': 'list', 'post': 'create'}), name='tarjetas-list'),
    path('tarjetas/<int:pk>/', TarjetaSistemaViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='tarjetas-detail'),
    
    # Acreditaciones
    path('acreditaciones/', SolicitudAcreditacionViewSet.as_view({'get': 'list', 'post': 'create'}), name='acreditaciones-list'),
    path('acreditaciones/<int:pk>/', SolicitudAcreditacionViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='acreditaciones-detail'),
    path('acreditaciones/<int:pk>/aprobar/', SolicitudAcreditacionViewSet.as_view({'patch': 'aprobar'}), name='acreditaciones-aprobar'),
    path('acreditaciones/<int:pk>/rechazar/', SolicitudAcreditacionViewSet.as_view({'patch': 'rechazar'}), name='acreditaciones-rechazar'),
    
    # Extracciones
    path('extracciones/', ExtraccionViewSet.as_view({'get': 'list', 'post': 'create'}), name='extracciones-list'),
    path('extracciones/<int:pk>/', ExtraccionViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='extracciones-detail'),
    path('extracciones/<int:pk>/aprobar/', ExtraccionViewSet.as_view({'patch': 'aprobar'}), name='extracciones-aprobar'),
    path('extracciones/<int:pk>/rechazar/', ExtraccionViewSet.as_view({'patch': 'rechazar'}), name='extracciones-rechazar'),
]

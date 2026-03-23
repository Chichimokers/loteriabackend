from django.urls import path
from .views import ModalidadViewSet, LoteriaViewSet, TiradaViewSet

urlpatterns = [
    # Modalidades
    path('modalidades/', ModalidadViewSet.as_view({'get': 'list', 'post': 'create'}), name='modalidades-list'),
    path('modalidades/<int:pk>/', ModalidadViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='modalidades-detail'),
    
    # Loterías
    path('loterias/', LoteriaViewSet.as_view({'get': 'list', 'post': 'create'}), name='loterias-list'),
    path('loterias/<int:pk>/', LoteriaViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='loterias-detail'),
    
    # Tiradas
    path('tiradas/', TiradaViewSet.as_view({'get': 'list', 'post': 'create'}), name='tiradas-list'),
    path('tiradas/<int:pk>/', TiradaViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='tiradas-detail'),
    path('tiradas/activas/', TiradaViewSet.as_view({'get': 'activas'}), name='tiradas-activas'),
    path('tiradas/resultados_hoy/', TiradaViewSet.as_view({'get': 'resultados_hoy'}), name='tiradas-resultados-hoy'),
    path('tiradas/ingresar_resultado/', TiradaViewSet.as_view({'post': 'ingresar_resultado'}), name='tiradas-ingresar-resultado'),
]

from django.urls import path
from .views import NotificacionViewSet

urlpatterns = [
    path('', NotificacionViewSet.as_view({'get': 'list'}), name='notificaciones-list'),
    path('<int:pk>/', NotificacionViewSet.as_view({'get': 'retrieve'}), name='notificaciones-detail'),
    path('<int:pk>/leer/', NotificacionViewSet.as_view({'patch': 'leer'}), name='notificaciones-leer'),
    path('no_leidas/', NotificacionViewSet.as_view({'get': 'no_leidas'}), name='notificaciones-no-leidas'),
    path('leer_todas/', NotificacionViewSet.as_view({'patch': 'leer_todas'}), name='notificaciones-leer-todas'),
    path('admin/', NotificacionViewSet.as_view({'get': 'admin'}), name='notificaciones-admin'),
    path('admin/no_leidas/', NotificacionViewSet.as_view({'get': 'admin_no_leidas'}), name='notificaciones-admin-no-leidas'),
    path('admin/leer_todas/', NotificacionViewSet.as_view({'patch': 'admin_leer_todas'}), name='notificaciones-admin-leer-todas'),
]

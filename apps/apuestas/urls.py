from django.urls import path
from .views import ApuestaViewSet

urlpatterns = [
    path('', ApuestaViewSet.as_view({'get': 'list', 'post': 'create'}), name='apuestas-list'),
    path('<int:pk>/', ApuestaViewSet.as_view({'get': 'retrieve'}), name='apuestas-detail'),
    path('mis_apuestas/', ApuestaViewSet.as_view({'get': 'mis_apuestas'}), name='apuestas-mias'),
    path('<int:pk>/calcular_premios/', ApuestaViewSet.as_view({'get': 'calcular_premios'}), name='apuestas-calcular'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModalidadViewSet, LoteriaViewSet, TiradaViewSet

router = DefaultRouter()
router.register(r'modalidades', ModalidadViewSet, basename='modalidades')
router.register(r'loterias', LoteriaViewSet, basename='loterias')
router.register(r'tiradas', TiradaViewSet, basename='tiradas')

urlpatterns = [
    path('', include(router.urls)),
]

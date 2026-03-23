from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApuestaViewSet

router = DefaultRouter()
router.register(r'', ApuestaViewSet, basename='apuestas')

urlpatterns = [
    path('', include(router.urls)),
]

"""
Main URL configuration for Loteria Backend project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.views.static import serve
from django.conf import settings


def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'Loteria Backend'})


def api_root(request):
    return JsonResponse({
        'service': 'Loteria Backend API',
        'version': '1.0.0',
        'message': 'Sistema de apuestas en loterías',
        'endpoints': {
            'usuarios': '/api/v1/usuarios/',
            'acreditaciones': '/api/v1/acreditaciones/',
            'extracciones': '/api/v1/extracciones/',
            'loterias': '/api/v1/loterias/',
            'tiradas': '/api/v1/tiradas/',
            'modalidades': '/api/v1/modalidades/',
            'apuestas': '/api/v1/apuestas/',
            'admin': '/api/v1/admin/',
        }
    })


urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('api/', api_root, name='api-root'),
    path('api/v1/', api_root, name='api-root-v1'),
    path('api/v1/usuarios/', include('apps.users.urls')),
    path('api/v1/loterias/', include('apps.loteria.urls')),
    path('api/v1/apuestas/', include('apps.apuestas.urls')),
    path('api/v1/admin/', admin.site.urls),
]

urlpatterns += [
    re_path(r'^api/v1/static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^api/v1/media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

admin.site.site_header = 'Loteria Backend Admin'
admin.site.site_title = 'Loteria Backend'
admin.site.index_title = 'Panel de Administración'

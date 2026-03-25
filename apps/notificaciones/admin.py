from django.contrib import admin
from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo', 'titulo', 'usuario', 'leida', 'fecha']
    list_filter = ['tipo', 'leida', 'fecha']
    search_fields = ['titulo', 'mensaje', 'usuario__email']
    list_editable = ['leida']
    readonly_fields = ['fecha']

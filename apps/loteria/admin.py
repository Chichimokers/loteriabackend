from django.contrib import admin
from .models import Modalidad, Loteria, Tirada, Resultado


@admin.register(Modalidad)
class ModalidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'premio_por_peso', 'descripcion']
    list_editable = ['premio_por_peso']


@admin.register(Loteria)
class LoteriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activa']
    list_editable = ['activa']


@admin.register(Tirada)
class TiradaAdmin(admin.ModelAdmin):
    list_display = ['loteria', 'hora', 'activa']
    list_filter = ['activa', 'loteria']
    ordering = ['hora']


@admin.register(Resultado)
class ResultadoAdmin(admin.ModelAdmin):
    list_display = ['tirada', 'fecha', 'pick_3', 'pick_4', 'created_at']
    list_filter = ['fecha', 'tirada__loteria']
    search_fields = ['tirada__loteria__nombre']

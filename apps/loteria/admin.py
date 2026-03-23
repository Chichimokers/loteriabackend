from django.contrib import admin
from .models import Modalidad, Loteria, Tirada


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
    list_display = ['loteria', 'hora', 'fecha', 'activa', 'pick_3', 'pick_4']
    list_filter = ['activa', 'fecha', 'loteria']
    search_fields = ['loteria__nombre']

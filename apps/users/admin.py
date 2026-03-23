from django.contrib import admin
from .models import Usuario, TarjetaSistema, SolicitudAcreditacion, Extraccion


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['email', 'movil', 'saldo_principal', 'saldo_extraccion', 'banco', 'fecha_registro']
    list_filter = ['banco', 'fecha_registro']
    search_fields = ['email', 'movil']
    readonly_fields = ['fecha_registro', 'password']


@admin.register(TarjetaSistema)
class TarjetaSistemaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'banco', 'activa']
    list_filter = ['banco', 'activa']
    search_fields = ['numero']


@admin.register(SolicitudAcreditacion)
class SolicitudAcreditacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'tarjeta', 'monto', 'estado', 'fecha']
    list_filter = ['estado', 'fecha']
    search_fields = ['id_transferencia', 'usuario__email']


@admin.register(Extraccion)
class ExtraccionAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'monto', 'estado', 'fecha']
    list_filter = ['estado', 'fecha']
    search_fields = ['usuario__email']

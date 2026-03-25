from django.contrib import admin
from django.contrib import messages
from .models import Usuario, TarjetaSistema, SolicitudAcreditacion, Extraccion


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['email', 'movil', 'saldo_principal', 'saldo_extraccion', 'banco', 'fecha_registro']
    list_filter = ['banco', 'fecha_registro']
    search_fields = ['email', 'movil']
    readonly_fields = ['fecha_registro', 'password']
    list_editable = ['saldo_principal', 'saldo_extraccion']
    
    fieldsets = (
        ('Información de cuenta', {
            'fields': ('email', 'username', 'password', 'movil')
        }),
        ('Información bancaria', {
            'fields': ('tarjeta_bancaria', 'banco')
        }),
        ('Saldos', {
            'fields': ('saldo_principal', 'saldo_extraccion')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas', {
            'fields': ('fecha_registro',)
        }),
    )
    
    actions = ['agregar_saldo', 'restar_saldo']
    
    @admin.action(description='Agregar 100 CUP al saldo principal')
    def agregar_saldo(self, request, queryset):
        for usuario in queryset:
            usuario.saldo_principal += 100
            usuario.save()
        self.message_user(request, f'Se agregó 100 CUP a {queryset.count()} usuario(s)', messages.SUCCESS)
    
    @admin.action(description='Restar 100 CUP al saldo principal')
    def restar_saldo(self, request, queryset):
        for usuario in queryset:
            if usuario.saldo_principal >= 100:
                usuario.saldo_principal -= 100
                usuario.save()
            else:
                self.message_user(request, f'El usuario {usuario.email} no tiene saldo suficiente', messages.WARNING)
        self.message_user(request, f'Se restó 100 CUP a los usuarios con saldo suficiente', messages.SUCCESS)


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

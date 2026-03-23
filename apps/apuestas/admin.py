from django.contrib import admin
from .models import Apuesta


@admin.register(Apuesta)
class ApuestaAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'loteria', 'modalidad', 'tirada', 'monto_total', 'premio_total', 'paga', 'fecha']
    list_filter = ['fecha', 'modalidad', 'loteria', 'paga']
    search_fields = ['usuario__email', 'numeros']

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    movil = models.CharField(max_length=15, unique=True)
    saldo_principal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_extraccion = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tarjeta_bancaria = models.CharField(max_length=20)
    banco = models.CharField(max_length=20, choices=[
        ('metropolitano', 'Metropolitano'),
        ('bandec', 'Bandec'),
        ('bpa', 'BPA'),
        ('monedero', 'Monedero')
    ])
    fecha_registro = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.email


class TarjetaSistema(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    movil = models.CharField(max_length=15)
    banco = models.CharField(max_length=20, choices=[
        ('metropolitano', 'Metropolitano'),
        ('bandec', 'Bandec'),
        ('bpa', 'BPA'),
        ('monedero', 'Monedero')
    ])
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Tarjeta del Sistema'
        verbose_name_plural = 'Tarjetas del Sistema'

    def __str__(self):
        return f"{self.numero} - {self.movil} ({self.banco})"


class SolicitudAcreditacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tarjeta = models.ForeignKey(TarjetaSistema, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    sms_confirmacion = models.CharField(max_length=10)
    id_transferencia = models.CharField(max_length=50, unique=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada')
    ], default='pendiente')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Solicitud de Acreditación'
        verbose_name_plural = 'Solicitudes de Acreditación'
        ordering = ['-fecha']

    def __str__(self):
        return f"Acreditación {self.id_transferencia} - {self.usuario.email}"


class Extraccion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada')
    ], default='pendiente')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Extracción'
        verbose_name_plural = 'Extracciones'
        ordering = ['-fecha']

    def __str__(self):
        return f"Extracción {self.id} - {self.usuario.email}"

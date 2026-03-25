from django.db import models
from apps.users.models import Usuario


class Notificacion(models.Model):
    TIPOS = [
        ('nuevo_usuario', 'Nuevo usuario registrado'),
        ('acreditacion_pendiente', 'Acreditación pendiente'),
        ('acreditacion_aprobada', 'Acreditación aprobada'),
        ('acreditacion_rechazada', 'Acreditación rechazada'),
        ('extraccion_pendiente', 'Extracción pendiente'),
        ('extraccion_aprobada', 'Extracción aprobada'),
        ('extraccion_rechazada', 'Extracción rechazada'),
        ('apuesta_creada', 'Apuesta creada'),
        ('apuesta_ganadora', 'Apuesta ganadora'),
        ('apuesta_perdedora', 'Apuesta perdedora'),
        ('resultado_publicado', 'Resultado publicado'),
        ('saldo_ajustado', 'Saldo ajustado'),
        ('saldo_bajo', 'Saldo bajo'),
    ]

    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='notificaciones',
        null=True,
        blank=True
    )
    tipo = models.CharField(max_length=30, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    datos = models.JSONField(null=True, blank=True)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha']

    def __str__(self):
        if self.usuario:
            return f"{self.titulo} - {self.usuario.email}"
        return f"{self.titulo} - Admin"

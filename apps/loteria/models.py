from django.db import models


class Modalidad(models.Model):
    nombre = models.CharField(max_length=10, unique=True, choices=[
        ('fijo', 'Fijo'),
        ('corrido', 'Corrido'),
        ('parle', 'Parlé'),
        ('pick_3', 'Pick 3')
    ])
    premio_por_peso = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Modalidad'
        verbose_name_plural = 'Modalidades'

    def __str__(self):
        return self.nombre


class Loteria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    foto = models.ImageField(upload_to='loterias/', null=True, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Lotería'
        verbose_name_plural = 'Loterías'

    def __str__(self):
        return self.nombre


class Tirada(models.Model):
    loteria = models.ForeignKey(Loteria, on_delete=models.CASCADE, related_name='tiradas')
    hora = models.TimeField()
    fecha = models.DateField()
    activa = models.BooleanField(default=True)
    pick_3 = models.CharField(max_length=3, null=True, blank=True)
    pick_4 = models.CharField(max_length=4, null=True, blank=True)

    class Meta:
        verbose_name = 'Tirada'
        verbose_name_plural = 'Tiradas'
        ordering = ['-fecha', '-hora']
        unique_together = ['loteria', 'hora', 'fecha']

    def __str__(self):
        return f"{self.loteria.nombre} - {self.fecha} {self.hora}"

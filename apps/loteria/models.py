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
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Tirada'
        verbose_name_plural = 'Tiradas'
        ordering = ['hora']
        unique_together = ['loteria', 'hora']

    def __str__(self):
        return f"{self.loteria.nombre} - {self.hora}"


class Resultado(models.Model):
    tirada = models.ForeignKey(Tirada, on_delete=models.CASCADE, related_name='resultados')
    fecha = models.DateField()
    pick_3 = models.CharField(max_length=3, null=True, blank=True)
    pick_4 = models.CharField(max_length=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Resultado'
        verbose_name_plural = 'Resultados'
        unique_together = ['tirada', 'fecha']
        ordering = ['-fecha', '-tirada__hora']

    def __str__(self):
        return f"{self.tirada.loteria.nombre} - {self.fecha} {self.tirada.hora}"

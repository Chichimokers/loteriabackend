from django.db import models
from apps.users.models import Usuario
from apps.loteria.models import Loteria, Tirada, Modalidad


class Apuesta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='apuestas')
    loteria = models.ForeignKey(Loteria, on_delete=models.CASCADE)
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE)
    tirada = models.ForeignKey(Tirada, on_delete=models.CASCADE, related_name='apuestas')
    numeros = models.JSONField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    monto_por_numero = models.DecimalField(max_digits=10, decimal_places=2)
    premiados = models.JSONField(null=True, blank=True)
    premio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Apuesta'
        verbose_name_plural = 'Apuestas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Apuesta {self.id} - {self.usuario.email}"

    def calcular_premios(self):
        from decimal import Decimal
        
        premios = []
        monto_total_premios = Decimal('0')

        if self.tirada.pick_3:
            for numero in self.numeros:
                if self._es_ganador(numero, self.tirada.pick_3):
                    premio = self.monto_por_numero * self.modalidad.premio_por_peso
                    premios.append({
                        "numero": numero,
                        "premio": float(premio),
                        "tipo": "pick_3"
                    })
                    monto_total_premios += premio

        if self.tirada.pick_4:
            for numero in self.numeros:
                if self._es_ganador(numero, self.tirada.pick_4):
                    premio = self.monto_por_numero * self.modalidad.premio_por_peso
                    premios.append({
                        "numero": numero,
                        "premio": float(premio),
                        "tipo": "pick_4"
                    })
                    monto_total_premios += premio

        self.premiados = premios
        self.premio_total = monto_total_premios
        return monto_total_premios

    def _es_ganador(self, numero, resultado):
        if self.modalidad.nombre == 'fijo':
            return numero[0] == resultado[0]
        elif self.modalidad.nombre == 'corrido':
            return all(digit in resultado for digit in numero)
        elif self.modalidad.nombre == 'parle':
            return numero == resultado
        elif self.modalidad.nombre == 'pick_3':
            return numero == resultado
        return False

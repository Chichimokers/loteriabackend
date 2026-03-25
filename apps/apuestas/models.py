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
    combinaciones_generadas = models.JSONField(null=True, blank=True)
    premiados = models.JSONField(null=True, blank=True)
    premio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paga = models.BooleanField(default=False)
    fecha = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Apuesta'
        verbose_name_plural = 'Apuestas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Apuesta {self.id} - {self.usuario.email}"

    def get_resultado(self):
        from apps.loteria.models import Resultado
        return Resultado.objects.filter(tirada=self.tirada, fecha=self.fecha).first()

    def _extraer_valores(self, resultado):
        pick_3 = resultado.pick_3 or ''
        pick_4 = resultado.pick_4 or ''

        fijo = pick_3[-2:] if len(pick_3) >= 2 else ''
        corrido1 = pick_4[:2] if len(pick_4) >= 2 else ''
        corrido2 = pick_4[-2:] if len(pick_4) >= 2 else ''
        centena = pick_3 if len(pick_3) == 3 else ''

        return {
            'fijo': fijo,
            'corrido1': corrido1,
            'corrido2': corrido2,
            'centena': centena,
        }

    def calcular_premios(self):
        from decimal import Decimal

        resultado = self.get_resultado()
        if not resultado or (not resultado.pick_3 and not resultado.pick_4):
            return Decimal('0')

        valores = self._extraer_valores(resultado)
        modalidad = self.modalidad.nombre
        premios = []
        monto_total_premios = Decimal('0')

        if modalidad == 'fijo':
            for numero in self.numeros:
                if numero == valores['fijo']:
                    premio = self.monto_por_numero * self.modalidad.premio_por_peso
                    premios.append({
                        "numero": numero,
                        "premio": float(premio),
                        "tipo": "fijo"
                    })
                    monto_total_premios += premio

        elif modalidad == 'corrido':
            for numero in self.numeros:
                if numero == valores['corrido1'] or numero == valores['corrido2']:
                    premio = self.monto_por_numero * self.modalidad.premio_por_peso
                    premios.append({
                        "numero": numero,
                        "premio": float(premio),
                        "tipo": "corrido"
                    })
                    monto_total_premios += premio

        elif modalidad == 'pick_3':
            for numero in self.numeros:
                if numero == valores['centena']:
                    premio = self.monto_por_numero * self.modalidad.premio_por_peso
                    premios.append({
                        "numero": numero,
                        "premio": float(premio),
                        "tipo": "pick_3"
                    })
                    monto_total_premios += premio

        elif modalidad == 'parle':
            numeros_validos = [valores['fijo'], valores['corrido1'], valores['corrido2']]
            
            if self.combinaciones_generadas:
                for pareja in self.combinaciones_generadas:
                    if pareja[0] in numeros_validos and pareja[1] in numeros_validos and pareja[0] != pareja[1]:
                        premio = self.monto_por_numero * self.modalidad.premio_por_peso
                        premios.append({
                            "numeros": pareja,
                            "premio": float(premio),
                            "tipo": "parle"
                        })
                        monto_total_premios += premio
            else:
                for pareja in self.numeros:
                    if len(pareja) == 2 and pareja[0] in numeros_validos and pareja[1] in numeros_validos and pareja[0] != pareja[1]:
                        premio = self.monto_por_numero * self.modalidad.premio_por_peso
                        premios.append({
                            "numeros": pareja,
                            "premio": float(premio),
                            "tipo": "parle"
                        })
                        monto_total_premios += premio

        self.premiados = premios
        self.premio_total = monto_total_premios
        self.paga = monto_total_premios > 0
        return monto_total_premios

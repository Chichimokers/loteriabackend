from rest_framework import serializers
from .models import Apuesta


class ApuestaSerializer(serializers.ModelSerializer):
    loteria_nombre = serializers.CharField(source='loteria.nombre', read_only=True)
    modalidad_nombre = serializers.CharField(source='modalidad.nombre', read_only=True)
    resultado = serializers.SerializerMethodField()

    class Meta:
        model = Apuesta
        fields = ['id', 'usuario', 'loteria', 'loteria_nombre', 'modalidad', 'modalidad_nombre', 
                  'tirada', 'numeros', 'monto_total', 'monto_por_numero', 'combinaciones_generadas',
                  'premiados', 'premio_total', 'paga', 'fecha', 'resultado']
        read_only_fields = ['id', 'usuario', 'monto_total', 'combinaciones_generadas', 
                           'premiados', 'premio_total', 'fecha', 'loteria_nombre', 
                           'modalidad_nombre', 'resultado', 'paga']

    def get_resultado(self, obj):
        resultado = obj.get_resultado()
        if resultado:
            return {
                'pick_3': resultado.pick_3,
                'pick_4': resultado.pick_4
            }
        return None


class ApuestaCreateSerializer(serializers.Serializer):
    tirada_id = serializers.IntegerField()
    numeros = serializers.ListField(child=serializers.CharField())
    monto_por_numero = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        from apps.loteria.models import Tirada, Modalidad
        
        tirada = Tirada.objects.filter(id=data['tirada_id'], activa=True).first()
        if not tirada:
            raise serializers.ValidationError({"tirada_id": "La tirada no existe o no está activa"})
        
        data['tirada'] = tirada
        
        modalidad_id = self.context.get('modalidad_id')
        modalidad = Modalidad.objects.filter(id=modalidad_id).first() if modalidad_id else None
        
        if not modalidad:
            raise serializers.ValidationError({"modalidad_id": "Modalidad no encontrada"})
        
        data['modalidad'] = modalidad
        numeros = data['numeros']
        
        if not numeros:
            raise serializers.ValidationError({"numeros": "Debe enviar al menos un número"})

        if modalidad.nombre == 'fijo':
            for n in numeros:
                if len(n) != 2 or not n.isdigit():
                    raise serializers.ValidationError(
                        {"numeros": f"Fijo requiere números de 2 dígitos. '{n}' no es válido"}
                    )

        elif modalidad.nombre == 'corrido':
            for n in numeros:
                if len(n) != 2 or not n.isdigit():
                    raise serializers.ValidationError(
                        {"numeros": f"Corrido requiere números de 2 dígitos. '{n}' no es válido"}
                    )

        elif modalidad.nombre == 'pick_3':
            for n in numeros:
                if len(n) != 3 or not n.isdigit():
                    raise serializers.ValidationError(
                        {"numeros": f"Pick 3 requiere números de 3 dígitos. '{n}' no es válido"}
                    )

        elif modalidad.nombre == 'parle':
            for pareja in numeros:
                if not isinstance(pareja, list) or len(pareja) != 2:
                    raise serializers.ValidationError(
                        {"numeros": "Parlé requiere parejas de 2 números. Ejemplo: [['37','75']]"}
                    )
                for n in pareja:
                    if len(n) != 2 or not n.isdigit():
                        raise serializers.ValidationError(
                            {"numeros": f"Cada número del parlé debe tener 2 dígitos. '{n}' no es válido"}
                        )

        return data


class CandadoCreateSerializer(serializers.Serializer):
    tirada_id = serializers.IntegerField()
    numeros = serializers.ListField(child=serializers.CharField())
    monto_por_numero = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        from apps.loteria.models import Tirada
        
        tirada = Tirada.objects.filter(id=data['tirada_id'], activa=True).first()
        if not tirada:
            raise serializers.ValidationError({"tirada_id": "La tirada no existe o no está activa"})
        
        data['tirada'] = tirada
        numeros = data['numeros']
        
        if len(numeros) < 2:
            raise serializers.ValidationError({"numeros": "Candado requiere mínimo 2 números"})
        
        for n in numeros:
            if len(n) != 2 or not n.isdigit():
                raise serializers.ValidationError(
                    {"numeros": f"Candado requiere números de 2 dígitos. '{n}' no es válido"}
                )

        return data

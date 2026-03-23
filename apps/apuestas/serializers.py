from rest_framework import serializers
from .models import Apuesta


class ApuestaSerializer(serializers.ModelSerializer):
    loteria_nombre = serializers.CharField(source='loteria.nombre', read_only=True)
    modalidad_nombre = serializers.CharField(source='modalidad.nombre', read_only=True)
    resultado = serializers.SerializerMethodField()

    class Meta:
        model = Apuesta
        fields = ['id', 'usuario', 'loteria', 'loteria_nombre', 'modalidad', 'modalidad_nombre', 
                  'tirada', 'numeros', 'monto_total', 'monto_por_numero', 
                  'premiados', 'premio_total', 'paga', 'fecha', 'resultado']
        read_only_fields = ['id', 'usuario', 'monto_total', 'premiados', 'premio_total', 'fecha', 'loteria_nombre', 'modalidad_nombre', 'resultado', 'paga']

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
    numeros = serializers.ListField(child=serializers.CharField(min_length=3, max_length=3))
    monto_por_numero = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        from apps.loteria.models import Tirada, Modalidad
        
        tirada = Tirada.objects.filter(id=data['tirada_id'], activa=True).first()
        if not tirada:
            raise serializers.ValidationError({"tirada_id": "La tirada no existe o no está activa"})
        
        data['tirada'] = tirada
        
        modalidad = Modalidad.objects.filter(id=self.context.get('modalidad_id')).first() if self.context.get('modalidad_id') else None
        
        for numero in data['numeros']:
            if len(numero) != 3 or not numero.isdigit():
                raise serializers.ValidationError({"numeros": f"El número {numero} debe tener 3 dígitos"})
        
        return data

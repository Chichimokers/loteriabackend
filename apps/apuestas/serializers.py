from rest_framework import serializers
from .models import Apuesta


class ApuestaSerializer(serializers.ModelSerializer):
    loteria_nombre = serializers.CharField(source='loteria.nombre', read_only=True)
    modalidad_nombre = serializers.CharField(source='modalidad.nombre', read_only=True)
    tirada_info = serializers.SerializerMethodField()

    class Meta:
        model = Apuesta
        fields = ['id', 'usuario', 'loteria', 'loteria_nombre', 'modalidad', 'modalidad_nombre', 
                  'tirada', 'tirada_info', 'numeros', 'monto_total', 'monto_por_numero', 
                  'premiados', 'premio_total', 'fecha']
        read_only_fields = ['id', 'usuario', 'monto_total', 'premiados', 'premio_total', 'fecha', 'loteria_nombre', 'modalidad_nombre', 'tirada_info']

    def get_tirada_info(self, obj):
        return {
            'fecha': str(obj.tirada.fecha),
            'hora': str(obj.tirada.hora),
            'pick_3': obj.tirada.pick_3,
            'pick_4': obj.tirada.pick_4
        }


class ApuestaCreateSerializer(serializers.Serializer):
    loteria_id = serializers.IntegerField()
    modalidad_id = serializers.IntegerField()
    tirada_id = serializers.IntegerField()
    numeros = serializers.ListField(child=serializers.CharField(min_length=3, max_length=3))
    monto_por_numero = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        from apps.loteria.models import Tirada, Modalidad
        
        tirada = Tirada.objects.filter(id=data['tirada_id'], activa=True).first()
        if not tirada:
            raise serializers.ValidationError({"tirada_id": "La tirada no existe o no está activa"})
        
        modalidad = Modalidad.objects.filter(id=data['modalidad_id']).first()
        if not modalidad:
            raise serializers.ValidationError({"modalidad_id": "La modalidad no existe"})
        
        for numero in data['numeros']:
            if len(numero) != 3 or not numero.isdigit():
                raise serializers.ValidationError({"numeros": f"El número {numero} debe tener 3 dígitos"})
        
        return data

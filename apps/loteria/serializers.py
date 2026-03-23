from rest_framework import serializers
from .models import Modalidad, Loteria, Tirada, Resultado


class ModalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modalidad
        fields = ['id', 'nombre', 'premio_por_peso', 'descripcion']
        read_only_fields = ['id']


class LoteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loteria
        fields = ['id', 'nombre', 'foto', 'activa']
        read_only_fields = ['id']
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.foto:
            ret['foto'] = instance.foto.url
        else:
            ret['foto'] = None
        return ret


class ResultadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resultado
        fields = ['id', 'tirada', 'fecha', 'pick_3', 'pick_4']
        read_only_fields = ['id']


class TiradaSerializer(serializers.ModelSerializer):
    loteria_nombre = serializers.CharField(source='loteria.nombre', read_only=True)
    resultado_hoy = serializers.SerializerMethodField()

    class Meta:
        model = Tirada
        fields = ['id', 'loteria', 'loteria_nombre', 'hora', 'activa', 'resultado_hoy']
        read_only_fields = ['id', 'loteria_nombre']
    
    def get_resultado_hoy(self, obj):
        from datetime import date
        hoy = date.today()
        resultado = obj.resultados.filter(fecha=hoy).first()
        if resultado:
            return {
                'pick_3': resultado.pick_3,
                'pick_4': resultado.pick_4,
                'fecha': str(resultado.fecha)
            }
        return None


class IngresarResultadoSerializer(serializers.Serializer):
    tirada_id = serializers.IntegerField()
    pick_3 = serializers.CharField(max_length=3, min_length=3, required=False, allow_blank=True)
    pick_4 = serializers.CharField(max_length=4, min_length=4, required=False, allow_blank=True)

    def validate(self, data):
        if not data.get('pick_3') and not data.get('pick_4'):
            raise serializers.ValidationError("Debe proporcionar al menos pick_3 o pick_4")
        return data

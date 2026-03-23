from rest_framework import serializers
from .models import Modalidad, Loteria, Tirada


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


class TiradaSerializer(serializers.ModelSerializer):
    loteria_nombre = serializers.CharField(source='loteria.nombre', read_only=True)

    class Meta:
        model = Tirada
        fields = ['id', 'loteria', 'loteria_nombre', 'hora', 'fecha', 'es_recurrente', 'activa', 'pick_3', 'pick_4']
        read_only_fields = ['id', 'loteria_nombre']
    
    def validate(self, data):
        if not data.get('es_recurrente') and not data.get('fecha'):
            raise serializers.ValidationError("Debe proporcionar una fecha o marcar como recurrente")
        return data


class ResultadoSerializer(serializers.Serializer):
    tirada_id = serializers.IntegerField()
    pick_3 = serializers.CharField(max_length=3, min_length=3, required=False, allow_blank=True)
    pick_4 = serializers.CharField(max_length=4, min_length=4, required=False, allow_blank=True)

    def validate(self, data):
        if not data.get('pick_3') and not data.get('pick_4'):
            raise serializers.ValidationError("Debe proporcionar al menos un resultado (pick_3 o pick_4)")
        return data

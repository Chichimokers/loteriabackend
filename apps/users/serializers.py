from rest_framework import serializers
from .models import Usuario, TarjetaSistema, SolicitudAcreditacion, Extraccion


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'movil', 'saldo_principal', 'saldo_extraccion', 'tarjeta_bancaria', 'banco', 'fecha_registro', 'is_staff']
        read_only_fields = ['id', 'saldo_principal', 'saldo_extraccion', 'fecha_registro', 'is_staff']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['email', 'password', 'movil', 'tarjeta_bancaria', 'banco']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TarjetaSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TarjetaSistema
        fields = ['id', 'numero', 'movil', 'banco', 'activa']
        read_only_fields = ['id']


class SolicitudAcreditacionSerializer(serializers.ModelSerializer):
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    tarjeta_numero = serializers.CharField(source='tarjeta.numero', read_only=True)

    class Meta:
        model = SolicitudAcreditacion
        fields = ['id', 'usuario', 'usuario_email', 'tarjeta', 'tarjeta_numero', 'monto', 'sms_confirmacion', 'id_transferencia', 'estado', 'fecha']
        read_only_fields = ['id', 'usuario_email', 'tarjeta_numero', 'estado', 'fecha']


class SolicitudAcreditacionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudAcreditacion
        fields = ['tarjeta', 'monto', 'sms_confirmacion', 'id_transferencia']

    def validate(self, data):
        if data['monto'] <= 0:
            raise serializers.ValidationError({"monto": "El monto debe ser mayor que 0"})
        
        if not data['tarjeta'].activa:
            raise serializers.ValidationError({"tarjeta": "La tarjeta no está activa"})
        
        return data


class ExtraccionSerializer(serializers.ModelSerializer):
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)

    class Meta:
        model = Extraccion
        fields = ['id', 'usuario', 'usuario_email', 'monto', 'estado', 'fecha']
        read_only_fields = ['id', 'usuario_email', 'estado', 'fecha']


class ExtraccionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extraccion
        fields = ['monto']

    def validate(self, data):
        usuario = self.context['request'].user
        
        if data['monto'] <= 0:
            raise serializers.ValidationError({"monto": "El monto debe ser mayor que 0"})
        
        if usuario.saldo_extraccion < data['monto']:
            raise serializers.ValidationError({"monto": "Saldo insuficiente para extracción"})
        
        return data

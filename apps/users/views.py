from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Usuario, TarjetaSistema, SolicitudAcreditacion, Extraccion
from .serializers import (
    UsuarioSerializer, UsuarioCreateSerializer,
    TarjetaSistemaSerializer,
    SolicitudAcreditacionSerializer, SolicitudAcreditacionCreateSerializer,
    ExtraccionSerializer, ExtraccionCreateSerializer
)
from apps.notificaciones.views import crear_notificacion


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def usuario_me(request):
    if request.method == 'GET':
        return Response(UsuarioSerializer(request.user).data)
    
    serializer = UsuarioSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        crear_notificacion(
            usuario=None,
            tipo='nuevo_usuario',
            titulo='Nuevo usuario registrado',
            mensaje=f'El usuario {user.email} se ha registrado en el sistema',
            datos={'email': user.email, 'movil': user.movil, 'banco': user.banco}
        )
        
        return Response(UsuarioSerializer(user).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def ajustar_saldo(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        usuario = get_object_or_404(Usuario, pk=pk)
        
        monto = request.data.get('monto')
        tipo = request.data.get('tipo', 'principal')
        operacion = request.data.get('operacion', 'sumar')
        
        if monto is None:
            return Response({'error': 'monto es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            monto = float(monto)
        except (ValueError, TypeError):
            return Response({'error': 'monto debe ser un número'}, status=status.HTTP_400_BAD_REQUEST)
        
        if monto <= 0:
            return Response({'error': 'monto debe ser mayor que 0'}, status=status.HTTP_400_BAD_REQUEST)
        
        if tipo not in ['principal', 'extraccion']:
            return Response({'error': 'tipo debe ser "principal" o "extraccion"'}, status=status.HTTP_400_BAD_REQUEST)
        
        if operacion not in ['sumar', 'restar']:
            return Response({'error': 'operacion debe ser "sumar" o "restar"'}, status=status.HTTP_400_BAD_REQUEST)
        
        if tipo == 'principal':
            if operacion == 'sumar':
                usuario.saldo_principal += monto
            else:
                if usuario.saldo_principal < monto:
                    return Response({'error': 'Saldo insuficiente para restar'}, status=status.HTTP_400_BAD_REQUEST)
                usuario.saldo_principal -= monto
        else:
            if operacion == 'sumar':
                usuario.saldo_extraccion += monto
            else:
                if usuario.saldo_extraccion < monto:
                    return Response({'error': 'Saldo de extracción insuficiente para restar'}, status=status.HTTP_400_BAD_REQUEST)
                usuario.saldo_extraccion -= monto
        
        usuario.save()
        
        crear_notificacion(
            usuario=usuario,
            tipo='saldo_ajustado',
            titulo='Saldo ajustado por administrador',
            mensaje=f'Tu saldo {tipo} fue {"aumentado" if operacion == "sumar" else "reducido"} en {monto} CUP por un administrador',
            datos={
                'tipo': tipo,
                'operacion': operacion,
                'monto': monto,
                'saldo_principal': str(usuario.saldo_principal),
                'saldo_extraccion': str(usuario.saldo_extraccion)
            }
        )
        
        return Response({
            'message': f'Saldo {tipo} actualizado correctamente',
            'usuario': usuario.email,
            'saldo_principal': str(usuario.saldo_principal),
            'saldo_extraccion': str(usuario.saldo_extraccion)
        })


class TarjetaSistemaViewSet(viewsets.ModelViewSet):
    queryset = TarjetaSistema.objects.all()
    serializer_class = TarjetaSistemaSerializer
    permission_classes = [IsAuthenticated]


class SolicitudAcreditacionViewSet(viewsets.ModelViewSet):
    queryset = SolicitudAcreditacion.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SolicitudAcreditacionCreateSerializer
        return SolicitudAcreditacionSerializer
    
    def get_queryset(self):
        queryset = SolicitudAcreditacion.objects.all() if self.request.user.is_staff else SolicitudAcreditacion.objects.filter(usuario=self.request.user)
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset
    
    def perform_create(self, serializer):
        acreditacion = serializer.save(usuario=self.request.user)
        
        crear_notificacion(
            usuario=None,
            tipo='acreditacion_pendiente',
            titulo='Nueva solicitud de acreditación',
            mensaje=f'El usuario {self.request.user.email} solicita acreditación de {acreditacion.monto} CUP',
            datos={
                'usuario_email': self.request.user.email,
                'monto': str(acreditacion.monto),
                'tarjeta': acreditacion.tarjeta.numero,
                'id_transferencia': acreditacion.id_transferencia
            }
        )
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def aprobar(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        acreditacion = self.get_object()
        acreditacion.estado = 'aprobada'
        acreditacion.save()
        
        usuario = acreditacion.usuario
        usuario.saldo_principal += acreditacion.monto
        usuario.save()
        
        crear_notificacion(
            usuario=usuario,
            tipo='acreditacion_aprobada',
            titulo='Acreditación aprobada',
            mensaje=f'Tu solicitud de acreditación por {acreditacion.monto} CUP ha sido aprobada',
            datos={
                'monto': str(acreditacion.monto),
                'nuevo_saldo': str(usuario.saldo_principal)
            }
        )
        
        return Response(SolicitudAcreditacionSerializer(acreditacion).data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def rechazar(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        acreditacion = self.get_object()
        acreditacion.estado = 'rechazada'
        acreditacion.save()
        
        crear_notificacion(
            usuario=acreditacion.usuario,
            tipo='acreditacion_rechazada',
            titulo='Acreditación rechazada',
            mensaje=f'Tu solicitud de acreditación por {acreditacion.monto} CUP ha sido rechazada',
            datos={'monto': str(acreditacion.monto)}
        )
        
        return Response(SolicitudAcreditacionSerializer(acreditacion).data)


class ExtraccionViewSet(viewsets.ModelViewSet):
    queryset = Extraccion.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ExtraccionCreateSerializer
        return ExtraccionSerializer
    
    def get_queryset(self):
        queryset = Extraccion.objects.all() if self.request.user.is_staff else Extraccion.objects.filter(usuario=self.request.user)
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset
    
    def perform_create(self, serializer):
        monto = serializer.validated_data['monto']
        usuario = self.request.user
        usuario.saldo_principal -= monto
        usuario.saldo_extraccion += monto
        usuario.save()
        extraccion = serializer.save(usuario=self.request.user)
        
        crear_notificacion(
            usuario=None,
            tipo='extraccion_pendiente',
            titulo='Nueva solicitud de extracción',
            mensaje=f'El usuario {usuario.email} solicita extracción de {monto} CUP',
            datos={
                'usuario_email': usuario.email,
                'monto': str(monto)
            }
        )
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def aprobar(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        extraccion = self.get_object()
        extraccion.estado = 'aprobada'
        extraccion.save()
        
        usuario = extraccion.usuario
        usuario.saldo_extraccion -= extraccion.monto
        usuario.save()
        
        crear_notificacion(
            usuario=usuario,
            tipo='extraccion_aprobada',
            titulo='Extracción aprobada',
            mensaje=f'Tu solicitud de extracción por {extraccion.monto} CUP ha sido aprobada. El dinero ha sido enviado.',
            datos={
                'monto': str(extraccion.monto),
                'nuevo_saldo_extraccion': str(usuario.saldo_extraccion)
            }
        )
        
        return Response(ExtraccionSerializer(extraccion).data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def rechazar(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        extraccion = self.get_object()
        extraccion.estado = 'rechazada'
        extraccion.save()
        
        usuario = extraccion.usuario
        usuario.saldo_extraccion -= extraccion.monto
        usuario.saldo_principal += extraccion.monto
        usuario.save()
        
        crear_notificacion(
            usuario=usuario,
            tipo='extraccion_rechazada',
            titulo='Extracción rechazada',
            mensaje=f'Tu solicitud de extracción por {extraccion.monto} CUP ha sido rechazada. El dinero ha sido devuelto a tu saldo principal.',
            datos={
                'monto': str(extraccion.monto),
                'nuevo_saldo_principal': str(usuario.saldo_principal)
            }
        )
        
        return Response(ExtraccionSerializer(extraccion).data)

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
        serializer.save(usuario=self.request.user)
    
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
        
        return Response(SolicitudAcreditacionSerializer(acreditacion).data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def rechazar(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        acreditacion = self.get_object()
        acreditacion.estado = 'rechazada'
        acreditacion.save()
        
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
        serializer.save(usuario=self.request.user)
    
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
        
        return Response(ExtraccionSerializer(extraccion).data)

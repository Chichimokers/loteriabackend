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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuario_me(request):
    return Response(UsuarioSerializer(request.user).data)


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
        serializer.save(usuario=self.request.user)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def aprobar(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        extraccion = self.get_object()
        extraccion.estado = 'aprobada'
        extraccion.save()
        
        return Response(ExtraccionSerializer(extraccion).data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def rechazar(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        extraccion = self.get_object()
        extraccion.estado = 'rechazada'
        extraccion.save()
        
        usuario = extraccion.usuario
        usuario.saldo_extraccion += extraccion.monto
        usuario.save()
        
        return Response(ExtraccionSerializer(extraccion).data)

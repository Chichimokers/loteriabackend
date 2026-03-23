from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from datetime import datetime

from .models import Modalidad, Loteria, Tirada
from .serializers import ModalidadSerializer, LoteriaSerializer, TiradaSerializer, ResultadoSerializer


class ModalidadViewSet(viewsets.ModelViewSet):
    queryset = Modalidad.objects.all()
    serializer_class = ModalidadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return Modalidad.objects.all()
        if not self.request.user.is_staff:
            return Modalidad.objects.none()
        return Modalidad.objects.all()


class LoteriaViewSet(viewsets.ModelViewSet):
    queryset = Loteria.objects.all()
    serializer_class = LoteriaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return Loteria.objects.filter(activa=True)
        if not self.request.user.is_staff:
            return Loteria.objects.none()
        return Loteria.objects.all()


class TiradaViewSet(viewsets.ModelViewSet):
    queryset = Tirada.objects.all()
    serializer_class = TiradaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Tirada.objects.all()
        
        if self.action in ['list', 'retrieve']:
            loteria_id = self.request.query_params.get('loteria_id')
            fecha = self.request.query_params.get('fecha')
            activa = self.request.query_params.get('activa')
            
            if loteria_id:
                queryset = queryset.filter(loteria_id=loteria_id)
            if fecha:
                queryset = queryset.filter(fecha=fecha)
            if activa is not None:
                queryset = queryset.filter(activa=activa.lower() == 'true')
            
            return queryset
        
        if not self.request.user.is_staff:
            return Tirada.objects.none()
        return queryset
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        from datetime import date, timedelta
        now = timezone.now()
        hoy = now.date()
        ayer = hoy - timedelta(days=1)
        
        # Mostrar tiradas de hoy y ayer que aún no están cerradas
        # Las tiradas recurrentes se consideran del día anterior
        from django.db.models import Q
        tiradas = Tirada.objects.filter(
            Q(es_recurrente=True, activa=True, loteria__activa=True) |
            Q(es_recurrente=False, activa=True, fecha__gte=hoy, loteria__activa=True)
        ).order_by('hora')
        
        serializer = self.get_serializer(tiradas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def resultados(self, request):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ResultadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tirada = get_object_or_404(Tirada, id=serializer.validated_data['tirada_id'])
        
        # Validar que la tirada sea de hoy o ayer
        from datetime import date, timedelta
        hoy = date.today()
        ayer = hoy - timedelta(days=1)
        
        if tirada.es_recurrente:
            # Las tiradas recurrentes se cerraron ayer
            pass
        elif tirada.fecha not in [hoy, ayer]:
            return Response(
                {'error': 'Solo se pueden ingresar resultados de tiradas de hoy o ayer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if serializer.validated_data.get('pick_3'):
            tirada.pick_3 = serializer.validated_data['pick_3']
        if serializer.validated_data.get('pick_4'):
            tirada.pick_4 = serializer.validated_data['pick_4']
        
        tirada.activa = False  # Marcar como inactiva después de ingresar resultados
        tirada.save()
        
        from apps.apuestas.models import Apuesta
        apuestas = Apuesta.objects.filter(tirada=tirada)
        for apuesta in apuestas:
            apuesta.calcular_premios()
            apuesta.save()
            
            if apuesta.premio_total > 0:
                usuario = apuesta.usuario
                usuario.saldo_principal += apuesta.premio_total
                usuario.save()
        
        return Response(TiradaSerializer(tirada).data)


from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Modalidad, Loteria, Tirada, Resultado
from .serializers import ModalidadSerializer, LoteriaSerializer, TiradaSerializer, ResultadoSerializer, IngresarResultadoSerializer


class ResultadoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Resultado.objects.all()
    serializer_class = ResultadoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Resultado.objects.all()
        fecha = self.request.query_params.get('fecha')
        loteria = self.request.query_params.get('loteria')
        
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        if loteria:
            queryset = queryset.filter(tirada__loteria__id=loteria)
        return queryset


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
        queryset = Tirada.objects.filter(loteria__activa=True)
        
        if self.action in ['list', 'retrieve', 'activas']:
            loteria_id = self.request.query_params.get('loteria_id')
            if loteria_id:
                queryset = queryset.filter(loteria_id=loteria_id)
            return queryset
        
        if not self.request.user.is_staff:
            return Tirada.objects.none()
        return queryset
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        tiradas = self.get_queryset().filter(activa=True).order_by('hora')
        serializer = self.get_serializer(tiradas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def resultados_hoy(self, request):
        from datetime import date
        hoy = date.today()
        
        tiradas = self.get_queryset().filter(activa=True)
        resultados = []
        
        for tirada in tiradas:
            resultado = tirada.resultados.filter(fecha=hoy).first()
            resultados.append({
                'id': tirada.id,
                'loteria': tirada.loteria.nombre,
                'hora': str(tirada.hora),
                'resultado': {
                    'pick_3': resultado.pick_3 if resultado else None,
                    'pick_4': resultado.pick_4 if resultado else None
                } if resultado else None
            })
        
        return Response(resultados)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def ingresar_resultado(self, request):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = IngresarResultadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        tirada = get_object_or_404(Tirada, id=serializer.validated_data['tirada_id'])
        
        from datetime import date
        hoy = date.today()
        
        if Resultado.objects.filter(tirada=tirada, fecha=hoy).exists():
            return Response(
                {'error': 'Esta tirada ya tiene un resultado asignado para hoy'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resultado = Resultado.objects.create(
            tirada=tirada,
            fecha=hoy,
            pick_3=serializer.validated_data.get('pick_3', ''),
            pick_4=serializer.validated_data.get('pick_4', '')
        )
        
        self._calcular_premios(tirada, hoy)
        
        return Response({
            'message': 'Resultado guardado',
            'resultado': {
                'tirada': tirada.loteria.nombre,
                'hora': str(tirada.hora),
                'fecha': str(hoy),
                'pick_3': resultado.pick_3,
                'pick_4': resultado.pick_4
            }
        }, status=status.HTTP_201_CREATED)
    
    def _calcular_premios(self, tirada, fecha):
        from apps.apuestas.models import Apuesta
        
        apuestas = Apuesta.objects.filter(tirada=tirada, fecha=fecha)
        
        for apuesta in apuestas:
            apuesta.calcular_premios()
            apuesta.save()
            
            if apuesta.premio_total > 0:
                usuario = apuesta.usuario
                usuario.saldo_principal += apuesta.premio_total
                usuario.save()

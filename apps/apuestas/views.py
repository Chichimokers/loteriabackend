from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.loteria.models import Loteria, Modalidad, Tirada
from .models import Apuesta
from .serializers import ApuestaSerializer, ApuestaCreateSerializer


class ApuestaViewSet(viewsets.ModelViewSet):
    queryset = Apuesta.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ApuestaCreateSerializer
        return ApuestaSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Apuesta.objects.all()
        return Apuesta.objects.filter(usuario=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = ApuestaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        usuario = request.user
        monto_por_numero = serializer.validated_data['monto_por_numero']
        numeros = serializer.validated_data['numeros']
        monto_total = monto_por_numero * len(numeros)
        
        if usuario.saldo_principal < monto_total:
            return Response(
                {'error': 'Saldo insuficiente'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loteria = get_object_or_404(Loteria, id=serializer.validated_data['loteria_id'], activa=True)
        modalidad = get_object_or_404(Modalidad, id=serializer.validated_data['modalidad_id'])
        tirada = get_object_or_404(Tirada, id=serializer.validated_data['tirada_id'], activa=True)
        
        apuesta = Apuesta.objects.create(
            usuario=usuario,
            loteria=loteria,
            modalidad=modalidad,
            tirada=tirada,
            numeros=numeros,
            monto_total=monto_total,
            monto_por_numero=monto_por_numero
        )
        
        usuario.saldo_principal -= monto_total
        usuario.save()
        
        return Response(ApuestaSerializer(apuesta).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def mis_apuestas(self, request):
        apuestas = Apuesta.objects.filter(usuario=request.user).order_by('-fecha')
        serializer = self.get_serializer(apuestas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def calcular_premios(self, request, pk=None):
        apuesta = self.get_object()
        apuesta.calcular_premios()
        apuesta.save()
        return Response(ApuestaSerializer(apuesta).data)

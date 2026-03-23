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
        modalidad_id = request.data.get('modalidad_id')
        tirada_id = request.data.get('tirada_id')
        
        if not modalidad_id:
            return Response({'error': 'modalidad_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        modalidad = get_object_or_404(Modalidad, id=modalidad_id)
        tirada = get_object_or_404(Tirada, id=tirada_id, activa=True)
        
        serializer = self.get_serializer(data=request.data)
        serializer.context['modalidad_id'] = modalidad_id
        serializer.is_valid(raise_exception=True)
        
        numeros = serializer.validated_data['numeros']
        monto_por_numero = serializer.validated_data['monto_por_numero']
        monto_total = monto_por_numero * len(numeros)
        
        if request.user.saldo_principal < monto_total:
            return Response({'error': 'Saldo insuficiente'}, status=status.HTTP_400_BAD_REQUEST)
        
        from datetime import date
        apuesta = Apuesta.objects.create(
            usuario=request.user,
            loteria=tirada.loteria,
            modalidad=modalidad,
            tirada=tirada,
            numeros=numeros,
            monto_total=monto_total,
            monto_por_numero=monto_por_numero,
            fecha=date.today()
        )
        
        request.user.saldo_principal -= monto_total
        request.user.save()
        
        return Response(ApuestaSerializer(apuesta).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def mis_apuestas(self, request):
        apuestas = self.get_queryset().order_by('-fecha')
        serializer = self.get_serializer(apuestas, many=True)
        return Response(serializer.data)

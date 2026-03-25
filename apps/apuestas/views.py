from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date
from itertools import combinations

from apps.loteria.models import Loteria, Modalidad, Tirada, Resultado
from .models import Apuesta
from .serializers import ApuestaSerializer, ApuestaCreateSerializer, CandadoCreateSerializer
from apps.notificaciones.views import crear_notificacion


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
    
    def _validar_tirada(self, tirada):
        hoy = date.today()
        ahora = timezone.now()
        
        if Resultado.objects.filter(tirada=tirada, fecha=hoy).exists():
            return {'error': 'No se puede apostar a una tirada que ya tiene resultado'}
        
        if ahora.time() >= tirada.hora:
            return {'error': f'No se puede apostar. La tirada es a las {tirada.hora} y ya son las {ahora.time()}'}
        
        return None

    def _obtener_numeros_previos(self, usuario, tirada, fecha):
        apuestas_previas = Apuesta.objects.filter(
            usuario=usuario,
            tirada=tirada,
            fecha=fecha
        )
        
        numeros_previos = set()
        parejas_previas = set()
        
        for apuesta in apuestas_previas:
            if apuesta.modalidad.nombre in ['fijo', 'corrido', 'pick_3']:
                for n in apuesta.numeros:
                    numeros_previos.add(n)
            elif apuesta.modalidad.nombre == 'parle':
                if apuesta.combinaciones_generadas:
                    for pareja in apuesta.combinaciones_generadas:
                        parejas_previas.add(tuple(sorted(pareja)))
                else:
                    for pareja in apuesta.numeros:
                        if isinstance(pareja, list) and len(pareja) == 2:
                            parejas_previas.add(tuple(sorted(pareja)))
        
        return numeros_previos, parejas_previas

    def create(self, request, *args, **kwargs):
        modalidad_id = request.data.get('modalidad_id')
        tirada_id = request.data.get('tirada_id')
        
        if not modalidad_id:
            return Response({'error': 'modalidad_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        modalidad = get_object_or_404(Modalidad, id=modalidad_id)
        tirada = get_object_or_404(Tirada, id=tirada_id, activa=True)
        
        error = self._validar_tirada(tirada)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.context['modalidad_id'] = modalidad_id
        serializer.is_valid(raise_exception=True)
        
        numeros = serializer.validated_data['numeros']
        monto_por_numero = serializer.validated_data['monto_por_numero']
        monto_total = monto_por_numero * len(numeros)
        
        numeros_previos, parejas_previas = self._obtener_numeros_previos(request.user, tirada, date.today())
        
        if modalidad.nombre in ['fijo', 'corrido', 'pick_3']:
            for n in numeros:
                if n in numeros_previos:
                    return Response(
                        {'error': f'El número {n} ya fue apostado hoy en esta tirada'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        elif modalidad.nombre == 'parle':
            for pareja in numeros:
                pareja_norm = tuple(sorted(pareja))
                if pareja_norm in parejas_previas:
                    return Response(
                        {'error': f'La pareja {pareja} ya fue apostada hoy en esta tirada'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        if request.user.saldo_principal < monto_total:
            return Response({'error': 'Saldo insuficiente'}, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        crear_notificacion(
            usuario=None,
            tipo='apuesta_creada',
            titulo='Nueva apuesta registrada',
            mensaje=f'{request.user.email} apostó {monto_total} CUP en {tirada.loteria.nombre} ({modalidad.nombre})',
            datos={
                'usuario_email': request.user.email,
                'loteria': tirada.loteria.nombre,
                'modalidad': modalidad.nombre,
                'tirada_hora': str(tirada.hora),
                'numeros': numeros,
                'monto_total': str(monto_total)
            }
        )
        
        return Response(ApuestaSerializer(apuesta).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def candado(self, request):
        tirada_id = request.data.get('tirada_id')
        
        if not tirada_id:
            return Response({'error': 'tirada_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        tirada = get_object_or_404(Tirada, id=tirada_id, activa=True)
        modalidad = get_object_or_404(Modalidad, nombre='parle')
        
        error = self._validar_tirada(tirada)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CandadoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        numeros = serializer.validated_data['numeros']
        monto_por_numero = serializer.validated_data['monto_por_numero']
        
        combinaciones = list(combinations(numeros, 2))
        combinaciones_generadas = [list(c) for c in combinaciones]
        monto_total = monto_por_numero * len(combinaciones_generadas)
        
        numeros_previos, parejas_previas = self._obtener_numeros_previos(request.user, tirada, date.today())
        
        for n in numeros:
            if n in numeros_previos:
                return Response(
                    {'error': f'El número {n} ya fue apostado hoy en esta tirada'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        for pareja in combinaciones:
            pareja_norm = tuple(sorted(pareja))
            if pareja_norm in parejas_previas:
                return Response(
                    {'error': f'La pareja {list(pareja)} ya fue apostada hoy en esta tirada'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if request.user.saldo_principal < monto_total:
            return Response({'error': 'Saldo insuficiente'}, status=status.HTTP_400_BAD_REQUEST)
        
        apuesta = Apuesta.objects.create(
            usuario=request.user,
            loteria=tirada.loteria,
            modalidad=modalidad,
            tirada=tirada,
            numeros=numeros,
            monto_total=monto_total,
            monto_por_numero=monto_por_numero,
            combinaciones_generadas=combinaciones_generadas,
            fecha=date.today()
        )
        
        request.user.saldo_principal -= monto_total
        request.user.save()
        
        crear_notificacion(
            usuario=None,
            tipo='apuesta_creada',
            titulo='Nueva apuesta de candado registrada',
            mensaje=f'{request.user.email} apostó {monto_total} CUP en candado de {tirada.loteria.nombre}',
            datos={
                'usuario_email': request.user.email,
                'loteria': tirada.loteria.nombre,
                'modalidad': 'candado',
                'tirada_hora': str(tirada.hora),
                'numeros': numeros,
                'combinaciones': len(combinaciones_generadas),
                'monto_total': str(monto_total)
            }
        )
        
        return Response(ApuestaSerializer(apuesta).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def mis_apuestas(self, request):
        apuestas = self.get_queryset().order_by('-fecha')
        serializer = self.get_serializer(apuestas, many=True)
        return Response(serializer.data)

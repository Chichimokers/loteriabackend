from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notificacion
from .serializers import NotificacionSerializer


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        count = Notificacion.objects.filter(usuario=request.user, leida=False).count()
        return Response({'no_leidas': count})

    @action(detail=False, methods=['get'])
    def admin(self, request):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        notificaciones = Notificacion.objects.filter(usuario=None)
        serializer = self.get_serializer(notificaciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def admin_no_leidas(self, request):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        count = Notificacion.objects.filter(usuario=None, leida=False).count()
        return Response({'no_leidas': count})

    @action(detail=True, methods=['patch'])
    def leer(self, request, pk=None):
        notificacion = self.get_object()
        notificacion.leida = True
        notificacion.save()
        return Response(NotificacionSerializer(notificacion).data)

    @action(detail=False, methods=['patch'])
    def leer_todas(self, request):
        Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
        return Response({'message': 'Todas las notificaciones marcadas como leídas'})

    @action(detail=False, methods=['patch'])
    def admin_leer_todas(self, request):
        if not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        Notificacion.objects.filter(usuario=None, leida=False).update(leida=True)
        return Response({'message': 'Todas las notificaciones de admin marcadas como leídas'})


def crear_notificacion(usuario=None, tipo='', titulo='', mensaje='', datos=None):
    return Notificacion.objects.create(
        usuario=usuario,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        datos=datos
    )

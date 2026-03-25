# SISTEMA DE NOTIFICACIONES - Lotería Backend

## Fecha: 2026-03-25

---

## RESUMEN

Se implementó un sistema completo de notificaciones basado en polling que permite a los clientes y administradores recibir alertas sobre eventos importantes del sistema.

---

## MODELO DE DATOS

### Tabla: `notificaciones_notificacion`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | BigAutoField | Identificador único |
| `usuario` | ForeignKey (nullable) | Usuario destinatario. NULL = notificación de admin |
| `tipo` | CharField | Tipo de evento (ver tabla de tipos) |
| `titulo` | CharField | Título corto de la notificación |
| `mensaje` | TextField | Mensaje completo |
| `datos` | JSONField (nullable) | Datos adicionales (monto, números, etc.) |
| `leida` | BooleanField | Si la notificación fue leída (default=False) |
| `fecha` | DateTimeField | Fecha de creación (auto) |

---

## TIPOS DE NOTIFICACIÓN

### Para el CLIENTE (usuario != NULL)

| Tipo | Evento que lo dispara |
|------|----------------------|
| `acreditacion_aprobada` | Admin aprueba solicitud de acreditación |
| `acreditacion_rechazada` | Admin rechaza solicitud de acreditación |
| `extraccion_aprobada` | Admin aprueba solicitud de extracción |
| `extraccion_rechazada` | Admin rechaza solicitud de extracción |
| `saldo_ajustado` | Admin ajusta saldo manualmente |
| `apuesta_ganadora` | Apuesta obtuvo premio |
| `apuesta_perdedora` | Apuesta no obtuvo premio |
| `resultado_publicado` | Resultado de lotería fue publicado |

### Para el ADMIN (usuario = NULL)

| Tipo | Evento que lo dispara |
|------|----------------------|
| `nuevo_usuario` | Nuevo usuario se registra |
| `acreditacion_pendiente` | Usuario solicita acreditación |
| `extraccion_pendiente` | Usuario solicita extracción |
| `apuesta_creada` | Usuario crea apuesta (normal o candado) |

---

## ENDPOINTS

### Para CLIENTES (autenticado)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/notificaciones/` | GET | Listar mis notificaciones |
| `/api/v1/notificaciones/{id}/` | GET | Ver detalle de notificación |
| `/api/v1/notificaciones/no_leidas/` | GET | Contar notificaciones no leídas |
| `/api/v1/notificaciones/{id}/leer/` | PATCH | Marcar notificación como leída |
| `/api/v1/notificaciones/leer_todas/` | PATCH | Marcar todas como leídas |

### Para ADMIN (autenticado + is_staff=True)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/notificaciones/admin/` | GET | Listar notificaciones de admin |
| `/api/v1/notificaciones/admin/no_leidas/` | GET | Contar notificaciones no leídas de admin |
| `/api/v1/notificaciones/admin/leer_todas/` | PATCH | Marcar todas como leídas |

---

## EJEMPLOS DE USO

### Contar notificaciones no leídas
```
GET /api/v1/notificaciones/no_leidas/

Response:
{
    "no_leidas": 5
}
```

### Listar notificaciones
```
GET /api/v1/notificaciones/

Response:
[
    {
        "id": 1,
        "usuario": 1,
        "tipo": "acreditacion_aprobada",
        "titulo": "Acreditación aprobada",
        "mensaje": "Tu solicitud de acreditación por 500 CUP ha sido aprobada",
        "datos": {
            "monto": "500",
            "nuevo_saldo": "1500"
        },
        "leida": false,
        "fecha": "2026-03-25T14:30:00Z"
    }
]
```

### Marcar como leída
```
PATCH /api/v1/notificaciones/1/leer/

Response:
{
    "id": 1,
    "usuario": 1,
    "tipo": "acreditacion_aprobada",
    "titulo": "Acreditación aprobada",
    "mensaje": "Tu solicitud de acreditación por 500 CUP ha sido aprobada",
    "datos": {...},
    "leida": true,
    "fecha": "2026-03-25T14:30:00Z"
}
```

### Notificaciones de admin
```
GET /api/v1/notificaciones/admin/

Response:
[
    {
        "id": 10,
        "usuario": null,
        "tipo": "nuevo_usuario",
        "titulo": "Nuevo usuario registrado",
        "mensaje": "El usuario cliente@example.com se ha registrado en el sistema",
        "datos": {
            "email": "cliente@example.com",
            "movil": "5351234567",
            "banco": "metropolitano"
        },
        "leida": false,
        "fecha": "2026-03-25T10:00:00Z"
    }
]
```

---

## ARCHIVOS CREADOS

| Archivo | Descripción |
|---------|-------------|
| `apps/notificaciones/__init__.py` | Init de la app |
| `apps/notificaciones/apps.py` | Configuración de la app |
| `apps/notificaciones/models.py` | Modelo Notificacion |
| `apps/notificaciones/serializers.py` | Serializer |
| `apps/notificaciones/views.py` | ViewSet + función crear_notificacion |
| `apps/notificaciones/urls.py` | Rutas |
| `apps/notificaciones/admin.py` | Admin de Django |
| `apps/notificaciones/migrations/0001_initial.py` | Migración inicial |

## ARCHIVOS MODIFICADOS

| Archivo | Cambio |
|---------|--------|
| `config/settings.py` | Agregado `apps.notificaciones` a INSTALLED_APPS |
| `config/urls.py` | Agregada ruta `/api/v1/notificaciones/` |
| `apps/users/views.py` | Notificaciones en: registro, acreditación, extracción, ajustar_saldo |
| `apps/loteria/views.py` | Notificaciones en: ingresar_resultado, _calcular_premios |
| `apps/apuestas/views.py` | Notificaciones en: create, candado |

---

## FUNCIÓN HELPER

La función `crear_notificacion` está disponible para crear notificaciones desde cualquier parte del sistema:

```python
from apps.notificaciones.views import crear_notificacion

crear_notificacion(
    usuario=None,  # NULL para admin, objeto Usuario para cliente
    tipo='nuevo_usuario',
    titulo='Nuevo usuario registrado',
    mensaje='El usuario cliente@example.com se ha registrado',
    datos={'email': 'cliente@example.com', 'banco': 'metropolitano'}
)
```

---

## NOTAS IMPORTANTES

1. **Sistema basado en polling**: El frontend debe consultar los endpoints cada X segundos para obtener nuevas notificaciones
2. **Notificaciones de admin**: Se guardan con `usuario=NULL` y solo son accesibles por usuarios con `is_staff=True`
3. **Notificaciones de cliente**: Se guardan con `usuario=ID` y solo son accesibles por el propietario
4. **Campo datos**: Contiene información adicional relevante al evento (monto, números, etc.)
5. **Sin notificaciones en tiempo real**: El sistema no usa WebSocket, es polling simple

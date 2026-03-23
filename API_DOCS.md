# Documentación de API - Loteria Backend

## Base URL
```
https://inventory.cloudns.be/api/v1/
```

---

## Autenticación

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/usuarios/` | Registrar nuevo usuario | No |
| POST | `/usuarios/token/` | Obtener access token | No |
| POST | `/usuarios/token/refresh/` | Refrescar access token | No |
| GET | `/usuarios/me/` | Obtener perfil actual | Sí |

### Registro de Usuario
```http
POST /api/v1/usuarios/
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "contraseña123",
  "movil": "5351234567",
  "tarjeta_bancaria": "1234567890123456",
  "banco": "metropolitano"
}
```
**Bancos válidos:** `metropolitano`, `bandec`, `bpa`, `monedero`

### Login
```http
POST /api/v1/usuarios/token/
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "contraseña123"
}
```
**Respuesta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "email": "usuario@example.com"
}
```

### Refresh Token
```http
POST /api/v1/usuarios/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Usuarios

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/usuarios/` | Listar todos los usuarios | Admin |
| POST | `/usuarios/` | Registrar usuario | No |
| GET | `/usuarios/{id}/` | Ver usuario específico | Sí |
| PATCH | `/usuarios/{id}/` | Actualizar usuario | Sí |
| GET | `/usuarios/me/` | Mi perfil | Sí |

### Mi Perfil
```http
GET /api/v1/usuarios/me/
Authorization: Bearer <token>
```
**Respuesta:**
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "movil": "5351234567",
  "saldo_principal": "1000.00",
  "saldo_extraccion": "500.00",
  "tarjeta_bancaria": "1234567890123456",
  "banco": "metropolitano",
  "fecha_registro": "2026-03-23T10:00:00Z"
}
```

---

## Tarjetas del Sistema

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/usuarios/tarjetas/` | Listar tarjetas activas | Sí |
| POST | `/usuarios/tarjetas/` | Crear tarjeta | Admin |
| GET | `/usuarios/tarjetas/{id}/` | Ver tarjeta | Admin |
| PATCH | `/usuarios/tarjetas/{id}/` | Editar tarjeta | Admin |
| DELETE | `/usuarios/tarjetas/{id}/` | Eliminar tarjeta | Admin |

### Crear Tarjeta (Admin)
```http
POST /api/v1/usuarios/tarjetas/
Authorization: Bearer <token_admin>
Content-Type: application/json

{
  "numero": "1234567890123456",
  "movil": "5351234567",
  "banco": "metropolitano",
  "activa": true
}
```

### Listar Tarjetas Activas
```http
GET /api/v1/usuarios/tarjetas/
Authorization: Bearer <token>
```
**Respuesta:**
```json
[
  {
    "id": 1,
    "numero": "1234567890123456",
    "movil": "5351234567",
    "banco": "metropolitano",
    "activa": true
  }
]
```

---

## Acreditaciones

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/usuarios/acreditaciones/` | Mis acreditaciones | Sí |
| POST | `/usuarios/acreditaciones/` | Solicitar acreditación | Sí |
| GET | `/usuarios/acreditaciones/{id}/` | Ver acreditación | Sí |
| PATCH | `/usuarios/acreditaciones/{id}/aprobar/` | Aprobar acreditación | Admin |
| PATCH | `/usuarios/acreditaciones/{id}/rechazar/` | Rechazar acreditación | Admin |

### Solicitar Acreditación
```http
POST /api/v1/usuarios/acreditaciones/
Authorization: Bearer <token>
Content-Type: application/json

{
  "tarjeta": 1,
  "monto": 1000.00,
  "sms_confirmacion": "123456",
  "id_transferencia": "TRF123456789"
}
```

### Aprobar Acreditación (Admin)
```http
PATCH /api/v1/usuarios/acreditaciones/{id}/aprobar/
Authorization: Bearer <token_admin>
```
**Efecto:** Se suma el monto al `saldo_principal` del usuario.

---

## Extracciones

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/usuarios/extracciones/` | Mis extracciones | Sí |
| POST | `/usuarios/extracciones/` | Solicitar extracción | Sí |
| GET | `/usuarios/extracciones/{id}/` | Ver extracción | Sí |
| PATCH | `/usuarios/extracciones/{id}/aprobar/` | Aprobar extracción | Admin |
| PATCH | `/usuarios/extracciones/{id}/rechazar/` | Rechazar extracción | Admin |

### Solicitar Extracción
```http
POST /api/v1/usuarios/extracciones/
Authorization: Bearer <token>
Content-Type: application/json

{
  "monto": 500.00
}
```
**Validación:** `monto <= saldo_extraccion`

### Aprobar Extracción (Admin)
```http
PATCH /api/v1/usuarios/extracciones/{id}/aprobar/
Authorization: Bearer <token_admin>
```

---

## Loterías

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/loterias/loterias/` | Listar loterías activas | Sí |
| POST | `/loterias/loterias/` | Crear lotería | Admin |
| GET | `/loterias/loterias/{id}/` | Ver lotería | Sí |
| PATCH | `/loterias/loterias/{id}/` | Editar lotería | Admin |
| DELETE | `/loterias/loterias/{id}/` | Eliminar lotería | Admin |

### Crear Lotería (Admin)
```http
POST /api/v1/loterias/loterias/
Authorization: Bearer <token_admin>
Content-Type: application/json

{
  "nombre": "Florida",
  "foto": <file>
}
```

---

## Modalidades

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/loterias/modalidades/` | Listar modalidades | Sí |
| POST | `/loterias/modalidades/` | Crear modalidad | Admin |
| GET | `/loterias/modalidades/{id}/` | Ver modalidad | Sí |
| PATCH | `/loterias/modalidades/{id}/` | Editar modalidad | Admin |
| DELETE | `/loterias/modalidades/{id}/` | Eliminar modalidad | Admin |

### Editar Premio (Admin)
```http
PATCH /api/v1/loterias/modalidades/{id}/
Authorization: Bearer <token_admin>
Content-Type: application/json

{
  "premio_por_peso": 600.00
}
```

---

## Tiradas

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/loterias/tiradas/` | Listar tiradas | Sí |
| POST | `/loterias/tiradas/` | Crear tirada | Admin |
| GET | `/loterias/tiradas/{id}/` | Ver tirada | Sí |
| PATCH | `/loterias/tiradas/{id}/` | Editar tirada | Admin |
| GET | `/loterias/tiradas/activas/` | Tiradas activas hoy | Sí |
| POST | `/loterias/tiradas/resultados/` | Ingresar resultados | Admin |

### Crear Tirada (Admin)
```http
POST /api/v1/loterias/tiradas/
Authorization: Bearer <token_admin>
Content-Type: application/json

{
  "loteria": 1,
  "hora": "21:30:00",
  "fecha": "2026-03-23"
}
```

### Tiradas Activas
```http
GET /api/v1/loterias/tiradas/activas/
Authorization: Bearer <token>
```

### Ingresar Resultados (Admin)
```http
POST /api/v1/loterias/tiradas/resultados/
Authorization: Bearer <token_admin>
Content-Type: application/json

{
  "tirada_id": 1,
  "pick_3": "123",
  "pick_4": "4567"
}
```
**Efecto:** 
- Se guardan los resultados
- Se calculan premios automáticamente
- Se acredita saldo a los ganadores

---

## Apuestas

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/apuestas/` | Mis apuestas | Sí |
| POST | `/apuestas/` | Crear apuesta | Sí |
| GET | `/apuestas/{id}/` | Ver apuesta | Sí |
| GET | `/apuestas/mis_apuestas/` | Ver mis apuestas | Sí |
| GET | `/apuestas/{id}/calcular_premios/` | Calcular premios | Sí |

### Crear Apuesta
```http
POST /api/v1/apuestas/
Authorization: Bearer <token>
Content-Type: application/json

{
  "loteria_id": 1,
  "modalidad_id": 1,
  "tirada_id": 1,
  "numeros": ["123", "456"],
  "monto_por_numero": 10.00
}
```
**Validaciones:**
- Solo números de 3 dígitos
- `monto_total = monto_por_numero * len(numeros)`
- `monto_total <= saldo_principal`
- Tirada debe estar activa

### Mis Apuestas
```http
GET /api/v1/apuestas/mis_apuestas/
Authorization: Bearer <token>
```

---

## Admin Django

| Ruta | Descripción |
|------|-------------|
| `/api/v1/admin/` | Panel de administración Django |

---

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| 400 | Solicitud incorrecta |
| 401 | No autenticado |
| 403 | No autorizado |
| 404 | Recurso no encontrado |
| 405 | Método no permitido |

### Errores Comunes
```json
{"error": "Saldo insuficiente"}
{"error": "La tirada no existe o no está activa"}
{"error": "El número debe tener 3 dígitos"}
{"error": "La tarjeta no está activa"}
{"error": "No autorizado"}
```

---

## Resumen de Endpoints

```
/api/v1/
├── usuarios/
│   ├── POST / (registro)
│   ├── POST /token/ (login)
│   ├── POST /token/refresh/
│   ├── GET /me/ (perfil)
│   ├── GET / (listar - admin)
│   ├── tarjetas/
│   │   ├── GET /
│   │   ├── POST /
│   │   └── {id}/
│   ├── acreditaciones/
│   │   ├── GET /
│   │   ├── POST /
│   │   ├── {id}/
│   │   ├── {id}/aprobar/
│   │   └── {id}/rechazar/
│   └── extracciones/
│       ├── GET /
│       ├── POST /
│       ├── {id}/
│       ├── {id}/aprobar/
│       └── {id}/rechazar/
│
├── loterias/
│   ├── modalidades/
│   │   ├── GET /
│   │   ├── POST /
│   │   └── {id}/
│   ├── loterias/
│   │   ├── GET /
│   │   ├── POST /
│   │   └── {id}/
│   └── tiradas/
│       ├── GET /
│       ├── POST /
│       ├── {id}/
│       ├── activas/ (GET)
│       └── resultados/ (POST)
│
├── apuestas/
│   ├── GET /
│   ├── POST /
│   ├── {id}/
│   └── mis_apuestas/ (GET)
│
└── admin/ (Django admin)
```

# Guía de Integración Frontend - Loteria Backend

## Estructura General

| Sección | Ruta | Descripción |
|---------|------|-------------|
| Frontend User | `/` | Panel de usuario |
| Frontend Admin | `/admin` | Panel de administración |
| API Base | `/api/v1/` | Endpoints del backend |

---

## 1. Autenticación

### Endpoints
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/usuarios/` | Registro de usuario |
| GET | `/api/v1/usuarios/me/` | Perfil del usuario actual |
| POST | `/api/v1/token/` | Obtener token JWT |
| POST | `/api/v1/token/refresh/` | Refrescar token JWT |

### Flujo de Auth
```javascript
// Registro
POST /api/v1/usuarios/
{
  "email": "usuario@example.com",
  "password": "contraseña123",
  "movil": "5351234567",
  "tarjeta_bancaria": "1234567890123456",
  "banco": "metropolitano"
}

// Login (obtener token)
POST /api/v1/token/
{
  "email": "usuario@example.com",
  "password": "contraseña123"
}

// Respuesta
{
  "access": "eyJ0eXAiOiJKV1Q...",
  "refresh": "eyJ0eXAiOiJKV1Q..."
}
```

### Headers de Authorization
```javascript
headers: {
  'Authorization': 'Bearer {access_token}',
  'Content-Type': 'application/json'
}
```

---

## 2. Panel de Usuario (`/`)

### 2.1 Header/Navegación
- Logo de la aplicación
- Menú: Inicio | Apuestas | Historial | Mi Perfil
- Saldo actual (actualizable)
- Botón de cerrar sesión

### 2.2 Dashboard - Saldo
**Recursos:**
- GET `/api/v1/usuarios/me/` → `saldo_principal`, `saldo_extraccion`

**Componentes:**
- Card de saldo principal (CUP)
- Card de saldo para extracción (CUP)
- Botón "Acreditar" → Modal de acreditación
- Botón "Extraer" → Modal de extracción

### 2.3 Modal Acreditar
**Endpoint:** `POST /api/v1/acreditaciones/`

** Campos del formulario:**
| Campo | Tipo | Validación |
|-------|------|------------|
| tarjeta_id | select | Lista de tarjetas activas |
| monto | number | > 0 |
| sms_confirmacion | text | 6 dígitos |
| id_transferencia | text | Único |

**Endpoint tarjetas:** `GET /api/v1/tarjetas/` (solo activas)

**Flujo:**
1. Usuario selecciona tarjeta del sistema
2. Ingresa monto a acreditar
3. Recibe SMS de confirmación
4. Ingresa código SMS + ID de transferencia
5. Submit → Estado "pendiente"
6. Admin aprueba → saldo se acredita

### 2.4 Modal Extraer
**Endpoint:** `POST /api/v1/extracciones/`

** Campos del formulario:**
| Campo | Tipo | Validación |
|-------|------|------------|
| monto | number | > 0, <= saldo_extraccion |

**Validación en frontend:**
- Mostrar saldo disponible
- Validar monto <= saldo antes de enviar
- Mensaje de error si saldo insuficiente

### 2.5 Apuestas - Lista Loterías
**Endpoints:**
- `GET /api/v1/loterias/` → Lista de loterías activas
- `GET /api/v1/tiradas/activas/` → Tiradas disponibles hoy
- `GET /api/v1/modalidades/` → Modalidades disponibles

**UI - Selector de lotería:**
```
[Seleccionar Lotería ▼]
├── Florida
├── La Caribeña
├── New York
└── etc.
```

**UI - Selector de tirada:**
```
[Seleccionar Horario ▼]
├── 10:00 AM - Florida
├── 2:00 PM - Florida  
├── 9:30 PM - La Caribeña
└── (mostrar fecha, hora, lotería)
```

**UI - Selector de modalidad:**
```
[Seleccionar Modalidad ▼]
├── Fijo (premio: 600)
├── Corrido (premio: 600)
├── Parlé (premio: 600)
└── Pick 3 (premio: 600)
```

### 2.6 Formulario de Apuesta
**Endpoint:** `POST /api/v1/apuestas/`

** Campos:**
| Campo | Tipo | Validación |
|-------|------|------------|
| loteria_id | hidden | ID de lotería seleccionada |
| modalidad_id | hidden | ID de modalidad seleccionada |
| tirada_id | hidden | ID de tirada seleccionada |
| numeros | array | Array de strings ["123", "456"] |
| monto_por_numero | number | > 0 |

**UI de números:**
```
Ingrese sus números (3 dígitos cada uno):
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ 123 │ │ 456 │ │ 789 │ │  +  │  [Agregar número]
└─────┘ └─────┘ └─────┘ └─────┘

Monto por número: [    10.00    ]
Monto total: 40.00 CUP
[ APOSTAR 40.00 CUP ]
```

**Validaciones:**
- Solo números de 3 dígitos
- Máximo 10 números por apuesta
- Monto total <= saldo principal
- Tirada debe estar activa

### 2.7 Historial de Apuestas
**Endpoint:** `GET /api/v1/apuestas/`

**UI - Lista:**
```
Mis Apuestas
├── Apuesta #123
│   ├── Lotería: Florida
│   ├── Modalidad: Fijo
│   ├── Números: 123, 456, 789
│   ├── Monto: 30.00 CUP
│   ├── Premio: 0.00 CUP ❌
│   └── Fecha: 2026-03-23 10:30
├── Apuesta #124
│   ├── Lotería: La Caribeña
│   ├── Modalidad: Parlé
│   ├── Números: 111
│   ├── Monto: 10.00 CUP
│   ├── Premio: 6000.00 CUP ✅
│   └── Fecha: 2026-03-22 14:00
└── ...
```

### 2.8 Mi Perfil
**Endpoint:** `GET /api/v1/usuarios/me/` (para ver), `PATCH` (para editar)

**Campos editables:**
- Email (solo lectura)
- Móvil
- Tarjeta bancaria
- Banco

---

## 3. Panel de Admin (`/admin`)

### 3.1 Sidebar/Navegación
```
📊 Dashboard
├── Usuarios
│   ├── Lista de usuarios
│   ├── Acreditaciones
│   └── Extracciones
├── Loterías
│   ├── Gestionar Loterías
│   ├── Gestionar Tiradas
│   └── Resultados
├── Modalidades
└── Informes
```

### 3.2 Dashboard Admin
**KPI Cards:**
- Total usuarios registrados
- Total apuestas hoy
- Volume de apuestas (CUP)
- Premios pagados hoy
- Saldo total en sistema

### 3.3 Gestión de Usuarios
**Lista de Usuarios:**
- `GET /api/v1/usuarios/`

**Tabla:**
| Email | Móvil | Saldo Principal | Saldo Extracción | Banco | Registrado |
|-------|-------|------------------|------------------|-------|------------|
| user1@... | 535... | 1000.00 | 500.00 | Metropolitano | 2026-03-20 |
| user2@... | 535... | 500.00 | 100.00 | Bandec | 2026-03-21 |

**Acciones por fila:**
- Ver detalles
- Editar saldo
- Bloquear usuario

### 3.4 Acreditaciones - Aprobar
**Lista pendientes:** `GET /api/v1/acreditaciones/?estado=pendiente`

**Tabla:**
| ID | Usuario | Tarjeta | Monto | SMS | ID Transferencia | Fecha |
|----|---------|---------|-------|-----|------------------|-------|
| 1 | user@... | ****3456 | 1000 | 123456 | TRF123 | 2026-03-23 |

**Acciones:**
- ✅ Aprobar → `PATCH /api/v1/acreditaciones/1/aprobar/`
- ❌ Rechazar → `PATCH /api/v1/acreditaciones/1/rechazar/`

**Al aprobar:**
- Se suma monto a `saldo_principal` del usuario
- Estado cambia a "aprobada"

### 3.5 Extracciones - Aprobar
**Lista pendientes:** `GET /api/v1/extracciones/?estado=pendiente`

**Tabla:**
| ID | Usuario | Monto | Estado | Fecha |
|----|---------|-------|--------|-------|
| 1 | user@... | 500 | Pendiente | 2026-03-23 |

**Acciones:**
- ✅ Aprobar → `PATCH /api/v1/extracciones/1/aprobar/`
- ❌ Rechazar → `PATCH /api/v1/extracciones/1/rechazar/`

**Al aprobar:**
- Se resta monto de `saldo_extraccion` del usuario
- Estado cambia a "aprobada"

### 3.6 Gestionar Loterías
**Endpoints:**
- `GET /api/v1/loterias/` - Lista
- `POST /api/v1/loterias/` - Crear
- `PATCH /api/v1/loterias/{id}/` - Editar
- `DELETE /api/v1/loterias/{id}/` - Eliminar (soft delete)

**Formulario crear:**
| Campo | Tipo |
|-------|------|
| nombre | text |
| foto | file/image |

### 3.7 Gestionar Tiradas
**Endpoints:**
- `GET /api/v1/tiradas/` - Lista
- `POST /api/v1/tiradas/` - Crear
- `PATCH /api/v1/tiradas/{id}/` - Editar

**Formulario crear:**
| Campo | Tipo |
|-------|------|
| loteria_id | select |
| hora | time |
| fecha | date |
| activa | checkbox |

**UI - Calendario de tiradas:**
- Vista por lotería
- Vista por fecha
- Indicador de estado (activa/inactiva)

### 3.8 Ingresar Resultados
**Endpoint:** `POST /api/v1/tiradas/resultados/`

**Formulario:**
| Campo | Tipo | Validación |
|-------|------|-------------|
| tirada_id | select | Tiradas activas |
| pick_3 | text | 3 dígitos |
| pick_4 | text | 4 dígitos |

**Al enviar:**
- Se actualizan pick_3 y pick_4 de la tirada
- Se calculan premios automáticamente
- Se acredita saldo a ganadores

### 3.9 Gestionar Modalidades
**Endpoints:**
- `GET /api/v1/modalidades/` - Lista
- `PATCH /api/v1/modalidades/{id}/` - Editar premio

**Tabla:**
| Modalidad | Premio por Peso | Descripción | Acciones |
|-----------|-----------------|-------------|----------|
| Fijo | 600 | Premio fijo | ✏️ Editar |
| Corrido | 600 | Premio corrido | ✏️ Editar |
| Parlé | 600 | Premio habló | ✏️ Editar |
| Pick 3 | 600 | Pick 3 | ✏️ Editar |

**Formulario editar:**
| Campo | Tipo |
|-------|------|
| premio_por_peso | number |

---

## 4. Notificaciones en Tiempo Real (Opcional)

### Eventos WebSocket
- `apuesta_ganadora` - Cuando una apuesta resulta ganadora
- `resultado_publicado` - Cuando se publican resultados
- `saldo_actualizado` - Cuando se acredita o descuenta saldo

---

## 5. Códigos de Error

| Código | Significado |
|--------|-------------|
| 400 | Datos inválidos |
| 401 | No autenticado |
| 403 | No autorizado |
| 404 | Recurso no encontrado |
| 409 | Conflicto (ej: email duplicado) |
| 422 | Validación de negocio fallida |

### Errores Comunes
```json
{"error": "Saldo insuficiente"}
{"error": "La tirada no existe o no está activa"}
{"error": "El número 12 debe tener 3 dígitos"}
{"error": "La tarjeta no está activa"}
```

---

## 6. Checklist de Funcionalidades

### Frontend Usuario
- [ ] Registro de usuario con email, móvil, tarjeta, banco
- [ ] Login con email/password → JWT
- [ ] Ver saldo principal y de extracción
- [ ] Modal de acreditación con tarjetas del sistema
- [ ] Modal de extracción con validación de saldo
- [ ] Selector de lotería, tirada, modalidad
- [ ] Formulario de apuesta con validación de números
- [ ] Lista de apuestas con resultados
- [ ] Perfil de usuario

### Frontend Admin
- [ ] Dashboard con KPIs
- [ ] Lista de usuarios con filtros
- [ ] Aprobar/rechazar acreditaciones
- [ ] Aprobar/rechazar extracciones
- [ ] CRUD de loterías
- [ ] CRUD de tiradas
- [ ] Ingresar resultados (pick_3, pick_4)
- [ ] Editar premios de modalidades

---

## 7. Rutas Resumen

### Endpoints Públicos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/usuarios/` | Registro |
| POST | `/api/v1/token/` | Login JWT |
| GET | `/api/v1/loterias/` | Loterías activas |
| GET | `/api/v1/tiradas/activas/` | Tiradas disponibles |
| GET | `/api/v1/modalidades/` | Modalidades |

### Endpoints Autenticados
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/usuarios/me/` | Mi perfil |
| POST | `/api/v1/acreditaciones/` | Solicitar acreditación |
| POST | `/api/v1/extracciones/` | Solicitar extracción |
| POST | `/api/v1/apuestas/` | Crear apuesta |
| GET | `/api/v1/apuestas/` | Mis apuestas |

### Endpoints Admin
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET/POST | `/api/v1/usuarios/` | Gestionar usuarios |
| PATCH | `/api/v1/acreditaciones/{id}/aprobar/` | Aprobar acreditación |
| PATCH | `/api/v1/extracciones/{id}/aprobar/` | Aprobar extracción |
| GET/POST | `/api/v1/loterias/` | Gestionar loterías |
| GET/POST | `/api/v1/tiradas/` | Gestionar tiradas |
| POST | `/api/v1/tiradas/resultados/` | Ingresar resultados |
| PATCH | `/api/v1/modalidades/{id}/` | Editar premio |

### Admin Django
| Ruta | Descripción |
|------|-------------|
| `/api/v1/admin/` | Panel admin Django completo |
| `/api/v1/admin/users/usuario/` | Gestión usuarios |
| `/api/v1/admin/users/tarjetasistema/` | Gestión tarjetas |
| `/api/v1/admin/loteria/modalidad/` | Gestión modalidades |
| `/api/v1/admin/loteria/loteria/` | Gestión loterías |
| `/api/v1/admin/loteria/tirada/` | Gestión tiradas |
| `/api/v1/admin/apuestas/apuesta/` | Gestión apuestas |

---

## 8. Ejemplo de Flujo Completo

```
1. Usuario se registra
   POST /api/v1/usuarios/
   
2. Usuario hace login
   POST /api/v1/token/
   
3. Usuario ve saldo = 0
   
4. Usuario solicita acreditación
   POST /api/v1/acreditaciones/
   { tarjeta: 1, monto: 1000, sms: "123456", id_transferencia: "TRF001" }
   
5. Admin aprueba acreditación
   PATCH /api/v1/acreditaciones/1/aprobar/
   
6. Usuario ve saldo = 1000
   
7. Usuario hace apuesta
   POST /api/v1/apuestas/
   { loteria: 1, modalidad: 1, tirada: 1, numeros: ["123"], monto_por_numero: 10 }
   
8. Usuario ve saldo = 990
   
9. Admin ingresa resultado
   POST /api/v1/tiradas/resultados/
   { tirada: 1, pick_3: "123" }
   
10. Sistema calcula premio y acredita
    usuario.saldo_principal += 6000
    usuario.saldo = 6990
```

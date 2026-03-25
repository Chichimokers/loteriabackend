# CAMBIOS REALIZADOS - Sistema Bolita Cubana Florida

## Fecha: 2026-03-25

---

## RESUMEN DE CAMBIOS

Se ajustó el sistema de apuestas para soportar correctamente las 4 modalidades de la bolita cubana Florida, donde el resultado se compone de pick_3 (Cash-3, 3 dígitos) y pick_4 (Play-4, 4 dígitos).

### Formato del resultado Florida

```
Resultado: pick_3 + pick_4 = 7 dígitos
Ejemplo:   837 + 7502 = 8377502

pick_3 = 837 (Cash-3)
pick_4 = 7502 (Play-4)

Valores extraídos:
- Fijo:     37  (últimos 2 dígitos de pick_3)
- Corrido1: 75  (primeros 2 dígitos de pick_4)
- Corrido2: 02  (últimos 2 dígitos de pick_4)
- Centena:  837 (pick_3 completo)
```

---

## ARCHIVOS MODIFICADOS

### 1. `apps/loteria/models.py`
**Cambio:** Se mantiene el modelo Modalidad con las 4 opciones originales (fijo, corrido, parlé, pick_3). No se agrega candado como modalidad.

### 2. `apps/apuestas/models.py`
**Cambios:**
1. Agregado campo `combinaciones_generadas` (JSONField) para guardar combinaciones de candado
2. Agregado método `_extraer_valores()` para extraer fijo, corrido1, corrido2, centena del resultado
3. Reescrito método `calcular_premios()` con lógica correcta para cada modalidad
4. Para parlé: si tiene `combinaciones_generadas`, evalúa cada combinación (candado)

### 3. `apps/apuestas/serializers.py`
**Cambios:**
1. Reescrito `ApuestaCreateSerializer` para validar según modalidad
2. Cambiado `numeros = serializers.ListField()` para aceptar arrays anidados (parlé)
3. Agregada validación de parejas duplicadas en parlé (ej: `["12","34"]` y `["34","12"]` no se permiten)
4. Agregado `CandadoCreateSerializer` para el endpoint de candado
5. Agregada validación de números duplicados en candado

### 4. `apps/apuestas/views.py`
**Cambios:**
1. Agregado método `_validar_tirada()` para reutilizar validaciones
2. Agregado endpoint `@action candado` que genera combinaciones automáticamente

### 5. `apps/apuestas/urls.py`
**Cambio:** Agregada ruta `candado/`

### 6. `.github/workflows/deploy.yml`
**Cambio:** Modalidades por defecto actualizadas

---

## ENDPOINTS

### Modalidades normales: `POST /api/v1/apuestas/`

**FIJO (múltiples números de 2 dígitos):**
```json
{
    "modalidad_id": 1,
    "tirada_id": 1,
    "numeros": ["37", "88", "12"],
    "monto_por_numero": "10.00"
}
```

**CORRIDO (múltiples números de 2 dígitos):**
```json
{
    "modalidad_id": 2,
    "tirada_id": 1,
    "numeros": ["75", "02"],
    "monto_por_numero": "10.00"
}
```

**PICK 3 (múltiples números de 3 dígitos):**
```json
{
    "modalidad_id": 3,
    "tirada_id": 1,
    "numeros": ["837", "123"],
    "monto_por_numero": "10.00"
}
```

**PARLÉ (parejas de 2 dígitos - NO se permiten duplicados ni inversas):**
```json
{
    "modalidad_id": 4,
    "tirada_id": 1,
    "numeros": [["37", "75"], ["37", "02"]],
    "monto_por_numero": "10.00"
}
```

**Ejemplo de error en parlé (parejas duplicadas):**
```json
{
    "modalidad_id": 4,
    "tirada_id": 1,
    "numeros": [["12", "34"], ["34", "12"]],
    "monto_por_numero": "10.00"
}
```
Respuesta:
```json
{
    "numeros": ["La pareja ['34', '12'] ya existe (o su inversa). No se permiten duplicados."]
}
```

---

### Candado (endpoint separado): `POST /api/v1/apuestas/candado/`

**CANDADO (array de números de 2 dígitos, genera combinaciones automáticas - NO se permiten duplicados):**
```json
{
    "tirada_id": 1,
    "numeros": ["37", "75", "02", "58"],
    "monto_por_numero": "10.00"
}
```

Resultado: C(4,2) = 6 combinaciones generadas:
- ["37","75"], ["37","02"], ["37","58"], ["75","02"], ["75","58"], ["02","58"]

Monto total: 10.00 × 6 = 60.00

**Ejemplo de error en candado (números duplicados):**
```json
{
    "tirada_id": 1,
    "numeros": ["37", "75", "37", "58"],
    "monto_por_numero": "10.00"
}
```
Respuesta:
```json
{
    "numeros": ["El número '37' está duplicado. No se permiten duplicados en candado."]
}
```

---

## VALIDACIONES IMPLEMENTADAS

| Modalidad | Validación |
|-----------|------------|
| **Fijo** | Array de strings de 2 dígitos |
| **Corrido** | Array de strings de 2 dígitos |
| **Pick 3** | Array de strings de 3 dígitos |
| **Parlé** | Array de parejas de 2 dígitos. No se permiten parejas duplicadas ni inversas (ej: `["12","34"]` = `["34","12"]`) |
| **Candado** | Array de strings de 2 dígitos. No se permiten números duplicados |

---

## LÓGICA DE PREMIOS

| Modalidad | Formato números | Cómo se evalúa | Ejemplo ganador |
|-----------|----------------|----------------|-----------------|
| **Fijo** | `["37"]` - 2 dígitos | `numero == pick_3[-2:]` | pick_3=837 → fijo=37 |
| **Corrido** | `["75"]` - 2 dígitos | `numero == pick_4[:2]` O `numero == pick_4[-2:]` | pick_4=7502 → corrido1=75, corrido2=02 |
| **Pick 3** | `["837"]` - 3 dígitos | `numero == pick_3` | pick_3=837 |
| **Parlé** | `[["37","75"]]` - parejas | Ambos coinciden con fijo/corrido1/corrido2 | fijo=37, corrido1=75 |
| **Candado** | `["37","75","02","58"]` | Cada pareja generada evalúa contra fijo/corrido1/corrido2 | Cualquier pareja que coincida |

---

## CAMPOS DE MODELO APUESTA

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `numeros` | JSONField | Números originales que envió el usuario |
| `combinaciones_generadas` | JSONField (nullable) | Combinaciones de parejas generadas para candado |
| `monto_por_numero` | Decimal | Monto apostado por cada número/pareja/combinación |
| `monto_total` | Decimal | `monto_por_numero × len(numeros)` o `monto_por_numero × len(combinaciones)` para candado |
| `premiados` | JSONField (nullable) | Array con los números ganadores y sus premios |
| `premio_total` | Decimal | Suma de todos los premios ganados |
| `paga` | Boolean | True si premio_total > 0 |

---

## NOTAS IMPORTANTES

1. **Candado NO es una modalidad separada.** Es un endpoint que usa la modalidad `parle` internamente.
2. **Los premios se configuran via admin** en el campo `premio_por_peso` de cada modalidad.
3. **El candado genera combinaciones C(n,2)** automáticamente a partir de los números enviados.
4. **La apuesta de candado se guarda como parlé** con el campo `combinaciones_generadas` lleno.
5. **No se permiten parejas duplicadas en parlé** (incluyendo inversas).
6. **No se permiten números duplicados en candado.**

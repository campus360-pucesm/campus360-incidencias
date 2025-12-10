# Control de Acceso y Permisos - Campus360 Incidencias

## Descripción General

El módulo de incidencias implementa un sistema de control de acceso basado en roles. El modelo sigue la arquitectura de microservicios donde:

- **Usuarios**: Gestionados por el módulo de autenticación (externa)
- **Roles**: Determinados por el JWT token del usuario autenticado
- **Incidencias**: Datos locales con restricciones de acceso según rol

## Roles Implementados

### 1. Administrador (`administrador` o `admin`)

**Permisos Completos:**

- ✓ Ver todos los tickets (sin filtros forzados)
- ✓ Asignar responsables a tickets
- ✓ Cambiar el estado de tickets
- ✓ Ver comentarios internos
- ✓ Eliminar tickets
- ✓ Ver todo el historial de cambios
- ✓ Crear nuevos tickets

### 2. Profesor/Estudiante (otros roles)

**Permisos Limitados:**

- ✓ Ver solo los tickets que ha creado (como `usuario_reportante_id`)
- ✓ Comentar en sus propios tickets
- ✓ Ver historial de sus propios tickets
- ✓ Crear nuevos tickets
- ✗ NO puede asignar responsables
- ✗ NO puede cambiar estados
- ✗ NO puede ver tickets de otros usuarios
- ✗ NO puede comentar en tickets de otros

## Mapeo de Funcionalidades a Restricciones

### Crear Ticket (POST /tickets)
- **Acceso**: Todos los usuarios autenticados
- **Nota**: El usuario autenticado es registrado como `usuario_reportante_id`

### Listar Tickets (GET /tickets)
- **Administrador**: Ve todos los tickets (con filtros opcionales)
- **Otros Roles**: Filtro automático `usuario_reportante_id = usuario_actual`

### Obtener Ticket Específico (GET /tickets/{ticket_id})
- **Administrador**: Acceso a cualquier ticket
- **Otros Roles**: Acceso solo si es el reportante

### Asignar Responsable (POST /tickets/{ticket_id}/asignar)
- **Acceso**: Solo administradores
- **Error**: 403 Forbidden para otros roles

### Cambiar Estado (POST /tickets/{ticket_id}/cambiar-estado)
- **Acceso**: Solo administradores
- **Error**: 403 Forbidden para otros roles

### Agregar Comentario (POST /tickets/{ticket_id}/comentarios)
- **Acceso**: El reportante del ticket y administradores
- **Validación**: Se verifica `usuario_reportante_id == usuario_actual`
- **Error**: 403 Forbidden si intenta comentar en ticket ajeno

### Listar Comentarios (GET /tickets/{ticket_id}/comentarios)
- **Acceso**: Solo el reportante y administradores
- **Parámetro `incluir_internos`**: Solo administradores pueden ver comentarios internos

### Eliminar Ticket (DELETE /tickets/{ticket_id})
- **Acceso**: Solo administradores
- **Error**: 403 Forbidden para otros roles

## Implementación Técnica

### Archivo de Utilidades: `app/utils/permissions.py`

Define funciones de validación de permisos:

```python
# Validaciones de rol
validar_es_administrador(usuario: dict) -> bool
validar_es_tecnico(usuario: dict) -> bool

# Validaciones que lanzan excepciones
requiere_administrador(usuario: dict)
requiere_tecnico(usuario: dict)

# Validaciones específicas de acceso
validar_acceso_incidencia(incidencia, usuario, usuario_id)
validar_puede_modificar_estado(incidencia, usuario)
validar_puede_asignar_responsable(incidencia, usuario)
validar_puede_comentar(incidencia, usuario, usuario_id)
```

### Integración en Routers

En `app/routers/incidencias.py`, cada endpoint:

1. Extrae el `usuario_id` del JWT token
2. Obtiene el rol del usuario desde el campo `role` del JWT
3. Aplica validaciones según la operación
4. Lanza `PermissionDenied` (HTTP 403) si falta permiso

**Ejemplo:**
```python
@router.post("/{ticket_id}/asignar")
async def asignar_responsable(..., usuario: dict = Depends(validate_jwt)):
    usuario_id = usuario.get("user_id", usuario.get("id", usuario.get("sub")))
    
    # Solo administradores
    requiere_administrador(usuario)
    
    # Continuar con la lógica...
```

### Extracción de Datos del JWT

El sistema soporta múltiples formatos de JWT token:

```python
usuario_id = usuario.get("user_id", 
              usuario.get("id", 
              usuario.get("sub")))

rol = usuario.get("role", 
      usuario.get("tipo_usuario", "")).lower()
```

Esto permite compatibilidad con diferentes implementaciones de autenticación.

## Excepciones de Acceso

### PermissionDenied (HTTP 403)

Se lanza cuando un usuario intenta una acción sin permisos:

```python
raise PermissionDenied(
    detail="Solo los administradores pueden realizar esta acción"
)
```

La respuesta HTTP es:
```json
{
    "detail": "Solo los administradores pueden realizar esta acción"
}
```

## Flujos de Autorización por Endpoint

### 1. Crear Ticket
```
Usuario autenticado?
├─ SÍ → Crear ticket con usuario_reportante_id = usuario_actual
└─ NO → HTTP 401 Unauthorized
```

### 2. Listar Tickets
```
Usuario autenticado?
├─ NO → HTTP 401 Unauthorized
├─ SÍ → Es administrador?
│   ├─ SÍ → Mostrar todos los tickets (aplicar filtros opcionales)
│   └─ NO → Mostrar solo tickets donde usuario_reportante_id = usuario_actual
```

### 3. Asignar Responsable
```
Usuario autenticado?
├─ NO → HTTP 401 Unauthorized
└─ SÍ → Es administrador?
    ├─ SÍ → Asignar responsable
    └─ NO → HTTP 403 Forbidden
```

### 4. Comentar en Ticket
```
Usuario autenticado?
├─ NO → HTTP 401 Unauthorized
├─ SÍ → Ticket existe?
│   ├─ NO → HTTP 404 Not Found
│   └─ SÍ → Es administrador O es el reportante?
│       ├─ SÍ → Crear comentario
│       └─ NO → HTTP 403 Forbidden
```

## Consideraciones de Seguridad

### 1. Validación en Múltiples Capas

- **Router**: Primera línea de validación, rechaza permisos
- **Service**: Lógica de negocio con checks adicionales
- **Base de datos**: No almacena data sin validación

### 2. JWT Token

- Debe contener campos: `user_id`/`id`/`sub` y `role`
- Se valida en el módulo de autenticación
- No se confía en datos del cliente

### 3. Filtrado de Datos

- Usuarios no-admin reciben automáticamente filtro `usuario_reportante_id`
- No se filtra en el cliente (se filtra en el servidor)

### 4. Ataque de Insecuridad de Control de Acceso Defectuoso (IDOR)

Mitigado mediante:
- Validación en router antes de acceder al recurso
- Verificación de ownership (`usuario_reportante_id`)
- Error consistente (404) para recursos no disponibles

## Testing de Permisos

Para probar el sistema:

### 1. Token de Administrador
```bash
curl -H "Authorization: Bearer {admin_token}" \
  http://localhost:8000/tickets?estado_codigo=pendiente
```
Espera: Todos los tickets en estado pendiente

### 2. Token de Estudiante
```bash
curl -H "Authorization: Bearer {student_token}" \
  http://localhost:8000/tickets
```
Espera: Solo tickets donde usuario_reportante_id = ID del estudiante

### 3. Intento de Asignar (no-admin)
```bash
curl -X POST \
  -H "Authorization: Bearer {student_token}" \
  http://localhost:8000/tickets/1/asignar \
  -d '{"responsable_id": "123"}'
```
Espera: HTTP 403 Forbidden

## Auditoría y Logging

El sistema de permisos se integra con el `historial_incidencias`:

- Cada cambio es registrado con el `usuario_id` que lo hizo
- Permite auditoría de quién modificó qué
- Los administradores pueden ver el historial completo

## Extensibilidad Futura

El sistema está diseñado para permitir:

1. **Nuevos Roles**: Agregar validaciones en `permissions.py`
2. **Permisos Granulares**: Expandir `validar_puede_*` functions
3. **Delegación**: Permitir que ciertos usuarios deleguen permisos
4. **Grupos**: Soportar grupos de usuarios con permisos comunes

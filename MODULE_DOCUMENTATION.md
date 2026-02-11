# Documentación técnica: Módulo de Incidencias (Campus360)

Este documento es una referencia técnica para desarrolladores e integradores. Contiene la arquitectura, los endpoints expuestos por la API, los modelos de entrada/salida (schemas), reglas de autorización y ejemplos de uso.

## Resumen rápido
- Servicio web construido con `FastAPI` y `SQLAlchemy`.
- Persistencia en PostgreSQL (estructura propia para `incidencias`, `comentarios`, `historial`) y lectura de la tabla `users` compartida.
- Autenticación basada en JWT; control de acceso por roles (`admin`, `tecnico`, `profesor`, `student`).

## 1. Arquitectura y decisiones técnicas

- Capa HTTP: `FastAPI` (`app.main` + routers en `app/routers`).
- Validación y serialización: `Pydantic` (schemas en `app/schemas/schemas.py`).
- Lógica de dominio: servicios en `app/services` (separación de responsabilidades; facilita testing y reuso).
- Persistencia: `SQLAlchemy` ORM (`app/models/models.py`) y SQL en `database/*.sql` para esquemas iniciales.
- Seguridad: `validate_jwt` en `app/dependencies.py` y utilidades RBAC en `app/utils/permissions.py`.

Motivación: diseño en capas (router → service → model) para mantener control sobre validaciones, reglas de negocio y evitar lógica en los controladores.

## 2. Modelos de datos (mapeo rápido)

- `Incidencia` (tabla `incidencias`): `id`, `titulo`, `descripcion`, `estado_id`, `prioridad_id`, `categoria_id`, `ubicacion_id`, `usuario_reportante_id`, `responsable_id`, `fecha_creacion`, `fecha_actualizacion`, `fecha_resolucion`.
- `HistorialIncidencia` (tabla `historial_incidencias`): `id`, `incidencia_id`, `accion`, `usuario_id`, `descripcion`, `valor_anterior`, `valor_nuevo`, `fecha_cambio`.
- `Comentario` (tabla `comentarios`): `id`, `incidencia_id`, `usuario_id`, `contenido`, `es_interno`, `fecha_creacion`.
- Catálogos: `Estado`, `Prioridad`, `Categoria`, `Recurso` (ubicaciones).

Para detalles de campos y tipos consultar `app/models/models.py`.

## 3. Endpoints (resumen técnico)

Todos los endpoints están prefijados con `/tickets` (ver `app/routers/incidencias.py`). A continuación se listan con: método, path, permisos, payload y schema de respuesta.

- GET `/tickets/catalogos/estados`
    - Descripción: Lista estados activos.
    - Permisos: cualquier usuario autenticado.
    - Response: `list[EstadoResponse]` (`app/schemas/schemas.py`).

- GET `/tickets/catalogos/prioridades`
    - Descripción: Lista prioridades activas.
    - Permisos: cualquier usuario autenticado.
    - Response: `list[PrioridadResponse]`.

- GET `/tickets/catalogos/categorias`
    - Descripción: Lista categorías.
    - Permisos: cualquier usuario autenticado.
    - Response: `list[CategoriaResponse]`.

- GET `/tickets/catalogos/ubicaciones`
    - Descripción: Lista ubicaciones (recursos). Nota: `id` de ubicaciones es `UUID`.
    - Permisos: cualquier usuario autenticado.
    - Response: `list[UbicacionResponse]`.

- POST `/tickets/`
    - Descripción: Crear incidencia.
    - Permisos: usuario autenticado.
    - Request body: `IncidenciaCreate` (ver `app/schemas/schemas.py`).
    - Response: `IncidenciaResponse` (status `201`).
    - Errores comunes: `400` (validación), `404` (usuario no encontrado).

- GET `/tickets/` (list)
    - Descripción: Listar incidencias con filtros y paginación.
    - Query params: `estado_codigo`, `prioridad_codigo`, `categoria_codigo`, `usuario_reportante_id`, `responsable_id`, `limit`, `offset`.
    - Permisos: administradores ven todo; otros usuarios ven solo sus reportes.
    - Response: `IncidenciasPaginatedResponse`.

- GET `/tickets/{ticket_id}`
    - Descripción: Obtener detalle completo de una incidencia.
    - Permisos: administradores o reportante.
    - Response: `IncidenciaResponse`.

- PUT `/tickets/{ticket_id}`
    - Descripción: Actualiza campos editables (categoría, prioridad, ubicación, título, descripción).
    - Permisos: administradores.
    - Request body: `IncidenciaUpdate`.
    - Response: `IncidenciaResponse`.

- POST `/tickets/{ticket_id}/asignar`
    - Descripción: Asignar responsable (técnico) a ticket.
    - Permisos: administradores.
    - Request body: `AsignarResponsableRequest`.
    - Response: `IncidenciaResponse`.

- POST `/tickets/{ticket_id}/cambiar-estado`
    - Descripción: Cambiar estado del ticket (p. ej. a `RESUELTA`). Si se marca resuelta se registra `fecha_resolucion`.
    - Permisos: administradores.
    - Request body: `CambiarEstadoRequest`.
    - Response: `IncidenciaResponse`.

- GET `/tickets/{ticket_id}/historial`
    - Descripción: Lista los registros de historial para una incidencia.
    - Permisos: administradores o reportante.
    - Response: `list[HistorialIncidenciaResponse]`.

- POST `/tickets/{ticket_id}/comentarios`
    - Descripción: Agregar comentario a una incidencia.
    - Permisos: reportante (y administradores para internos).
    - Request body: `ComentarioCreate`.
    - Response: `ComentarioResponse` (status `201`).

- GET `/tickets/{ticket_id}/comentarios`
    - Descripción: Listar comentarios; opcional `incluir_internos` (solo admin puede incluirlos).
    - Permisos: reportante o administradores.
    - Response: `list[ComentarioResponse]`.

- DELETE `/tickets/{ticket_id}`
    - Descripción: Eliminar incidencia (irreversible).
    - Permisos: administradores.
    - Response: `204 No Content`.

## 4. Schemas (mapping rápido)

Los schemas están definidos en `app/schemas/schemas.py`. A continuación un resumen por uso.

- Creación de incidencia (request): `IncidenciaCreate`
    - Campos principales: `titulo: str`, `descripcion: str`, `prioridad_codigo: Optional[str]`, `categoria_codigo: Optional[str]`, `ubicacion_codigo: Optional[str]`.

- Respuesta detalle de incidencia: `IncidenciaResponse`
    - Campos: `id: int`, `titulo`, `descripcion`, `estado: EstadoResponse`, `prioridad: PrioridadResponse`, `categoria: Optional[CategoriaResponse]`, `ubicacion: Optional[UbicacionResponse]`, `reportante: UsuarioSimpleResponse`, `responsable: Optional[UsuarioSimpleResponse]`, `historial: List[HistorialIncidenciaResponse]`, `comentarios: List[ComentarioResponse]`.

- Listado paginado: `IncidenciasPaginatedResponse`
    - Estructura: `{ incidencias: List[IncidenciaListResponse], total: int, limit: int, offset: int, has_more: bool }`.

- Comentarios: `ComentarioCreate` (request) / `ComentarioResponse` (response)

- Catálogos: `EstadoResponse`, `PrioridadResponse`, `CategoriaResponse`, `UbicacionResponse` (nota: `UbicacionResponse.id` es `UUID`).

Consultar `app/schemas/schemas.py` para obtener tipos, nombres de campos y aliases.

## 5. Reglas de autorización

- `validate_jwt` (dependencia) extrae `user_id`, `email`, `full_name` y `role`.
- Utilidades en `app/utils/permissions.py` implementan:
    - `validar_es_administrador(usuario)`
    - `requiere_administrador(usuario)` → lanza `PermissionDenied` si no.
    - `validar_acceso_incidencia(incidencia, usuario, usuario_id)` → valida reportante/admin.
    - `validar_puede_comentar(incidencia, usuario, usuario_id)` → permite comentar si reportante o admin.

## 6. Errores y códigos HTTP relevantes

- `400 Bad Request` → errores de validación o datos faltantes (por ejemplo prioridad/categoría inválida).
- `401 Unauthorized` → JWT ausente o inválido (gestión en `validate_jwt`).
- `403 Forbidden` → acciones restringidas por rol (ej. asignar, cambiar estado, eliminar).
- `404 Not Found` → incidencia, usuario o recurso no encontrado.
- `500 Internal Server Error` → error no manejado en servicio; revisar logs y stacktrace.

## 7. Consejos para debugging y tests rápidos

- Levantar servidor local con `uvicorn app.main:app --reload`.
- Usar `curl` o Postman para probar endpoints; incluir header `Authorization: Bearer <JWT>`.
- Comprobar schemas con `pytest` si existen tests en `tests/`.

Ejemplo minimal `curl` para crear incidencia:

```bash
curl -X POST http://localhost:8000/tickets/ \
    -H "Authorization: Bearer <JWT>" \
    -H "Content-Type: application/json" \
    -d '{"titulo":"Luz rota en sala A","descripcion":"La lámpara 3 está fundida","prioridad_codigo":"media","categoria_codigo":"infraestructura"}'
```

Ejemplo de respuesta (parcial) `IncidenciaResponse`:

```json
{
    "id": 123,
    "titulo": "Luz rota en sala A",
    "descripcion": "La lámpara 3 está fundida",
    "estado": { "id": 1, "codigo": "pendiente", "nombre": "Pendiente" },
    "prioridad": { "id": 2, "codigo": "media", "nombre": "Media" },
    "reportante": { "id": "uuid-user-1", "email": "alumno@uni.edu", "full_name": "Alumno Ejemplo" }
}
```

## 8. Siguientes pasos / mejoras sugeridas

- Documentar contract tests para `users` compartida (asegurar campos requeridos por JWT y por consultas directas a `users`).
- Añadir OpenAPI examples (en decorators `response_model` / `example`) para facilitar integraciones.
- Añadir tests de integración que levanten una base de datos en memoria o contenedor y validen flujo completo creación → asignación → cambio de estado.

---
Archivo actualizado: [MODULE_DOCUMENTATION.md](MODULE_DOCUMENTATION.md)

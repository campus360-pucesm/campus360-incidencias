# Documentación del Módulo de Incidencias - Campus360

Este documento describe la arquitectura, flujo y funcionamiento del módulo de **Incidencias** del proyecto Campus360. Este servicio permite la gestión del ciclo de vida de tickets de soporte, desde su creación por estudiantes o profesores hasta su resolución por personal técnico.

## 1. Descripción General

El módulo de Incidencias es un microservicio (o servicio modular) encargado de:
*   Recibir reportes de problemas (infraestructura, equipos, limpieza, etc.).
*   Clasificar y asignar estos reportes a responsables.
*   Mantener un historial de auditoría de todas las acciones.
*   Facilitar la comunicación mediante comentarios.

## 2. Arquitectura Técnica

### Stack Tecnológico
*   **Lenguaje**: Python 3.9+
*   **Framework Web**: FastAPI
*   **ORM**: SQLAlchemy
*   **Base de Datos**: PostgreSQL (Supabase)
*   **Autenticación**: Validación de tokens JWT (integración con microservicio de Auth).

### Integración con Base de Datos General
El módulo no funciona de forma aislada, sino que se integra con el ecosistema de Campus360:
*   **Tabla Compartida (`public.users`)**: El módulo lee la información de usuarios (autores y responsables) directamente de la tabla `users` del esquema general del proyecto. No gestiona usuarios independientemente.
*   **Esquema Propio**: Define sus propias tablas para `incidencias`, `comentarios`, `historial`, etc., relacionándolas con `users` mediante Foreign Keys.

## 3. Modelo de Datos

### Diagrama ER Simplificado (Lógico)

```mermaid
erDiagram
    USERS ||--o{ INCIDENCIAS : "reporta (1:N)"
    USERS ||--o{ INCIDENCIAS : "es responsable (1:N)"
    USERS ||--o{ COMENTARIOS : "escribe (1:N)"
    USERS ||--o{ HISTORIAL : "ejecuta acción (1:N)"
    
    INCIDENCIAS ||--|{ HISTORIAL : "tiene (1:N)"
    INCIDENCIAS ||--|{ COMENTARIOS : "tiene (1:N)"
    INCIDENCIAS ||--|{ ADJUNTOS : "tiene (1:N)"
    
    INCIDENCIAS }|--|| ESTADOS : "tiene estado"
    INCIDENCIAS }|--|| PRIORIDADES : "tiene prioridad"
    INCIDENCIAS }|--|| CATEGORIAS : "tiene categoría"
```

### Tablas Principales
1.  **`incidencias`**: Tabla central. Contiene título, descripción, y referencias a los catálogos y usuarios.
2.  **`historial_incidencias`**: Registro de auditoría inmutable. Guarda *quién* cambió *qué*, *cuándo* y los valores `antes` y `después`.
3.  **`comentarios`**: Hilo de conversación asociado a un ticket.
4.  **`users` (Externa)**: Tabla maestra de usuarios del sistema (Students, Admins, Tecnicos).

## 4. Flujos Clave

### A. Creación de Ticket (Estudiante/Profesor)
1.  **Cliente**: Envía `POST /tickets/` con título, descripción y categoría.
2.  **API**: 
    *   Valida el JWT del usuario.
    *   Verifica que el usuario exista en la tabla `users`.
    *   Asigna estado inicial **PENDIENTE**.
    *   Crea el registro en DB.
    *   Genera un registro automático en `historial_incidencias` ("Ticket creado").

### B. Asignación y Triaje (Administrador)
1.  **Admin**: Consulta `GET /tickets/?estado=pendiente`.
2.  **API**: Retorna lista filtrada.
3.  **Admin**: Envía `POST /tickets/{id}/asignar` con el ID de un técnico.
4.  **API**:
    *   Verifica rol de Admin.
    *   Actualiza el campo `responsable_id` y cambia estado a **ASIGNADA**.
    *   Guarda el cambio en el historial.

### C. Resolución (Técnico/Admin)
1.  **Técnico**: Trabaja en la incidencia y envía `POST /tickets/{id}/cambiar-estado`.
2.  **API**: Actualiza estado a **RESUELTA** (o EN PROGRESO).
3.  **API**: Si se resuelve, marca `fecha_resolucion`.
4.  **Sistema**: Permite agregar comentarios internos o públicos durante el proceso.

## 5. Permisos y Seguridad

El control de acceso se basa en Roles (RBAC) extraídos del JWT:

| Acción | Rol 'student' / 'profesor' | Rol 'admin' | Reportante (Dueño) |
| :--- | :---: | :---: | :---: |
| **Crear Ticket** | ✅ Sí | ✅ Sí | ✅ Sí |
| **Ver Mis Tickets** | ✅ Sí | ✅ Sí | ✅ Sí |
| **Ver Todos los Tickets** | ❌ No | ✅ Sí | ❌ No |
| **Editar Ticket** | ❌ No | ✅ Sí | ❌ No |
| **Cambiar Estado** | ❌ No | ✅ Sí | ❌ No |
| **Asignar Responsable** | ❌ No | ✅ Sí | ❌ No |
| **Comentar** | ❌ No (*) | ✅ Sí | ✅ Sí |
| **Ver Historial** | ❌ No (*) | ✅ Sí | ✅ Sí |

(*) Solo si es el creador del ticket.

## 6. Estructura del Proyecto

```
/app
  /models       -> Definición de tablas SQLAlchemy (Usuario, Incidencia...)
  /routers      -> Endpoints de la API (Rutas /tickets)
  /services     -> Lógica de negocio (CRUD, validaciones complejas)
  /schemas      -> Modelos Pydantic para validación de entrada/salida (DTOs)
  /utils        -> Funciones de permisos (permissions.py) y helpers
  /database     -> Scripts SQL puros (schema.sql)
  main.py       -> Punto de entrada, configuración de FastAPI y CORS
```

## 7. Configuración de Base de Datos
El sistema utiliza un archivo `.env` para la conexión.
*   **Variable**: `DATABASE_URL`
*   **Formato Supabase**: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`

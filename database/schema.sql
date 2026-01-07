-- =============================================================================
-- Campus360 Incidencias - Schema de Base de Datos (Microservicio)
-- =============================================================================
-- Este archivo define la estructura de la base de datos para el módulo de
-- gestión de incidencias de Campus360.
-- 
-- ARQUITECTURA DE MICROSERVICIOS:
-- - Usuarios: Gestionados por módulo de autenticación/usuarios
-- - Salones/Ubicaciones: Gestionados por módulo de salones
-- - Este módulo solo almacena información de tickets/incidencias
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TABLAS DE CATÁLOGO (Información interna del módulo)
-- -----------------------------------------------------------------------------

-- -----------------------------------------------------------------------------
-- TABLA: estados
-- Catálogo de estados posibles para incidencias (RF4: Estados del ticket)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS estados (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    orden INTEGER NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Datos iniciales de estados
INSERT INTO estados (codigo, nombre, descripcion, orden) VALUES
    ('pendiente', 'Pendiente', 'Estado inicial, incidencia creada pero no asignada', 1),
    ('asignada', 'Asignada', 'Incidencia asignada a un responsable', 2),
    ('en_proceso', 'En Proceso', 'Responsable está trabajando en la incidencia', 3),
    ('resuelta', 'Resuelta', 'Incidencia resuelta, pendiente de cierre', 4),
    ('cerrada', 'Cerrada', 'Incidencia cerrada definitivamente', 5),
    ('cancelada', 'Cancelada', 'Incidencia cancelada', 6)
ON CONFLICT (codigo) DO NOTHING;

-- -----------------------------------------------------------------------------
-- TABLA: prioridades
-- Catálogo de niveles de prioridad
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prioridades (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    nivel INTEGER NOT NULL,
    color VARCHAR(7),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Datos iniciales de prioridades
INSERT INTO prioridades (codigo, nombre, descripcion, nivel, color) VALUES
    ('baja', 'Baja', 'No urgente, puede esperar', 1, '#28A745'),
    ('media', 'Media', 'Prioridad normal', 2, '#FFC107'),
    ('alta', 'Alta', 'Requiere atención pronta', 3, '#FD7E14'),
    ('urgente', 'Urgente', 'Requiere atención inmediata', 4, '#DC3545')
ON CONFLICT (codigo) DO NOTHING;

-- -----------------------------------------------------------------------------
-- TABLA: categorias
-- Catálogo de categorías de incidencias
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Datos iniciales de categorías
INSERT INTO categorias (codigo, nombre, descripcion) VALUES
    ('infraestructura', 'Infraestructura', 'Problemas de edificios, aulas, mobiliario'),
    ('tecnologia', 'Tecnología', 'Problemas de equipos, redes, software'),
    ('servicios', 'Servicios', 'Problemas con servicios generales'),
    ('seguridad', 'Seguridad', 'Incidencias de seguridad'),
    ('limpieza', 'Limpieza', 'Problemas de limpieza y mantenimiento'),
    ('otros', 'Otros', 'Otras incidencias no categorizadas')
ON CONFLICT (codigo) DO NOTHING;


-- =============================================================================
-- TABLA: incidencias
-- Modelo principal para las incidencias/tickets (RF2: Crear incidencia)
-- Solo almacena datos de incidencias, referencias a usuarios y salones se
-- obtienen de otros microservicios mediante endpoints
-- =============================================================================
CREATE TABLE IF NOT EXISTS incidencias (
    id SERIAL PRIMARY KEY,
    
    -- Información básica
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    
    -- Referencias a catálogos internos (FK)
    estado_id INTEGER NOT NULL,
    prioridad_id INTEGER NOT NULL,
    categoria_id INTEGER,
    
    -- Referencias a microservicios externos (solo IDs, sin FK)
    usuario_reportante_id TEXT NOT NULL,  -- ID del usuario (desde módulo de usuarios)
    responsable_id TEXT,  -- ID del técnico/responsable (desde módulo de usuarios)
    salon_id TEXT,  -- ID del salón (desde módulo de salones)
    
    -- Timestamps
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE,
    fecha_resolucion TIMESTAMP WITH TIME ZONE,
    
    -- Foreign Keys solo para catálogos internos
    CONSTRAINT fk_incidencias_estado 
        FOREIGN KEY (estado_id) REFERENCES estados(id),
    CONSTRAINT fk_incidencias_prioridad 
        FOREIGN KEY (prioridad_id) REFERENCES prioridades(id),
    CONSTRAINT fk_incidencias_categoria 
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_incidencias_titulo ON incidencias(titulo);
CREATE INDEX IF NOT EXISTS idx_incidencias_estado ON incidencias(estado_id);
CREATE INDEX IF NOT EXISTS idx_incidencias_prioridad ON incidencias(prioridad_id);
CREATE INDEX IF NOT EXISTS idx_incidencias_categoria ON incidencias(categoria_id);
CREATE INDEX IF NOT EXISTS idx_incidencias_usuario_reportante ON incidencias(usuario_reportante_id);
CREATE INDEX IF NOT EXISTS idx_incidencias_responsable ON incidencias(responsable_id);
CREATE INDEX IF NOT EXISTS idx_incidencias_salon ON incidencias(salon_id);
CREATE INDEX IF NOT EXISTS idx_incidencias_fecha_creacion ON incidencias(fecha_creacion);

-- -----------------------------------------------------------------------------
-- TABLA: historial_incidencias
-- Historial de cambios de una incidencia (RF7: Historial)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS historial_incidencias (
    id SERIAL PRIMARY KEY,
    
    -- Relación con incidencia
    incidencia_id INTEGER NOT NULL,
    
    -- Información del cambio
    accion VARCHAR(100) NOT NULL,
    descripcion TEXT,
    usuario_id TEXT NOT NULL,  -- Usuario que realizó la acción
    
    -- Valores anteriores y nuevos (almacenados como JSON)
    valor_anterior TEXT,
    valor_nuevo TEXT,
    
    -- Timestamp
    fecha_cambio TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
    
-- Índices para historial
CREATE INDEX IF NOT EXISTS idx_historial_incidencia ON historial_incidencias(incidencia_id);
CREATE INDEX IF NOT EXISTS idx_historial_usuario ON historial_incidencias(usuario_id);
CREATE INDEX IF NOT EXISTS idx_historial_fecha ON historial_incidencias(fecha_cambio);

-- -----------------------------------------------------------------------------
-- TABLA: adjuntos
-- Archivos adjuntos a incidencias (Normalización - relación 1:N)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS adjuntos (
    id SERIAL PRIMARY KEY,
    incidencia_id INTEGER NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    tipo_mime VARCHAR(100),
    tamanio_bytes BIGINT,
    ruta_almacenamiento TEXT NOT NULL,  -- Ruta en el sistema de archivos o URL de storage
    usuario_id TEXT NOT NULL,  -- Usuario que subió el archivo (ID del módulo de usuarios)
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    CONSTRAINT fk_adjuntos_incidencia 
        FOREIGN KEY (incidencia_id) REFERENCES incidencias(id) ON DELETE CASCADE
);

-- Índice para adjuntos
CREATE INDEX IF NOT EXISTS idx_adjuntos_incidencia ON adjuntos(incidencia_id);

-- -----------------------------------------------------------------------------
-- TABLA: comentarios
-- Comentarios en incidencias (Normalización - relación 1:N)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS comentarios (
    id SERIAL PRIMARY KEY,
    incidencia_id INTEGER NOT NULL,
    usuario_id TEXT NOT NULL,  -- ID del usuario (desde módulo de usuarios)
    contenido TEXT NOT NULL,
    es_interno BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE,
    
    -- Foreign Keys
    CONSTRAINT fk_comentarios_incidencia 
        FOREIGN KEY (incidencia_id) REFERENCES incidencias(id) ON DELETE CASCADE
);

-- Índices para comentarios
CREATE INDEX IF NOT EXISTS idx_comentarios_incidencia ON comentarios(incidencia_id);
CREATE INDEX IF NOT EXISTS idx_comentarios_usuario ON comentarios(usuario_id);

-- =============================================================================
-- VISTAS (Para simplificar consultas comunes)
-- =============================================================================

-- Vista de incidencias con información de catálogos
CREATE OR REPLACE VIEW v_incidencias_detalles AS
SELECT 
    i.id,
    i.titulo,
    i.descripcion,
    e.codigo AS estado_codigo,
    e.nombre AS estado_nombre,
    p.codigo AS prioridad_codigo,
    p.nombre AS prioridad_nombre,
    p.nivel AS prioridad_nivel,
    c.codigo AS categoria_codigo,
    c.nombre AS categoria_nombre,
    i.usuario_reportante_id,
    i.responsable_id,
    i.salon_id,
    i.fecha_creacion,
    i.fecha_actualizacion,
    i.fecha_resolucion
FROM incidencias i
    INNER JOIN estados e ON i.estado_id = e.id
    INNER JOIN prioridades p ON i.prioridad_id = p.id
    LEFT JOIN categorias c ON i.categoria_id = c.id;

-- =============================================================================
-- DOCUMENTACIÓN DE ARQUITECTURA DE MICROSERVICIOS
-- =============================================================================
--
-- INFORMACIÓN INTERNA (almacenada en esta BD):
--   - Estados: Catálogo de estados de incidencias
--   - Prioridades: Catálogo de prioridades
--   - Categorías: Catálogo de tipos de incidencias
--   - Incidencias: Tickets/incidencias
--   - Historial: Cambios en incidencias
--   - Comentarios: Comentarios en incidencias
--   - Adjuntos: Archivos adjuntos
--
-- INFORMACIÓN EXTERNA (obtenida de otros microservicios):
--   - Usuarios: Desde módulo de autenticación/usuarios
--     Campos: id, nombre, email, rol, etc.
--     Endpoints: GET /usuarios/{id}, GET /usuarios/{email}
--   - Salones: Desde módulo de salones
--     Campos: id, nombre, edificio, piso, etc.
--     Endpoints: GET /salones/{id}
--
-- CONTROL DE ACCESO:
--   - Administrador: Puede ver todos los tickets, asignar responsables, cambiar estados
--   - Profesor/Estudiante: Solo ve sus propios tickets (como reportante)
--                          Solo puede crear tickets, no modificar procesos
--
-- FLUJO DE ESTADOS TÍPICO:
--   pendiente → asignada → en_proceso → resuelta → cerrada
--                                     ↘ cancelada
--
-- REQUERIMIENTOS FUNCIONALES IMPLEMENTADOS:
--   RF2: Crear incidencia - Tabla incidencias
--   RF3: Asignar responsable - Solo administrador
--   RF4: Estados del ticket - Solo administrador
--   RF5: Consultar incidencias - Con filtros por rol
--   RF7: Historial - Tabla historial_incidencias
-- =============================================================================

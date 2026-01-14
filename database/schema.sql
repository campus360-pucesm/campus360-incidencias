-- =============================================================================
-- Campus360 Incidencias - Schema de Base de Datos (Microservicio)
-- =============================================================================
-- Este archivo define la estructura de la base de datos para el módulo de
-- gestión de incidencias de Campus360.
-- 
-- INTEGRACIÓN CON ESQUEMA GENERAL:
-- - Usuarios: Se utiliza la tabla 'public.users' del esquema general.
-- - Salones: Se hace referencia a IDs externos (o tablas public.clases/recursos).
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TABLAS DE CATÁLOGO (Deben crearse primero)
-- -----------------------------------------------------------------------------

-- ESTADOS
CREATE TABLE IF NOT EXISTS estados (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    orden INTEGER NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO estados (codigo, nombre, descripcion, orden) VALUES
    ('pendiente', 'Pendiente', 'Estado inicial, incidencia creada pero no asignada', 1),
    ('asignada', 'Asignada', 'Incidencia asignada a un responsable', 2),
    ('en_proceso', 'En Proceso', 'Responsable está trabajando en la incidencia', 3),
    ('resuelta', 'Resuelta', 'Incidencia resuelta, pendiente de cierre', 4),
    ('cerrada', 'Cerrada', 'Incidencia cerrada definitivamente', 5),
    ('cancelada', 'Cancelada', 'Incidencia cancelada', 6)
ON CONFLICT (codigo) DO NOTHING;

-- PRIORIDADES
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

INSERT INTO prioridades (codigo, nombre, descripcion, nivel, color) VALUES
    ('baja', 'Baja', 'No urgente, puede esperar', 1, '#28A745'),
    ('media', 'Media', 'Prioridad normal', 2, '#FFC107'),
    ('alta', 'Alta', 'Requiere atención pronta', 3, '#FD7E14'),
    ('urgente', 'Urgente', 'Requiere atención inmediata', 4, '#DC3545')
ON CONFLICT (codigo) DO NOTHING;

-- CATEGORÍAS
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO categorias (codigo, nombre, descripcion) VALUES
    ('infraestructura', 'Infraestructura', 'Problemas de edificios, aulas, mobiliario'),
    ('tecnologia', 'Tecnología', 'Problemas de equipos, redes, software'),
    ('servicios', 'Servicios', 'Problemas con servicios generales'),
    ('seguridad', 'Seguridad', 'Incidencias de seguridad'),
    ('limpieza', 'Limpieza', 'Problemas de limpieza y mantenimiento'),
    ('otros', 'Otros', 'Otras incidencias no categorizadas')
ON CONFLICT (codigo) DO NOTHING;

-- -----------------------------------------------------------------------------
-- TABLAS PRINCIPALES
-- -----------------------------------------------------------------------------

-- INCIDENCIAS
CREATE TABLE IF NOT EXISTS incidencias (
    id SERIAL PRIMARY KEY,
    
    -- Información básica
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    
    -- Referencias a catálogos internos (FK)
    estado_id INTEGER NOT NULL,
    prioridad_id INTEGER NOT NULL,
    categoria_id INTEGER,
    
    -- Referencias a tablas generales (public.users)
    -- NOTA: Se asume que public.users.id es TEXT.
    usuario_reportante_id TEXT NOT NULL,
    responsable_id TEXT,
    
    -- Referencia a Salón/Recurso (puede ser ID de public.clases o public.recursos)
    salon_id TEXT,
    
    -- Timestamps
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE,
    fecha_resolucion TIMESTAMP WITH TIME ZONE,
    
    -- Constraints FK internas
    CONSTRAINT fk_incidencias_estado FOREIGN KEY (estado_id) REFERENCES estados(id),
    CONSTRAINT fk_incidencias_prioridad FOREIGN KEY (prioridad_id) REFERENCES prioridades(id),
    CONSTRAINT fk_incidencias_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    
    -- Constraints FK a esquema public
    CONSTRAINT fk_incidencias_reportante FOREIGN KEY (usuario_reportante_id) REFERENCES public.users(id),
    CONSTRAINT fk_incidencias_responsable FOREIGN KEY (responsable_id) REFERENCES public.users(id)
);

CREATE INDEX IF NOT EXISTS idx_incidencias_titulo ON incidencias(titulo);
CREATE INDEX IF NOT EXISTS idx_incidencias_estado ON incidencias(estado_id);
CREATE INDEX IF NOT EXISTS idx_incidencias_prioridad ON incidencias(prioridad_id);
CREATE INDEX IF NOT EXISTS idx_incidencias_usuario_reportante ON incidencias(usuario_reportante_id);
CREATE INDEX IF NOT EXISTS idx_incidencias_responsable ON incidencias(responsable_id);

-- HISTORIAL
CREATE TABLE IF NOT EXISTS historial_incidencias (
    id SERIAL PRIMARY KEY,
    incidencia_id INTEGER NOT NULL,
    accion VARCHAR(100) NOT NULL,
    descripcion TEXT,
    usuario_id TEXT NOT NULL, -- FK a public.users
    valor_anterior TEXT,
    valor_nuevo TEXT,
    fecha_cambio TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_historial_incidencia FOREIGN KEY (incidencia_id) REFERENCES incidencias(id) ON DELETE CASCADE,
    CONSTRAINT fk_historial_usuario FOREIGN KEY (usuario_id) REFERENCES public.users(id)
);

CREATE INDEX IF NOT EXISTS idx_historial_incidencia ON historial_incidencias(incidencia_id);

-- ADJUNTOS
CREATE TABLE IF NOT EXISTS adjuntos (
    id SERIAL PRIMARY KEY,
    incidencia_id INTEGER NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    tipo_mime VARCHAR(100),
    tamanio_bytes BIGINT,
    ruta_almacenamiento TEXT NOT NULL,
    usuario_id TEXT NOT NULL, -- FK a public.users
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_adjuntos_incidencia FOREIGN KEY (incidencia_id) REFERENCES incidencias(id) ON DELETE CASCADE,
    CONSTRAINT fk_adjuntos_usuario FOREIGN KEY (usuario_id) REFERENCES public.users(id)
);

CREATE INDEX IF NOT EXISTS idx_adjuntos_incidencia ON adjuntos(incidencia_id);

-- COMENTARIOS
CREATE TABLE IF NOT EXISTS comentarios (
    id SERIAL PRIMARY KEY,
    incidencia_id INTEGER NOT NULL,
    usuario_id TEXT NOT NULL, -- FK a public.users
    contenido TEXT NOT NULL,
    es_interno BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT fk_comentarios_incidencia FOREIGN KEY (incidencia_id) REFERENCES incidencias(id) ON DELETE CASCADE,
    CONSTRAINT fk_comentarios_usuario FOREIGN KEY (usuario_id) REFERENCES public.users(id)
);

CREATE INDEX IF NOT EXISTS idx_comentarios_incidencia ON comentarios(incidencia_id);

-- -----------------------------------------------------------------------------
-- VISTAS
-- -----------------------------------------------------------------------------

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
    u_repo.full_name AS usuario_reportante_nombre,
    i.responsable_id,
    u_resp.full_name AS responsable_nombre,
    i.salon_id,
    i.fecha_creacion,
    i.fecha_actualizacion,
    i.fecha_resolucion
FROM incidencias i
    INNER JOIN estados e ON i.estado_id = e.id
    INNER JOIN prioridades p ON i.prioridad_id = p.id
    LEFT JOIN categorias c ON i.categoria_id = c.id
    LEFT JOIN public.users u_repo ON i.usuario_reportante_id = u_repo.id
    LEFT JOIN public.users u_resp ON i.responsable_id = u_resp.id;

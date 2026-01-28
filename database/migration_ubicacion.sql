-- =============================================================================
-- Script de migración: Cambiar salon_id a ubicacion_id
-- =============================================================================
-- Ejecutar este script si la tabla incidencias ya existe con salon_id

-- 1. Agregar nueva columna ubicacion_id
ALTER TABLE incidencias 
ADD COLUMN IF NOT EXISTS ubicacion_id UUID;

-- 2. Crear índice para la nueva columna
CREATE INDEX IF NOT EXISTS idx_incidencias_ubicacion ON incidencias(ubicacion_id);

-- 3. Agregar constraint FK a recursos
ALTER TABLE incidencias 
ADD CONSTRAINT fk_incidencias_ubicacion 
FOREIGN KEY (ubicacion_id) REFERENCES public.recursos(id);

-- 4. Eliminar columna salon_id (opcional, solo si no la necesitas)
-- ALTER TABLE incidencias DROP COLUMN IF EXISTS salon_id;

-- 5. Actualizar la vista
DROP VIEW IF EXISTS v_incidencias_detalles;

CREATE VIEW v_incidencias_detalles AS
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
    i.ubicacion_id,
    r.codigo AS ubicacion_codigo,
    r.nombre AS ubicacion_nombre,
    r.ubicacion AS ubicacion_direccion,
    i.fecha_creacion,
    i.fecha_actualizacion,
    i.fecha_resolucion
FROM incidencias i
    INNER JOIN estados e ON i.estado_id = e.id
    INNER JOIN prioridades p ON i.prioridad_id = p.id
    LEFT JOIN categorias c ON i.categoria_id = c.id
    LEFT JOIN public.users u_repo ON i.usuario_reportante_id = u_repo.id
    LEFT JOIN public.users u_resp ON i.responsable_id = u_resp.id
    LEFT JOIN public.recursos r ON i.ubicacion_id = r.id;

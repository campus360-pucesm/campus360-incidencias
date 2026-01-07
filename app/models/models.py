from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config import Base


# =============================================================================
# TABLAS DE CATÁLOGO (Normalización 3NF)
# =============================================================================

class Estado(Base):
    """
    Catálogo de estados posibles para incidencias.
    RF4: Estados del ticket
    """
    __tablename__ = "estados"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    orden = Column(Integer, nullable=False, default=0)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relación inversa
    incidencias = relationship("Incidencia", back_populates="estado_rel")

    def __repr__(self):
        return f"<Estado(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Prioridad(Base):
    """
    Catálogo de niveles de prioridad.
    """
    __tablename__ = "prioridades"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    nivel = Column(Integer, nullable=False)
    color = Column(String(7), nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relación inversa
    incidencias = relationship("Incidencia", back_populates="prioridad_rel")

    def __repr__(self):
        return f"<Prioridad(codigo='{self.codigo}', nivel={self.nivel})>"


class Categoria(Base):
    """
    Catálogo de categorías de incidencias.
    Normalización 2NF - elimina redundancia
    """
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relación inversa
    incidencias = relationship("Incidencia", back_populates="categoria_rel")

    def __repr__(self):
        return f"<Categoria(codigo='{self.codigo}', nombre='{self.nombre}')>"


class Ubicacion(Base):
    """
    Catálogo de ubicaciones físicas (salones).
    NOTA: En arquitectura de microservicios, los salones se obtienen del módulo de salones.
    Esta tabla solo almacena IDs de referencia.
    """
    __tablename__ = "ubicaciones"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    edificio = Column(String(100), nullable=True)
    piso = Column(String(20), nullable=True)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Ubicacion(codigo='{self.codigo}', nombre='{self.nombre}')>"





# =============================================================================
# TABLAS PRINCIPALES
# =============================================================================

class Incidencia(Base):
    """
    Modelo principal para las incidencias/tickets.
    RF2: Crear incidencia
    Normalizado a 3NF con referencias a catálogos internos.
    Referencias a usuarios y salones se obtienen de otros microservicios.
    """
    __tablename__ = "incidencias"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    
    # Referencias a catálogos internos (FK - Normalización 3NF)
    estado_id = Column(Integer, ForeignKey("estados.id"), nullable=False, index=True)
    prioridad_id = Column(Integer, ForeignKey("prioridades.id"), nullable=False, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True, index=True)
    
    # Referencias a microservicios externos (solo IDs, sin FK)
    usuario_reportante_id = Column(String(100), nullable=False, index=True)  # ID del usuario desde módulo de usuarios
    responsable_id = Column(String(100), nullable=True, index=True)  # ID del técnico desde módulo de usuarios
    salon_id = Column(String(100), nullable=True, index=True)  # ID del salón desde módulo de salones
    
    # Timestamps
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    fecha_resolucion = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    estado_rel = relationship("Estado", back_populates="incidencias")
    prioridad_rel = relationship("Prioridad", back_populates="incidencias")
    categoria_rel = relationship("Categoria", back_populates="incidencias")
    historial = relationship("HistorialIncidencia", back_populates="incidencia", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="incidencia", cascade="all, delete-orphan")
    adjuntos = relationship("Adjunto", back_populates="incidencia", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Incidencia(id={self.id}, titulo='{self.titulo}')>"


class HistorialIncidencia(Base):
    """
    Modelo para el historial de cambios de una incidencia.
    RF7: Historial
    """
    __tablename__ = "historial_incidencias"

    id = Column(Integer, primary_key=True, index=True)
    incidencia_id = Column(Integer, ForeignKey("incidencias.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Información del cambio
    accion = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    usuario_id = Column(String(100), nullable=False, index=True)  # ID del usuario (desde módulo de usuarios)
    
    # Valores anteriores y nuevos
    valor_anterior = Column(Text, nullable=True)
    valor_nuevo = Column(Text, nullable=True)
    
    # Timestamp
    fecha_cambio = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relaciones
    incidencia = relationship("Incidencia", back_populates="historial")

    def __repr__(self):
        return f"<HistorialIncidencia(id={self.id}, incidencia_id={self.incidencia_id}, accion='{self.accion}')>"


class Comentario(Base):
    """
    Comentarios en incidencias.
    Normalización - relación 1:N
    """
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    incidencia_id = Column(Integer, ForeignKey("incidencias.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(String(100), nullable=False, index=True)  # ID del usuario (desde módulo de usuarios)
    contenido = Column(Text, nullable=False)
    es_interno = Column(Boolean, nullable=False, default=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    incidencia = relationship("Incidencia", back_populates="comentarios")

    def __repr__(self):
        return f"<Comentario(id={self.id}, incidencia_id={self.incidencia_id})>"


class Adjunto(Base):
    """
    Archivos adjuntos a incidencias.
    Normalización - relación 1:N
    """
    __tablename__ = "adjuntos"

    id = Column(Integer, primary_key=True, index=True)
    incidencia_id = Column(Integer, ForeignKey("incidencias.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre_archivo = Column(String(255), nullable=False)
    tipo_mime = Column(String(100), nullable=True)
    tamanio_bytes = Column(BigInteger, nullable=True)
    ruta_almacenamiento = Column(Text, nullable=False)
    usuario_id = Column(String(100), nullable=False)  # ID del usuario (desde módulo de usuarios)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relaciones
    incidencia = relationship("Incidencia", back_populates="adjuntos")

    def __repr__(self):
        return f"<Adjunto(id={self.id}, nombre='{self.nombre_archivo}')>"


# =============================================================================
# Constantes para códigos de estado (para uso en servicios)
# =============================================================================
class EstadoCodigo:
    """Códigos de estado para uso en la lógica de negocio"""
    PENDIENTE = "pendiente"
    ASIGNADA = "asignada"
    EN_PROCESO = "en_proceso"
    RESUELTA = "resuelta"
    CERRADA = "cerrada"
    CANCELADA = "cancelada"


class PrioridadCodigo:
    """Códigos de prioridad para uso en la lógica de negocio"""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"

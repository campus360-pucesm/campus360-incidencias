from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


# =============================================================================
# Schemas para Catálogos (Normalización 3NF)
# =============================================================================

class EstadoBase(BaseModel):
    """Schema base para estados"""
    codigo: str = Field(..., max_length=20)
    nombre: str = Field(..., max_length=50)
    descripcion: Optional[str] = None
    orden: int = Field(default=0)
    activo: bool = Field(default=True)


class EstadoResponse(EstadoBase):
    """Schema de respuesta para estados"""
    id: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class PrioridadBase(BaseModel):
    """Schema base para prioridades"""
    codigo: str = Field(..., max_length=20)
    nombre: str = Field(..., max_length=50)
    descripcion: Optional[str] = None
    nivel: int
    color: Optional[str] = Field(None, max_length=7)
    activo: bool = Field(default=True)


class PrioridadResponse(PrioridadBase):
    """Schema de respuesta para prioridades"""
    id: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoriaBase(BaseModel):
    """Schema base para categorías"""
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)


class CategoriaCreate(CategoriaBase):
    """Schema para crear categoría"""
    pass


class CategoriaResponse(CategoriaBase):
    """Schema de respuesta para categorías"""
    id: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class UbicacionBase(BaseModel):
    """Schema base para ubicaciones"""
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=200)
    edificio: Optional[str] = Field(None, max_length=100)
    piso: Optional[str] = Field(None, max_length=20)
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)


class UbicacionCreate(UbicacionBase):
    """Schema para crear ubicación"""
    pass


class UbicacionResponse(UbicacionBase):
    """Schema de respuesta para ubicaciones"""
    id: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class UsuarioBase(BaseModel):
    """Schema base para usuarios"""
    email: str = Field(..., max_length=255)
    full_name: Optional[str] = Field(None, max_length=200)
    role: str = Field(default="usuario", max_length=50)
    activo: bool = Field(default=True)


class UsuarioCreate(UsuarioBase):
    """Schema para crear usuario"""
    id: str = Field(..., max_length=100)
    password_hash: str


class UsuarioUpdate(BaseModel):
    """Schema para actualizar usuario"""
    email: Optional[str] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=200)
    role: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None


class UsuarioResponse(UsuarioBase):
    """Schema de respuesta para usuarios"""
    id: str
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UsuarioSimpleResponse(BaseModel):
    """Schema simplificado de usuario para incluir en otras respuestas"""
    id: str
    full_name: Optional[str] = None
    email: str

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Schemas para Incidencias
# =============================================================================

class IncidenciaBase(BaseModel):
    """Schema base para incidencias"""
    titulo: str = Field(..., min_length=1, max_length=200, description="Título de la incidencia")
    descripcion: str = Field(..., min_length=1, description="Descripción detallada de la incidencia")


class IncidenciaCreate(IncidenciaBase):
    """
    Schema para crear una nueva incidencia. RF2: Crear incidencia
    Usa códigos de catálogo en lugar de IDs para facilitar la creación
    """
    prioridad_codigo: str = Field(default="media", description="Código de prioridad")
    categoria_codigo: Optional[str] = Field(None, description="Código de categoría")
    ubicacion_codigo: Optional[str] = Field(None, description="Código de ubicación")


class IncidenciaUpdate(BaseModel):
    """Schema para actualizar una incidencia"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = Field(None, min_length=1)
    estado_codigo: Optional[str] = Field(None, description="Código del nuevo estado")
    prioridad_codigo: Optional[str] = Field(None, description="Código de prioridad")
    categoria_codigo: Optional[str] = Field(None, description="Código de categoría")
    ubicacion_codigo: Optional[str] = Field(None, description="Código de ubicación")


class HistorialIncidenciaResponse(BaseModel):
    """Schema para el historial de una incidencia. RF7: Historial"""
    id: int
    incidencia_id: int
    accion: str
    descripcion: Optional[str]
    usuario: UsuarioSimpleResponse
    valor_anterior: Optional[str]
    valor_nuevo: Optional[str]
    fecha_cambio: datetime

    model_config = ConfigDict(from_attributes=True)


class ComentarioBase(BaseModel):
    """Schema base para comentarios"""
    contenido: str = Field(..., min_length=1, description="Contenido del comentario")
    es_interno: bool = Field(default=False, description="Si es solo visible para técnicos")


class ComentarioCreate(ComentarioBase):
    """Schema para crear comentario"""
    pass


class ComentarioResponse(ComentarioBase):
    """Schema de respuesta para comentarios"""
    id: int
    incidencia_id: int
    usuario: UsuarioSimpleResponse
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AdjuntoResponse(BaseModel):
    """Schema de respuesta para adjuntos"""
    id: int
    incidencia_id: int
    nombre_archivo: str
    tipo_mime: Optional[str]
    tamanio_bytes: Optional[int]
    usuario: UsuarioSimpleResponse
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidenciaResponse(IncidenciaBase):
    """Schema de respuesta para una incidencia. RF5: Consultar incidencias"""
    id: int
    estado: EstadoResponse
    prioridad: PrioridadResponse
    categoria: Optional[CategoriaResponse] = None
    ubicacion: Optional[UbicacionResponse] = None
    reportante: UsuarioSimpleResponse
    responsable: Optional[UsuarioSimpleResponse] = None
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    fecha_resolucion: Optional[datetime] = None
    historial: List[HistorialIncidenciaResponse] = []
    comentarios: List[ComentarioResponse] = []

    model_config = ConfigDict(from_attributes=True)


class IncidenciaListResponse(BaseModel):
    """Schema para listar incidencias con paginación"""
    id: int
    titulo: str
    estado: EstadoResponse
    prioridad: PrioridadResponse
    categoria: Optional[CategoriaResponse] = None
    reportante: UsuarioSimpleResponse
    responsable: Optional[UsuarioSimpleResponse] = None
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Schemas para Filtros y Búsqueda
# =============================================================================

class IncidenciaFilters(BaseModel):
    """Filtros para consultar incidencias"""
    estado_codigo: Optional[str] = None
    prioridad_codigo: Optional[str] = None
    categoria_codigo: Optional[str] = None
    usuario_reportante_id: Optional[str] = None
    responsable_id: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# =============================================================================
# Schemas para Operaciones Especiales
# =============================================================================

class AsignarResponsableRequest(BaseModel):
    """Schema para asignar un responsable. RF3: Asignar responsable"""
    responsable_id: str = Field(..., description="ID del responsable a asignar")
    comentario: Optional[str] = Field(None, description="Comentario sobre la asignación")


class CambiarEstadoRequest(BaseModel):
    """Schema para cambiar el estado de una incidencia. RF4: Estados del ticket"""
    estado_codigo: str = Field(..., description="Código del nuevo estado")
    comentario: Optional[str] = Field(None, description="Comentario sobre el cambio de estado")


# =============================================================================
# Schemas para Respuestas Paginadas
# =============================================================================

class PaginatedResponse(BaseModel):
    """Schema genérico para respuestas paginadas"""
    items: List
    total: int
    limit: int
    offset: int
    has_more: bool


class IncidenciasPaginatedResponse(BaseModel):
    """Schema para respuesta paginada de incidencias"""
    incidencias: List[IncidenciaListResponse]
    total: int
    limit: int
    offset: int
    has_more: bool

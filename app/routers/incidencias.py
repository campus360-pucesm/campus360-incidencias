from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.dependencies import get_db, validate_jwt
from app.schemas.schemas import (
    IncidenciaCreate,
    IncidenciaResponse,
    IncidenciaUpdate,
    IncidenciaListResponse,
    AsignarResponsableRequest,
    CambiarEstadoRequest,
    HistorialIncidenciaResponse,
    EstadoResponse,
    PrioridadResponse,
    CategoriaResponse,
    UbicacionResponse,
    ComentarioCreate,
    ComentarioResponse,
    IncidenciasPaginatedResponse
)
from app.services.services import (
    IncidenciaService, HistorialService, CatalogoService, 
    UsuarioService, ComentarioService
)
from app.utils import (
    validar_es_administrador,
    requiere_administrador,
    validar_acceso_incidencia,
    validar_puede_comentar,
    PermissionDenied
)

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"]
)


# =============================================================================
# Endpoints de Catálogos
# =============================================================================

@router.get(
    "/catalogos/estados",
    response_model=list[EstadoResponse],
    summary="Listar estados",
    description="Obtiene el catálogo de estados disponibles"
)
async def listar_estados(
    db: Session = Depends(get_db)
):
    """Lista todos los estados activos"""
    return CatalogoService.listar_estados(db)


@router.get(
    "/catalogos/prioridades",
    response_model=list[PrioridadResponse],
    summary="Listar prioridades",
    description="Obtiene el catálogo de prioridades disponibles"
)
async def listar_prioridades(
    db: Session = Depends(get_db)
):
    """Lista todas las prioridades activas"""
    return CatalogoService.listar_prioridades(db)


@router.get(
    "/catalogos/categorias",
    response_model=list[CategoriaResponse],
    summary="Listar categorías",
    description="Obtiene el catálogo de categorías disponibles"
)
async def listar_categorias(
    db: Session = Depends(get_db)
):
    """Lista todas las categorías activas"""
    return CatalogoService.listar_categorias(db)


@router.get(
    "/catalogos/ubicaciones",
    response_model=list[UbicacionResponse],
    summary="Listar ubicaciones",
    description="Obtiene el catálogo de ubicaciones disponibles"
)
async def listar_ubicaciones(
    db: Session = Depends(get_db)
):
    """Lista todas las ubicaciones activas"""
    return CatalogoService.listar_ubicaciones(db)


# =============================================================================
# Endpoints de Incidencias
# =============================================================================

@router.post(
    "/",
    response_model=IncidenciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo ticket",
    description="RF2: Crear incidencia - Permite a los usuarios reportar un nuevo ticket"
)
async def crear_incidencia(
    incidencia_data: IncidenciaCreate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(validate_jwt)
):
    """
    Crea un nuevo ticket.
    Requiere autenticación JWT válida.
    """
    try:
        incidencia = IncidenciaService.crear_incidencia(
            db=db,
            incidencia_data=incidencia_data,
            usuario_id=usuario.get("user_id", usuario.get("id", usuario.get("sub"))),
            usuario_email=usuario.get("email", ""),
            usuario_nombre=usuario.get("full_name", usuario.get("name"))
        )
        return incidencia
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=IncidenciasPaginatedResponse,
    summary="Listar tickets",
    description="RF5: Consultar incidencias - Lista tickets con filtros opcionales y paginación"
)
async def listar_incidencias(
    estado_codigo: Optional[str] = Query(None, description="Filtrar por código de estado"),
    prioridad_codigo: Optional[str] = Query(None, description="Filtrar por código de prioridad"),
    categoria_codigo: Optional[str] = Query(None, description="Filtrar por código de categoría"),
    usuario_reportante_id: Optional[str] = Query(None, description="Filtrar por ID de usuario reportante"),
    responsable_id: Optional[str] = Query(None, description="Filtrar por ID de responsable"),
    limit: int = Query(10, ge=1, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: Session = Depends(get_db),
    usuario: dict = Depends(validate_jwt)
):
    """
    Lista tickets con filtros opcionales.
    
    Reglas de acceso:
    - Administrador: Ve todos los tickets
    - Profesor/Estudiante: Solo ve los tickets que ha reportado
    
    Requiere autenticación JWT válida.
    """
    usuario_id = usuario.get("user_id", usuario.get("id", usuario.get("sub")))
    es_admin = validar_es_administrador(usuario)
    
    # Si no es administrador, forzar filtro por usuario reportante
    if not es_admin:
        usuario_reportante_id = usuario_id
    
    incidencias, total = IncidenciaService.listar_incidencias(
        db=db,
        estado_codigo=estado_codigo,
        prioridad_codigo=prioridad_codigo,
        categoria_codigo=categoria_codigo,
        usuario_reportante_id=usuario_reportante_id,
        responsable_id=responsable_id,
        limit=limit,
        offset=offset
    )
    
    return {
        "incidencias": incidencias,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }


@router.get(
    "/{ticket_id}",
    response_model=IncidenciaResponse,
    summary="Obtener ticket por ID",
    description="RF5: Consultar incidencias - Obtiene los detalles completos de un ticket"
)
async def obtener_incidencia(
    ticket_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(validate_jwt)
):
    """
    Obtiene los detalles de un ticket específico.
    
    Reglas de acceso:
    - Administrador: Puede ver cualquier ticket
    - Profesor/Estudiante: Solo puede ver los tickets que ha reportado
    
    Requiere autenticación JWT válida.
    """
    usuario_id = usuario.get("user_id", usuario.get("id", usuario.get("sub")))
    incidencia = IncidenciaService.obtener_incidencia(db, ticket_id)
    
    if not incidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )
    
    # Validar acceso
    try:
        validar_acceso_incidencia(incidencia, usuario, usuario_id)
    except PermissionDenied as e:
        raise e
    
    return incidencia


@router.put(
    "/{ticket_id}",
    response_model=IncidenciaResponse,
    summary="Actualizar ticket",
    description="Actualiza los datos de un ticket existente"
)
async def actualizar_incidencia(
    ticket_id: int,
    incidencia_data: IncidenciaUpdate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(validate_jwt)
):
    """
    Actualiza un ticket existente.
    
    Restricción: Solo administradores pueden actualizar tickets.
    
    Requiere autenticación JWT válida.
    """
    usuario_id = usuario.get("user_id", usuario.get("id", usuario.get("sub")))
    
    # Solo administradores pueden actualizar tickets
    try:
        requiere_administrador(usuario)
    except PermissionDenied as e:
        raise e
    
    # Obtener usuario interno
    usuario_interno = UsuarioService.obtener_o_crear_usuario(
        db=db,
        usuario_id=usuario_id,
        email=usuario.get("email", ""),
        full_name=usuario.get("full_name", usuario.get("name"))
    )
    
    incidencia = IncidenciaService.actualizar_incidencia(
        db=db,
        incidencia_id=ticket_id,
        incidencia_data=incidencia_data,
        usuario_id=usuario_interno.id
    )
    
    if not incidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )
    
    return incidencia


@router.post(
    "/{ticket_id}/asignar",
    response_model=IncidenciaResponse,
    summary="Asignar responsable",
    description="RF3: Asignar responsable - Asigna un técnico/responsable a un ticket"
)
async def asignar_responsable(
    ticket_id: int,
    asignacion_data: AsignarResponsableRequest,
    db: Session = Depends(get_db),
    usuario: dict = Depends(validate_jwt)
):
    """
    Asigna un responsable a un ticket.
    
    Restricción: Solo administradores pueden asignar responsables.
    
    Requiere autenticación JWT válida.
    """
    usuario_id = usuario.get("user_id", usuario.get("id", usuario.get("sub")))
    
    # Solo administradores pueden asignar responsables
    try:
        requiere_administrador(usuario)
    except PermissionDenied as e:
        raise e
    
    # Obtener usuario interno
    usuario_interno = UsuarioService.obtener_o_crear_usuario(
        db=db,
        usuario_id=usuario_id,
        email=usuario.get("email", ""),
        full_name=usuario.get("full_name", usuario.get("name"))
    )
    
    try:
        incidencia = IncidenciaService.asignar_responsable(
            db=db,
            incidencia_id=ticket_id,
            asignacion_data=asignacion_data,
            usuario_id=usuario_interno.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    if not incidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )
    
    return incidencia


@router.post(
    "/{ticket_id}/cambiar-estado",
    response_model=IncidenciaResponse,
    summary="Cambiar estado de ticket",
    description="RF4: Estados del ticket - Cambia el estado de un ticket"
)
async def cambiar_estado(
    ticket_id: int,
    cambio_estado: CambiarEstadoRequest,
    db: Session = Depends(get_db),
    usuario: dict = Depends(validate_jwt)
):
    """
    Cambia el estado de un ticket.
    
    Restricción: Solo administradores pueden cambiar el estado de un ticket.
    
    Requiere autenticación JWT válida.
    """
    usuario_id = usuario.get("user_id", usuario.get("id", usuario.get("sub")))
    
    # Solo administradores pueden cambiar estados
    try:
        requiere_administrador(usuario)
    except PermissionDenied as e:
        raise e
    
    # Obtener usuario interno
    usuario_interno = UsuarioService.obtener_o_crear_usuario(
        db=db,
        usuario_id=usuario_id,
        email=usuario.get("email", ""),
        full_name=usuario.get("full_name", usuario.get("name"))
    )
    
    try:
        incidencia = IncidenciaService.cambiar_estado(
            db=db,
            incidencia_id=ticket_id,
            cambio_estado=cambio_estado,
            usuario_id=usuario_interno.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    if not incidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )
    
    return incidencia


@router.get(
    "/{ticket_id}/historial",
    response_model=list[HistorialIncidenciaResponse],
    summary="Obtener historial de ticket",
    description="RF7: Historial - Obtiene el historial completo de cambios de un ticket"
)
async def obtener_historial(
    ticket_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(validate_jwt)
):
    """
    Obtiene el historial completo de un ticket.
    
    Restricción: Solo el reportante y administradores pueden ver el historial.
    
    Requiere autenticación JWT válida.
    """
    usuario_id = usuario.get("user_id", usuario.get("id", usuario.get("sub")))
    
    # Verificar que el ticket existe
    incidencia = IncidenciaService.obtener_incidencia(db, ticket_id)
    if not incidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )
    
    # Validar acceso al ticket
    try:
        validar_acceso_incidencia(incidencia, usuario, usuario_id)
    except PermissionDenied as e:
        raise e
    
    historial = HistorialService.obtener_historial(db, ticket_id)
    return historial


# =============================================================================
# Endpoints de Comentarios
# =============================================================================

@router.post(
    "/{ticket_id}/comentarios",
    response_model=ComentarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar comentario",
    description="Agrega un comentario a un ticket"
)
async def agregar_comentario(
    ticket_id: int,
    comentario_data: ComentarioCreate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(validate_jwt)
):
    """
    Agrega un comentario a un ticket.
    
    Restricción: Solo el reportante del ticket puede comentar.
    
    Requiere autenticación JWT válida.
    """
    usuario_id = usuario.get("user_id", usuario.get("id", usuario.get("sub")))
    
    # Verificar que el ticket existe
    incidencia = IncidenciaService.obtener_incidencia(db, ticket_id)
    if not incidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )
    
    # Validar acceso
    try:
        validar_puede_comentar(incidencia, usuario, usuario_id)
    except PermissionDenied as e:
        raise e
    
    # Obtener usuario interno
    usuario_interno = UsuarioService.obtener_o_crear_usuario(
        db=db,
        usuario_id=usuario_id,
        email=usuario.get("email", ""),
        full_name=usuario.get("full_name", usuario.get("name"))
    )
    
    comentario = ComentarioService.crear_comentario(
        db=db,
        incidencia_id=ticket_id,
        comentario_data=comentario_data,
        usuario_id=usuario_interno.id
    )
    
    return comentario


@router.get(
    "/{ticket_id}/comentarios",
    response_model=list[ComentarioResponse],
    summary="Listar comentarios",
    description="Lista los comentarios de un ticket"
)
async def listar_comentarios(
    ticket_id: int,
    incluir_internos: bool = Query(False, description="Incluir comentarios internos"),
    db: Session = Depends(get_db),
    usuario: dict = Depends(validate_jwt)
):
    """
    Lista los comentarios de un ticket.
    
    Restricción: Solo el reportante y administradores pueden ver comentarios.
    
    Requiere autenticación JWT válida.
    """
    usuario_id = usuario.get("user_id", usuario.get("id", usuario.get("sub")))
    
    # Verificar que el ticket existe
    incidencia = IncidenciaService.obtener_incidencia(db, ticket_id)
    if not incidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )
    
    # Validar acceso al ticket
    try:
        validar_acceso_incidencia(incidencia, usuario, usuario_id)
    except PermissionDenied as e:
        raise e
    
    # Solo administradores pueden ver comentarios internos
    if incluir_internos and not validar_es_administrador(usuario):
        incluir_internos = False
    
    comentarios = ComentarioService.listar_comentarios(
        db=db,
        incidencia_id=ticket_id,
        incluir_internos=incluir_internos
    )
    
    return comentarios


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ticket",
    description="Elimina un ticket (solo para administradores)"
)
async def eliminar_incidencia(
    ticket_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(validate_jwt)
):
    """
    Elimina un ticket.
    
    Restricción: Solo administradores pueden eliminar tickets.
    
    Requiere autenticación JWT válida.
    """
    # Solo administradores pueden eliminar
    try:
        requiere_administrador(usuario)
    except PermissionDenied as e:
        raise e
    
    eliminada = IncidenciaService.eliminar_incidencia(db, ticket_id)
    
    if not eliminada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )
    
    return None

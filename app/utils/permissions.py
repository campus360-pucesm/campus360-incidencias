"""
Utilidades para control de permisos en el módulo de incidencias.

En arquitectura de microservicios:
- Administrador: Puede ver todos los tickets, asignar responsables, cambiar estados
- Profesor/Estudiante: Solo ve sus propios tickets (como reportante)
                       Solo puede crear tickets, no modificar procesos
"""

from fastapi import HTTPException, status


class PermissionDenied(HTTPException):
    """Excepción personalizada para denegación de permisos"""
    def __init__(self, detail: str = "No tiene permisos para realizar esta acción"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


def validar_es_administrador(usuario: dict) -> bool:
    """
    Valida si el usuario es administrador.
    El rol viene desde el JWT del módulo de autenticación.
    """
    role = usuario.get("role", usuario.get("tipo_usuario", "")).lower()
    return role in ["administrador", "admin"]


def validar_es_tecnico(usuario: dict) -> bool:
    """
    Valida si el usuario es técnico (puede cambiar estados y asignar).
    El rol viene desde el JWT del módulo de autenticación.
    """
    role = usuario.get("role", usuario.get("tipo_usuario", "")).lower()
    return role in ["tecnico", "administrador", "admin"]


def requiere_administrador(usuario: dict):
    """
    Verifica que el usuario sea administrador.
    Si no lo es, lanza una excepción.
    """
    if not validar_es_administrador(usuario):
        raise PermissionDenied(
            detail="Solo los administradores pueden realizar esta acción"
        )


def requiere_tecnico(usuario: dict):
    """
    Verifica que el usuario sea técnico o administrador.
    Si no lo es, lanza una excepción.
    """
    if not validar_es_tecnico(usuario):
        raise PermissionDenied(
            detail="Solo los técnicos y administradores pueden realizar esta acción"
        )


def validar_acceso_incidencia(incidencia, usuario: dict, usuario_id: str):
    """
    Valida si el usuario puede acceder a la incidencia.
    
    Reglas:
    - Administrador: Puede acceder a cualquier incidencia
    - No-Administrador: Solo puede acceder si es el reportante
    """
    es_admin = validar_es_administrador(usuario)
    
    if not es_admin and incidencia.usuario_reportante_id != usuario_id:
        raise PermissionDenied(
            detail="No puede acceder a incidencias de otros usuarios"
        )


def validar_puede_modificar_estado(incidencia, usuario: dict):
    """
    Valida si el usuario puede modificar el estado de la incidencia.
    
    Reglas:
    - Solo administradores pueden cambiar estados
    """
    requiere_administrador(usuario)


def validar_puede_asignar_responsable(incidencia, usuario: dict):
    """
    Valida si el usuario puede asignar responsable a la incidencia.
    
    Reglas:
    - Solo administradores pueden asignar responsables
    """
    requiere_administrador(usuario)


def validar_puede_crear_incidencia(usuario: dict) -> bool:
    """
    Valida si el usuario puede crear una incidencia.
    
    Reglas:
    - Todos los usuarios autenticados pueden crear incidencias
    """
    return True  # Cualquier usuario autenticado puede crear


def validar_puede_comentar(incidencia, usuario: dict, usuario_id: str):
    """
    Valida si el usuario puede comentar en la incidencia.
    
    Reglas:
    - El reportante de la incidencia siempre puede comentar
    - Otros usuarios no pueden comentar en incidencias que no crearon
    - Los administradores siempre pueden comentar
    """
    es_admin = validar_es_administrador(usuario)
    es_reportante = incidencia.usuario_reportante_id == usuario_id
    
    if not es_admin and not es_reportante:
        raise PermissionDenied(
            detail="Solo el reportante de la incidencia puede comentar"
        )

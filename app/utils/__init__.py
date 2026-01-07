"""Utilidades del módulo de incidencias"""

from .permissions import (
    PermissionDenied,
    validar_es_administrador,
    validar_es_tecnico,
    requiere_administrador,
    requiere_tecnico,
    validar_acceso_incidencia,
    validar_puede_modificar_estado,
    validar_puede_asignar_responsable,
    validar_puede_crear_incidencia,
    validar_puede_comentar,
)

__all__ = [
    "PermissionDenied",
    "validar_es_administrador",
    "validar_es_tecnico",
    "requiere_administrador",
    "requiere_tecnico",
    "validar_acceso_incidencia",
    "validar_puede_modificar_estado",
    "validar_puede_asignar_responsable",
    "validar_puede_crear_incidencia",
    "validar_puede_comentar",
]

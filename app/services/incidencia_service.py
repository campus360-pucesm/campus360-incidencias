def crear_incidencia(db: Session, incidencia_data: IncidenciaCreate, usuario_id: str, usuario_email: str, usuario_nombre: Optional[str] = None):
    incidencia = Incidencia(**incidencia_data, usuario_id=usuario_id, usuario_email=usuario_email, usuario_nombre=usuario_nombre)
    db.add(incidencia)
    db.commit()
    db.refresh(incidencia)

    # Serialize the incidencia before returning
    return serialize_incidencia(incidencia)
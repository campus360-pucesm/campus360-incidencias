from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional, Tuple
from datetime import datetime, timezone
from app.models.models import (
    Incidencia, HistorialIncidencia, Usuario, Estado, Prioridad, 
    Categoria, Ubicacion, Comentario, Adjunto, EstadoCodigo, PrioridadCodigo
)
from app.schemas.schemas import (
    IncidenciaCreate, IncidenciaUpdate, AsignarResponsableRequest, 
    CambiarEstadoRequest, ComentarioCreate
)


# =============================================================================
# Servicios para Catálogos
# =============================================================================

class CatalogoService:
    """Servicio para operaciones de catálogos"""

    @staticmethod
    def obtener_estado_por_codigo(db: Session, codigo: str) -> Optional[Estado]:
        """Obtiene un estado por su código"""
        return db.query(Estado).filter(Estado.codigo == codigo, Estado.activo == True).first()

    @staticmethod
    def obtener_prioridad_por_codigo(db: Session, codigo: str) -> Optional[Prioridad]:
        """Obtiene una prioridad por su código"""
        return db.query(Prioridad).filter(Prioridad.codigo == codigo, Prioridad.activo == True).first()

    @staticmethod
    def obtener_categoria_por_codigo(db: Session, codigo: str) -> Optional[Categoria]:
        """Obtiene una categoría por su código"""
        return db.query(Categoria).filter(Categoria.codigo == codigo, Categoria.activo == True).first()

    @staticmethod
    def obtener_ubicacion_por_codigo(db: Session, codigo: str) -> Optional[Ubicacion]:
        """Obtiene una ubicación por su código"""
        return db.query(Ubicacion).filter(Ubicacion.codigo == codigo, Ubicacion.activo == True).first()

    @staticmethod
    def listar_estados(db: Session, solo_activos: bool = True) -> List[Estado]:
        """Lista todos los estados"""
        query = db.query(Estado)
        if solo_activos:
            query = query.filter(Estado.activo == True)
        return query.order_by(Estado.orden).all()

    @staticmethod
    def listar_prioridades(db: Session, solo_activos: bool = True) -> List[Prioridad]:
        """Lista todas las prioridades"""
        query = db.query(Prioridad)
        if solo_activos:
            query = query.filter(Prioridad.activo == True)
        return query.order_by(Prioridad.nivel).all()

    @staticmethod
    def listar_categorias(db: Session, solo_activos: bool = True) -> List[Categoria]:
        """Lista todas las categorías"""
        query = db.query(Categoria)
        if solo_activos:
            query = query.filter(Categoria.activo == True)
        return query.order_by(Categoria.nombre).all()

    @staticmethod
    def listar_ubicaciones(db: Session, solo_activos: bool = True) -> List[Ubicacion]:
        """Lista todas las ubicaciones"""
        query = db.query(Ubicacion)
        if solo_activos:
            query = query.filter(Ubicacion.activo == True)
        return query.order_by(Ubicacion.edificio, Ubicacion.piso, Ubicacion.nombre).all()


# =============================================================================
# Servicio de Usuarios
# =============================================================================

class UsuarioService:
    """Servicio para operaciones de usuarios"""

    @staticmethod
    def obtener_o_crear_usuario(
        db: Session,
        usuario_id: str,
        email: str,
        full_name: Optional[str] = None,
        role: str = "usuario",
        password_hash: str = ""
    ) -> Usuario:
        """
        Obtiene un usuario por su ID o lo crea si no existe.
        Esto permite sincronizar usuarios desde el servicio de autenticación.
        """
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

        if not usuario:
            usuario = Usuario(
                id=usuario_id,
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                role=role
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
        else:
            # Actualizar datos si han cambiado
            updated = False
            if email and usuario.email != email:
                usuario.email = email
                updated = True
            if full_name and usuario.full_name != full_name:
                usuario.full_name = full_name
                updated = True
            if updated:
                db.commit()
                db.refresh(usuario)

        return usuario

    @staticmethod
    def obtener_usuario_por_id(db: Session, usuario_id: str) -> Optional[Usuario]:
        """Obtiene un usuario por su ID"""
        return db.query(Usuario).filter(Usuario.id == usuario_id).first()

    @staticmethod
    def obtener_usuario_por_email(db: Session, email: str) -> Optional[Usuario]:
        """Obtiene un usuario por su email"""
        return db.query(Usuario).filter(Usuario.email == email).first()

    @staticmethod
    def listar_tecnicos(db: Session) -> List[Usuario]:
        """Lista usuarios con rol de técnico o administrador"""
        return db.query(Usuario).filter(
            Usuario.role.in_(["tecnico", "administrador"]),
            Usuario.activo == True
        ).all()


# =============================================================================
# Servicio de Incidencias
# =============================================================================

class IncidenciaService:
    """Servicio para la lógica de negocio de incidencias"""

    @staticmethod
    def crear_incidencia(
        db: Session,
        incidencia_data: IncidenciaCreate,
        usuario_id: str,
        usuario_email: str,
        usuario_nombre: Optional[str] = None
    ) -> Incidencia:
        """
        Crea una nueva incidencia.
        RF2: Crear incidencia
        """
        # Obtener o crear usuario
        usuario = UsuarioService.obtener_o_crear_usuario(
            db=db,
            usuario_id=usuario_id,
            email=usuario_email,
            full_name=usuario_nombre
        )

        # Obtener estado inicial (pendiente)
        estado = CatalogoService.obtener_estado_por_codigo(db, EstadoCodigo.PENDIENTE)
        if not estado:
            raise ValueError("Estado 'pendiente' no encontrado en catálogo")

        # Obtener prioridad
        prioridad = CatalogoService.obtener_prioridad_por_codigo(
            db, incidencia_data.prioridad_codigo or PrioridadCodigo.MEDIA
        )
        if not prioridad:
            raise ValueError(f"Prioridad '{incidencia_data.prioridad_codigo}' no encontrada")

        # Obtener categoría (opcional)
        categoria = None
        if incidencia_data.categoria_codigo:
            categoria = CatalogoService.obtener_categoria_por_codigo(db, incidencia_data.categoria_codigo)

        # Obtener ubicación (opcional)
        ubicacion = None
        if incidencia_data.ubicacion_codigo:
            ubicacion = CatalogoService.obtener_ubicacion_por_codigo(db, incidencia_data.ubicacion_codigo)

        # Crear incidencia
        incidencia = Incidencia(
            titulo=incidencia_data.titulo,
            descripcion=incidencia_data.descripcion,
            estado_id=estado.id,
            prioridad_id=prioridad.id,
            categoria_id=categoria.id if categoria else None,
            ubicacion_id=ubicacion.id if ubicacion else None,
            usuario_reportante_id=usuario.id
        )
        
        db.add(incidencia)
        db.commit()
        db.refresh(incidencia)
        
        # Crear registro en historial
        HistorialService.crear_registro(
            db=db,
            incidencia_id=incidencia.id,
            accion="creada",
            usuario_id=usuario.id,
            descripcion="Incidencia creada"
        )
        
        return incidencia

    @staticmethod
    def obtener_incidencia(db: Session, incidencia_id: int) -> Optional[Incidencia]:
        """Obtiene una incidencia por su ID con todas las relaciones"""
        return db.query(Incidencia)\
            .options(
                joinedload(Incidencia.estado_rel),
                joinedload(Incidencia.prioridad_rel),
                joinedload(Incidencia.categoria_rel),
                joinedload(Incidencia.ubicacion_rel),
                joinedload(Incidencia.reportante),
                joinedload(Incidencia.responsable),
                joinedload(Incidencia.historial).joinedload(HistorialIncidencia.usuario),
                joinedload(Incidencia.comentarios).joinedload(Comentario.usuario)
            )\
            .filter(Incidencia.id == incidencia_id)\
            .first()

    @staticmethod
    def listar_incidencias(
        db: Session,
        estado_codigo: Optional[str] = None,
        prioridad_codigo: Optional[str] = None,
        categoria_codigo: Optional[str] = None,
        usuario_reportante_id: Optional[str] = None,
        responsable_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Tuple[List[Incidencia], int]:
        """
        Lista incidencias con filtros opcionales.
        RF5: Consultar incidencias
        """
        query = db.query(Incidencia)\
            .options(
                joinedload(Incidencia.estado_rel),
                joinedload(Incidencia.prioridad_rel),
                joinedload(Incidencia.categoria_rel),
                joinedload(Incidencia.reportante),
                joinedload(Incidencia.responsable)
            )
        
        # Aplicar filtros
        if estado_codigo:
            estado = CatalogoService.obtener_estado_por_codigo(db, estado_codigo)
            if estado:
                query = query.filter(Incidencia.estado_id == estado.id)
        
        if prioridad_codigo:
            prioridad = CatalogoService.obtener_prioridad_por_codigo(db, prioridad_codigo)
            if prioridad:
                query = query.filter(Incidencia.prioridad_id == prioridad.id)
        
        if categoria_codigo:
            categoria = CatalogoService.obtener_categoria_por_codigo(db, categoria_codigo)
            if categoria:
                query = query.filter(Incidencia.categoria_id == categoria.id)
        
        if usuario_reportante_id:
            query = query.filter(Incidencia.usuario_reportante_id == usuario_reportante_id)
        
        if responsable_id:
            query = query.filter(Incidencia.responsable_id == responsable_id)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginación y ordenar por fecha de creación descendente
        incidencias = query.order_by(desc(Incidencia.fecha_creacion))\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return incidencias, total

    @staticmethod
    def actualizar_incidencia(
        db: Session,
        incidencia_id: int,
        incidencia_data: IncidenciaUpdate,
        usuario_id: str
    ) -> Optional[Incidencia]:
        """Actualiza una incidencia existente"""
        incidencia = IncidenciaService.obtener_incidencia(db, incidencia_id)
        
        if not incidencia:
            return None
        
        cambios = []
        
        # Actualizar título
        if incidencia_data.titulo and incidencia_data.titulo != incidencia.titulo:
            cambios.append(("titulo", incidencia.titulo, incidencia_data.titulo))
            incidencia.titulo = incidencia_data.titulo
        
        # Actualizar descripción
        if incidencia_data.descripcion and incidencia_data.descripcion != incidencia.descripcion:
            cambios.append(("descripcion", incidencia.descripcion, incidencia_data.descripcion))
            incidencia.descripcion = incidencia_data.descripcion
        
        # Actualizar prioridad
        if incidencia_data.prioridad_codigo:
            prioridad = CatalogoService.obtener_prioridad_por_codigo(db, incidencia_data.prioridad_codigo)
            if prioridad and prioridad.id != incidencia.prioridad_id:
                cambios.append(("prioridad", incidencia.prioridad_rel.codigo, prioridad.codigo))
                incidencia.prioridad_id = prioridad.id
        
        # Actualizar categoría
        if incidencia_data.categoria_codigo:
            categoria = CatalogoService.obtener_categoria_por_codigo(db, incidencia_data.categoria_codigo)
            if categoria:
                old_cat = incidencia.categoria_rel.codigo if incidencia.categoria_rel else None
                if categoria.id != incidencia.categoria_id:
                    cambios.append(("categoria", old_cat, categoria.codigo))
                    incidencia.categoria_id = categoria.id
        
        # Actualizar ubicación
        if incidencia_data.ubicacion_codigo:
            ubicacion = CatalogoService.obtener_ubicacion_por_codigo(db, incidencia_data.ubicacion_codigo)
            if ubicacion:
                old_ubi = incidencia.ubicacion_rel.codigo if incidencia.ubicacion_rel else None
                if ubicacion.id != incidencia.ubicacion_id:
                    cambios.append(("ubicacion", old_ubi, ubicacion.codigo))
                    incidencia.ubicacion_id = ubicacion.id
        
        db.commit()
        db.refresh(incidencia)
        
        # Registrar cambios en historial
        for campo, valor_anterior, valor_nuevo in cambios:
            HistorialService.crear_registro(
                db=db,
                incidencia_id=incidencia_id,
                accion=f"{campo}_actualizado",
                usuario_id=usuario_id,
                descripcion=f"Campo {campo} actualizado",
                valor_anterior=str(valor_anterior) if valor_anterior else None,
                valor_nuevo=str(valor_nuevo)
            )
        
        return incidencia

    @staticmethod
    def asignar_responsable(
        db: Session,
        incidencia_id: int,
        asignacion_data: AsignarResponsableRequest,
        usuario_id: int
    ) -> Optional[Incidencia]:
        """
        Asigna un responsable a una incidencia.
        RF3: Asignar responsable
        """
        incidencia = IncidenciaService.obtener_incidencia(db, incidencia_id)
    @staticmethod
    def asignar_responsable(
        db: Session,
        incidencia_id: int,
        asignacion_data: AsignarResponsableRequest,
        usuario_id: str
    ) -> Optional[Incidencia]:
        """
        Asigna un responsable a una incidencia.
        RF3: Asignar responsable
        """
        incidencia = IncidenciaService.obtener_incidencia(db, incidencia_id)
        
        if not incidencia:
            return None
        
        # Verificar que el responsable existe
        responsable = UsuarioService.obtener_usuario_por_id(db, asignacion_data.responsable_id)
        if not responsable:
            raise ValueError(f"Usuario con ID {asignacion_data.responsable_id} no encontrado")
        
        responsable_anterior_id = incidencia.responsable_id
        responsable_anterior_nombre = incidencia.responsable.nombre_completo if incidencia.responsable else None
        incidencia.responsable_id = asignacion_data.responsable_id
        
        # Si estaba pendiente, cambiar a asignada
        if incidencia.estado_rel.codigo == EstadoCodigo.PENDIENTE:
            estado_asignada = CatalogoService.obtener_estado_por_codigo(db, EstadoCodigo.ASIGNADA)
            if estado_asignada:
                incidencia.estado_id = estado_asignada.id
        
        db.commit()
        db.refresh(incidencia)
        
        # Registrar en historial
        HistorialService.crear_registro(
            db=db,
            incidencia_id=incidencia_id,
            accion="responsable_asignado",
            usuario_id=usuario_id,
            descripcion=asignacion_data.comentario or f"Responsable asignado: {responsable.nombre_completo}",
            valor_anterior=responsable_anterior_nombre,
            valor_nuevo=responsable.nombre_completo
        )
        
        return incidencia

    @staticmethod
    def cambiar_estado(
        db: Session,
        incidencia_id: int,
        cambio_estado: CambiarEstadoRequest,
        usuario_id: str
    ) -> Optional[Incidencia]:
        """
        Cambia el estado de una incidencia.
        RF4: Estados del ticket
        """
        incidencia = IncidenciaService.obtener_incidencia(db, incidencia_id)
        
        if not incidencia:
            return None
        
        # Obtener nuevo estado
        nuevo_estado = CatalogoService.obtener_estado_por_codigo(db, cambio_estado.estado_codigo)
        if not nuevo_estado:
            raise ValueError(f"Estado '{cambio_estado.estado_codigo}' no encontrado")
        
        estado_anterior_codigo = incidencia.estado_rel.codigo
        estado_anterior_nombre = incidencia.estado_rel.nombre
        incidencia.estado_id = nuevo_estado.id
        
        # Si se resuelve, registrar fecha de resolución
        if cambio_estado.estado_codigo == EstadoCodigo.RESUELTA:
            incidencia.fecha_resolucion = datetime.now(timezone.utc)
        elif estado_anterior_codigo == EstadoCodigo.RESUELTA and cambio_estado.estado_codigo != EstadoCodigo.RESUELTA:
            incidencia.fecha_resolucion = None
        
        db.commit()
        db.refresh(incidencia)
        
        # Registrar en historial
        HistorialService.crear_registro(
            db=db,
            incidencia_id=incidencia_id,
            accion="estado_cambiado",
            usuario_id=usuario_id,
            descripcion=cambio_estado.comentario or f"Estado cambiado a {nuevo_estado.nombre}",
            valor_anterior=estado_anterior_nombre,
            valor_nuevo=nuevo_estado.nombre
        )
        
        return incidencia

    @staticmethod
    def eliminar_incidencia(db: Session, incidencia_id: int) -> bool:
        """Elimina una incidencia"""
        incidencia = db.query(Incidencia).filter(Incidencia.id == incidencia_id).first()
        
        if not incidencia:
            return False
        
        db.delete(incidencia)
        db.commit()
        return True


# =============================================================================
# Servicio de Historial
# =============================================================================

class HistorialService:
    """Servicio para el historial de incidencias"""

    @staticmethod
    def crear_registro(
        db: Session,
        incidencia_id: int,
        accion: str,
        usuario_id: str,
        descripcion: Optional[str] = None,
        valor_anterior: Optional[str] = None,
        valor_nuevo: Optional[str] = None
    ) -> HistorialIncidencia:
        """
        Crea un registro en el historial de una incidencia.
        RF7: Historial
        """
        registro = HistorialIncidencia(
            incidencia_id=incidencia_id,
            accion=accion,
            descripcion=descripcion,
            usuario_id=usuario_id,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo
        )
        
        db.add(registro)
        db.commit()
        db.refresh(registro)
        
        return registro

    @staticmethod
    def obtener_historial(
        db: Session,
        incidencia_id: int
    ) -> List[HistorialIncidencia]:
        """Obtiene el historial completo de una incidencia"""
        return db.query(HistorialIncidencia)\
            .options(joinedload(HistorialIncidencia.usuario))\
            .filter(HistorialIncidencia.incidencia_id == incidencia_id)\
            .order_by(HistorialIncidencia.fecha_cambio.desc())\
            .all()


# =============================================================================
# Servicio de Comentarios
# =============================================================================

class ComentarioService:
    """Servicio para comentarios de incidencias"""

    @staticmethod
    def crear_comentario(
        db: Session,
        incidencia_id: int,
        comentario_data: ComentarioCreate,
        usuario_id: str
    ) -> Comentario:
        """Crea un nuevo comentario en una incidencia"""
        comentario = Comentario(
            incidencia_id=incidencia_id,
            usuario_id=usuario_id,
            contenido=comentario_data.contenido,
            es_interno=comentario_data.es_interno
        )
        
        db.add(comentario)
        db.commit()
        db.refresh(comentario)
        
        # Registrar en historial
        HistorialService.crear_registro(
            db=db,
            incidencia_id=incidencia_id,
            accion="comentario_agregado",
            usuario_id=usuario_id,
            descripcion="Nuevo comentario agregado"
        )
        
        return comentario

    @staticmethod
    def listar_comentarios(
        db: Session,
        incidencia_id: int,
        incluir_internos: bool = False
    ) -> List[Comentario]:
        """Lista comentarios de una incidencia"""
        query = db.query(Comentario)\
            .options(joinedload(Comentario.usuario))\
            .filter(Comentario.incidencia_id == incidencia_id)
        
        if not incluir_internos:
            query = query.filter(Comentario.es_interno == False)
        
        return query.order_by(Comentario.fecha_creacion).all()

"""
Script para inicializar la base de datos.
Ejecutar: python init_db.py
"""
from app.config import engine, Base, SessionLocal
from app.models.models import (
    Estado, Prioridad, Categoria, Ubicacion, Usuario,
    Incidencia, HistorialIncidencia, Comentario, Adjunto,
    EstadoCodigo, PrioridadCodigo
)


def init_catalogos(db):
    """Inicializa los catálogos con datos por defecto"""
    
    # Estados
    estados_data = [
        {"codigo": EstadoCodigo.PENDIENTE, "nombre": "Pendiente", "descripcion": "Estado inicial, incidencia creada pero no asignada", "orden": 1},
        {"codigo": EstadoCodigo.ASIGNADA, "nombre": "Asignada", "descripcion": "Incidencia asignada a un responsable", "orden": 2},
        {"codigo": EstadoCodigo.EN_PROCESO, "nombre": "En Proceso", "descripcion": "Responsable está trabajando en la incidencia", "orden": 3},
        {"codigo": EstadoCodigo.RESUELTA, "nombre": "Resuelta", "descripcion": "Incidencia resuelta, pendiente de cierre", "orden": 4},
        {"codigo": EstadoCodigo.CERRADA, "nombre": "Cerrada", "descripcion": "Incidencia cerrada definitivamente", "orden": 5},
        {"codigo": EstadoCodigo.CANCELADA, "nombre": "Cancelada", "descripcion": "Incidencia cancelada", "orden": 6},
    ]
    
    for estado_data in estados_data:
        existe = db.query(Estado).filter(Estado.codigo == estado_data["codigo"]).first()
        if not existe:
            estado = Estado(**estado_data)
            db.add(estado)
    
    # Prioridades
    prioridades_data = [
        {"codigo": PrioridadCodigo.BAJA, "nombre": "Baja", "descripcion": "No urgente, puede esperar", "nivel": 1, "color": "#28A745"},
        {"codigo": PrioridadCodigo.MEDIA, "nombre": "Media", "descripcion": "Prioridad normal", "nivel": 2, "color": "#FFC107"},
        {"codigo": PrioridadCodigo.ALTA, "nombre": "Alta", "descripcion": "Requiere atención pronta", "nivel": 3, "color": "#FD7E14"},
        {"codigo": PrioridadCodigo.URGENTE, "nombre": "Urgente", "descripcion": "Requiere atención inmediata", "nivel": 4, "color": "#DC3545"},
    ]
    
    for prioridad_data in prioridades_data:
        existe = db.query(Prioridad).filter(Prioridad.codigo == prioridad_data["codigo"]).first()
        if not existe:
            prioridad = Prioridad(**prioridad_data)
            db.add(prioridad)
    
    # Categorías
    categorias_data = [
        {"codigo": "infraestructura", "nombre": "Infraestructura", "descripcion": "Problemas de edificios, aulas, mobiliario"},
        {"codigo": "tecnologia", "nombre": "Tecnología", "descripcion": "Problemas de equipos, redes, software"},
        {"codigo": "servicios", "nombre": "Servicios", "descripcion": "Problemas con servicios generales"},
        {"codigo": "seguridad", "nombre": "Seguridad", "descripcion": "Incidencias de seguridad"},
        {"codigo": "limpieza", "nombre": "Limpieza", "descripcion": "Problemas de limpieza y mantenimiento"},
        {"codigo": "otros", "nombre": "Otros", "descripcion": "Otras incidencias no categorizadas"},
    ]
    
    for categoria_data in categorias_data:
        existe = db.query(Categoria).filter(Categoria.codigo == categoria_data["codigo"]).first()
        if not existe:
            categoria = Categoria(**categoria_data)
            db.add(categoria)
    
    # Ubicaciones
    ubicaciones_data = [
        {"codigo": "edificio_a_p1", "nombre": "Edificio A - Piso 1", "edificio": "Edificio A", "piso": "1"},
        {"codigo": "edificio_a_p2", "nombre": "Edificio A - Piso 2", "edificio": "Edificio A", "piso": "2"},
        {"codigo": "edificio_b_p1", "nombre": "Edificio B - Piso 1", "edificio": "Edificio B", "piso": "1"},
        {"codigo": "biblioteca", "nombre": "Biblioteca Central", "edificio": "Biblioteca", "piso": "PB"},
        {"codigo": "cafeteria", "nombre": "Cafetería", "edificio": "Servicios", "piso": "PB"},
        {"codigo": "laboratorio_1", "nombre": "Laboratorio de Cómputo 1", "edificio": "Edificio C", "piso": "1"},
        {"codigo": "laboratorio_2", "nombre": "Laboratorio de Cómputo 2", "edificio": "Edificio C", "piso": "2"},
        {"codigo": "auditorio", "nombre": "Auditorio Principal", "edificio": "Edificio Central", "piso": "PB"},
    ]
    
    for ubicacion_data in ubicaciones_data:
        existe = db.query(Ubicacion).filter(Ubicacion.codigo == ubicacion_data["codigo"]).first()
        if not existe:
            ubicacion = Ubicacion(**ubicacion_data)
            db.add(ubicacion)
    
    db.commit()
    print("✓ Catálogos inicializados")


def init_db():
    """Crea todas las tablas en la base de datos e inicializa catálogos"""
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tablas creadas exitosamente")
    
    print("Inicializando catálogos...")
    db = SessionLocal()
    try:
        init_catalogos(db)
    finally:
        db.close()
    
    print("\n✓ Base de datos inicializada correctamente")
    print("\nTablas creadas:")
    print("  - estados (catálogo)")
    print("  - prioridades (catálogo)")
    print("  - categorias (catálogo)")
    print("  - ubicaciones (catálogo)")
    print("  - usuarios")
    print("  - incidencias")
    print("  - historial_incidencias")
    print("  - comentarios")
    print("  - adjuntos")


if __name__ == "__main__":
    init_db()


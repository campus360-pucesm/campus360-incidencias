from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, incidencias, db
from app.config import engine, Base
from app.models.models import Incidencia, HistorialIncidencia

# Crear tablas al iniciar (solo en desarrollo)
# En producción, usar migraciones con Alembic
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CAMPUS360 - Incidencias",
    version="1.0.0",
    description="Módulo de Gestión de Incidencias - API REST con Swagger",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router)
app.include_router(incidencias.router)
app.include_router(db.router)

@app.get("/")
def root():
    return {
        "message": "CAMPUS360 - Módulo de Gestión de Incidencias",
        "version": "1.0.0",
        "docs": "/docs"
    }

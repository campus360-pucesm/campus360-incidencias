import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/campus360_incidencias"
)

# Crear motor de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=10,
    max_overflow=20
)

# Crear clase base para modelos
Base = declarative_base()

# Crear factory de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuración JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_AUTH_SERVICE_URL = os.getenv("JWT_AUTH_SERVICE_URL", "http://localhost:8000/auth/validate")

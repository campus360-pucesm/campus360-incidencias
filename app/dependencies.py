from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import httpx
from app.config import SessionLocal, JWT_AUTH_SERVICE_URL

# Security scheme para JWT
security = HTTPBearer()

def get_db():
    """
    Dependencia para obtener sesión de base de datos.
    Cierra automáticamente la sesión al finalizar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def validate_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Valida el token JWT con el servicio de autenticación.
    RF1: Validación JWT
    """
    token = credentials.credentials
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                JWT_AUTH_SERVICE_URL,
                json={"token": token},
                timeout=5.0
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return user_data
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido o expirado"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticación no disponible"
        )

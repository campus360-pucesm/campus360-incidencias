from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.dependencies import get_db


router = APIRouter(
    prefix="/db",
    tags=["database-health"]
)

@router.get("/")
def db_health_check(db: Session = Depends(get_db)):
    try:
        # Verificar conexión ejecutando una consulta simple
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

"""
Script para probar la conexión a la base de datos.
Ejecutar: python test_connection.py
"""
from app.config import engine, SessionLocal
from sqlalchemy import text

def test_connection():
    """Prueba la conexión a la base de datos"""
    try:
        print("Probando conexión a la base de datos...")
        
        # Intentar crear una sesión y ejecutar una query simple
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            print("✓ Conexión exitosa a la base de datos")
            return True
        finally:
            db.close()
            
    except Exception as e:
        print(f"✗ Error al conectar a la base de datos: {e}")
        print("\nAsegúrate de que:")
        print("1. PostgreSQL esté ejecutándose")
        print("2. La base de datos 'campus360_incidencias' exista")
        print("3. Las credenciales en .env sean correctas")
        return False

if __name__ == "__main__":
    test_connection()


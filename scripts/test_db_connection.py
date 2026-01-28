import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add the parent directory to sys.path to import app modules if needed, 
# though we are just using sqlalchemy directly here mostly.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_connection():
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL no está definido en el archivo .env")
        print("  Por favor copia .env.example a .env y configura tus credenciales.")
        return False

    print(f"Probando conexión a: {database_url.split('@')[-1]}") # Hide password

    try:
        from sqlalchemy.engine.url import make_url
        url = make_url(database_url)
        print(f"  Usuario: {url.username}")
        print(f"  Host: {url.host}")
        print(f"  Puerto: {url.port}")
        print(f"  Base de datos: {url.database}")
        
        # Supabase requiere SSL
        engine = create_engine(database_url, connect_args={"sslmode": "require"})
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ ¡Conexión exitosa a la base de datos!")
            return True

    except Exception as e:
        print(f"❌ Error al conectar a la base de datos:")
        print(f"  {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()

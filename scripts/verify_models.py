import sys
import os

# Add the project directory to sys.path
sys.path.append(os.getcwd())

try:
    from app.models.models import Usuario, Incidencia
    print("✅ Successfully imported Usuario and Incidencia")
    
    # Check relationships
    if hasattr(Incidencia, 'reportante'):
         print("✅ Incidencia.reportante relationship exists")
    else:
         print("❌ Incidencia.reportante relationship MSSING")

except ImportError as e:
    print(f"❌ ImportError: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

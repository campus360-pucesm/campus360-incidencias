# Frontend - Campus360 Incidencias

Frontend sencillo en HTML, CSS y JavaScript para probar todas las funcionalidades del backend de gestión de incidencias.

## 🚀 Cómo usar

### 1. Iniciar el Backend

Primero, asegúrate de que el backend está corriendo:

```bash
cd campus360-incidencias
uvicorn app.main:app --reload
```

El backend estará disponible en `http://localhost:8000`

### 2. Abrir el Frontend

Puedes abrir el frontend de varias formas:

#### Opción A: Directamente en el navegador
Simplemente abre el archivo `index.html` en tu navegador.

#### Opción B: Con un servidor local (recomendado)
```bash
# Con Python
cd frontend
python -m http.server 3000

# O con Node.js (si tienes live-server instalado)
npx live-server
```

Luego abre `http://localhost:3000` en tu navegador.

### 3. Configurar Token JWT

Para probar las funcionalidades que requieren autenticación:

1. Obtén un token JWT válido de tu sistema de autenticación
2. Pégalo en el campo "Token JWT..." en la cabecera
3. Haz clic en "Configurar Token"
4. Haz clic en "Probar Conexión" para verificar

## 📋 Funcionalidades

### Catálogos
- Ver todos los **Estados** disponibles
- Ver todas las **Prioridades** disponibles
- Ver todas las **Categorías** disponibles
- Ver todas las **Ubicaciones** disponibles

### Tickets
- **Listar tickets** con filtros:
  - Por estado
  - Por prioridad
  - Por categoría
  - Paginación (límite y offset)
- **Crear nuevo ticket** con:
  - Título
  - Descripción
  - Prioridad
  - Categoría (opcional)
  - Ubicación (opcional)

### Detalle de Ticket
- Ver información completa del ticket
- Ver **historial de cambios**
- Ver y agregar **comentarios**

### Acciones (requieren rol de administrador)
- **Cambiar estado** de un ticket
- **Asignar responsable** a un ticket
- **Actualizar** datos de un ticket
- **Eliminar** un ticket

## 🎨 Estructura de Archivos

```
frontend/
├── index.html    # Estructura HTML
├── styles.css    # Estilos CSS
├── app.js        # Lógica JavaScript
└── README.md     # Este archivo
```

## 🔧 Configuración

Si tu backend corre en una URL diferente, modifica la constante en `app.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## 📝 Notas

- El token JWT se guarda en localStorage para persistir entre sesiones
- La mayoría de endpoints requieren autenticación
- Las acciones de administrador (cambiar estado, asignar, eliminar) requieren rol de administrador
- Los usuarios regulares solo pueden ver sus propios tickets

## 🎯 Endpoints Probables

| Funcionalidad | Método | Endpoint |
|--------------|--------|----------|
| Listar estados | GET | `/tickets/catalogos/estados` |
| Listar prioridades | GET | `/tickets/catalogos/prioridades` |
| Listar categorías | GET | `/tickets/catalogos/categorias` |
| Listar ubicaciones | GET | `/tickets/catalogos/ubicaciones` |
| Listar tickets | GET | `/tickets/` |
| Crear ticket | POST | `/tickets/` |
| Obtener ticket | GET | `/tickets/{id}` |
| Actualizar ticket | PUT | `/tickets/{id}` |
| Eliminar ticket | DELETE | `/tickets/{id}` |
| Cambiar estado | POST | `/tickets/{id}/cambiar-estado` |
| Asignar responsable | POST | `/tickets/{id}/asignar` |
| Ver historial | GET | `/tickets/{id}/historial` |
| Listar comentarios | GET | `/tickets/{id}/comentarios` |
| Agregar comentario | POST | `/tickets/{id}/comentarios` |

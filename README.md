# CAMPUS360 — INCIDENCIAS

Microservicio desarrollado para el ecosistema CAMPUS360 en la materia Desarrollo de Sistemas de Información.

## 🚀 Tecnologías
* Python 3.10+
* FastAPI
* Uvicorn
* PostgreSQL
* Swagger UI (automático)

## 📁 Estructura del proyecto

    /app
        /routers
        /schemas
        /models
        /services

## ▶ Cómo ejecutar el proyecto

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📌 Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET    | /health  | Verificar servicio |
| ...    | ...      | Funciones del módulo |

## 👥 Integrantes del Equipo
* Dev Principal: Daniel Zambrano Macias y Marlon Mendoza Mendoza
* Product Owner del módulo: Yhony Cantos
* Scrum Master asignado: Yakov Seni

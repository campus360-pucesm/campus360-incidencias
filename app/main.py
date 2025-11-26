from fastapi import FastAPI
from app.routers import health, incidencias

app = FastAPI(
    title="CAMPUS360 - Incidencias",
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(incidencias.router)

@app.get("/")
def root():
    return {"message": "CAMPUS360 microservice running"}

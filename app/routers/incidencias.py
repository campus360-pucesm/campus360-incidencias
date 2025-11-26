from fastapi import APIRouter

router = APIRouter(
    prefix="/incidencias",
    tags=["incidencias"]
)

@router.post("/")
def crear_ticket():
    return {"message": "Ticket creado"}

@router.get("/")
def listar_tickets():
    return {"tickets": []}

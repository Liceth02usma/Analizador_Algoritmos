from fastapi import APIRouter

router = APIRouter(
    prefix="/algorithm",       # prefijo común
    tags=["Algorithm"]         # agrupa en la doc Swagger
)

@router.post("/upload")
def upload_algorithm(code: str):
    # Aquí luego usarías el parser para convertir el pseudocódigo
    return {"status": "ok", "received_code": code}


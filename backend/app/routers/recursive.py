from fastapi import APIRouter


router = APIRouter(
    prefix="/recursive",      
    tags=["Recursive"]         
)

@router.post("/CreateTree")
def create_tree(data: dict):
    # Lógica para crear un árbol
    return {"message": "Árbol creado", "data": data}


@router.post("/ResolveRecurrence")
def recurrence(data: dict):
    # Lógica para resolver la recurrencia
    return {"message": "Recurrencia resuelta"}
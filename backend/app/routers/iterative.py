from fastapi import APIRouter


router = APIRouter(
    prefix="/iterative",      
    tags=["Iterative"]         
)

@router.post("/CreateFlowDiagram")
def create_flow_diagram(data: dict):
    # Lógica para crear un diagrama de flujo
    return {"message": "Diagrama de flujo creado", "data": data}



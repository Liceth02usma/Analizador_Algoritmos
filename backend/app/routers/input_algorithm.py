from fastapi import APIRouter
from app.controllers.control_input import ControlInput
from app.schemas.pseudocode_request import PseudocodeRequest

router = APIRouter()

@router.post("/parse")
async def parse_code(request: PseudocodeRequest):
    """
    Recibe pseudocódigo (texto plano)
    → Llama a ControlInput.parse_pseudocode()
    → Devuelve el AST como JSON
    """
    result = ControlInput.parse_pseudocode(request.pseudocode)
    return {"ast": result}

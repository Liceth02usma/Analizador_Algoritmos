# app/routers/input_algorithm.py
from fastapi import APIRouter
from app.controllers.control_input import ControlInput
from app.schemas.pseudocode_request import PseudocodeRequest
from app.controllers.algorithm_type_controller import analyze_algorithm_type
from app.parsers.parser import parse_pseudocode

router = APIRouter()

@router.post("/parse")
async def parse_code(request: PseudocodeRequest):
    """Solo genera el AST (sin LLM)."""
    result = ControlInput.parse_pseudocode(request.pseudocode)
    return {"ast": result}

@router.post("/analyze")
async def analyze_algorithm(payload: dict):
    """Genera el AST y además ejecuta el agente AlgorithmTypeAgent."""
    pseudocode = payload.get("pseudocode", "")
    if not pseudocode:
        return {"error": "No se proporcionó pseudocódigo"}

    ast = parse_pseudocode(pseudocode)
    algo_type_result = analyze_algorithm_type(pseudocode, ast)

    return {
        "ast": ast,
        "algorithm_type": algo_type_result,
    }

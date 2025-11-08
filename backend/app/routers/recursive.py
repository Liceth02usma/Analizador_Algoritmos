from fastapi import APIRouter
from ..controllers.controller_recursive import ControlRecursive
from ..models.request import AnalysisRecursive


router = APIRouter(
    prefix="/recursive",      
    tags=["Recursive"]         
)

@router.post("/Analysis")
def generate_Analysis(data: AnalysisRecursive):
    return ControlRecursive().analyze_from_parsed_tree(
        data.algorithm_name,
        data.pseudocode
    )
from fastapi import APIRouter
from ..controllers.controller_recursive import ControlRecursive
from ..models.AnalysisRequestRecursive import AnalysisRequestRecursive


router = APIRouter(
    prefix="/recursive",      
    tags=["Recursive"]         
)

@router.post("/Analysis")
def generate_Analysis(data: AnalysisRequestRecursive):
    return ControlRecursive().analyze_from_parsed_tree(
        data.algorithm_name,
        data.pseudocode
    )
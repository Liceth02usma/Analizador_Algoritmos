from fastapi import APIRouter
from ..controllers.controller_iterative import ControlIterative
from ..models.AnalysisRequest import AnalysisRequest


router = APIRouter(
    prefix="/iterative",      
    tags=["Iterative"]         
)

@router.post("/Analysis")
def generate_Analysis(data: AnalysisRequest):
    return ControlIterative().analyze_from_parsed_tree(
        data.algorithm_name,
        data.pseudocode
    )
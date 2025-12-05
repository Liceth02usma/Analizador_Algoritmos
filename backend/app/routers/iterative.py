from fastapi import APIRouter
from ..controllers.controller_iterative import ControlIterative
from ..schemas.request import AnalysisIterative


router = APIRouter(prefix="/iterative", tags=["Iterative"])


@router.post("/Analysis")
def generate_Analysis(data: AnalysisIterative):
    return ControlIterative().analyze_from_parsed_tree(
        data.algorithm_name, data.pseudocode
    )

from fastapi import APIRouter

from ..controllers.controller_recursive import ControlRecursive

from ..controllers.control_input import ControlInput
from ..schemas.request import AnalysisRecursive


router = APIRouter(prefix="/recursive", tags=["Recursive"])


@router.post("/Analysis")
def generate_Analysis(data: AnalysisRecursive):
    control_input = ControlInput()
    return control_input.get_mock_analysis()
    # return ControlRecursive().analyze_from_parsed_tree("No se", data.pseudocode)
    # return ControlRecursive().analyze_from_parsed_tree(
    #     data.algorithm_name,
    #     data.pseudocode
    # )

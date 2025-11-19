# app/routers/input_algorithm.py

from fastapi import APIRouter
from app.controllers.control_input import ControlInput
from app.schemas.pseudocode_request import PseudocodeRequest
from app.controllers.algorithm_type_controller import analyze_algorithm_type
from app.controllers.algorithm_classifier_controller import classify_algorithm
from app.parsers.parser import parser, TreeToDict
from app.external_services.Agentes.IterativeAnalyzerAgent import IterativeAnalyzerAgent

router = APIRouter()

@router.post("/parse")
async def parse_code(request: PseudocodeRequest):
    """Solo genera el AST (sin LLM)."""
    result = ControlInput.parse_pseudocode(request.pseudocode)
    return {"ast": result}


@router.post("/analyze")
async def analyze_algorithm(payload: dict):
    pseudocode = payload.get("pseudocode")

    # 1️⃣ Parsear pseudocódigo → obtenemos el AST (Tree)
    tree = parser.parse(pseudocode)
    transformer = TreeToDict()
    ast_dict = transformer.transform(tree)

    # 2️⃣ Tipo de algoritmo (recursivo / iterativo / DP) → usa el Tree
    algo_type_result = analyze_algorithm_type(pseudocode, tree)

    # 3️⃣ Extraemos solo el tipo textual
    algo_type_value = (
        algo_type_result.get("detected_type")
        if isinstance(algo_type_result, dict)
        else algo_type_result.detected_type
    )

    # 4️⃣ Clasificación funcional / estructural → usa el dict
    algo_class_result = classify_algorithm(pseudocode, tree, algo_type_value)

    print("=== ✅ Resultado final del segundo agente ===")
    print(algo_class_result)

    """
    if "iterativo" in algo_type_value:
        print("⚙️ Invocando IterativeAnalyzerAgent...")
        
        iterative_agent = IterativeAnalyzerAgent(model_type="Modelo_Razonamiento")
        efficiency_result = iterative_agent.analyze_iterative_algorithm(
            pseudocode=pseudocode,
            ast=ast_dict,
            algorithm_name=algo_class_result.get("algorithm_name", "Algoritmo iterativo"),
            functional_class=algo_class_result.get("functional_class", None),
            structural_pattern=algo_class_result.get("structural_pattern", "iteración simple"),
            additional_info="Análisis automático desde backend"
        )
        print("=== 🤖 Resultado del análisis de eficiencia iterativa ===")
        print(efficiency_result)
        
    elif "recursivo" in algo_type_value or "dinámica" in algo_type_value:
        print("⚙️ (Pendiente) Invocar agente para recursivos o programación dinámica")
        # Aquí luego invocaremos RecursiveOrDPAnalyzerAgent
        efficiency_result = {"message": "Agente de análisis recursivo/DP aún no implementado."}
    else:
        print("⚠️ Tipo de algoritmo no reconocido para análisis de eficiencia.")
    """
    # 5️⃣ Retornar todo al frontend
    return {
        "ast": ast_dict,
        "algorithm_type": algo_type_result,
        "algorithm_classification": algo_class_result
        #"efficiency_analysis": efficiency_result
    }
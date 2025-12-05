from fastapi import APIRouter, Body, HTTPException
from app.controllers.control_input import ControlInput
from app.schemas.pseudocode_request import PseudocodeRequest

# Controladores de Análisis
from app.controllers.algorithm_classifier_controller import classify_algorithm
from app.controllers.iterative_controller import analyze_iterative
from ..controllers.controller_recursive import ControlRecursive

# Agente Completo para comparación
from app.external_services.Agentes.CompleteAnalysisAgent import CompleteAnalysisAgent

# Imports para el método save_analysis_to_json
import json
from pathlib import Path
from datetime import datetime
from app.controllers.algorithm_type_controller import AlgorithmClassifier
import time

router = APIRouter()

@router.post("/translate")
async def translate_input(payload: dict = Body(...)):
    """
    Traduce lenguaje natural a pseudocódigo usando el agente.
    Retorna el pseudocódigo generado para que sobrescriba el input.
    """
    from app.external_services.Agentes.NaturalLanguageToPseudocodeAgent import NaturalLanguageToPseudocodeAgent
    
    user_input = payload.get("text", "")
    
    if not user_input.strip():
        return {"error": "El input no puede estar vacío"}
    
    try:
        translator = NaturalLanguageToPseudocodeAgent(model_type="Gemini_Rapido")
        result = translator.translate(user_input)
        
        if not result.was_successful:
            return {
                "error": result.error_message or "No se pudo traducir el input",
                "success": False
            }
        
        return {
            "success": True,
            "pseudocode": result.pseudocode,
            "original_input": user_input
        }
    except Exception as e:
        return {
            "error": f"Error al traducir: {str(e)}",
            "success": False
        }


@router.post("/parse")
async def parse_code(request: PseudocodeRequest):
    """Solo genera el AST (sin LLM). Útil para validar sintaxis en tiempo real."""
    # Asumimos false para parseo directo, o podrías agregar el campo al request si quisieras
    result = ControlInput.process_input(request.pseudocode, is_natural_language=False)
    return result


@router.post("/analyze")
async def analyze_algorithm(payload: dict = Body(...)):
    """
    Endpoint principal de análisis.
    Payload: { "pseudocode": "..." }
    
    IMPORTANTE: El pseudocódigo ya debe estar en formato válido (traducido o ingresado manualmente).
    NO intenta traducir nuevamente (eso se hace en /translate).
    """
    raw_input = payload.get("pseudocode", "")

    # 1️⃣ FASE DE PRE-PROCESAMIENTO (Solo Parsing, SIN traducción)
    # is_natural_language=False para evitar traducción duplicada
    processed_input = ControlInput.process_input(raw_input, is_natural_language=False)
    
    if "error" in processed_input:
        return processed_input # Retornamos el error al frontend

    # Obtenemos los datos limpios y validados
    valid_pseudocode = processed_input["pseudocode"]
    valid_ast = processed_input["ast"]

    print("✅ AST generado correctamente. Iniciando análisis de complejidad...")

    classifier = AlgorithmClassifier()
    result = classifier.classify(valid_ast)

    # 2️⃣ FASE DE IDENTIFICACIÓN (Tipo de Algoritmo)
    #algo_type_result = determine_algorithm_type(valid_ast, valid_pseudocode)

    # Extraemos el tipo (ej: "iterativo", "recursivo")
    algo_type_value = result.get("algorithm_type", "desconocido")

    print(f"=== Tipo de Algoritmo detectado: {algo_type_value} ===")

    # 3️⃣ FASE DE CLASIFICACIÓN (Nombre del Algoritmo)
    algo_class_result = classify_algorithm(valid_pseudocode, valid_ast, algo_type_value)

    # Obtenemos el nombre más probable o genérico
    algorithm_name = algo_class_result.get(
        "possible_known_algorithms", ["Algoritmo Desconocido"]
    )[0]

    print(f"=== Algoritmo identificado: {algorithm_name} ({algo_type_value}) ===")

    final_analysis = None
    print(valid_pseudocode, "Pseudocódigo válido")
    # 4️⃣ ENRUTAMIENTO POR TIPO (Iterativo vs Recursivo)
    if "iterativo" in algo_type_value.lower():
        print("⚙️ Invocando Pipeline Iterativo...")
        # final_analysis = analyze_iterative(
        #     pseudocode=valid_pseudocode,
        #     ast=valid_ast,
        #     algorithm_name=algorithm_name,
        # )
        final_analysis = analyze_iterative(
            pseudocode=valid_pseudocode,  # Usamos el código limpio/traducido
            ast=valid_ast,
            algorithm_name=algorithm_name,
        )

    elif (
        "recursivo" in algo_type_value.lower() or "dinámica" in algo_type_value.lower()
    ):
        print("⚙️ (Pendiente) Invocando Pipeline Recursivo...")
        final_analysis = ControlRecursive().analyze_from_parsed_tree(
            algorithm_name=algorithm_name,
            pseudocode=valid_pseudocode,
            parsed_tree=valid_ast,
        )

    else:
        print("⚠️ Tipo de algoritmo no reconocido.")
        final_analysis = {
            "error": f"No se pudo determinar si es iterativo o recursivo. Tipo detectado: {algo_type_value}"
        }

    # 5️⃣ RETORNO AL FRONTEND
    analisis_data = {
        "input_metadata": {
            "source_type": processed_input["source_type"],
            "final_pseudocode": valid_pseudocode
        },
        "classification": {"type": algo_type_value, "name": algorithm_name},
        "analysis": final_analysis,
    }
    
    # Guardar solución especializada para comparación posterior
    save_specialized_solution(algorithm_name, valid_pseudocode, final_analysis)
    
    analisis = save_analysis_to_json(analisis_data, "data_iterative45.json")
    print(analisis, "ANALISIS GUARDADO")
    return analisis_data



def save_analysis_to_json(
    analysis_data: dict,
    filename: str = None,
    output_dir: str = "output"
) -> dict:
    """
    Guarda el resultado del análisis en un archivo JSON.
    
    Args:
        analysis_data: Diccionario con los resultados del análisis
        filename: Nombre del archivo (opcional). Si no se proporciona, se genera automáticamente
        output_dir: Directorio donde guardar el archivo (default: "output")
    
    Returns:
        dict con información sobre el archivo guardado
    """
    try:
        # Crear directorio si no existe
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo si no se proporciona
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            algo_name = analysis_data.get("classification", {}).get("name", "algorithm")
            algo_name = algo_name.replace(" ", "_").lower()
            filename = f"{algo_name}_{timestamp}.json"
        
        # Asegurar extensión .json
        if not filename.endswith(".json"):
            filename += ".json"
        
        # Ruta completa del archivo
        file_path = output_path / filename
        
        # Guardar con formato legible (indent=2)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "file_path": str(file_path),
            "filename": filename,
            "size_bytes": file_path.stat().st_size
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# SISTEMA DE COMPARACIÓN: ESPECIALIZADOS VS COMPLETO
# ============================================================================

# Storage temporal para soluciones especializadas (en producción usar Redis/DB)
_specialized_solutions = {}


def save_specialized_solution(algorithm_name: str, pseudocode: str, solution: dict):
    """Guarda la solución de agentes especializados para comparación posterior."""
    key = f"{algorithm_name}_{hash(pseudocode)}"
    _specialized_solutions[key] = {
        "algorithm_name": algorithm_name,
        "pseudocode": pseudocode,
        "solution": solution,
        "timestamp": datetime.now().isoformat()
    }
    print(f"✅ Solución especializada guardada: {key}")


def get_specialized_solution(algorithm_name: str, pseudocode: str) -> dict:
    """Recupera la solución especializada guardada."""
    key = f"{algorithm_name}_{hash(pseudocode)}"
    return _specialized_solutions.get(key)


@router.post("/compare")
async def compare_analysis(payload: dict = Body(...)):
    """
    Compara el análisis de agentes especializados vs agente completo.
    
    Payload: {
        "algorithm_name": "BubbleSort",
        "pseudocode": "..."
    }
    
    Returns:
        Datos estructurados para gráficas de comparación
    """
    algorithm_name = payload.get("algorithm_name")
    pseudocode = payload.get("pseudocode")
    
    if not algorithm_name or not pseudocode:
        raise HTTPException(400, "algorithm_name y pseudocode son requeridos")
    
    # 1. Obtener solución especializada guardada
    specialized = get_specialized_solution(algorithm_name, pseudocode)
    
    if not specialized:
        raise HTTPException(
            404, 
            "No se encontró análisis especializado previo. Ejecute /analyze primero."
        )
    
    print(f"\n{'='*80}")
    print(f"🔬 INICIANDO COMPARACIÓN: {algorithm_name}")
    print(f"{'='*80}\n")
    
    # 2. Ejecutar agente completo (sin contexto)
    print("🤖 Ejecutando CompleteAnalysisAgent (sin especialización)...")
    start_time = time.time()
    
    try:
        complete_agent = CompleteAnalysisAgent()
        complete_response = complete_agent.analyze(pseudocode=pseudocode)
        
        complete_execution_time = time.time() - start_time
        
        # Convertir respuesta Pydantic a dict
        if hasattr(complete_response, 'model_dump'):
            complete_result = complete_response.model_dump(mode='json')
        elif hasattr(complete_response, 'dict'):
            complete_result = complete_response.dict()
        else:
            complete_result = complete_response
        
        # 📊 Extraer tokens del agente completo usando los atributos de AgentBase
        complete_tokens = {
            "input": complete_agent._last_input_tokens,
            "output": complete_agent._last_output_tokens,
            "total": complete_agent._last_total_tokens
        }
        
        print(f"\n📊 CompleteAnalysisAgent - Tokens: {complete_tokens['total']:,}")
        print(f"⏱️ CompleteAnalysisAgent - Tiempo: {complete_execution_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Error en CompleteAnalysisAgent: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Error ejecutando agente completo: {str(e)}")
    
    # 3. Extraer datos de solución especializada
    specialized_solution = specialized["solution"]
    
    # Convertir a dict si es objeto Pydantic
    if hasattr(specialized_solution, 'model_dump'):
        specialized_solution = specialized_solution.model_dump(mode='json')
    elif hasattr(specialized_solution, 'dict'):
        specialized_solution = specialized_solution.dict()
    
    # Calcular tokens especializados (suma de todos los agentes)
    specialized_tokens = extract_specialized_tokens(specialized_solution)
    
    # 4. Preparar datos de comparación
    comparison_data = {
        "metadata": {
            "algorithm_name": algorithm_name,
            "compared_at": datetime.now().isoformat(),
            "specialized_timestamp": specialized["timestamp"]
        },
        
        # Comparación de tokens
        "tokens_comparison": {
            "specialized": specialized_tokens,
            "complete": complete_tokens,
            "difference": {
                "input": specialized_tokens["input"] - complete_tokens["input"],
                "output": specialized_tokens["output"] - complete_tokens["output"],
                "total": specialized_tokens["total"] - complete_tokens["total"]
            },
            "percentage_difference": {
                "total": ((specialized_tokens["total"] - complete_tokens["total"]) / complete_tokens["total"] * 100) if complete_tokens["total"] > 0 else 0
            }
        },
        
        # Comparación de complejidad
        "complexity_comparison": {
            "specialized": extract_complexity(specialized_solution),
            "complete": complete_result.get("final_complexity", "N/A"),
            "match": compare_complexity(
                extract_complexity(specialized_solution),
                complete_result.get("final_complexity", "")
            )
        },
        
        # Comparación de métodos
        "methods_comparison": {
            "specialized": extract_methods(specialized_solution),
            "complete": complete_result.get("solution_method", "Análisis completo sin especialización")
        },
        
        # Comparación de detalle
        "detail_comparison": {
            "specialized_steps": count_solution_steps(specialized_solution),
            "complete_steps": len(complete_result.get("solution_steps", [])),
            "specialized_cases": count_cases(specialized_solution),
            "complete_cases": 1  # Agente completo no diferencia casos
        },
        
        # Tiempo de ejecución
        "execution_time": {
            "specialized": specialized_solution.get("extra", {}).get("project_metadata", {}).get("execution_time", 0),
            "complete": complete_execution_time
        },
        
        # Datos completos para inspección
        "full_results": {
            "specialized": specialized_solution,
            "complete": complete_result
        }
    }
    
    # 5. Guardar comparación
    save_comparison_result(algorithm_name, comparison_data)
    
    print(f"\n{'='*80}")
    print(f"✅ COMPARACIÓN COMPLETADA")
    print(f"📊 Tokens - Especializado: {specialized_tokens['total']} | Completo: {complete_tokens['total']}")
    print(f"⏱️  Tiempo - Especializado: {specialized_solution.get('_execution_time', 0):.2f}s | Completo: {complete_execution_time:.2f}s")
    print(f"{'='*80}\n")
    
    return comparison_data


# ============================================================================
# FUNCIONES AUXILIARES DE COMPARACIÓN
# ============================================================================

def extract_specialized_tokens(solution: dict) -> dict:
    """Extrae y suma tokens de todos los agentes especializados."""
    total_input = 0
    total_output = 0
    
    # Buscar tokens en extra.project_metadata (ubicación correcta)
    extra = solution.get("extra", {})
    if "project_metadata" in extra:
        metadata = extra["project_metadata"]
        if "total_tokens" in metadata:
            total_tokens_data = metadata["total_tokens"]
            total_input = total_tokens_data.get("input", 0)
            total_output = total_tokens_data.get("output", 0)
    
    return {
        "input": total_input,
        "output": total_output,
        "total": total_input + total_output
    }


def extract_complexity(solution: dict) -> str:
    """Extrae la complejidad principal de la solución especializada."""
    if "cases" in solution and solution["cases"]:
        # Tomar el peor caso o el primer caso disponible
        worst_case = next((c for c in solution["cases"] if "worst" in c.get("case_name", "").lower()), solution["cases"][0])
        return worst_case.get("big_o", "N/A")
    return "N/A"


def extract_methods(solution: dict) -> list:
    """Extrae los métodos usados por agentes especializados."""
    methods = []
    
    if "cases" in solution:
        for case in solution["cases"]:
            if "method" in case:
                methods.append(case["method"])
    
    return list(set(methods)) or ["Análisis especializado multi-agente"]


def compare_complexity(complexity1: str, complexity2: str) -> bool:
    """Compara si dos complejidades son equivalentes."""
    # Normalizar (quitar espacios, paréntesis, etc.)
    c1 = complexity1.replace(" ", "").replace("(", "").replace(")", "").lower()
    c2 = complexity2.replace(" ", "").replace("(", "").replace(")", "").lower()
    return c1 == c2


def count_solution_steps(solution: dict) -> int:
    """Cuenta pasos de solución en análisis especializado."""
    total_steps = 0
    if "cases" in solution:
        for case in solution["cases"]:
            if "steps" in case:
                total_steps += len(case["steps"])
    return total_steps


def count_cases(solution: dict) -> int:
    """Cuenta casos analizados."""
    return len(solution.get("cases", []))


def save_comparison_result(algorithm_name: str, comparison_data: dict):
    """Guarda resultado de comparación en archivo JSON."""
    output_dir = Path("output/comparisons")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{algorithm_name.replace(' ', '_').lower()}_comparison_{timestamp}.json"
    
    file_path = output_dir / filename
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(comparison_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Comparación guardada: {file_path}")
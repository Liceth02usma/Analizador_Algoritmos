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
    from app.external_services.Agentes.NaturalLanguageToPseudocodeAgent import (
        NaturalLanguageToPseudocodeAgent,
    )

    user_input = payload.get("text", "")

    if not user_input.strip():
        return {"error": "El input no puede estar vacío"}

    try:
        translator = NaturalLanguageToPseudocodeAgent(model_type="Gemini_Rapido")
        result = translator.translate(user_input)

        if not result.was_successful:
            return {
                "error": result.error_message or "No se pudo traducir el input",
                "success": False,
            }

        return {
            "success": True,
            "pseudocode": result.pseudocode,
            "original_input": user_input,
        }
    except Exception as e:
        return {"error": f"Error al traducir: {str(e)}", "success": False}


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
        return processed_input  # Retornamos el error al frontend

    # Obtenemos los datos limpios y validados
    valid_pseudocode = processed_input["pseudocode"]
    valid_ast = processed_input["ast"]

    print("✅ AST generado correctamente. Iniciando análisis de complejidad...")

    classifier = AlgorithmClassifier()
    result = classifier.classify(valid_ast)

    # 2️⃣ FASE DE IDENTIFICACIÓN (Tipo de Algoritmo)
    # algo_type_result = determine_algorithm_type(valid_ast, valid_pseudocode)

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
        final_analysis = analyze_iterative(
            pseudocode=valid_pseudocode,
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
            "final_pseudocode": valid_pseudocode,
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
    analysis_data: dict, filename: str = None, output_dir: str = "output"
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
            "size_bytes": file_path.stat().st_size,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# SISTEMA DE COMPARACIÓN: ESPECIALIZADOS VS COMPLETO
# ============================================================================

# Storage temporal para soluciones especializadas (en producción usar Redis/DB)
_specialized_solutions = {}
# Storage temporal para resultados de comparación (cache)
_comparison_results = {}


def save_specialized_solution(algorithm_name: str, pseudocode: str, solution: dict):
    """Guarda la solución de agentes especializados para comparación posterior."""
    key = f"{algorithm_name}_{hash(pseudocode)}"
    _specialized_solutions[key] = {
        "algorithm_name": algorithm_name,
        "pseudocode": pseudocode,
        "solution": solution,
        "timestamp": datetime.now().isoformat(),
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
            "No se encontró análisis especializado previo. Ejecute /analyze primero.",
        )

    print(f"\n{'='*80}")
    print(f"🔬 INICIANDO COMPARACIÓN: {algorithm_name}")
    print(f"{'='*80}\n")

    # Generar key de cache única
    cache_key = f"{algorithm_name}_{hash(pseudocode)}_comparison"

    # Verificar si ya existe un resultado de comparación
    if cache_key in _comparison_results:
        print("✅ Resultado de comparación encontrado en cache")
        cached_result = _comparison_results[cache_key]
        print(
            f"📊 Tokens - Especializado: {cached_result['tokens_comparison']['specialized']['total']} | Completo: {cached_result['tokens_comparison']['complete']['total']}"
        )
        print(
            f"⏱️  Tiempo - Especializado: {cached_result['execution_time']['specialized']:.2f}s | Completo: {cached_result['execution_time']['complete']:.2f}s"
        )
        return cached_result

    # 2. Ejecutar agente completo (sin contexto)
    print("🤖 Ejecutando CompleteAnalysisAgent (sin especialización)...")
    start_time = time.time()

    try:
        complete_agent = CompleteAnalysisAgent()
        complete_response = complete_agent.analyze(pseudocode=pseudocode)

        complete_execution_time = time.time() - start_time

        # Convertir respuesta Pydantic a dict
        if hasattr(complete_response, "model_dump"):
            complete_result = complete_response.model_dump(mode="json")
        elif hasattr(complete_response, "dict"):
            complete_result = complete_response.dict()
        else:
            complete_result = complete_response

        # 📊 Extraer tokens del agente completo usando los atributos de AgentBase
        complete_tokens = {
            "input": complete_agent._last_input_tokens,
            "output": complete_agent._last_output_tokens,
            "total": complete_agent._last_total_tokens,
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
    if hasattr(specialized_solution, "model_dump"):
        specialized_solution = specialized_solution.model_dump(mode="json")
    elif hasattr(specialized_solution, "dict"):
        specialized_solution = specialized_solution.dict()

    # Calcular tokens especializados (suma de todos los agentes)
    specialized_tokens = extract_specialized_tokens(specialized_solution)

    # Extraer tiempo de ejecución especializado con fallback
    print(f"\n🔍 DEBUG execution_time - Buscando en extra.project_metadata...")
    specialized_time = (
        specialized_solution.get("extra", {})
        .get("project_metadata", {})
        .get("execution_time", 0)
    )
    print(f"   Encontrado en project_metadata: {specialized_time}")
    
    if specialized_time == 0:
        # Fallback: buscar en el nivel raíz
        print(f"⚠️ Tiempo en 0, intentando fallback a nivel raíz...")
        specialized_time = specialized_solution.get("execution_time", 0)
        print(f"   Encontrado en nivel raíz: {specialized_time}")

    print(f"\n📊 Agentes Especializados - Tokens: {specialized_tokens['total']:,}")
    print(f"⏱️ Agentes Especializados - Tiempo: {specialized_time:.2f}s")

    # 4. Preparar datos de comparación
    comparison_data = {
        "metadata": {
            "algorithm_name": algorithm_name,
            "compared_at": datetime.now().isoformat(),
            "specialized_timestamp": specialized["timestamp"],
        },
        # Comparación de tokens
        "tokens_comparison": {
            "specialized": specialized_tokens,
            "complete": complete_tokens,
            "difference": {
                "input": specialized_tokens["input"] - complete_tokens["input"],
                "output": specialized_tokens["output"] - complete_tokens["output"],
                "total": specialized_tokens["total"] - complete_tokens["total"],
            },
            "percentage_difference": {
                "total": (
                    (
                        (specialized_tokens["total"] - complete_tokens["total"])
                        / complete_tokens["total"]
                        * 100
                    )
                    if complete_tokens["total"] > 0
                    else 0
                )
            },
        },
        # Comparación de complejidad
        "complexity_comparison": {
            "specialized": extract_complexity(specialized_solution),
            "complete": complete_result.get("final_complexity", "N/A"),
            "match": compare_complexity(
                extract_complexity(specialized_solution),
                complete_result.get("final_complexity", ""),
            ),
        },
        # Comparación de métodos
        "methods_comparison": {
            "specialized": extract_methods(specialized_solution),
            "complete": complete_result.get(
                "solution_method", "Análisis completo sin especialización"
            ),
        },
        # Comparación de detalle
        "detail_comparison": {
            "specialized_steps": count_solution_steps(specialized_solution),
            "complete_steps": len(complete_result.get("solution_steps", [])),
            "specialized_cases": count_cases(specialized_solution),
            "complete_cases": 1,  # Agente completo no diferencia casos
        },
        # Tiempo de ejecución
        "execution_time": {
            "specialized": specialized_time,
            "complete": complete_execution_time,
            "difference": specialized_time - complete_execution_time,
            "percentage_difference": (
                (
                    (specialized_time - complete_execution_time)
                    / complete_execution_time
                    * 100
                )
                if complete_execution_time > 0
                else 0
            ),
        },
        # Análisis completo del agente para mostrar en frontend
        "complete_agent_analysis": {
            "algorithm_name": complete_result.get("algorithm_name", algorithm_name)
            or algorithm_name,
            "algorithm_purpose": complete_result.get(
                "algorithm_purpose", "No especificado"
            )
            or "No especificado",
            "algorithm_category": complete_result.get("algorithm_category", "General")
            or "General",
            "algorithm_type": complete_result.get("algorithm_type", "iterative")
            or "iterative",
            # Ecuaciones y complejidad
            "equation": complete_result.get("equation", "No disponible")
            or "No disponible",
            "final_complexity": complete_result.get("final_complexity", "N/A") or "N/A",
            # Notación asintótica
            "asymptotic_best": complete_result.get("asymptotic_best", "N/A") or "N/A",
            "asymptotic_worst": complete_result.get("asymptotic_worst", "N/A") or "N/A",
            "asymptotic_average": complete_result.get("asymptotic_average", "N/A")
            or "N/A",
            # Método y pasos de solución
            "solution_method": complete_result.get(
                "solution_method", "Análisis completo sin especialización"
            )
            or "Análisis completo sin especialización",
            "solution_steps": complete_result.get("solution_steps", []) or [],
            "steps_count": len(complete_result.get("solution_steps", [])),
            # Análisis línea por línea
            "line_by_line_analysis": complete_result.get("line_by_line_analysis", [])
            or [],
            # Métricas de ejecución
            "execution_time": complete_execution_time,
            "tokens_used": complete_tokens["total"],
        },
        # Datos completos para inspección
        "full_results": {
            "specialized": specialized_solution,
            "complete": complete_result,
        },
    }

    # 5. Guardar comparación en archivo y cache
    save_comparison_result(algorithm_name, comparison_data)
    _comparison_results[cache_key] = comparison_data

    print(f"\n{'='*80}")
    print(f"✅ COMPARACIÓN COMPLETADA")
    print(
        f"📊 Tokens - Especializado: {specialized_tokens['total']:,} | Completo: {complete_tokens['total']:,}"
    )
    print(
        f"⏱️  Tiempo - Especializado: {specialized_time:.2f}s | Completo: {complete_execution_time:.2f}s"
    )
    print(f"💾 Resultado guardado en cache: {cache_key}")
    
    # 🔍 VALIDACIÓN FINAL - RESUMEN DE DATOS ENVIADOS AL FRONTEND
    print("\n" + "="*80)
    print("✅ VALIDACIÓN FINAL - DATOS QUE RECIBIRÁ EL FRONTEND")
    print("="*80)
    print(f"\n📊 TOKENS ESPECIALIZADOS:")
    print(f"   Input:  {specialized_tokens.get('input', 0):,} tokens")
    print(f"   Output: {specialized_tokens.get('output', 0):,} tokens")
    print(f"   TOTAL:  {specialized_tokens.get('total', 0):,} tokens")
    print(f"\n⏱️  TIEMPO ESPECIALIZADO: {specialized_time:.3f} segundos")
    print(f"\n🤖 AGENTE COMPLETO:")
    print(f"   Tokens Input:  {complete_tokens.get('input', 0):,} tokens")
    print(f"   Tokens Output: {complete_tokens.get('output', 0):,} tokens")
    print(f"   TOKENS TOTAL:  {complete_tokens.get('total', 0):,} tokens")
    print(f"   TIEMPO:        {complete_execution_time:.3f} segundos")
    print(f"   COMPLEJIDAD:   {comparison_data['complete_agent_analysis']['final_complexity']}")
    print(f"\n📈 DIFERENCIAS:")
    print(f"   Tokens:  {comparison_data['tokens_comparison']['difference']['total']:+,} tokens")
    print(f"   Tiempo:  {comparison_data['execution_time']['difference']:+.3f} segundos")
    print("="*80 + "\n")

    return comparison_data


# ============================================================================
# FUNCIONES AUXILIARES DE COMPARACIÓN
# ============================================================================


def extract_specialized_tokens(solution: dict) -> dict:
    """Extrae y suma tokens de todos los agentes especializados."""
    print(f"\n🔍 DEBUG extract_specialized_tokens - Inicio")
    print(f"📦 Keys en solution: {list(solution.keys())}")
    
    total_input = 0
    total_output = 0

    # Buscar tokens en extra.project_metadata.total_tokens
    extra = solution.get("extra", {})
    print(f"📦 Keys en extra: {list(extra.keys())}")
    
    if "project_metadata" in extra:
        metadata = extra["project_metadata"]
        print(f"📦 Keys en project_metadata: {list(metadata.keys())}")
        
        if "total_tokens" in metadata:
            total_tokens_data = metadata["total_tokens"]
            print(f"✅ Encontrado total_tokens: {total_tokens_data}")
            total_input = total_tokens_data.get("input", 0)
            total_output = total_tokens_data.get("output", 0)
        else:
            print(f"⚠️ NO se encontró 'total_tokens' en project_metadata")

    # Si no encontramos en total_tokens, intentar buscar directamente en metadata
    if total_input == 0 and total_output == 0:
        print(f"⚠️ Tokens en 0, intentando fallback a token_usage...")
        if "project_metadata" in extra:
            metadata = extra["project_metadata"]
            # Buscar token_usage como estructura alternativa
            if "token_usage" in metadata:
                token_usage = metadata["token_usage"]
                print(f"✅ Encontrado token_usage: {token_usage}")
                for agent_name, agent_tokens in token_usage.items():
                    if isinstance(agent_tokens, dict):
                        agent_input = agent_tokens.get("input", 0)
                        agent_output = agent_tokens.get("output", 0)
                        print(f"   - {agent_name}: input={agent_input}, output={agent_output}")
                        total_input += agent_input
                        total_output += agent_output
            else:
                print(f"❌ NO se encontró 'token_usage' en project_metadata")

    result = {
        "input": total_input,
        "output": total_output,
        "total": total_input + total_output,
    }
    print(f"🎯 RESULTADO FINAL extract_specialized_tokens: {result}\n")
    return result


def extract_complexity(solution: dict) -> str:
    """Extrae la complejidad principal de la solución especializada."""
    # Opción 1: Buscar en extra.cases (iterativos)
    extra = solution.get("extra", {})
    if "cases" in extra and extra["cases"]:
        worst_case = next(
            (c for c in extra["cases"] if "worst" in c.get("case_name", "").lower()),
            extra["cases"][0],
        )
        big_o = worst_case.get("big_o", "")
        if big_o:
            return big_o

    # Opción 2: Buscar en asymptotic_notation (nivel raíz)
    asymptotic = solution.get("asymptotic_notation", {})
    if asymptotic:
        return asymptotic.get(
            "worst", asymptotic.get("average", asymptotic.get("best", "N/A"))
        )

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

from fastapi import APIRouter, Body
from app.controllers.control_input import ControlInput
from app.schemas.pseudocode_request import PseudocodeRequest

# Controladores de Análisis
from app.controllers.algorithm_classifier_controller import classify_algorithm
from app.controllers.iterative_controller import analyze_iterative
from ..controllers.controller_recursive import ControlRecursive

# Imports para el método save_analysis_to_json
import json
from pathlib import Path
from datetime import datetime
from app.controllers.algorithm_type_controller import AlgorithmClassifier

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
        # final_analysis = analyze_iterative(
        #     pseudocode=valid_pseudocode,  # Usamos el código limpio/traducido
        #     ast=valid_ast,
        #     algorithm_name=algorithm_name,
        # )

    elif (
        "recursivo" in algo_type_value.lower() or "dinámica" in algo_type_value.lower()
    ):
        print("⚙️ (Pendiente) Invocando Pipeline Recursivo...")
        final_analysis = {
            "error": "Análisis recursivo aún no implementado."
        }
        # final_analysis = ControlRecursive().analyze_from_parsed_tree(
        #     algorithm_name=algorithm_name,
        #     pseudocode=valid_pseudocode,
        #     parsed_tree=valid_ast,
        # )

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
    analisis = save_analysis_to_json(analisis_data, "data_iterative2.json")
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
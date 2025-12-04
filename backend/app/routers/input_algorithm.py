from fastapi import APIRouter, Body
from app.controllers.control_input import ControlInput
from app.schemas.pseudocode_request import PseudocodeRequest

# Controladores de Análisis
from app.controllers.algorithm_type_controller import determine_algorithm_type
from app.controllers.algorithm_classifier_controller import classify_algorithm
from app.controllers.iterative_controller import analyze_iterative
from ..controllers.controller_recursive import ControlRecursive

# Imports para el método save_analysis_to_json
import json
from pathlib import Path
from datetime import datetime

router = APIRouter()


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
    Payload: { "pseudocode": "...", "is_natural_language": true/false }
    """
    raw_input = payload.get("pseudocode", "")
    is_natural = payload.get("is_natural_language", True)

    # 1️⃣ FASE DE PRE-PROCESAMIENTO (Traducción + Parsing)
    # ControlInput se encarga de llamar al LLM si es necesario y luego a Lark
    processed_input = ControlInput.process_input(
        raw_input, is_natural_language=is_natural
    )

    if "error" in processed_input:
        return processed_input  # Retornamos el error al frontend (400 o 422 implícito)

    # Obtenemos los datos limpios y validados
    valid_pseudocode = processed_input["pseudocode"]
    valid_ast = processed_input["ast"]

    print("✅ AST generado correctamente. Iniciando análisis de complejidad...")

    # 2️⃣ FASE DE IDENTIFICACIÓN (Tipo de Algoritmo)
    # Usamos el AST validado, no parseamos de nuevo
    # Nota: analyze_algorithm_type puede necesitar el 'tree' objeto de Lark o el dict.
    # Si tus funciones viejas requieren el objeto Tree crudo, tendrías que ajustar ControlInput,
    # pero como usamos TreeToDict, asumimos que trabajan con diccionarios.

    algo_type_result = determine_algorithm_type(valid_ast, valid_pseudocode)

    # Extraemos el tipo (ej: "iterativo", "recursivo")
    algo_type_value = algo_type_result.get("detected_type", "desconocido")

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
            "final_pseudocode": valid_pseudocode,  # Devolvemos el código generado para que el usuario lo vea
        },
        "classification": {"type": algo_type_value, "name": algorithm_name},
        "analysis": final_analysis,
    }
    analisis = save_analysis_to_json(analisis_data, "data_recursive.json")
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
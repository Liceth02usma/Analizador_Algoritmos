# app/controllers/algorithm_type_controller.py
"""
from app.external_services.Agentes.AlgorithmTypeAgent import AlgorithmTypeAgent

def analyze_algorithm_type(pseudocode: str, ast: dict):
   
    Analiza el tipo del algoritmo usando el agente LLM AlgorithmTypeAgent.
    Recibe el pseudocódigo y el AST del parser.
    Retorna un diccionario con la respuesta del agente.
   
    try:
        agent = AlgorithmTypeAgent(model_type="Gemini_Rapido")

        print("\n=== 🤖 Invocando AlgorithmTypeAgent ===")
        response = agent.analyze_type(pseudocode=pseudocode)
        print(f"✅ Tipo detectado: {response.detected_type}")
        print(f"💡 Indicadores: {response.key_indicators}")
        print(f"📈 Confianza: {response.confidence_level}")
        print(f"🧩 Justificación: {response.justification}")

        return response.model_dump()

    except Exception as e:
        print("⚠️ Error al analizar el tipo de algoritmo:", e)
        return {"error": str(e)}

"""
def determine_algorithm_type(ast: dict, pseudocode: str) -> dict:
    """
    Clasificación DETERMINISTA basada en el AST.
    """
    has_loops = False
    has_recursion = False
    
    # Buscamos el nombre de la función principal
    func_name = None
    
    # Recorrido recursivo del AST (Depth First Search)
    def traverse(node):
        nonlocal has_loops, has_recursion, func_name
        
        if isinstance(node, dict):
            # 1. Detectar nombre función
            if node.get("type") == "procedure_def":
                func_name = node.get("name")
            
            # 2. Detectar Ciclos
            if node.get("type") in ["for", "while", "repeat"]:
                has_loops = True
            
            # 3. Detectar Recursión (Llamada a sí mismo)
            if node.get("type") == "call" or node.get("type") == "CALL":
                if func_name and node.get("name") == func_name:
                    has_recursion = True
            
            # Seguir bajando
            for v in node.values():
                traverse(v)
        elif isinstance(node, list):
            for item in node:
                traverse(item)

    traverse(ast)

    # Lógica de decisión
    if has_recursion:
        # Nota: Un algoritmo puede tener bucles y ser recursivo, 
        # pero para análisis de complejidad, la recursión domina la técnica (Master Theorem).
        return {"detected_type": "recursivo"}
    elif has_loops:
        return {"detected_type": "iterativo"}
    else:
        # Secuencial puro (O(1) o O(n) lineal simple) se trata como iterativo
        return {"detected_type": "iterativo"}

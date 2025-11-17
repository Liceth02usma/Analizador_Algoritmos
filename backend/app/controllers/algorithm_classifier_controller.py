from app.external_services.Agentes.AlgorithmClassifierAgent import AlgorithmClassifierAgent
from app.parsers.parser import TreeToDict

agent = AlgorithmClassifierAgent(model_type="Modelo_Razonamiento")

def classify_algorithm(pseudocode: str, ast, algo_type: str):
    """
    Controlador que ejecuta la clasificación funcional y estructural del algoritmo.
    Asegura que el AST sea un diccionario, incluso si llega como Tree (de Lark).
    """
    # ✅ Detectar si es Tree por tipo de nombre (más robusto)
    if type(ast).__name__ == "Tree":
        try:
            transformer = TreeToDict()
            ast = transformer.transform(ast)
            print("🌳 AST convertido correctamente a dict.")
        except Exception as e:
            print("⚠️ Error al convertir el AST a dict:", e)
            ast = {"error": "No se pudo transformar el AST"}

    # ✅ Asegurar tipo de algoritmo como string
    if isinstance(algo_type, dict):
        algo_type = algo_type.get("detected_type", "desconocido")

    # Debug
    print("\n=== 🤖 Invocando AlgorithmClassifierAgent ===")
    print("🧩 Tipo de algoritmo:", algo_type)
    print("📘 Tipo de AST:", type(ast))

    # ✅ Ejecutar agente
    result = agent.classify_algorithm(pseudocode, ast, algo_type)
    return result.model_dump()



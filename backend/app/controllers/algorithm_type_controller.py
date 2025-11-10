# app/controllers/algorithm_type_controller.py
from app.external_services.Agentes.AlgorithmTypeAgent import AlgorithmTypeAgent

def analyze_algorithm_type(pseudocode: str, ast: dict):
    """
    Analiza el tipo del algoritmo usando el agente LLM AlgorithmTypeAgent.
    Recibe el pseudocódigo y el AST del parser.
    Retorna un diccionario con la respuesta del agente.
    """
    try:
        agent = AlgorithmTypeAgent(model_type="Modelo_Razonamiento")

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


import os
from dotenv import load_dotenv

load_dotenv()

from app.external_services.Agentes.Agent import AgentBase
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from langchain_core.tools import tool


# ========================================================================
# 📘 SCHEMAS DE DATOS
# ========================================================================


class AlgorithmInput(BaseModel):
    """Contexto de entrada para el agente"""

    algorithm_name: Optional[str] = Field(
        default=None, description="Nombre del algoritmo (si se conoce)"
    )
    pseudocode: str = Field(description="Pseudocódigo completo del algoritmo")
    parsed_tree: Optional[Dict[str, Any]] = Field(
        default=None, description="Árbol sintáctico (AST) generado por el parser"
    )
    additional_info: Optional[str] = Field(
        default=None, description="Información contextual o notas adicionales"
    )


class AlgorithmTypeResponse(BaseModel):
    """Salida estructurada del agente"""

    algorithm_name: Optional[str] = Field(
        default=None, description="Nombre del algoritmo analizado"
    )
    detected_type: str = Field(
        description="Tipo de algoritmo detectado: 'recursivo', 'iterativo' o 'programación dinámica'"
    )
    justification: str = Field(
        description="Explicación técnica y detallada de la clasificación"
    )
    key_indicators: List[str] = Field(
        description="Características clave detectadas que sustentan la clasificación"
    )
    confidence_level: float = Field(
        description="Nivel de confianza (0.0 a 1.0) basado en la evidencia"
    )


# ========================================================================
# 🧰 HERRAMIENTAS AUXILIARES
# ========================================================================


@tool
def detect_keywords(pseudocode: str) -> Dict[str, int]:
    """Detecta palabras clave indicativas de estructuras iterativas o recursivas."""
    pseudocode_lower = pseudocode.lower()
    keywords = {
        "for": pseudocode_lower.count("for"),
        "while": pseudocode_lower.count("while"),
        "repeat": pseudocode_lower.count("repeat"),
        "call": pseudocode_lower.count("call"),
        "recursion": pseudocode_lower.count("recursion"),
        "memo": pseudocode_lower.count("memo"),
        "table": pseudocode_lower.count("table"),
        "dp": pseudocode_lower.count("dp"),
        "cache": pseudocode_lower.count("cache"),
    }
    return {"detected_keywords": keywords}


@tool
def count_recursive_calls(pseudocode: str) -> int:
    """Cuenta cuántas veces el algoritmo se llama a sí mismo."""
    import re

    lines = pseudocode.splitlines()
    recursive_calls = 0
    for line in lines:
        if re.search(r"call\s+\w+", line.lower()) or re.search(
            r"\breturn\s+\w+\(.*\)", line.lower()
        ):
            recursive_calls += 1
    return {"recursive_call_count": recursive_calls}


# ========================================================================
# 🤖 AGENTE PRINCIPAL
# ========================================================================


class AlgorithmTypeAgent(AgentBase[AlgorithmTypeResponse]):
    """LLM que clasifica el algoritmo (iterativo, recursivo o programación dinámica)."""

    def _configure(self) -> None:
        """Configuración del agente"""
        self.tools = [detect_keywords, count_recursive_calls]
        self.context_schema = AlgorithmInput
        self.response_format = AlgorithmTypeResponse

        self.SYSTEM_PROMPT = """
Eres un experto en análisis de algoritmos y estructuras computacionales.

Tu tarea es analizar un pseudocódigo junto con su estructura sintáctica (AST)
y clasificar el algoritmo como uno de los siguientes tipos:
1️⃣ Iterativo: usa bucles (`for`, `while`, `repeat`) sin llamadas recursivas.
2️⃣ Recursivo: el algoritmo se invoca a sí mismo directa o indirectamente.
3️⃣ Programación dinámica: resuelve subproblemas, guarda resultados (memoización/tablas),
   y evita cálculos repetidos.

🔹 Usa la información del pseudocódigo para contexto humano
🔹 Usa el AST (estructura jerárquica) para confirmar patrones estructurales.

⚙️ Reglas:
- Si hay llamadas a sí mismo → Recursivo.
- Si hay `for` o `while` y no hay recursión → Iterativo.
- Si hay tablas, arreglos de memoización o subproblemas → Programación dinámica.
- Si hay mezcla de recursión + memoización → Clasifícalo como Programación dinámica.

🧠 Tu salida debe ser estructurada:
- detected_type: uno de ["recursivo", "iterativo", "programación dinámica"]
- justification: explicación técnica
- key_indicators: lista de características observadas
- confidence_level: número entre 0.0 y 1.0
"""

    def analyze_type(
        self,
        pseudocode: str,
        parsed_tree: Optional[Dict[str, Any]] = None,
        algorithm_name: Optional[str] = None,
        additional_info: Optional[str] = None,
        thread_id: str = "algo_type_session",
    ) -> AlgorithmTypeResponse:
        """Analiza el pseudocódigo y el AST para determinar el tipo de algoritmo."""

        context = AlgorithmInput(
            algorithm_name=algorithm_name,
            pseudocode=pseudocode,
            parsed_tree=parsed_tree,
            additional_info=additional_info,
        )

        content = f"""
Analiza el siguiente pseudocódigo y su estructura en AST.

Pseudocódigo:
{pseudocode}

AST:
{parsed_tree}

Determina si el algoritmo es iterativo, recursivo o de programación dinámica.
Incluye una justificación técnica y los indicadores clave encontrados.
"""

        result = self.invoke_simple(
            content=content, thread_id=thread_id, context=context.model_dump()
        )

        response = self.extract_response(result)
        if response is None:
            raise ValueError(
                "❌ No se obtuvo una respuesta estructurada válida del agente."
            )

        return response


# ========================================================================
# 🧪 PRUEBA LOCAL
# ========================================================================

if __name__ == "__main__":
    agent = AlgorithmTypeAgent(model_type="Modelo_Razonamiento")

    code = """
    factorial(n)
    begin
        if (n = 0) then
            return 1
        else
            return n * factorial(n - 1)
    end
    """

    fake_ast = {
        "type": "procedure_def",
        "name": "factorial",
        "params": ["n"],
        "body": [
            {
                "type": "if",
                "cond": {"lhs": "n", "op": "=", "rhs": 0},
                "then": [{"type": "return", "value": 1}],
                "else": [
                    {
                        "type": "return",
                        "value": {
                            "op": "*",
                            "lhs": "n",
                            "rhs": {
                                "type": "call",
                                "name": "factorial",
                                "args": [{"op": "-", "lhs": "n", "rhs": 1}],
                            },
                        },
                    }
                ],
            }
        ],
    }

    res = agent.analyze_type(
        pseudocode=code, parsed_tree=fake_ast, algorithm_name="Factorial"
    )
    print("🔹 Tipo detectado:", res.detected_type)
    print("🧩 Confianza:", res.confidence_level)
    print("📘 Indicadores:", res.key_indicators)
    print("💬 Justificación:", res.justification)

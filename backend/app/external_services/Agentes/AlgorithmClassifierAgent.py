import os
from dotenv import load_dotenv

import sys

sys.path.append(os.getenv("PYTHONPATH", "backend"))


load_dotenv()

from app.external_services.Agentes.Agent import AgentBase
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from langchain_core.tools import tool

# ========================================================================
# 📘 SCHEMAS DE DATOS
# ========================================================================


class AlgorithmClassifierInput(BaseModel):
    """Entrada del agente de clasificación funcional y estructural."""

    pseudocode: str = Field(description="Pseudocódigo completo del algoritmo")
    ast: Any = Field(
        description="Árbol sintáctico abstracto (AST) generado por el parser (puede ser un objeto Tree o un dict)"
    )
    algorithm_type: str = Field(
        description="Tipo general detectado: recursivo, iterativo o programación dinámica"
    )
    algorithm_name: Optional[str] = Field(
        default=None, description="Nombre conocido del algoritmo (opcional)"
    )
    additional_info: Optional[str] = Field(
        default=None, description="Contexto adicional del análisis"
    )


class AlgorithmClassifierResponse(BaseModel):
    """Salida estructurada del agente de clasificación funcional."""

    functional_class: str = Field(
        description="Clasificación funcional: ordenamiento, búsqueda, etc."
    )
    structural_pattern: str = Field(
        description="Patrón estructural: divide y vencerás, DP, greedy, etc."
    )
    confidence_level: float = Field(description="Nivel de confianza (0.0 a 1.0)")
    justification: str = Field(
        description="Explicación técnica del razonamiento de clasificación"
    )
    key_features: List[str] = Field(
        description="Rasgos detectados en el pseudocódigo/AST que llevaron a la decisión"
    )
    possible_known_algorithms: List[str] = Field(
        description="Nombres posibles de algoritmos reconocidos (si aplica)"
    )


# ========================================================================
# 🧰 HERRAMIENTAS AUXILIARES
# ========================================================================


@tool
def extract_keywords_from_ast(ast: Dict[str, Any]) -> Dict[str, int]:
    """
    Extrae indicadores del AST que pueden ayudar a clasificar el tipo de algoritmo.
    """
    if not isinstance(ast, dict):
        try:
            from app.parsers.parser import TreeToDict

            transformer = TreeToDict()
            ast = transformer.transform(ast)
        except Exception:
            ast = {}
    import json

    ast_str = json.dumps(ast).lower()
    keywords = {
        "sort": ast_str.count("sort"),
        "search": ast_str.count("search"),
        "divide": ast_str.count("divide"),
        "merge": ast_str.count("merge"),
        "pivot": ast_str.count("pivot"),
        "heap": ast_str.count("heap"),
        "table": ast_str.count("table"),
        "memo": ast_str.count("memo"),
        "min": ast_str.count("min"),
        "max": ast_str.count("max"),
        "path": ast_str.count("path"),
        "matrix": ast_str.count("matrix"),
    }
    return {"ast_keywords": keywords}


@tool
def summarize_ast_structure(ast: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resume la estructura del AST para dar contexto al agente (número de bucles, condicionales, recursiones, etc.)
    """
    if not isinstance(ast, dict):
        try:
            from app.parsers.parser import TreeToDict

            transformer = TreeToDict()
            ast = transformer.transform(ast)
        except Exception:
            ast = {}
    from collections import Counter

    def traverse(node, counter):
        if isinstance(node, dict):
            t = node.get("type")
            if t:
                counter[t] += 1
            for v in node.values():
                traverse(v, counter)
        elif isinstance(node, list):
            for item in node:
                traverse(item, counter)

    counter = Counter()
    traverse(ast, counter)
    return {"structure_summary": dict(counter)}


# ========================================================================
# 🤖 AGENTE PRINCIPAL
# ========================================================================


class AlgorithmClassifierAgent(AgentBase[AlgorithmClassifierResponse]):
    """Agente LLM que clasifica el tipo de algoritmo (funcional y estructural)."""

    def _configure(self) -> None:
        self.tools = [extract_keywords_from_ast, summarize_ast_structure]
        self.context_schema = AlgorithmClassifierInput
        self.response_format = AlgorithmClassifierResponse

        self.SYSTEM_PROMPT = """Eres un experto en análisis de algoritmos.
Tu tarea es clasificar un algoritmo dado (en pseudocódigo y AST) en dos dimensiones:

1️⃣ **Clasificación funcional**
   - Ejemplos: ordenamiento, búsqueda, optimización, grafos, numérico, etc.

2️⃣ **Patrón estructural**
   - Ejemplos: divide y vencerás, programación dinámica, recursión pura, iteración simple, greedy, backtracking, etc.

Usa la siguiente información:
- El pseudocódigo (texto natural)
- El AST (estructura del algoritmo)
- El tipo general (iterativo, recursivo, programación dinámica)

Reglas:
- Si el algoritmo es recursivo y divide datos → "divide y vencerás"
- Si guarda subproblemas en tabla/memo → "programación dinámica"
- Si busca un elemento → "búsqueda"
- Si compara e intercambia elementos → "ordenamiento"
- Si busca mínimo/máximo global → "optimización"
- Si toma decisiones parciales → "greedy" o "backtracking"
- Si tiene un patrón claro (ej. quicksort, mergesort) identifícalo como posible nombre conocido.
- tu salida debe ser:

{
  "functional_class": "string",
  "structural_pattern": "string",
  "confidence_level": 0.0,
  "justification": "string",
  "key_features": ["string", "..."],
  "possible_known_algorithms": ["string", "..."]
}
- Devuelve únicamente ese JSON (nada más).

Incluye:
- Clasificación funcional y estructural
- Justificación técnica
- Rasgos o evidencias encontradas (palabras, estructuras)
- Posibles algoritmos conocidos (si los hay)
- Nivel de confianza (0.0 a 1.0)
"""

    def classify_algorithm(
        self,
        pseudocode: str,
        ast: Dict[str, Any],
        algorithm_type: str,
        algorithm_name: Optional[str] = None,
        additional_info: Optional[str] = None,
        thread_id: str = "algo_classifier_thread",
    ) -> AlgorithmClassifierResponse:
        """Ejecuta la clasificación estructural y funcional del algoritmo."""
        context = AlgorithmClassifierInput(
            pseudocode=pseudocode,
            ast=ast,
            algorithm_type=algorithm_type,
            algorithm_name=algorithm_name,
            additional_info=additional_info,
        )

        content = f"""
Analiza el siguiente pseudocódigo y su árbol AST. 
Clasifícalo funcional y estructuralmente según su comportamiento.

📘 Tipo detectado previamente: {algorithm_type}
📄 Pseudocódigo:
{pseudocode}

🌳 AST resumido:
{ast}
"""

        result = self.invoke_simple(
            content=content,
            thread_id=thread_id,
            context=context.model_dump(),
        )

        response = self.extract_response(result)
        if response is None:
            raise ValueError(
                "No se pudo obtener una respuesta estructurada del agente de clasificación."
            )

        return response


# ========================================================================
# 🚀 PRUEBA LOCAL
# ========================================================================

if __name__ == "__main__":
    agent = AlgorithmClassifierAgent(model_type="Modelo_Razonamiento")

    pseudocode = """
    quicksort(A, low, high)
    begin
        if low < high then
            p 🡨 partition(A, low, high)
            quicksort(A, low, p - 1)
            quicksort(A, p + 1, high)
        end
    end
    """

    ast_example = {
        "type": "procedure_def",
        "name": "quicksort",
        "params": ["A", "low", "high"],
        "body": [
            {
                "type": "if",
                "cond": {"lhs": "low", "op": "<", "rhs": "high"},
                "then": [
                    {"type": "assign", "var": "p", "value": "partition(A, low, high)"},
                    {"type": "call", "name": "quicksort", "args": ["A", "low", "p-1"]},
                    {"type": "call", "name": "quicksort", "args": ["A", "p+1", "high"]},
                ],
            }
        ],
    }

    result = agent.classify_algorithm(
        pseudocode=pseudocode,
        ast=ast_example,
        algorithm_type="recursivo",
        algorithm_name="QuickSort",
    )

    print(f"🧩 Clasificación funcional: {result.functional_class}")
    print(f"⚙️ Patrón estructural: {result.structural_pattern}")
    print(f"💡 Confianza: {result.confidence_level}")
    print(f"🔍 Rasgos detectados: {result.key_features}")
    print(f"📘 Posibles algoritmos: {result.possible_known_algorithms}")
    print(f"\n📖 Justificación:\n{result.justification}")

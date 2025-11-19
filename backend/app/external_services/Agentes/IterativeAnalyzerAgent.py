import os
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.append(os.getenv("PYTHONPATH", "backend"))

from app.external_services.Agentes.Agent import AgentBase
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from langchain_core.tools import tool

# ============================================================================
# 📘 SCHEMAS DE DATOS
# ============================================================================

class IterativeAnalysisInput(BaseModel):
    """Entrada para el agente IterativeAnalyzer."""
    pseudocode: str = Field(description="Pseudocódigo del algoritmo iterativo.")
    ast: Dict[str, Any] = Field(description="Árbol sintáctico abstracto del pseudocódigo.")
    algorithm_name: Optional[str] = Field(default=None, description="Nombre o etiqueta del algoritmo.")
    functional_class: Optional[str] = Field(default=None, description="Tipo funcional detectado (búsqueda, ordenamiento, etc.)")
    structural_pattern: Optional[str] = Field(default=None, description="Tipo estructural (iteración simple, anidada, etc.)")
    additional_info: Optional[str] = Field(default=None, description="Información adicional o contexto del análisis.")


class IterativeAnalysisResponse(BaseModel):
    """Salida del agente IterativeAnalyzer."""
    algorithm_name: str = Field(description="Nombre del algoritmo analizado.")
    case_analysis: List[str] = Field(description="Casos analizados: mejor, promedio y peor.")
    line_costs: Dict[str, List[Dict[str, str]]] = Field(description="Costo por línea de pseudocódigo para cada caso.")
    efficiency_functions: Dict[str, str] = Field(description="Función de eficiencia T(n) para cada caso.")
    summations: Dict[str, str] = Field(description="Sumatorias para cada caso antes de simplificar.")
    complexity_summary: Dict[str, str] = Field(description="Orden de complejidad Big-O para cada caso.")
    explanation: str = Field(description="Explicación técnica de cómo se determinaron los costos y funciones.")


# ============================================================================
# 🧰 HERRAMIENTAS AUXILIARES
# ============================================================================

@tool
def extract_loop_info(ast: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analiza el AST para identificar bucles, variables de control e iteraciones esperadas.
    """
    loop_count = 0
    nested_loops = 0
    loop_variables = []

    def traverse(node, depth=0):
        nonlocal loop_count, nested_loops
        if isinstance(node, dict):
            if node.get("type") in ("for", "while"):
                loop_count += 1
                if depth > 0:
                    nested_loops += 1
                loop_variables.append(node.get("var", "i"))
            for v in node.values():
                traverse(v, depth + 1)
        elif isinstance(node, list):
            for item in node:
                traverse(item, depth)

    traverse(ast)
    return {
        "loop_count": loop_count,
        "nested_loops": nested_loops,
        "loop_variables": loop_variables,
    }


@tool
def estimate_line_costs(pseudocode: str) -> List[Dict[str, str]]:
    """
    Asigna un costo simbólico (c1, c2, ...) a cada línea del pseudocódigo.
    """
    lines = [l.strip() for l in pseudocode.split("\n") if l.strip()]
    costs = []
    for i, line in enumerate(lines, start=1):
        costs.append({
            "line": str(i),
            "description": line,
            "cost": f"c{i}"
        })
    return costs


# ============================================================================
# 🤖 AGENTE PRINCIPAL
# ============================================================================

class IterativeAnalyzerAgent(AgentBase[IterativeAnalysisResponse]):
    """Agente especializado en analizar algoritmos iterativos."""

    def _configure(self) -> None:
        self.tools = [extract_loop_info, estimate_line_costs]
        self.context_schema = IterativeAnalysisInput
        self.response_format = IterativeAnalysisResponse

        self.SYSTEM_PROMPT = """
Eres un experto en análisis de algoritmos especializado en ALGORITMOS ITERATIVOS.

Tu tarea es analizar el pseudocódigo y determinar lo siguiente:
1️⃣ El mejor caso, peor caso y caso promedio.
2️⃣ El costo de cada línea (usa notación simbólica: c1, c2, c3, ...).
3️⃣ Las funciones de eficiencia T(n) para cada caso.
4️⃣ Las sumatorias Σ(...) correspondientes a cada caso.
5️⃣ Explica brevemente cómo se obtuvieron las ecuaciones.

⚙️ Reglas de análisis:
- El **mejor caso** ocurre cuando el número de iteraciones o comparaciones es mínimo (por ejemplo, cuando se encuentra el resultado en la primera iteración).
- El **peor caso** ocurre cuando el número de iteraciones es máximo (normalmente n o n²).
- El **caso promedio** es un término intermedio basado en una distribución uniforme.
- Si hay bucles anidados, la cantidad de iteraciones se multiplica (por ejemplo, dos bucles anidados → n × n).
- Usa las variables del pseudocódigo (n, i, j, etc.) para expresar las iteraciones.
- No calcules la notación Big-O. Solo entrega las sumatorias y expresiones exactas.

🧮 Instrucciones específicas:
- Muestra la lista de líneas y su costo individual en el formato:
  [
    {"line": "1", "description": "i ← 0", "cost": "c1"},
    {"line": "2", "description": "while i < n", "cost": "c2"},
    ...
  ]

- Para cada caso (mejor, promedio, peor), proporciona:
  - `efficiency_functions`: las ecuaciones T(n) en términos de las sumatorias.
  - `summations`: las sumatorias explícitas, por ejemplo:
    Σ_{i=1}^{n} (c3 + c4)
    Σ_{i=1}^{n} Σ_{j=1}^{i} (c2 + c3)
  - `explanation`: una breve justificación del razonamiento.

🧾 Formato de salida (JSON estructurado):
{
  "line_costs": {
      "best_case": [...],
      "average_case": [...],
      "worst_case": [...]
  },
  "efficiency_functions": {
      "best_case": "T_best(n) = c1 + Σ_{i=1}^{1} (c2 + c3)",
      "average_case": "T_avg(n) = c1 + Σ_{i=1}^{n/2} (c2 + c3)",
      "worst_case": "T_worst(n) = c1 + Σ_{i=1}^{n} (c2 + c3)"
  },
  "summations": {
      "best_case": "Σ_{i=1}^{1} (c2 + c3)",
      "average_case": "Σ_{i=1}^{n/2} (c2 + c3)",
      "worst_case": "Σ_{i=1}^{n} (c2 + c3)"
  },
  "explanation": "Descripción breve del razonamiento y de cómo se obtuvieron las ecuaciones."
}

⚠️ Importante:
No simplifiques las sumatorias ni calcules su resultado final.
No determines la complejidad Big-O.
El objetivo es dejar las expresiones listas para que otro módulo (EquationSolverAgent) las resuelva.
"""


    def analyze_iterative_algorithm(
        self,
        pseudocode: str,
        ast: Dict[str, Any],
        algorithm_name: Optional[str] = None,
        functional_class: Optional[str] = None,
        structural_pattern: Optional[str] = None,
        additional_info: Optional[str] = None,
        thread_id: str = "iterative_analysis_thread"
    ) -> IterativeAnalysisResponse:
        """Ejecuta el análisis completo de un algoritmo iterativo."""

        context = IterativeAnalysisInput(
            pseudocode=pseudocode,
            ast=ast,
            algorithm_name=algorithm_name,
            functional_class=functional_class,
            structural_pattern=structural_pattern,
            additional_info=additional_info,
        )

        content = f"""
Analiza el siguiente algoritmo ITERATIVO y determina su mejor, peor y caso promedio.

📘 Nombre: {algorithm_name or "No especificado"}
📂 Clase funcional: {functional_class or "Desconocida"}
🔁 Patrón estructural: {structural_pattern or "Iterativo"}

Pseudocódigo:
{pseudocode}

AST (resumen):
{ast}
"""

        result = self.invoke_simple(
            content=content,
            thread_id=thread_id,
            context=context.model_dump()
        )

        response = self.extract_response(result)
        if response is None:
            raise ValueError("No se pudo obtener una respuesta estructurada del IterativeAnalyzerAgent.")

        return response


# ============================================================================
# 🚀 PRUEBA LOCAL
# ============================================================================

if __name__ == "__main__":
    agent = IterativeAnalyzerAgent(model_type="Modelo_Razonamiento")

    pseudocode = """
    i ← 0
    while i < n do
        if A[i] == x then
            return i
        end if
        i ← i + 1
    end while
    """

    ast_example = {
        "type": "while",
        "cond": {"lhs": "i", "op": "<", "rhs": "n"},
        "body": [
            {"type": "if", "cond": {"lhs": "A[i]", "op": "==", "rhs": "x"}, "then": [{"type": "return", "value": "i"}]},
            {"type": "assign", "var": "i", "value": "i+1"}
        ]
    }

    result = agent.analyze_iterative_algorithm(
        pseudocode=pseudocode,
        ast=ast_example,
        algorithm_name="búsqueda_lineal",
        functional_class="búsqueda",
        structural_pattern="iteración simple"
    )

    print(f"\n📘 Algoritmo: {result.algorithm_name}")
    print(f"📊 Casos: {result.case_analysis}")
    print(f"\n⚙️ Costos por línea:")
    for case, lines in result.line_costs.items():
        print(f"  ➤ {case.upper()}:")
        for l in lines:
            print(f"     L{l['line']}: {l['description']} → {l['cost']}")

    print("\n🧮 Funciones de eficiencia:")
    for case, eq in result.efficiency_functions.items():
        print(f"  {case.capitalize()}: {eq}")

    print("\n∑ Sumatorias:")
    for case, summ in result.summations.items():
        print(f"  {case.capitalize()}: {summ}")

    print("\n📈 Complejidades:")
    for case, bigo in result.complexity_summary.items():
        print(f"  {case.capitalize()}: {bigo}")

    print("\n🧠 Explicación:")
    print(result.explanation)

# ================================================================
#  IterativeAnalyzerAgent.py
#  Analizador de algoritmos iterativos (formato académico del libro)
# ================================================================
"""
import json
from typing import Any, Dict, List, Optional

from app.external_services.Agentes.Agent import AgentBase

# ✅ IMPORTACIÓN CORRECTA
#from app.models import costing

from app.models.iterative.execution_counter import ExecutionCounter
from app.models.iterative.cost_table_builder import CostTableBuilder
from app.models.iterative.efficiency_builder import EfficiencyBuilder
from app.models.iterative.outcome_formatter import OutputFormatter

from pydantic import BaseModel, Field


# ================================================================
#  MODELOS DE ENTRADA / SALIDA
# ================================================================

class IterativeAnalysisInput(BaseModel):
    pseudocode: str
    ast: Any
    algorithm_name: Optional[str] = None
    functional_class: Optional[str] = None
    structural_pattern: Optional[str] = None
    additional_info: Optional[str] = None


class IterativeAnalysisResponse(BaseModel):
    algorithm_name: str
    case_analysis: List[str]
    line_costs: Dict[str, List[Dict[str, str]]]
    efficiency_functions: Dict[str, str]
    summations: Dict[str, str]
    complexity_summary: Dict[str, str]
    explanation: str


# ================================================================
#  AGENTE PRINCIPAL
# ================================================================

class IterativeAnalyzerAgent(AgentBase[IterativeAnalysisResponse]):

    def _configure(self):
        self.context_schema = IterativeAnalysisInput
        self.response_format = IterativeAnalysisResponse

        self.SYSTEM_PROMPT = 
Eres un experto en análisis de algoritmos iterativos. 
Tu trabajo es estructurar la salida en el formato académico del libro:
- Coste por línea
- Número de operaciones elementales por línea
- Sumatorias
- Funciones T(n)
- No calcular Big-O



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

        context = IterativeAnalysisInput(
            pseudocode=pseudocode,
            ast=ast,
            algorithm_name=algorithm_name,
            functional_class=functional_class,
            structural_pattern=structural_pattern,
            additional_info=additional_info
        )

        # ===========================================================
        # (2) COSTOS POR LÍNEA
        # ===========================================================





        # ❌ ELIMINADA la línea incorrecta:
        # line_cost_table = costing.build_cost_table(pseudocode)

        # ===========================================================
        # (3) CONTADOR DE ITERACIONES
        # ===========================================================
        # 1) Contador de iteraciones
        counter = ExecutionCounter(ast)
        iteration_model = counter.build_iteration_model()

        # 2) Tabla de costos correcta (recibe iteration_model)
        cost_builder = CostTableBuilder(ast, iteration_model)
        base_cost_table = cost_builder.build_table()

        # 3) T(n)
        efficiency_builder = EfficiencyBuilder(
            pseudocode=pseudocode,
            line_cost_table=base_cost_table,
            iteration_model=iteration_model,
        )
        efficiency = efficiency_builder.build_efficiency()


        # ===========================================================
        # (5) SALIDA FORMATEADA
        # ===========================================================
        formatter = OutputFormatter()
        formatted_line_costs = formatter.format_line_cost_table(
            line_cost_table=base_cost_table,      # <-- CORREGIDO
            iteration_model=iteration_model
        )

        formatted_T = {
            "best_case": efficiency["best_case"]["T"],
            "average_case": efficiency["average_case"]["T"],
            "worst_case": efficiency["worst_case"]["T"],
        }

        formatted_summations = {
            "best_case": efficiency["best_case"]["summation"],
            "average_case": efficiency["average_case"]["summation"],
            "worst_case": efficiency["worst_case"]["summation"],
        }

        return IterativeAnalysisResponse(
            algorithm_name=algorithm_name or "Algoritmo iterativo",
            case_analysis=["mejor caso", "caso promedio", "peor caso"],
            line_costs=formatted_line_costs,
            efficiency_functions=formatted_T,
            summations=formatted_summations,
            complexity_summary={
                "best_case": "No calculado (módulo Big-O separado)",
                "average_case": "No calculado (módulo Big-O separado)",
                "worst_case": "No calculado (módulo Big-O separado)"
            },
            explanation=(
                "Las funciones T(n) se obtienen multiplicando el costo elemental "
                "por el número de ejecuciones de cada línea. "
                "El agente no resuelve sumatorias ni calcula Big-O."
            )
        )



"""
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
    ast: Any = Field(description="Árbol sintáctico abstracto del pseudocódigo.")
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
def extract_loop_info(ast: Any) -> Dict[str, Any]:
    """
    Analiza el AST (Lark Tree o diccionario) e identifica loops, variables de control
    y niveles de anidamiento para algoritmos iterativos.
    """
    from lark import Tree, Token

    loop_count = 0
    nested_loops = 0
    loop_variables = []

    def traverse(node, depth=0):
        nonlocal loop_count, nested_loops

        if isinstance(node, Tree):
            node_type = node.data

            if node_type in ("for", "while"):
                loop_count += 1
                if depth > 0:
                    nested_loops += 1

            for child in node.children:
                if isinstance(child, Token):
                    loop_variables.append(child.value)

            for child in node.children:
                traverse(child, depth + 1)

        elif isinstance(node, list):
            for item in node:
                traverse(item, depth)

        elif isinstance(node, dict):
            if node.get("type") in ("for", "while"):
                loop_count += 1
                if depth > 0:
                    nested_loops += 1
                loop_variables.append(node.get("var", "i"))

            for v in node.values():
                traverse(v, depth + 1)

    traverse(ast)

    return {
        "loop_count": loop_count,
        "nested_loops": nested_loops,
        "loop_variables": loop_variables,
    }


def serialize_ast(ast):
    try:
        return ast.pretty()
    except:
        return str(ast)


@tool
def estimate_line_costs(pseudocode: str) -> List[Dict[str, str]]:
    """
    Asigna un costo simbólico c_i a cada línea del pseudocódigo,
    generando una estructura para analizar costos por instrucción.
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
- El mejor caso ocurre cuando el número de iteraciones es mínimo.
- El peor caso ocurre cuando el número de iteraciones es máximo.
- El caso promedio es un término intermedio supuesto uniforme.
- Si hay bucles anidados, las iteraciones se multiplican.
- Usa las variables del pseudocódigo (n, i, j...) para las expresiones.
- No calcules la notación Big-O.

🧾 Formato solicitado:
{
 "line_costs": { ... },
 "efficiency_functions": { ... },
 "summations": { ... },
 "explanation": "..."
}
        """

    def analyze_iterative_algorithm(
        self,
        pseudocode: str,
        ast: Dict[str, Any],
        algorithm_name: Optional[str] = None,
        functional_class: Optional[str] = None,
        structural_pattern: Optional[str] = None,
        additional_info: Optional[str] = None,
        thread_id: str = "iterative_analysis_thread",
    ) -> IterativeAnalysisResponse:

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
            {
                "type": "if",
                "cond": {"lhs": "A[i]", "op": "==", "rhs": "x"},
                "then": [{"type": "return", "value": "i"}]
            },
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

    print("\n⚙️ Costos por línea:")
    for case, lines in result.line_costs.items():
        print(f" ➤ {case.upper()}:")
        for l in lines:
            print(f"  L{l['line']}: {l['description']} → {l['cost']}")

    print("\n🧮 Funciones de eficiencia:")
    for case, eq in result.efficiency_functions.items():
        print(f" {case.capitalize()}: {eq}")

    print("\n∑ Sumatorias:")
    for case, summ in result.summations.items():
        print(f" {case.capitalize()}: {summ}")

    print("\n📈 Complejidades:")
    for case, bigo in result.complexity_summary.items():
        print(f" {case.capitalize()}: {bigo}")

    print("\n🧠 Explicación:")
    print(result.explanation)

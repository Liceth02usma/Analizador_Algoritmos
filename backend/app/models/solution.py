from pydantic import BaseModel, field_validator
from typing import List, Dict, Any, Optional, Union


class Solution(BaseModel):
    type: str  # "iterative" | "recursive"

    # Explicación del código y análisis general
    code_explain: Optional[str] = None
    complexity_line_to_line: Optional[Union[str, List[Dict[str, Any]]]] = None
    explain_complexity: Optional[str] = None
    asymptotic_notation: Optional[Dict[str, str]] = None
    # {
    #   "best": "Ω(1)",
    #   "worst": "O(n²)",
    #   "average": "Θ(n log n)",
    #   "explanation": "..."
    # }
    algorithm_name: Optional[str] = None  # "Merge Sort", "Binary Search", etc.
    algorithm_category: Optional[str] = (
        None  # "Divide and Conquer", "Dynamic Programming"
    )
    # Ecuación: sumatoria o recurrencia (puede ser única o lista para múltiples casos)
    equation: Optional[Union[str, List[str]]] = None

    # Método de resolución (recursivo): árbol, maestro, expansión, etc. (puede ser único o lista)
    method_solution: Optional[Union[str, List[str]]] = None

    # Resultado de resolver ecuación (puede ser único o lista)
    solution_equation: Optional[Union[str, List[str]]] = None

    # Pasos para explicar solución (puede ser lista de strings o lista de dicts con info completa)
    explain_solution_steps: Optional[Union[List[str], List[Dict[str, Any]]]] = None

    # Diagramas (árboles, flujos, gráficos)
    diagrams: Optional[Dict[str, Any]] = None

    # Información adicional (debugging, extras opcionales)
    extra: Dict[str, Any] = {}

    def to_backend(self) -> Dict[str, Any]:
        """
        Retorna un diccionario EXACTO listo para ser enviado como respuesta backend
        (ej. FastAPI, Flask, JSONResponse).

        No altera el formato, no imprime texto bonito como __str__;
        simplemente devuelve la estructura cruda.
        """
        return self.model_dump()

    def __str__(self) -> str:
        """Reporte técnico bonito con soporte para múltiples casos."""
        lines = []
        lines.append("=" * 80)
        lines.append("  ALGORITHM ANALYSIS RESULT")
        lines.append("=" * 80)
        lines.append(f"Type: {self.type}")
        lines.append("")

        if self.code_explain:
            lines.append("▶ Code Explanation:")
            lines.append(self.code_explain)
            lines.append("")

        if self.explain_complexity:
            lines.append("▶ Complexity Explanation:")
            lines.append(self.explain_complexity)
            lines.append("")

        # Manejar complexity_line_to_line que puede ser string o lista
        if self.complexity_line_to_line:
            if isinstance(self.complexity_line_to_line, str):
                lines.append("▶ Pseudocode:")
                lines.append(self.complexity_line_to_line)
                lines.append("")
            else:
                lines.append("▶ Line-by-Line Complexity:")
                for item in self.complexity_line_to_line:
                    lines.append(
                        f"  Line {item.get('line')}: {item.get('complexity')} → {item.get('code')}"
                    )
                lines.append("")

        # Manejar ecuaciones (puede ser única o lista para múltiples casos)
        if self.equation:
            lines.append("▶ Recurrence Equation(s):")
            if isinstance(self.equation, list):
                for i, eq in enumerate(self.equation):
                    case_names = ["Best Case", "Worst Case", "Average Case"]
                    case_name = case_names[i] if i < len(case_names) else f"Case {i+1}"
                    lines.append(f"  {case_name}: {eq}")
            else:
                lines.append(f"  {self.equation}")
            lines.append("")

        # Manejar métodos de solución (puede ser único o lista)
        if self.method_solution:
            lines.append("▶ Solution Method(s) Used:")
            if isinstance(self.method_solution, list):
                for i, method in enumerate(self.method_solution):
                    case_names = ["Best Case", "Worst Case", "Average Case"]
                    case_name = case_names[i] if i < len(case_names) else f"Case {i+1}"
                    lines.append(f"  {case_name}: {method}")
            else:
                lines.append(f"  {self.method_solution}")
            lines.append("")

        # Manejar complejidades resueltas (puede ser única o lista)
        if self.solution_equation:
            lines.append("▶ Complexity Result(s):")
            if isinstance(self.solution_equation, list):
                for i, sol in enumerate(self.solution_equation):
                    case_names = ["Best Case", "Worst Case", "Average Case"]
                    case_name = case_names[i] if i < len(case_names) else f"Case {i+1}"
                    lines.append(f"  {case_name}: {sol}")
            else:
                lines.append(f"  {self.solution_equation}")
            lines.append("")

        # Manejar notación asintótica (Ω, O, Θ)
        if self.asymptotic_notation:
            lines.append("▶ Asymptotic Notation:")
            if isinstance(self.asymptotic_notation, str):
                lines.append(f"  {self.asymptotic_notation}")
            elif isinstance(self.asymptotic_notation, list):
                for i, notation in enumerate(self.asymptotic_notation):
                    case_names = ["Best Case (Ω)", "Worst Case (O)", "Average Case (Θ)"]
                    case_name = case_names[i] if i < len(case_names) else f"Case {i+1}"
                    lines.append(f"  {case_name}: {notation}")
            elif isinstance(self.asymptotic_notation, dict):
                # Soporte para diccionario con claves best/worst/average
                if "best" in self.asymptotic_notation:
                    lines.append(f"  Best Case (Ω): {self.asymptotic_notation['best']}")
                if "worst" in self.asymptotic_notation:
                    lines.append(
                        f"  Worst Case (O): {self.asymptotic_notation['worst']}"
                    )
                if "average" in self.asymptotic_notation:
                    lines.append(
                        f"  Average Case (Θ): {self.asymptotic_notation['average']}"
                    )
                if "explanation" in self.asymptotic_notation:
                    lines.append(
                        f"\n  Explanation: {self.asymptotic_notation['explanation']}"
                    )
            lines.append("")

        # Manejar pasos de resolución (puede ser lista de strings o lista de dicts)
        if self.explain_solution_steps:
            lines.append("▶ Detailed Analysis:")
            lines.append("")

            # Si son diccionarios con análisis completo
            if self.explain_solution_steps and isinstance(
                self.explain_solution_steps[0], dict
            ):
                for i, analysis in enumerate(self.explain_solution_steps, 1):
                    case_type = analysis.get("case_type", "unknown")
                    case_display = {
                        "best_case": "BEST CASE",
                        "worst_case": "WORST CASE",
                        "average_case": "AVERAGE CASE",
                        "single": "ANALYSIS",
                    }.get(case_type, case_type.upper())

                    lines.append(f"  [{i}] {case_display}")
                    lines.append(f"      Equation: {analysis.get('equation', 'N/A')}")
                    lines.append(f"      Method: {analysis.get('method', 'N/A')}")
                    lines.append(
                        f"      Complexity: {analysis.get('complexity', 'N/A')}"
                    )

                    if analysis.get("classification_confidence"):
                        lines.append(
                            f"      Classification Confidence: {analysis['classification_confidence']:.2f}"
                        )

                    if analysis.get("explanation"):
                        lines.append(
                            f"      Explanation: {analysis['explanation'][:150]}..."
                        )

                    if analysis.get("steps"):
                        lines.append(
                            f"      Resolution Steps: {len(analysis['steps'])} steps"
                        )

                    lines.append("")
            else:
                # Si son strings simples
                for step in self.explain_solution_steps:
                    lines.append(f"  - {step}")
                lines.append("")

        # Manejar diagramas
        if self.diagrams:
            lines.append("▶ Diagrams & Trees:")

            lines.append(f"  (See 'diagrams' attribute for details){self.diagrams}")

        return "\n".join(lines)

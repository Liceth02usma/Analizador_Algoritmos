from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class Solution(BaseModel):
    type: str                        # "iterative" | "recursive"
    
    # Explicación del código y análisis general
    code_explain: Optional[str]      
    complexity_line_to_line: Optional[List[Dict[str, Any]]]
    explain_complexity: Optional[str]

    # Ecuación: sumatoria o recurrencia
    equation: Optional[str]                      
    
    # Método de resolución (recursivo): árbol, maestro, expansión, etc.
    method_solution: Optional[str]               
    
    # Resultado de resolver ecuación
    solution_equation: Optional[str]             
    
    # Pasos para explicar solución
    explain_solution_steps: Optional[List[str]]   
    
    # Diagramas (árboles, flujos, gráficos)
    diagrams: Optional[Dict[str, Any]]           

    # Información adicional (debugging, extras opcionales)
    extra: Dict[str, Any] = {}


    def __str__(self) -> str:
        """Reporte técnico bonito."""
        lines = []
        lines.append("===== Algorithm Analysis Result =====")
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

        if self.complexity_line_to_line:
            lines.append("▶ Line-by-Line Complexity:")
            for item in self.complexity_line_to_line:
                lines.append(f"  Line {item.get('line')}: {item.get('complexity')} → {item.get('code')}")
            lines.append("")

        if self.equation:
            lines.append("▶ Equation:")
            lines.append(self.equation)
            lines.append("")

        if self.method_solution:
            lines.append("▶ Solution Method Used:")
            lines.append(self.method_solution)
            lines.append("")

        if self.solution_equation:
            lines.append("▶ Solved Equation:")
            lines.append(self.solution_equation)
            lines.append("")

        if self.explain_solution_steps:
            lines.append("▶ Step-by-Step Resolution:")
            for step in self.explain_solution_steps:
                lines.append(f"  - {step}")
            lines.append("")

        if self.diagrams:
            lines.append("▶ Diagrams:")
            for name, diagram in self.diagrams.items():
                lines.append(f"  {name}: {diagram}")
            lines.append("")

        return "\n".join(lines)

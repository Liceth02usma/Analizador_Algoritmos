"""
CostTableBuilder corregido
- Ya no llama get_loop_iterations() directamente (que requiere 'case').
- Usa iteration_model producido por ExecutionCounter.
- Devuelve los 3 casos: best, average, worst.
"""

from typing import Any, Dict, List
from .costing import cost_of_statement

class CostTableBuilder:

    def __init__(self, ast: Any, iteration_model: Dict[str, Dict[str, str]]):
        """
        ast : AST crudo de Lark
        iteration_model : {
            "best": {"1": "1", "2": "n", ...},
            "average": {...},
            "worst": {...}
        }
        """
        self.ast = self._flatten_ast(ast)
        self.iteration_model = iteration_model

    # --------------------------------------------
    # Aplanar AST
    # --------------------------------------------
    def _flatten_ast(self, node: Any) -> List[Dict[str, Any]]:
        if isinstance(node, list):
            final = []
            for x in node:
                final.extend(self._flatten_ast(x))
            return final

        if not isinstance(node, dict) and not hasattr(node, "children"):
            return []

        # Lark Tree
        if hasattr(node, "data"):
            flat = []
            for child in node.children:
                flat.extend(self._flatten_ast(child))
            return flat

        # Nodo con "body"
        if isinstance(node, dict) and "body" in node:
            return [node] + self._flatten_ast(node["body"])

        return [node] if isinstance(node, dict) else []

    # ------------------------------------------------------------
    # Construcción de tabla con los 3 casos
    # ------------------------------------------------------------
    def build_table(self):
        rows = []

        for line_number, stmt in enumerate(self.ast, start=1):
            stmt_type = stmt.get("type", "stmt")
            base_cost = cost_of_statement(stmt)

            best_iter = self.iteration_model["best"].get(str(line_number), "1")
            avg_iter = self.iteration_model["average"].get(str(line_number), "1")
            worst_iter = self.iteration_model["worst"].get(str(line_number), "1")

            rows.append({
                "line": str(line_number),
                "statement": stmt_type,
                "cost": str(base_cost),
                "executions_best": best_iter,
                "executions_average": avg_iter,
                "executions_worst": worst_iter,
                "total_best": f"{base_cost} * {best_iter}",
                "total_average": f"{base_cost} * {avg_iter}",
                "total_worst": f"{base_cost} * {worst_iter}"
            })

        return rows

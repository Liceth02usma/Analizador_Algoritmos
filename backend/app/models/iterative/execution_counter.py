"""
Clase ExecutionCounter para calcular las iteraciones de cada línea
del pseudocódigo según mejor, promedio y peor caso.
Incluye tus funciones auxiliares pero ahora organizadas en OOP.
"""

from typing import Any, Dict, List


# ===============================================================
# Funciones auxiliares originales (se mantienen intactas)
# ===============================================================


def _is_increment(expr):
    return isinstance(expr, dict) and expr.get("op") == "+"


def _is_decrement(expr):
    return isinstance(expr, dict) and expr.get("op") == "-"


def _is_multiplication(expr):
    return isinstance(expr, dict) and expr.get("op") == "*"


def _is_division(expr):
    return isinstance(expr, dict) and expr.get("op") in ("/", "div")


def _find_control_updates(var, body):
    for stmt in body:
        if isinstance(stmt, dict) and stmt.get("type") == "assign":
            if stmt.get("var") == var:
                return stmt.get("value")
    return None


def _analyze_condition(cond):
    return cond.get("lhs"), cond.get("op"), cond.get("rhs")


def count_iterations_for(node, case: str) -> str:
    a = node.get("from")
    b = node.get("to")

    if not isinstance(a, int) or not isinstance(b, int):
        return "n"

    total = b - a + 1

    if case == "best":
        return "1"
    elif case == "average":
        return f"{total}/2"
    else:
        return str(total)


def count_iterations_while(node, case: str) -> str:
    cond = node.get("cond")
    body = node.get("body", [])

    lhs, op, rhs = _analyze_condition(cond)
    update = _find_control_updates(lhs, body)

    if update is None:
        return "1" if case == "best" else ("n/2" if case == "average" else "n")

    if op == "<" and _is_increment(update):
        return "1" if case == "best" else ("n/2" if case == "average" else "n")

    if op == ">" and _is_decrement(update):
        return "1" if case == "best" else ("n/2" if case == "average" else "n")

    if op in (">", ">=") and _is_division(update):
        return (
            "1" if case == "best" else ("log2(n)/2" if case == "average" else "log2(n)")
        )

    if op in ("<", "<=") and _is_multiplication(update):
        return (
            "1" if case == "best" else ("log2(n)/2" if case == "average" else "log2(n)")
        )

    return "1" if case == "best" else ("n/2" if case == "average" else "n")


def get_loop_iterations(loop_node: Dict[str, Any], case: str) -> str:
    t = loop_node.get("type")

    if t == "for":
        return count_iterations_for(loop_node, case)
    elif t == "while":
        return count_iterations_while(loop_node, case)
    elif t == "repeat":
        if case == "best":
            return "1"
        elif case == "average":
            return "n/2"
        else:
            return "n"

    return "1"


# ===============================================================
# NUEVA CLASE ExecutionCounter (lo que espera tu agente)
# ===============================================================


class ExecutionCounter:
    """
    Recorre el AST y genera para cada línea el número de iteraciones
    en mejor, promedio y peor caso.
    """

    def __init__(self, ast: Any):
        self.ast = ast

    def build_iteration_model(self) -> Dict[str, Dict[str, str]]:
        """
        Recorre el AST linealmente y devuelve:

        {
            "best":   { "1": "1", "2": "n", ... },
            "average": { ... },
            "worst":   { ... }
        }
        """
        model = {"best": {}, "average": {}, "worst": {}}

        # AST puede ser lista de statements (procedimiento), así que lo aplanamos
        statements = self._flatten_ast(self.ast)

        for line_number, stmt in enumerate(statements, start=1):
            stmt_type = stmt.get("type")

            if stmt_type in ["for", "while", "repeat"]:
                model["best"][str(line_number)] = get_loop_iterations(stmt, "best")
                model["average"][str(line_number)] = get_loop_iterations(
                    stmt, "average"
                )
                model["worst"][str(line_number)] = get_loop_iterations(stmt, "worst")

            else:
                # Instrucción normal → 1 ejecución en cualquier caso
                model["best"][str(line_number)] = "1"
                model["average"][str(line_number)] = "1"
                model["worst"][str(line_number)] = "1"

        return model

    # --------------------------------------------------------------
    # Método interno: aplana estructuras begin/end del AST
    # --------------------------------------------------------------
    def _flatten_ast(self, node: Any) -> List[Dict[str, Any]]:
        """
        Convierte estructuras begin…end / cuerpos de ciclos en un listado plano
        de sentencias para poder numerarlas como en el libro.
        """

        if isinstance(node, list):
            final = []
            for x in node:
                final.extend(self._flatten_ast(x))
            return final

        if not isinstance(node, dict):
            return []

        if "body" in node:
            return [node] + self._flatten_ast(node["body"])

        if node.get("type") == "if":
            out = [node]
            out.extend(self._flatten_ast(node.get("then", [])))
            out.extend(self._flatten_ast(node.get("else", [])))
            return out

        return [node]

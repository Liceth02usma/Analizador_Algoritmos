# backend/app/models/costing.py

"""
Módulo de costos para operaciones elementales + multiplicación por iteraciones.
Aplica reglas híbridas: reglas fijas universales + reglas del libro.
"""

from typing import Dict, Any
from .execution_counter import get_loop_iterations


# ============================================================
# COSTOS ELEMENTALES (Reglas universales + reglas del libro)
# ============================================================

ELEMENTARY_COSTS = {
    "assign": 1,  # x ← y, x ← x+1
    "array_access": 2,  # A[i]
    "field_access": 2,  # obj.field
    "comparison": 1,  # <, >, <=, >=, =, ≠
    "arith_op": 1,  # +, -, *, /
    "logic_op": 1,  # and, or, not
    "call": 2,  # CALL f(x)
    "return": 1,
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================


def _is_arith(expr: Any) -> bool:
    return isinstance(expr, dict) and expr.get("op") in [
        "+",
        "-",
        "*",
        "/",
        "mod",
        "div",
    ]


def _is_comparison(node: Dict) -> bool:
    return (
        isinstance(node, dict)
        and "op" in node
        and node["op"] in ["<", ">", "<=", ">=", "=", "≠"]
    )


def _is_logic(node: Dict) -> bool:
    return isinstance(node, dict) and node.get("op") in ["and", "or", "not"]


def _cost_expr(expr: Any) -> int:
    """
    Determina el costo elemental de una expresión.
    """
    # Número o variable → costo 0
    if isinstance(expr, (int, str)):
        return 0

    if not isinstance(expr, dict):
        return 0

    # A[i]
    if expr.get("type") == "array_access":
        return ELEMENTARY_COSTS["array_access"]

    # obj.field
    if expr.get("type") == "field_access":
        return ELEMENTARY_COSTS["field_access"]

    # Llamada
    if expr.get("type") == "call":
        return ELEMENTARY_COSTS["call"]

    # Aritmética
    if _is_arith(expr):
        # op + costo recursivo de operandos
        return (
            ELEMENTARY_COSTS["arith_op"]
            + _cost_expr(expr["lhs"])
            + _cost_expr(expr["rhs"])
        )

    return 0


# ============================================================
# COSTO DE UNA SENTENCIA INDIVIDUAL
# ============================================================


def cost_of_statement(stmt: Dict[str, Any]) -> int:
    """
    Devuelve el costo elemental de una sola sentencia.
    No incluye multiplicación por número de iteraciones.
    """
    t = stmt.get("type")

    # -------------------------
    # Asignación
    # -------------------------
    if t == "assign":
        value = stmt.get("value")
        return ELEMENTARY_COSTS["assign"] + _cost_expr(value)

    # -------------------------
    # Llamada
    # -------------------------
    if t == "call":
        return ELEMENTARY_COSTS["call"] + sum(
            _cost_expr(arg) for arg in stmt.get("args", [])
        )

    # -------------------------
    # Return
    # -------------------------
    if t == "return":
        return ELEMENTARY_COSTS["return"] + _cost_expr(stmt.get("value"))

    # -------------------------
    # IF
    # -------------------------
    if t == "if":
        cond = stmt.get("cond")
        cond_cost = 0

        if _is_comparison(cond):
            cond_cost = ELEMENTARY_COSTS["comparison"]
        elif _is_logic(cond):
            cond_cost = ELEMENTARY_COSTS["logic_op"]

        return cond_cost

    # -------------------------
    # Estructuras de control (FOR, WHILE, REPEAT)
    # Su costo elemental de "ciclo" es 1 (costo por evaluar condición)
    # -------------------------
    if t in ["for", "while", "repeat"]:
        return 1

    # Comentarios no cuestan
    if t == "comment":
        return 0

    return 0


# ============================================================
# COSTEO TOTAL DE UN CICLO
# ============================================================


def compute_loop_cost(loop_node: Dict[str, Any]) -> Dict[str, Any]:
    """
    Devuelve:
        {
            "iterations": "n",
            "body_cost": 5,
            "total": "5*n"
        }
    """

    iters = get_loop_iterations(loop_node)
    body = loop_node.get("body", [])

    body_cost = sum(cost_of_statement(stmt) for stmt in body)

    return {
        "iterations": iters,
        "body_cost": body_cost,
        "total": f"{body_cost} * {iters}",
    }


# ============================================================
# COSTEO TOTAL GENERAL
# ============================================================


def compute_cost(ast: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa el AST completo y devuelve los costos de cada sentencia
    y el total acumulado simbólicamente.
    """
    results = []
    total_symbolic = []

    for stmt in ast:
        t = stmt.get("type")

        if t in ["for", "while", "repeat"]:
            info = compute_loop_cost(stmt)
            results.append(
                {
                    "type": t,
                    "iterations": info["iterations"],
                    "body_cost": info["body_cost"],
                    "total": info["total"],
                }
            )
            total_symbolic.append(f"({info['total']})")
            continue

        # Sentencia normal
        c = cost_of_statement(stmt)
        results.append({"type": t, "cost": c})
        total_symbolic.append(str(c))

    final_expression = " + ".join(total_symbolic)

    return {"steps": results, "total_cost_expression": final_expression}

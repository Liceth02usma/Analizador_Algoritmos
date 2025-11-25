"""
Adaptación del formateador original para que el agente pueda usarlo
como una clase OutputFormatter, manteniendo la lógica de tu archivo base.
"""

from typing import Dict, List, Any

# ============================================================
# 1. Funciones originales (copiadas desde backend/app/models/outcome_formatter.py)
# ============================================================

def format_cost_table(steps: List[Dict[str, Any]]) -> str:
    lines = []
    header = (
        "Línea | Operación | Coste Elem. | # Ejecuciones | Coste Total\n"
        "----- | --------- | ----------- | ------------- | -----------"
    )
    lines.append(header)

    for idx, step in enumerate(steps, start=1):

        op = step.get("type", "")
        cost = step.get("cost", "")
        iters = ""

        if "iterations" in step:
            iters = step["iterations"]
            total = step["total"]
        else:
            iters = "1"
            total = str(cost)

        row = f"{idx} | {op} | {cost} | {iters} | {total}"
        lines.append(row)

    return "\n".join(lines)


def build_summation_expression(steps: List[Dict[str, Any]]) -> str:
    terms = []

    for step in steps:
        if "iterations" in step:
            body = step["body_cost"]
            iters = step["iterations"]
            terms.append(f"{body} * {iters}")
        else:
            terms.append(str(step.get("cost", 0)))

    return " + ".join(terms)


def assemble_full_function(total_cost_expression: str) -> str:
    return f"T(n) = {total_cost_expression}"


def format_full_output(cost_data: Dict[str, Any]) -> Dict[str, str]:
    steps = cost_data["steps"]
    table = format_cost_table(steps)

    summation_expr = build_summation_expression(steps)
    t_of_n = assemble_full_function(cost_data["total_cost_expression"])

    return {
        "table": table,
        "summation": summation_expr,
        "T_of_n": t_of_n
    }


# ============================================================
# 2. NUEVA CLASE OutputFormatter (lo que el agente espera)
# ============================================================

class OutputFormatter:

    def format_line_cost_table(self, line_cost_table, iteration_model):
        """
        Produce el formato requerido por IterativeAnalysisResponse,
        donde TODOS los campos deben ser strings.
        """

        formatted = {}

        for case in ["best_case", "average_case", "worst_case"]:
            key = case.replace("_case", "")
            case_rows = []

            for entry in line_cost_table:
                ln = str(entry["line"])        # convertir a string
                cost = str(entry["cost"])      # convertir a string
                execs = iteration_model[key].get(ln, "1")

                case_rows.append({
                    "line": ln,
                    "statement": str(entry["statement"]),
                    "cost": cost,
                    "executions": str(execs)
                })

            formatted[case] = case_rows

        return formatted

    def format_total_output(self, cost_data):
        return format_full_output(cost_data)


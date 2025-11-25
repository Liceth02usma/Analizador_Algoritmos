"""
Construye T(n) para mejor, promedio y peor caso
multiplicando costo por línea × número de ejecuciones.
"""

from typing import Dict, Any, List
from .execution_counter import ExecutionCounter


class EfficiencyBuilder:

    def __init__(self, pseudocode: str, line_cost_table, iteration_model):
        self.pseudocode = pseudocode
        self.line_cost_table = line_cost_table
        self.iteration_model = iteration_model

    def build_efficiency(self) -> Dict[str, Dict[str, str]]:
        """
        Devuelve:
        {
            "best_case":    {"T": "...", "summation": "..."},
            "average_case": {"T": "...", "summation": "..."},
            "worst_case":   {"T": "...", "summation": "..."}
        }
        """

        results = {}

        for case in ["best_case", "average_case", "worst_case"]:
            T, summation = self._build_case(case)
            results[case] = {
                "T": T,
                "summation": summation
            }

        return results

    def _build_case(self, case: str):
        """
        Aplica:
        T(n) = sum( costo_linea_i × iteraciones_i )
        """
        case_key = case.replace("_case", "")
        iteration_info = self.iteration_model[case_key]

        parts_T = []
        parts_sum = []

        for line in self.line_cost_table:
            line_num = line["line"]
            cost_value = line["cost"]
            cost_str = str(cost_value)


            iter_str = iteration_info.get(str(line_num), "1")

            parts_T.append(f"{cost_str} * {iter_str}")
            parts_sum.append(f"Σ({cost_str}, {iter_str})")

        return " + ".join(parts_T), " + ".join(parts_sum)

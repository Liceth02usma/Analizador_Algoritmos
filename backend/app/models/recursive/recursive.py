from typing import Optional, List, Dict, Any

from .clasification_equation import classify_recurrence, StrategyType
from ..algorithm import Algorithm
from ..complexity import Complexity
from ..algorithm_pattern import AlgorithmPatterns
from .recurrence_analysis import RecurrenceEquationAgent, RecurrenceOutput
from .recurrence_method import RecurrenceMethods
from .tree import RecurrenceTreeAgent
from ..solution import Solution


class Recursive(Algorithm):
    """
    Representa un algoritmo recursivo.
    Analiza casos base, relaciones de recurrencia y construye árboles de recursión.
    Compatible con la gramática Lark (detecta llamadas recursivas con CALL).
    """

    def __init__(self, name: str, pseudocode: str, case):
        super().__init__(name, pseudocode)
        self.type = "Recursivo"
        self.base_case_condition: str = ""
        self.recurrence_relation: str = ""
        self.recursion_depth: int = 0
        self.recurrence_equation: str = ""
        self.recursive_calls: int = 0
        self.recursive_call_nodes: List[Dict[str, Any]] = []
        self.type_case = case

    def extract_recurrence(self) -> str:
        """
        Extrae la relación de recurrencia del algoritmo recursivo.
        Analiza la estructura AST para encontrar llamadas recursivas y su patrón.
        Returns:
            String con la relación de recurrencia (ej: "T(n) = 2T(n/2) + n")
        """
        self.recursive_call_nodes = []

        def find_recursive_calls(node: Any):
            """Encuentra todas las llamadas recursivas al mismo procedimiento en cualquier parte del árbol."""
            if isinstance(node, dict):

                if (
                    node.get("type") == "call"
                    and node.get("name", "").lower() == self.name.lower()
                ):
                    self.recursive_call_nodes.append(node)

                for value in node.values():
                    find_recursive_calls(value)
            elif isinstance(node, list):

                for item in node:
                    find_recursive_calls(item)

        find_recursive_calls(self.structure)

        self.recursive_calls = len(self.recursive_call_nodes)

    def get_analysis_recurrence(self) -> RecurrenceOutput:
        """
        Utiliza el agente RecurrenceAnalysis para obtener la ecuación de recurrencia.

        Returns:
            RecurrenceOutput: Objeto con la ecuación de recurrencia y caso de análisis.
                            En caso de error, retorna ecuación indicando el fallo.
        """
        solutions_equation = []
        solutions_explain = []
        # Obtiene la ecuacion de recurrencia
        recurrence_result = self._get_equation_recurrence()
        print(recurrence_result)

        
        if recurrence_result.has_multiple_cases and self.type_case:
 
            best_case = recurrence_result.best_case.recurrence_equation
            worst_case = recurrence_result.worst_case.recurrence_equation
            average_case = recurrence_result.average_case.recurrence_equation

            equation = [best_case, worst_case, average_case]
            # Generar árboles para múltiples casos
            Trees = self._create_tree(
                best_case=best_case,
                worst_case=worst_case,
                average_case=average_case
            )
        else:
            equation = recurrence_result.recurrence_equation
            # Generar árbol para ecuación única
            Trees = self._create_tree(single_equation=equation)
        
        result = self._classify_recurrence(equation)
        for r in result:
            solution_equation = self._solution_equation_recurrence(r.equation_normalized, r.method)
            solutions_equation.append(solution_equation.complexity)
            solutions_explain.append(solution_equation.detailed_explanation)
        
        print(Trees, "ESTE ES EL ARBOL DESDE RECURRENCE")
        return Solution(
            type="Recursivo",
            code_explain="Explicacion de lo que hace el codigo",
            complexity_line_to_line=self.pseudocode,
            equation= equation,
            method_solution= [r.method.value for r in result],
            solution_equation= solutions_equation,
            explain_solution_steps= solutions_explain,
            diagrams= Trees,
        )
    

    def _get_equation_recurrence(self):
        analysis_agent = RecurrenceEquationAgent(
            model_type="Modelo_Preciso", enable_verbose=True
        )
        recurrence_result = analysis_agent.analyze_recurrence(self)
        return recurrence_result

    def _classify_recurrence(self, equation_recurrence):
        result_master = classify_recurrence(
            equation=equation_recurrence,
            use_agent=True,  
            verbose=True,  
        )

        print(f"\n Resultado Final:")
        print(f"  Método: {result_master.method.value}")
        print(f"  Confianza: {result_master.confidence:.2f}")
        print(f"  Razón: {result_master.reasoning}")
        return result_master

    def _solution_equation_recurrence(self, equation_recurrence, method):

        # se le pasa el metodo a recurrence_analysis
        self.recurrence_equation = equation_recurrence
        recurrence_resolve = RecurrenceMethods(recurrence=self.recurrence_equation)
        recurrence_resolve.set_strategy(StrategyType[method.name])
        solution = recurrence_resolve.solve()
        print(solution, "ESTE ES LA SOLUCION FINAL")

        return solution

        #print(self.create_tree(), "ESTE ES EL ARBOL DESDE RECURRENCE")

    def _create_tree(
        self, 
        best_case: Optional[str] = None,
        worst_case: Optional[str] = None,
        average_case: Optional[str] = None,
        single_equation: Optional[str] = None
    ) -> dict:
        """
        Construye los bosquejos de árboles de recursión del algoritmo.
        Genera uno o múltiples árboles según el tipo de caso.

        Args:
            best_case: Ecuación del mejor caso (opcional)
            worst_case: Ecuación del peor caso (opcional)
            average_case: Ecuación del caso promedio (opcional)
            single_equation: Ecuación única si no hay casos múltiples (opcional)

        Returns:
            dict: RecurrenceTreeResponse con los bosquejos de árboles generados
        """
        # Instanciar el agente
        tree_agent = RecurrenceTreeAgent(
            model_type="Modelo_Codigo",
            enable_verbose=True,
        )

        # Llamar al método del agente con los parámetros apropiados
        result = tree_agent.generate_tree_sketches(
            best_case=best_case,
            worst_case=worst_case,
            average_case=average_case,
            single_equation=single_equation,
            max_depth=4,  # Profundidad del bosquejo
            thread_id=f"tree_{self.name}",
        )

        print(result, "ESTE ES EL RESULTADO DEL ARBOL")

        # Retornar el resultado (RecurrenceTreeResponse)
        return result

    def identify_pattern(self) -> AlgorithmPatterns:
        """
        Identifica patrones algorítmicos en código recursivo.

        Returns:
            Objeto AlgorithmPatterns con el patrón detectado
        """

        return ""

    def analyze_complexity(self) -> Complexity:
        """
        Realiza el análisis completo de complejidad del algoritmo recursivo.

        Returns:
            Objeto Complexity con el análisis detallado
        """
        return ""

    def extract_base_case(self) -> List[Dict[str, Any]]:
        """
        Extrae la condición del caso base del algoritmo recursivo.
        Detecta tanto casos base explícitos (con return) como implícitos.

        Returns:
            Lista de diccionarios con los casos base detectados
        """
        base_cases = []

        def find_base_case(node: Any, path: str = "root") -> None:
            """Busca if statements que podrían ser casos base."""
            if isinstance(node, dict):

                if node.get("type") == "if":
                    then_body = node.get("then", [])
                    else_body = node.get("else", [])
                    cond = node.get("cond", {})

                    has_return_in_then = False
                    if isinstance(then_body, list):
                        for stmt in then_body:
                            if isinstance(stmt, dict) and stmt.get("type") == "return":
                                has_return_in_then = True
                                break
                    elif (
                        isinstance(then_body, dict)
                        and then_body.get("type") == "return"
                    ):
                        has_return_in_then = True

                    if has_return_in_then:
                        base_cases.append(
                            {
                                "condition": str(cond),
                                "return_value": "detected",
                                "path": path,
                                "type": "explicit",
                            }
                        )

                    has_recursive_call = False
                    if isinstance(then_body, list):
                        for stmt in then_body:
                            if self._contains_recursive_call(stmt):
                                has_recursive_call = True
                                break
                    elif self._contains_recursive_call(then_body):
                        has_recursive_call = True

                    if has_recursive_call and not else_body:

                        negated_cond = self._negate_condition(cond)
                        base_cases.append(
                            {
                                "condition": negated_cond,
                                "return_value": "implicit",
                                "path": path,
                                "type": "implicit",
                            }
                        )

                for key, value in node.items():
                    if key not in ["type"]:
                        find_base_case(value, f"{path}/{key}")

            elif isinstance(node, list):
                for i, item in enumerate(node):
                    find_base_case(item, f"{path}[{i}]")

        find_base_case(self.structure)

        self.base_case_condition = f"{len(base_cases)} casos base detectados"
        return base_cases

    def _contains_recursive_call(self, node: Any) -> bool:
        """Verifica si un nodo contiene alguna llamada recursiva."""
        if isinstance(node, dict):
            if (
                node.get("type") == "call"
                and node.get("name", "").lower() == self.name.lower()
            ):
                return True
            for value in node.values():
                if self._contains_recursive_call(value):
                    return True
        elif isinstance(node, list):
            for item in node:
                if self._contains_recursive_call(item):
                    return True
        return False

    def _negate_condition(self, cond: Dict[str, Any]) -> str:
        """Niega una condición simple para representar el caso base implícito."""
        if not isinstance(cond, dict):
            return f"not ({str(cond)})"

        op = cond.get("op", "")
        lhs = cond.get("lhs", "")
        rhs = cond.get("rhs", "")

        negation_map = {
            "<": ">=",
            ">": "<=",
            "<=": ">",
            ">=": "<",
            "=": "!=",
            "!=": "=",
            "==": "!=",
        }

        negated_op = negation_map.get(op, f"not {op}")
        return f"{lhs} {negated_op} {rhs}"




"""
1. Primero vamos a hacer el diseño de Solution para mandar la solucion al frontend
3. Solucionar el arbol para que envie los 3 casos o uno  (crear promtpt)
"""
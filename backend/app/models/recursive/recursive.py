from typing import Optional, List, Dict, Any

from .equation_characteristic import CharacteristicEquationStrategy

from .clasification_equation import classify_recurrence, StrategyType
from ..algorithm import Algorithm
from ..complexity import Complexity
from ..algorithm_pattern import AlgorithmPatterns
from .recurrence_analysis import RecurrenceEquationAgent, RecurrenceOutput
from .recurrence_method import RecurrenceMethods
from .tree import RecurrenceTreeAgent
from .tree_method import TreeMethodStrategy
from ..solution import Solution
from .complexity_line_agent import ComplexityLineByLineAgent
from .equation_simplification import simplify_recurrence_equation
from ...utils.helpers import generate_tree_visualization, generate_tree_method_diagram
from ...external_services.Agentes.ComplexityAnalysisAgent import (
    ComplexityAnalysisService,
)


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
        # =====================================================================
        # 1. OBTENER ECUACIONES DE RECURRENCIA
        # =====================================================================
        recurrence_result = self._get_equation_recurrence()

        # =====================================================================
        # 2. DETERMINAR ECUACIONES A ANALIZAR
        # =====================================================================
        equations_to_analyze = []
        equation_display = []

        if recurrence_result.has_multiple_cases and self.type_case:
            # Casos múltiples: mejor, peor y promedio
            equations_to_analyze = [
                ("best_case", recurrence_result.best_case.recurrence_equation),
                ("worst_case", recurrence_result.worst_case.recurrence_equation),
                ("average_case", recurrence_result.average_case.recurrence_equation),
            ]
            equation_display = [
                recurrence_result.best_case.recurrence_equation,
                recurrence_result.worst_case.recurrence_equation,
                recurrence_result.average_case.recurrence_equation,
            ]
        else:
            # Caso individual/general
            equations_to_analyze = [("single", recurrence_result.recurrence_equation)]
            equation_display = recurrence_result.recurrence_equation

        # =====================================================================
        # 3. SIMPLIFICAR CASO PROMEDIO (si existe)
        # =====================================================================
        average_case_simplification = None

        if recurrence_result.has_multiple_cases and self.type_case:
            # Buscar el caso promedio en la lista
            for i, (case_type, eq) in enumerate(equations_to_analyze):
                if case_type == "average_case":
                    # Verificar si necesita simplificación
                    needs_simplification = any(
                        indicator in eq.lower()
                        for indicator in [
                            "σ",
                            "∑",
                            "sum",
                            "Σ",
                            "avg",
                            "donde",
                            "where",
                            "1/n",
                            "1/(n",
                        ]
                    )

                    if needs_simplification:
                        try:
                            simplification_result = simplify_recurrence_equation(
                                equation=eq,
                                enable_verbose=True,
                            )

                            if simplification_result.confidence > 0.5:
                                # Guardar información de simplificación
                                average_case_simplification = {
                                    "original": eq,
                                    "simplified": simplification_result.simplified_equation,
                                    "steps": simplification_result.simplification_steps,
                                    "explicit_form": simplification_result.explicit_form,
                                    "summation_resolved": simplification_result.summation_resolved,
                                    "confidence": simplification_result.confidence,
                                    "pattern_type": simplification_result.pattern_type,
                                }

                                # Reemplazar en la lista de ecuaciones a clasificar
                                equations_to_analyze[i] = (
                                    "average_case",
                                    simplification_result.simplified_equation,
                                )

                                # También actualizar en equation_display
                                equation_display[i] = (
                                    simplification_result.simplified_equation
                                )

                        except Exception:
                            pass
                    break  # Solo procesamos el average_case

        # =====================================================================
        # 4. CLASIFICAR Y RESOLVER ECUACIONES
        # =====================================================================
        analysis_results = []
        resolved_equations = {}

        for case_type, eq in equations_to_analyze:
            # Clasificar la ecuación
            classification = self._classify_recurrence(eq)

            # Obtener solución unificada
            if isinstance(classification, list):
                classifications = classification
            else:
                classifications = [classification]

            for cls in classifications:
                # Usar la ecuación ORIGINAL (eq) en lugar de la normalizada
                recurrence_resolve = RecurrenceMethods(
                    recurrence=eq  # ← Usar eq original del clasificador
                )
                recurrence_resolve.set_strategy(cls.method)

                # solve() retorna RecurrenceSolution unificado
                unified_solution = recurrence_resolve.solve()

                # Guardar ecuación resuelta (forma cerrada) para generar árbol después
                if unified_solution.complexity:
                    resolved_equations[case_type] = unified_solution.complexity
                else:
                    resolved_equations[case_type] = cls.equation_normalized

                # Agregar información de simplificación si es el caso promedio
                simplification_info = None
                if case_type == "average_case" and average_case_simplification:
                    simplification_info = average_case_simplification

                # Recopilar toda la información relevante
                analysis_results.append(
                    {
                        "case_type": case_type,
                        "equation": eq,  # ← Ecuación original
                        "original_equation": (
                            average_case_simplification["original"]
                            if simplification_info
                            else eq  # ← Ecuación original
                        ),
                        "simplification": simplification_info,
                        "method": cls.method.value,
                        "method_enum": cls.method,
                        "complexity": unified_solution.complexity,
                        "steps": unified_solution.steps or [],
                        "explanation": unified_solution.detailed_explanation
                        or unified_solution.explanation,
                        "details": unified_solution.details,
                        "classification_confidence": cls.confidence,
                        "classification_reasoning": cls.reasoning,
                    }
                )

        # =====================================================================
        # 5. GENERAR ÁRBOLES DE RECURSIÓN
        # =====================================================================
        if recurrence_result.has_multiple_cases and self.type_case:
            # Usar ecuaciones ORIGINALES (con average simplificado si aplica)
            avg_eq = (
                equation_display[2]
                if isinstance(equation_display, list)
                else recurrence_result.average_case.recurrence_equation
            )

            tree_sketches = self._create_tree(
                best_case=recurrence_result.best_case.recurrence_equation,
                worst_case=recurrence_result.worst_case.recurrence_equation,
                average_case=avg_eq,
            )
        else:
            # Caso único - usar la ecuación original
            tree_sketches = self._create_tree(
                single_equation=recurrence_result.recurrence_equation
            )

        mermaid_code = generate_tree_visualization(tree_sketches)

        # =====================================================================
        # 6. REPLICAR CASO ÚNICO EN MEJOR, PEOR Y PROMEDIO (si aplica)
        # =====================================================================
        has_multiple = recurrence_result.has_multiple_cases and self.type_case

        if not has_multiple and len(analysis_results) == 1:
            # Replicar el caso único en mejor, peor y promedio
            single_result = analysis_results[0].copy()

            # Crear 3 copias con diferentes case_type
            best_result = single_result.copy()
            best_result["case_type"] = "best_case"

            worst_result = single_result.copy()
            worst_result["case_type"] = "worst_case"

            avg_result = single_result.copy()
            avg_result["case_type"] = "average_case"

            # Reemplazar analysis_results con los 3 casos
            analysis_results = [best_result, worst_result, avg_result]

            # Convertir equation_display a lista de 3 elementos iguales
            if isinstance(equation_display, str):
                equation_display = [
                    equation_display,
                    equation_display,
                    equation_display,
                ]

        # Construir diagrams que incluya árboles de recursión + árboles del método
        diagrams = {
            "recursion_trees": mermaid_code,
        }

        # Agregar árboles del método (si se usó TreeMethod)
        for result in analysis_results:
            if result["method_enum"] == StrategyType.TREE_METHOD:
                tree_details = result["details"]

                if tree_details:
                    # Preparar el payload según la estructura esperada por generate_tree_method_diagram
                    tree_payload = {
                        "applicable": True,
                        "method": result["equation"],
                        "tree_depth": tree_details.get("tree_depth", "desconocido"),
                        "levels_detail": tree_details.get("levels_detail", []),
                        "work_per_level": tree_details.get("work_per_level", []),
                        "complexity": result.get("complexity", "O(?)"),
                    }

                    # Llamada a la función correcta del helper
                    mermaid_diagram = generate_tree_method_diagram(tree_payload)

                    # Guardar el diagrama con la clave apropiada
                    diagrams[f"tree_method_{result['case_type']}"] = mermaid_diagram

        # =====================================================================
        # ANÁLISIS DE COMPLEJIDAD LÍNEA POR LÍNEA
        # =====================================================================
        complexity_agent = ComplexityLineByLineAgent(
            model_type="Gemini_Rapido", enable_verbose=True
        )

        code_explain = None
        complexity_line_to_line = self.pseudocode
        explain_complexity = None

        try:
            if self.type_case and recurrence_result.has_multiple_cases:
                complexity_analysis = complexity_agent.analyze_multiple_cases(
                    pseudocode=self.pseudocode, algorithm_name=self.name
                )

                code_explain = complexity_analysis.best_case.code_explanation
                complexity_line_to_line = (
                    f"=== MEJOR CASO ===\n{complexity_analysis.best_case.pseudocode_annotated}\n\n"
                    f"=== PEOR CASO ===\n{complexity_analysis.worst_case.pseudocode_annotated}\n\n"
                    f"=== CASO PROMEDIO ===\n{complexity_analysis.average_case.pseudocode_annotated}"
                )
                explain_complexity = (
                    f"Mejor caso: {complexity_analysis.best_case.complexity_explanation}\n\n"
                    f"Peor caso: {complexity_analysis.worst_case.complexity_explanation}\n\n"
                    f"Caso promedio: {complexity_analysis.average_case.complexity_explanation}"
                )
            else:
                complexity_analysis = complexity_agent.analyze_single_case(
                    pseudocode=self.pseudocode, algorithm_name=self.name
                )

                code_explain = complexity_analysis.analysis.code_explanation
                complexity_line_to_line = (
                    complexity_analysis.analysis.pseudocode_annotated
                )
                explain_complexity = complexity_analysis.analysis.complexity_explanation

        except Exception:
            code_explain = f"Algoritmo: {self.name}"
            explain_complexity = "No se pudo generar análisis automático"

        # =====================================================================
        # 7. DETERMINAR NOTACIÓN ASINTÓTICA CON COMPLEXITYANALYSISSERVICE
        # =====================================================================
        # Preparar datos para el servicio de complejidad
        cases_for_complexity = []
        for result in analysis_results:
            case_name = result["case_type"]
            # Mapear nombres internos a nombres legibles
            if case_name == "best_case":
                display_name = "Mejor Caso"
            elif case_name == "worst_case":
                display_name = "Peor Caso"
            elif case_name == "average_case":
                display_name = "Caso Promedio"
            else:
                display_name = "General"

            # Usar la complejidad resuelta (forma cerrada)
            efficiency_function = result.get("complexity", "n")

            cases_for_complexity.append(
                {"case_name": display_name, "efficiency_function": efficiency_function}
            )

        # Invocar el servicio de análisis de complejidad
        complexity_service = ComplexityAnalysisService()
        asymptotic_response = complexity_service.determine_complexity(
            algorithm_name=self.name, cases_data=cases_for_complexity
        )

        # =====================================================================
        # 8. ORGANIZAR SOLUTION PARA ENVIAR AL FRONTEND
        # =====================================================================

        # Construir asymptotic_notation desde la respuesta del servicio
        asymptotic_notation = {"explanation": asymptotic_response.final_conclusion}

        # Mapear resultados a mejor/peor/promedio
        for asym_result in asymptotic_response.analysis:
            if (
                "mejor" in asym_result.case_name.lower()
                or "best" in asym_result.case_name.lower()
            ):
                asymptotic_notation["best"] = asym_result.formatted_notation
            elif (
                "peor" in asym_result.case_name.lower()
                or "worst" in asym_result.case_name.lower()
            ):
                asymptotic_notation["worst"] = asym_result.formatted_notation
            elif (
                "promedio" in asym_result.case_name.lower()
                or "average" in asym_result.case_name.lower()
            ):
                asymptotic_notation["average"] = asym_result.formatted_notation
            else:
                # Caso general - replicar en todos
                asymptotic_notation["best"] = asym_result.formatted_notation
                asymptotic_notation["worst"] = asym_result.formatted_notation
                asymptotic_notation["average"] = asym_result.formatted_notation

        # Asegurar que todos los casos existen (fallback)
        default_complexity = asymptotic_notation.get("worst", "O(n)")
        asymptotic_notation.setdefault("best", default_complexity)
        asymptotic_notation.setdefault("worst", default_complexity)
        asymptotic_notation.setdefault("average", default_complexity)

        return Solution(
            type="Recursivo",
            code_explain=code_explain,
            complexity_line_to_line=complexity_line_to_line,
            explain_complexity=explain_complexity,
            equation=equation_display,
            algorithm_name=self.name,
            algorithm_category="Recursivo",
            asymptotic_notation=asymptotic_notation,
            method_solution=[r["method"] for r in analysis_results],
            solution_equation=[
                r["complexity"] for r in analysis_results if r["complexity"]
            ],
            explain_solution_steps=analysis_results,
            diagrams=diagrams,
            extra={
                "has_multiple_cases": has_multiple,
                "analysis_details": analysis_results,
                "was_replicated": not has_multiple,
            },
        )

    def _get_equation_recurrence(self):
        analysis_agent = RecurrenceEquationAgent(
            model_type="Gemini_Rapido", enable_verbose=True
        )
        recurrence_result = analysis_agent.analyze_recurrence(self)
        return recurrence_result

    def _classify_recurrence(self, equation_recurrence):
        result_master = classify_recurrence(
            equation=equation_recurrence,
            use_agent=True,
            verbose=True,
        )

        return result_master

    def _solution_equation_recurrence(self, equation_recurrence, method):

        # se le pasa el metodo a recurrence_analysis
        self.recurrence_equation = equation_recurrence
        recurrence_resolve = RecurrenceMethods(recurrence=self.recurrence_equation)
        recurrence_resolve.set_strategy(StrategyType[method.name])
        solution = recurrence_resolve.solve()

        return solution

        # print(self.create_tree(), "ESTE ES EL ARBOL DESDE RECURRENCE")

    def _create_tree(
        self,
        best_case: Optional[str] = None,
        worst_case: Optional[str] = None,
        average_case: Optional[str] = None,
        single_equation: Optional[str] = None,
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
            model_type="Gemini_Rapido",
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

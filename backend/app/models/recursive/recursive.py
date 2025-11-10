from typing import Optional, List, Dict, Any
from app.models.algorithm import Algorithm
from app.models.complexity import Complexity
from app.models.recursive.tree import Tree
from app.models.recursive.recurrence_method import RecurrenceMethods
from app.models.algorithm_pattern import AlgorithmPatterns


class Recursive(Algorithm):
    """
    Representa un algoritmo recursivo.
    Analiza casos base, relaciones de recurrencia y construye árboles de recursión.
    Compatible con la gramática Lark (detecta llamadas recursivas con CALL).
    """

    def __init__(self, name: str, pseudocode: str):
        super().__init__(name, pseudocode)
        self.type = "Recursivo"
        self.base_case_condition: str = ""
        self.recurrence_relation: str = ""
        self.recursion_depth: int = 0
        self.recursive_calls: int = 0
        self.recursive_call_nodes: List[Dict[str, Any]] = []

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
                # Recorre todos los valores del diccionario
                for value in node.values():
                    find_recursive_calls(value)
            elif isinstance(node, list):
                # Recorre todos los elementos de la lista
                for item in node:
                    find_recursive_calls(item)

        find_recursive_calls(self.structure)

        self.recursive_calls = len(self.recursive_call_nodes)

        if self.recursive_calls == 0:
            self.recurrence_relation = "T(n) = O(1)"
            return self.recurrence_relation

        division_pattern = False
        subtraction_pattern = False
        divide_by_factor = 2

        # Helper para buscar la definición de una variable en el AST
        def find_assignment_value(var_name: str, node: Any) -> str:
            if isinstance(node, dict):
                if (
                    node.get("type") == "assign"
                    and node.get("var", "").lower() == var_name.lower()
                ):
                    val = node.get("value")
                    return str(val)
                for value in node.values():
                    result = find_assignment_value(var_name, value)
                    if result:
                        return result
            elif isinstance(node, list):
                for item in node:
                    result = find_assignment_value(var_name, item)
                    if result:
                        return result
            return ""

        for call_node in self.recursive_call_nodes:
            args = call_node.get("args", [])
            # Si solo hay un argumento, revisa ese
            if len(args) == 1:
                arg_str = str(args[0]).lower()
                expr_str = find_assignment_value(arg_str, self.structure)
                if not expr_str:
                    expr_str = arg_str
                # Detectar división
                if "/" in expr_str or "div" in expr_str:
                    division_pattern = True
                    if "/2" in expr_str or "/ 2" in expr_str:
                        divide_by_factor = 2
                    elif "/3" in expr_str or "/ 3" in expr_str:
                        divide_by_factor = 3
                # Detectar resta
                elif "-" in expr_str:
                    subtraction_pattern = True
            # Si hay más de un argumento, revisa todos
            else:
                for arg in args:
                    arg_str = str(arg).lower()
                    expr_str = find_assignment_value(arg_str, self.structure)
                    if not expr_str:
                        expr_str = arg_str
                    # Detectar división
                    if "/" in expr_str or "div" in expr_str:
                        division_pattern = True
                        if "/2" in expr_str or "/ 2" in expr_str:
                            divide_by_factor = 2
                        elif "/3" in expr_str or "/ 3" in expr_str:
                            divide_by_factor = 3
                    # Detectar resta
                    elif "-" in expr_str:
                        subtraction_pattern = True

        # Construir la relación de recurrencia basada en el patrón
        if division_pattern:
            # Patrón de divide y conquista: T(n) = aT(n/b) + f(n)
            a = self.recursive_calls
            b = divide_by_factor
            if a == 1:
                self.recurrence_relation = f"T(n) = T(n/{b}) + O(1)"
            elif a == 2 and b == 2:
                self.recurrence_relation = f"T(n) = 2T(n/2) + O(n)"
            else:
                self.recurrence_relation = f"T(n) = {a}T(n/{b}) + O(n)"
        elif subtraction_pattern:
            # Patrón de recursión lineal: T(n) = T(n-k) + f(n)
            if self.recursive_calls == 1:
                self.recurrence_relation = "T(n) = T(n-1) + O(1)"
            elif self.recursive_calls == 2:
                self.recurrence_relation = "T(n) = T(n-1) + T(n-2) + O(1)"
            else:
                self.recurrence_relation = f"T(n) = {self.recursive_calls}T(n-1) + O(1)"
        else:
            # Patrón genérico
            self.recurrence_relation = f"T(n) = {self.recursive_calls}T(n/2) + O(1)"

        return self.recurrence_relation

    def build_recursion_tree(self) -> Tree:
        """
        Construye el árbol de recursión para visualizar las llamadas.

        Returns:
            Objeto Tree con la estructura del árbol de recursión
        """
        tree = Tree(root="T(n)")

        # Construir árbol basado en la relación de recurrencia
        # Por simplicidad, construimos hasta cierta profundidad
        max_depth = min(
            self.recursion_depth, 4
        )  # Limitar para no crear árboles muy grandes

        self._build_tree_recursive(tree, "T(n)", 0, max_depth)

        return tree

    def _build_tree_recursive(
        self, tree: Tree, node: str, current_depth: int, max_depth: int
    ) -> None:
        """
        Construye el árbol de recursión de forma recursiva.

        Args:
            tree: Objeto Tree a construir
            node: Nodo actual
            current_depth: Profundidad actual
            max_depth: Profundidad máxima
        """
        if current_depth >= max_depth:
            return

        # Determinar el tipo de división basado en la relación
        if "/2" in self.recurrence_relation:
            # División por 2
            for i in range(self.recursive_calls):
                child = f"T(n/{2**(current_depth+1)})"
                tree.add_node(node, child)
                self._build_tree_recursive(tree, child, current_depth + 1, max_depth)
        elif "-1" in self.recurrence_relation:
            # Substracción de 1
            child = f"T(n-{current_depth+1})"
            tree.add_node(node, child)
            self._build_tree_recursive(tree, child, current_depth + 1, max_depth)
        else:
            # Caso genérico
            for i in range(self.recursive_calls):
                child = f"T(n/{2**(current_depth+1)})_{i}"
                tree.add_node(node, child)
                self._build_tree_recursive(tree, child, current_depth + 1, max_depth)

    def solve_recurrence(self, method: str = "master") -> str:
        """
        Resuelve la relación de recurrencia usando el método especificado.

        Args:
            method: Método a usar ('master', 'substitution', 'iterative')

        Returns:
            String con la solución de la complejidad
        """
        rec_methods = RecurrenceMethods(self.recurrence_relation)

        if method == "master":
            solution = rec_methods.apply_master_theorem(self.recurrence_relation)
        elif method == "substitution":
            solution = rec_methods.substitution_method(self.recurrence_relation)
        elif method == "iterative":
            solution = rec_methods.iterative_method(self.recurrence_relation)
        else:
            solution = rec_methods.apply_master_theorem(self.recurrence_relation)

        return solution

    def estimate_complexity(self) -> Complexity:
        """
        Estima la complejidad del algoritmo recursivo.

        Returns:
            Objeto Complexity con el análisis completo
        """
        # Extraer relación de recurrencia
        self.extract_recurrence()

        # Resolver usando métodos de recurrencia
        rec_methods = RecurrenceMethods(self.recurrence_relation)
        rec_methods.apply_master_theorem(self.recurrence_relation)

        # Crear objeto de complejidad
        complexity = Complexity()
        complexity.compute_from_recurrence(rec_methods)

        self.complexity = complexity
        return complexity

    def identify_pattern(self) -> AlgorithmPatterns:
        """
        Identifica patrones algorítmicos en código recursivo.

        Returns:
            Objeto AlgorithmPatterns con el patrón detectado
        """
        pattern = AlgorithmPatterns()
        pattern.pattern_name = "Recursión General"
        pattern.description = "Patrón recursivo no clasificado"
        pattern.complexity_hint = "Requiere análisis detallado"

        return pattern

    def analyze_complexity(self) -> Complexity:
        """
        Realiza el análisis completo de complejidad del algoritmo recursivo.

        Returns:
            Objeto Complexity con el análisis detallado
        """
        # Preprocesar el código (parsear con Lark)
        self.preprocess_code()

        # Extraer relación de recurrencia
        self.extract_recurrence()

        # Estimar profundidad de recursión basada en el patrón
        if "/2" in self.recurrence_relation:
            self.recursion_depth = 10  # log₂(n) aproximadamente
        elif "-1" in self.recurrence_relation:
            self.recursion_depth = 20  # n aproximadamente
        else:
            self.recursion_depth = 10

        # Calcular complejidad
        return self.estimate_complexity()

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
                # Buscar sentencias if
                if node.get("type") == "if":
                    then_body = node.get("then", [])
                    else_body = node.get("else", [])
                    cond = node.get("cond", {})

                    # Caso 1: then contiene un return directo (caso base explícito)
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

                    # Caso 2: El then contiene llamadas recursivas pero no hay else
                    # Esto significa que cuando la condición es False, termina implícitamente
                    has_recursive_call = False
                    if isinstance(then_body, list):
                        for stmt in then_body:
                            if self._contains_recursive_call(stmt):
                                has_recursive_call = True
                                break
                    elif self._contains_recursive_call(then_body):
                        has_recursive_call = True

                    # Si hay llamadas recursivas en el then pero no hay else,
                    # la negación de la condición es un caso base implícito
                    if has_recursive_call and not else_body:
                        # Crear condición negada
                        negated_cond = self._negate_condition(cond)
                        base_cases.append(
                            {
                                "condition": negated_cond,
                                "return_value": "implicit",
                                "path": path,
                                "type": "implicit",
                            }
                        )

                # Buscar recursivamente
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

        # Negar operadores de comparación
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
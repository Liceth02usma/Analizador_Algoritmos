from typing import List, Dict, Any
from app.models.algorithm import Algorithm
from app.models.complexity import Complexity
from app.models.algorithm_pattern import AlgorithmPatterns
from app.models.flowdiagram import FlowDiagram


class Iterative(Algorithm):
    """
    Representa un algoritmo iterativo.

    Responsabilidades:
    - Almacenar la estructura del algoritmo
    - Detectar ciclos usando DFS recursivo
    - Guardar detalles completos de cada ciclo
    - Proporcionar información para análisis de complejidad

    Attributes:
        loop_types (List[str]): Tipos de ciclos detectados ['for', 'while', 'repeat']
        loop_details (List[Dict]): Información detallada de cada ciclo
        nested_loops (int): Nivel máximo de anidamiento
        operations_count (int): Total de operaciones en el algoritmo
    """

    def __init__(self, name: str, pseudocode: str):
        super().__init__(name, pseudocode)
        self.type = "Iterativo"
        self.loop_types: List[str] = []
        self.loop_details: List[Dict[str, Any]] = []
        self.nested_loops: int = 0
        self.operations_count: int = 0
        self.operations_per_loop: int = 0

    def detect_loops(self) -> None:
        """
        Detecta todos los ciclos en el pseudocódigo parseado.
        Usa DFS (Depth-First Search) recursivo para recorrer el AST.

        Guarda en self.loop_details:
        - type: 'for' | 'while' | 'repeat'
        - depth: nivel de anidamiento (1, 2, 3...)
        - loop_number: número secuencial del ciclo
        - variable: variable de control (solo FOR)
        - from/to: rango (solo FOR)
        - condition: condición (WHILE/REPEAT)
        - body: cuerpo del ciclo
        - parent: tipo del nodo padre
        - is_nested: si está dentro de otro ciclo
        - range_pattern: patrón detectado del rango
        - operations_count: operaciones en el cuerpo
        """
        self.loop_types = []
        self.loop_details = []

        def analyze_node(
            node: Any, depth: int = 0, parent_info: Dict[str, Any] = None
        ) -> int:
            """
            Analiza recursivamente el AST para encontrar ciclos.

            Args:
                node: Nodo del AST (dict, list, o primitivo)
                depth: Profundidad actual de anidamiento
                parent_info: Información del nodo padre

            Returns:
                Profundidad máxima encontrada en este subárbol
            """
            max_depth = depth

            # CASO 1: Nodo es un diccionario (estructura con tipo)
            if isinstance(node, dict):
                stmt_type = node.get("type", "")

                # === DETECTAR CICLO FOR ===
                if stmt_type == "for":
                    self.loop_types.append("for")
                    current_depth = depth + 1
                    max_depth = max(max_depth, current_depth)

                    loop_info = {
                        "type": "for",
                        "depth": current_depth,
                        "loop_number": len(self.loop_types),
                        "variable": node.get("var", "unknown"),
                        "from": self._extract_value(node.get("from", "unknown")),
                        "to": self._extract_value(node.get("to", "unknown")),
                        "body": node.get("body", []),
                        "parent": parent_info.get("type") if parent_info else "root",
                        "is_nested": depth > 0,
                        "nesting_level": current_depth,
                    }

                    # Analizar patrón del rango
                    loop_info["range_pattern"] = self._analyze_range_pattern(
                        loop_info["from"], loop_info["to"]
                    )

                    # Contar operaciones en el cuerpo
                    loop_info["operations_count"] = self._count_operations_in_body(
                        loop_info["body"]
                    )

                    self.loop_details.append(loop_info)

                    # RECURSIÓN: Analizar el cuerpo del FOR
                    body = node.get("body", [])
                    body_depth = analyze_node(body, current_depth, loop_info)
                    max_depth = max(max_depth, body_depth)

                # === DETECTAR CICLO WHILE ===
                elif stmt_type == "while":
                    self.loop_types.append("while")
                    current_depth = depth + 1
                    max_depth = max(max_depth, current_depth)

                    loop_info = {
                        "type": "while",
                        "depth": current_depth,
                        "loop_number": len(self.loop_types),
                        "condition": self._extract_condition(node.get("cond", {})),
                        "body": node.get("body", []),
                        "parent": parent_info.get("type") if parent_info else "root",
                        "is_nested": depth > 0,
                        "nesting_level": current_depth,
                    }

                    loop_info["operations_count"] = self._count_operations_in_body(
                        loop_info["body"]
                    )

                    self.loop_details.append(loop_info)

                    # RECURSIÓN: Analizar el cuerpo del WHILE
                    body = node.get("body", [])
                    body_depth = analyze_node(body, current_depth, loop_info)
                    max_depth = max(max_depth, body_depth)

                # === DETECTAR CICLO REPEAT ===
                elif stmt_type == "repeat":
                    self.loop_types.append("repeat")
                    current_depth = depth + 1
                    max_depth = max(max_depth, current_depth)

                    loop_info = {
                        "type": "repeat",
                        "depth": current_depth,
                        "loop_number": len(self.loop_types),
                        "condition": self._extract_condition(node.get("cond", {})),
                        "body": node.get("body", []),
                        "parent": parent_info.get("type") if parent_info else "root",
                        "is_nested": depth > 0,
                        "nesting_level": current_depth,
                    }

                    loop_info["operations_count"] = self._count_operations_in_body(
                        loop_info["body"]
                    )

                    self.loop_details.append(loop_info)

                    # RECURSIÓN: Analizar el cuerpo del REPEAT
                    body = node.get("body", [])
                    body_depth = analyze_node(body, current_depth, loop_info)
                    max_depth = max(max_depth, body_depth)

                # === OTRAS ESTRUCTURAS (que pueden contener ciclos) ===
                elif stmt_type == "if":
                    # Analizar bloque THEN
                    then_body = node.get("then", [])
                    then_depth = analyze_node(then_body, depth, node)
                    max_depth = max(max_depth, then_depth)

                    # Analizar bloque ELSE
                    else_body = node.get("else", [])
                    if else_body:
                        else_depth = analyze_node(else_body, depth, node)
                        max_depth = max(max_depth, else_depth)

                elif stmt_type == "procedure_def":
                    body = node.get("body", [])
                    body_depth = analyze_node(body, depth, node)
                    max_depth = max(max_depth, body_depth)

                else:
                    # Buscar recursivamente en otros nodos
                    for key, value in node.items():
                        if key != "type":
                            child_depth = analyze_node(value, depth, node)
                            max_depth = max(max_depth, child_depth)

            # CASO 2: Nodo es una lista
            elif isinstance(node, list):
                for item in node:
                    child_depth = analyze_node(item, depth, parent_info)
                    max_depth = max(max_depth, child_depth)

            # CASO 3: Tipos primitivos (no hacer nada)

            return max_depth

        # Ejecutar análisis recursivo
        self.nested_loops = analyze_node(self.structure, 0)

        # Contar operaciones totales
        self.operations_count = self._count_operations()

    # ========================================
    # Métodos auxiliares privados
    # ========================================

    def _extract_value(self, value: Any) -> Any:
        """Extrae valor de expresiones (número, variable, expresión)."""
        if isinstance(value, (int, str)):
            return value
        elif isinstance(value, dict):
            if "op" in value:
                lhs = self._extract_value(value.get("lhs", ""))
                rhs = self._extract_value(value.get("rhs", ""))
                return f"{lhs} {value['op']} {rhs}"
            return str(value)
        return str(value)

    def _extract_condition(self, condition: Any) -> str:
        """Extrae representación de una condición."""
        if isinstance(condition, dict):
            lhs = self._extract_value(condition.get("lhs", ""))
            op = condition.get("op", "")
            rhs = self._extract_value(condition.get("rhs", ""))

            if op:
                return f"{lhs} {op} {rhs}"

            # Operadores lógicos
            if condition.get("op") == "and":
                left = self._extract_condition(condition.get("lhs", {}))
                right = self._extract_condition(condition.get("rhs", {}))
                return f"({left} and {right})"
            elif condition.get("op") == "or":
                left = self._extract_condition(condition.get("lhs", {}))
                right = self._extract_condition(condition.get("rhs", {}))
                return f"({left} or {right})"
            elif condition.get("op") == "not":
                value = self._extract_condition(condition.get("value", {}))
                return f"not ({value})"

            return str(condition)
        return str(condition)

    def _analyze_range_pattern(self, from_val: Any, to_val: Any) -> str:
        """Detecta patrón del rango de un FOR."""
        from_str = str(from_val).lower()
        to_str = str(to_val).lower()

        if from_str in ["0", "0"]:
            if "n" in to_str or "length" in to_str:
                return "zero_based_to_n"
            return "zero_based"
        elif from_str in ["1", "1"]:
            if "n" in to_str or "length" in to_str:
                return "one_based_to_n"
            return "one_based"
        elif "n" in to_str or "length" in to_str:
            return "linear_to_n"
        return "custom"

    def _count_operations_in_body(self, body: List[Any]) -> int:
        """Cuenta operaciones en el cuerpo de un ciclo."""
        operations = 0

        def count_in_node(node):
            nonlocal operations
            if isinstance(node, dict):
                # Operaciones aritméticas
                if "op" in node and node["op"] in ["+", "-", "*", "/", "mod", "div"]:
                    operations += 1
                # Asignaciones
                if node.get("type") == "assign":
                    operations += 1
                # Llamadas
                if node.get("type") == "call":
                    operations += 1
                # Comparaciones
                if node.get("type") == "comparison":
                    operations += 1

                for value in node.values():
                    count_in_node(value)
            elif isinstance(node, list):
                for item in node:
                    count_in_node(item)

        count_in_node(body)
        return operations

    def _count_operations(self) -> int:
        """Cuenta todas las operaciones en el algoritmo."""
        if not self.structure:
            return 0

        operations = 0

        def count_in_node(node):
            nonlocal operations
            if isinstance(node, dict):
                if "op" in node and node["op"] in ["+", "-", "*", "/", "mod", "div"]:
                    operations += 1
                if node.get("type") in ["assign", "call"]:
                    operations += 1

                for value in node.values():
                    count_in_node(value)
            elif isinstance(node, list):
                for item in node:
                    count_in_node(item)

        count_in_node(self.structure)
        return operations

    # ========================================
    # Métodos públicos para análisis
    # ========================================

    def get_loop_summary(self) -> str:
        """
        Genera resumen legible de todos los ciclos detectados.

        Returns:
            String formateado con el resumen
        """
        if not self.loop_details:
            return "❌ No se detectaron ciclos en el algoritmo."

        summary = "\n" + "=" * 70 + "\n"
        summary += "  📊 RESUMEN DE CICLOS DETECTADOS\n"
        summary += "=" * 70 + "\n\n"

        summary += f"🔢 Total de ciclos: {len(self.loop_details)}\n"
        summary += f"📏 Nivel máximo de anidamiento: {self.nested_loops}\n"
        summary += f"🔄 Tipos de ciclos: {', '.join(set(self.loop_types))}\n"
        summary += f"⚙️  Operaciones totales: {self.operations_count}\n\n"

        for loop in self.loop_details:
            summary += (
                f"--- 🔁 Ciclo #{loop['loop_number']} ({loop['type'].upper()}) ---\n"
            )
            summary += f"  📍 Nivel: {loop['nesting_level']}\n"
            summary += f"  👤 Padre: {loop['parent']}\n"
            summary += f"  🪆 Anidado: {'Sí' if loop['is_nested'] else 'No'}\n"

            if loop["type"] == "for":
                summary += f"  🔢 Variable: {loop['variable']}\n"
                summary += f"  📐 Rango: {loop['from']} → {loop['to']}\n"
                summary += f"  🎯 Patrón: {loop['range_pattern']}\n"
            else:
                summary += f"  ❓ Condición: {loop['condition']}\n"

            summary += f"  ⚙️  Operaciones: {loop['operations_count']}\n\n"

        return summary

    def estimate_complexity(self) -> Complexity:
        """
        Estima la complejidad temporal y espacial del algoritmo iterativo.

        Delega el cálculo al modelo Complexity, proporcionando la información
        necesaria sobre los ciclos detectados.

        Returns:
            Objeto Complexity con el análisis completo
        """
        complexity = Complexity()

        # Delegar el cálculo de complejidad al modelo Complexity
        complexity.compute_from_loops(self)

        # Guardar referencia
        self.complexity = complexity
        return complexity

    def identify_pattern(self) -> str:
        """
        Identifica patrones algorítmicos.
        Delega la detección al modelo AlgorithmPatterns.

        Returns:
            Objeto AlgorithmPatterns con el patrón detectado
        """

        return ""

    def analyze_complexity(self) -> Complexity:
        """
        Realiza el análisis completo de complejidad del algoritmo iterativo.

        Este método implementa el contrato abstracto de la clase Algorithm.
        Coordina el preprocesamiento, detección de ciclos y estimación de complejidad.

        Returns:
            Objeto Complexity con el análisis detallado
        """
        # 1. Preprocesar el código (parsear con Lark si no se ha hecho)
        if not self.structure:
            self.preprocess_code()

        # 2. Detectar ciclos en la estructura
        if not self.loop_details:
            self.detect_loops()

        # 3. Estimar complejidad basada en los ciclos
        complexity = self.estimate_complexity()

        # 4. Almacenar referencia
        self.complexity = complexity

        return complexity
    

    def generate_flow_diagram(self) -> "FlowDiagram":
        """
        Genera un diagrama de flujo del algoritmo.
        
        Returns:
            Objeto FlowDiagram con la representación gráfica
        """
        
        flow_diagram = FlowDiagram()
        flow_diagram.build_from_algorithm(self)
        return flow_diagram

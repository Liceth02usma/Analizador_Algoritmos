from typing import List, Dict, Any
from app.models.algorithm import Algorithm
from app.models.complexity import Complexity
from .flowdiagram import FlowDiagram


class Iterative(Algorithm):

    def __init__(self, name: str, pseudocode: str):
        super().__init__(name, pseudocode)
        self.type = "Iterativo"
        self.loop_types: List[str] = []
        self.loop_details: List[Dict[str, Any]] = []
        self.nested_loops: int = 0
        self.operations_count: int = 0
        self.operations_per_loop: int = 0

    def detect_loops(self) -> None:
        self.loop_types = []
        self.loop_details = []

        def analyze_node(
            node: Any, depth: int = 0, parent_info: Dict[str, Any] = None
        ) -> int:
            max_depth = depth

            if isinstance(node, dict):
                stmt_type = node.get("type", "")

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

                    loop_info["range_pattern"] = self._analyze_range_pattern(
                        loop_info["from"], loop_info["to"]
                    )

                    loop_info["operations_count"] = self._count_operations_in_body(
                        loop_info["body"]
                    )

                    self.loop_details.append(loop_info)

                    body = node.get("body", [])
                    body_depth = analyze_node(body, current_depth, loop_info)
                    max_depth = max(max_depth, body_depth)

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

                    body = node.get("body", [])
                    body_depth = analyze_node(body, current_depth, loop_info)
                    max_depth = max(max_depth, body_depth)

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

                    body = node.get("body", [])
                    body_depth = analyze_node(body, current_depth, loop_info)
                    max_depth = max(max_depth, body_depth)

                elif stmt_type == "if":

                    then_body = node.get("then", [])
                    then_depth = analyze_node(then_body, depth, node)
                    max_depth = max(max_depth, then_depth)

                    else_body = node.get("else", [])
                    if else_body:
                        else_depth = analyze_node(else_body, depth, node)
                        max_depth = max(max_depth, else_depth)

                elif stmt_type == "procedure_def":
                    body = node.get("body", [])
                    body_depth = analyze_node(body, depth, node)
                    max_depth = max(max_depth, body_depth)

                else:

                    for key, value in node.items():
                        if key != "type":
                            child_depth = analyze_node(value, depth, node)
                            max_depth = max(max_depth, child_depth)

            elif isinstance(node, list):
                for item in node:
                    child_depth = analyze_node(item, depth, parent_info)
                    max_depth = max(max_depth, child_depth)

            return max_depth

        self.nested_loops = analyze_node(self.structure, 0)

        self.operations_count = self._count_operations()

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

                if "op" in node and node["op"] in ["+", "-", "*", "/", "mod", "div"]:
                    operations += 1

                if node.get("type") == "assign":
                    operations += 1

                if node.get("type") == "call":
                    operations += 1

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

    def estimate_complexity(self):

        pass

    def identify_pattern(self) -> str:
        return ""

    def analyze_complexity(self):

        if not self.structure:
            self.preprocess_code()

        if not self.loop_details:
            self.detect_loops()

    def generate_flow_diagram(self):
        pass

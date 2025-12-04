from abc import ABC, abstractmethod
import code

from app.parsers.parser import TreeToDict
from typing import List, Optional, Dict, Any
from lark import Tree as LarkTree

from .complexity import Complexity
from .algorithm_pattern import AlgorithmPatterns
from .solution import Solution


class Algorithm(ABC):

    def __init__(self, name: str, pseudocode: str):
        self.name: str = name
        self.pseudocode: str = pseudocode
        self.type: str = ""
        self.structure: List[Dict[str, Any]] = []
        self.tokens: List = []
        self.parsed_tree: Optional[LarkTree] = None
        self.complexity = None
        self._parser = None
        self.type_case = True

    def preprocess_code(self) -> None:
        """
        Preprocesa el código: parsing con Lark y extracción de estructura.
        """
        try:

            transformer = TreeToDict()
            self.parsed_tree = transformer.get_parser().parse(self.pseudocode)

            transformed = transformer.transform(self.parsed_tree)

            if hasattr(transformed, "children"):
                self.structure = transformed.children

            elif isinstance(transformed, list):
                self.structure = transformed

            elif isinstance(transformed, dict):
                self.structure = [transformed]
            else:
                self.structure = transformed

            self.tokens = self._extract_tokens_from_tree(self.structure)
            print(self.structure, "Estructura del algoritmo")

        except Exception as e:

            print(f"Warning: Error al parsear con Lark: {e}")

    def _extract_tokens_from_tree(self, tree: Any) -> List[str]:
        """
        Extrae tokens del árbol parseado.

        Args:
            tree: Árbol o estructura de datos

        Returns:
            Lista de tokens
        """
        tokens = []

        if isinstance(tree, dict):

            if "type" in tree:
                tokens.append(tree["type"])

            for value in tree.values():
                tokens.extend(self._extract_tokens_from_tree(value))

        elif isinstance(tree, list):
            for item in tree:
                tokens.extend(self._extract_tokens_from_tree(item))

        elif isinstance(tree, str):
            tokens.append(tree)

        return tokens

    @abstractmethod
    def identify_pattern(self) -> "AlgorithmPatterns":
        """
        Identifica el patrón algorítmico (debe ser implementado por subclases).

        Returns:
            Objeto AlgorithmPatterns con el patrón detectado
        """
        pass

    @abstractmethod
    def analyze_complexity(self) -> "Complexity":
        """
        Analiza la complejidad del algoritmo (debe ser implementado por subclases).

        Returns:
            Objeto Complexity con el análisis completo
        """
        pass

    def count_statement_type(self, stmt_type: str) -> int:
        """
        Cuenta cuántas sentencias de un tipo específico hay en el algoritmo.

        Args:
            stmt_type: Tipo de sentencia ('for', 'while', 'if', 'call', etc.)

        Returns:
            Cantidad de sentencias de ese tipo
        """
        count = 0

        def count_recursive(node):
            nonlocal count
            if isinstance(node, dict):
                if node.get("type") == stmt_type:
                    count += 1
                for value in node.values():
                    count_recursive(value)
            elif isinstance(node, list):
                for item in node:
                    count_recursive(item)

        count_recursive(self.structure)
        return count

    def get_max_nesting_level(self) -> int:
        """
        Calcula el nivel máximo de anidamiento en el algoritmo.

        Returns:
            Nivel máximo de anidamiento
        """

        def calculate_depth(node, current_depth=0):
            if isinstance(node, dict):
                stmt_type = node.get("type", "")

                if stmt_type in ["for", "while", "repeat", "if"]:
                    current_depth += 1

                max_depth = current_depth

                for key in ["body", "then", "else"]:
                    if key in node:
                        depth = calculate_depth(node[key], current_depth)
                        max_depth = max(max_depth, depth)

                for key, value in node.items():
                    if key not in ["type", "body", "then", "else"]:
                        depth = calculate_depth(value, current_depth)
                        max_depth = max(max_depth, depth)

                return max_depth

            elif isinstance(node, list):
                max_depth = current_depth
                for item in node:
                    depth = calculate_depth(item, current_depth)
                    max_depth = max(max_depth, depth)
                return max_depth

            return current_depth

        return calculate_depth(self.structure)

from abc import ABC, abstractmethod
import code

# Transformar árbol a estructura de datos
from app.parsers.parser import TreeToDict
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from lark import Lark, Tree as LarkTree
import os

# Usar TYPE_CHECKING para evitar imports circulares
if TYPE_CHECKING:
    from app.models.complexity import Complexity
    from app.models.flowdiagram import FlowDiagram
    from app.models.algorithm_pattern import AlgorithmPatterns


class Algorithm(ABC):
    """
    Clase abstracta base que representa un algoritmo genérico.
    Proporciona la estructura común para análisis de algoritmos iterativos y recursivos.
    Compatible con la gramática Lark definida en pseudocode.lark
    """

    def __init__(self, name: str, pseudocode: str):
        self.name: str = name
        self.pseudocode: str = pseudocode
        self.type: str = ""
        self.structure: List[Dict[str, Any]] = []  # AST del pseudocódigo
        self.tokens: List = []
        self.parsed_tree: Optional[LarkTree] = None  # Árbol de Lark
        self.complexity = None  # Objeto Complexity
        self._parser = None  # Parser Lark lazy-loaded

    def load_algorithm(self, source: str) -> None:
        """
        Carga el algoritmo desde una fuente externa.
        
        Args:
            source: Ruta del archivo o string con el pseudocódigo
        """
        if source.endswith(('.txt', '.algo', '.pseudo')):
            with open(source, 'r', encoding='utf-8') as f:
                self.pseudocode = f.read()
        else:
            self.pseudocode = source


    def preprocess_code(self) -> None:
        """
        Preprocesa el código: parsing con Lark y extracción de estructura.
        """
        try:
            # Parsear con Lark
            transformer = TreeToDict()
            self.parsed_tree = transformer.get_parser().parse(self.pseudocode)
            
            transformed = transformer.transform(self.parsed_tree)
            
            # Si el resultado es un Tree, extraer sus hijos
            if hasattr(transformed, 'children'):
                self.structure = transformed.children
            # Si es una lista, usarla directamente
            elif isinstance(transformed, list):
                self.structure = transformed
            # Si es un diccionario, envolverlo en lista
            elif isinstance(transformed, dict):
                self.structure = [transformed]
            else:
                self.structure = transformed
            
            # Extraer tokens básicos del árbol
            self.tokens = self._extract_tokens_from_tree(self.structure)
            
        except Exception as e:
            # Si falla el parsing, usar método básico
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
            # Extraer tipo de nodo
            if 'type' in tree:
                tokens.append(tree['type'])
            
            # Recursivamente extraer de los valores
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
                if node.get('type') == stmt_type:
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
                stmt_type = node.get('type', '')
                
                # Incrementar profundidad para estructuras de control
                if stmt_type in ['for', 'while', 'repeat', 'if']:
                    current_depth += 1
                
                max_depth = current_depth
                
                # Buscar en el cuerpo de las estructuras
                for key in ['body', 'then', 'else']:
                    if key in node:
                        depth = calculate_depth(node[key], current_depth)
                        max_depth = max(max_depth, depth)
                
                # Buscar en otros valores
                for key, value in node.items():
                    if key not in ['type', 'body', 'then', 'else']:
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

    def summarize_analysis(self) -> str:
        """
        Genera un resumen textual del análisis realizado.
        
        Returns:
            String con el resumen del análisis
        """
        if not self.complexity:
            return f"Algoritmo: {self.name}\nTipo: {self.type}\nEstado: Sin análisis"
        
        summary_lines = [
            f"=== Resumen de Análisis: {self.name} ===",
            f"Tipo: {self.type}",
            f"",
            f"Complejidad Temporal:",
            f"  - Peor caso: {self.complexity.worst_case}",
            f"  - Mejor caso: {self.complexity.best_case}",
            f"  - Caso promedio: {self.complexity.average_case}",
            f"",
            f"Complejidad Espacial: {self.complexity.space_complexity}",
        ]
        
        # Agregar información específica según tipo
        if self.type == "Iterativo" and hasattr(self, 'nested_loops'):
            summary_lines.append(f"")
            summary_lines.append(f"Ciclos detectados: {len(self.loop_types)}")
            summary_lines.append(f"Nivel de anidamiento: {self.nested_loops}")
        
        return "\n".join(summary_lines)


"""
Controlador para el análisis de algoritmos recursivos.

Este módulo implementa ControlRecursive que orquesta el análisis completo
de algoritmos recursivos a partir del árbol sintáctico parseado.
"""

from typing import Dict, Any, Optional, List, Union
from lark import Tree as LarkTree

from app.controllers.control_algorithm import ControlAlgorithm
from backend.app.models.recursive.recursive import Recursive
from app.models.complexity import Complexity
from app.models.recurrence_method import RecurrenceMethods
from app.models.algorithm_pattern import AlgorithmPatterns
from app.models.tree import Tree as RecTree
from app.parsers.parser import TreeToDict


class ControlRecursive(ControlAlgorithm):
    """
    Controlador para el análisis de algoritmos recursivos.

    Funcionalidades:
    - Detecta casos base y recursivos
    - Extrae relaciones de recurrencia
    - Resuelve la recurrencia usando múltiples métodos
    - Calcula la profundidad de recursión
    - Construye árboles de recursión
    - Detecta patrones recursivos conocidos
    - Genera diagramas de flujo y árboles
    - Exporta resultados en múltiples formatos

    Attributes:
        base_cases (int): Número de casos base detectados
        recursion_depth (int): Profundidad máxima de recursión estimada
        recurrence_relation (str): Relación de recurrencia extraída
        complexity (Complexity): Objeto con análisis de complejidad
        algorithm (Recursive): Instancia del modelo Recursive
        recursive_calls (List[Dict]): Detalles de las llamadas recursivas
        base_case_details (List[Dict]): Detalles de los casos base
        pattern (Dict): Patrón algorítmico detectado
    """

    def __init__(self):
        """Inicializa el controlador recursivo."""
        super().__init__()  # Inicializa tree y complexity de la clase base
        self.base_cases: int = 0
        self.recursion_depth: int = 0
        self.recurrence_relation: str = ""
        self.algorithm: Optional[Recursive] = None
        self.base_case_details: List[Dict[str, Any]] = []
        self.pattern: Dict[str, Any] = {}
        self.recurrence_solver: Optional[RecurrenceMethods] = None
        # Almacena el árbol de recursión construido por el modelo
        self.recursion_tree = None

    def analyze(self, tree: LarkTree, **kwargs) -> None:
        """
        Implementación del método abstracto analyze.

        Analiza el algoritmo recursivo a partir del árbol sintáctico.
        Este método actúa como wrapper para analyze_from_parsed_tree.

        Args:
            tree: Árbol sintáctico parseado
            **kwargs: Puede incluir 'algorithm_name', 'pseudocode', 'structure'
        """
        algorithm_name = kwargs.get("algorithm_name", "UnknownAlgorithm")
        pseudocode = kwargs.get("pseudocode", "")
        structure = kwargs.get("structure", None)

        # Validar el árbol
        if not self._validate_tree(tree):
            raise ValueError("El árbol sintáctico proporcionado no es válido")

        # Almacenar el árbol en la clase base
        self.tree = tree

        # Realizar el análisis
        self.analyze_from_parsed_tree(
            algorithm_name=algorithm_name,
            pseudocode=pseudocode,
            parsed_tree=tree,
            structure=structure,
        )

    def analyze_from_parsed_tree(
        self,
        algorithm_name: str,
        pseudocode: str,
        parsed_tree: Optional[LarkTree] = None,
        structure: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Analiza un algoritmo recursivo a partir del árbol parseado.

        Este es el método principal que orquesta todo el análisis:
        1. Parsea el código si no se proporciona el árbol
        2. Crea instancia del modelo Recursive
        3. Extrae la relación de recurrencia
        4. Detecta casos base y llamadas recursivas
        5. Calcula la complejidad
        6. Resuelve la recurrencia con múltiples métodos
        7. Construye el árbol de recursión
        8. Detecta patrones
        9. Genera diagramas

        Args:
            algorithm_name: Nombre del algoritmo
            pseudocode: Código fuente en pseudocódigo
            parsed_tree: Árbol sintáctico pre-parseado (opcional)
            structure: Estructura dict pre-transformada (opcional)

        Returns:
            Dict con todos los resultados del análisis:
            {
                'algorithm': {nombre, tipo, código},
                'analysis': {casos_base, llamadas_recursivas, profundidad, relación},
                'complexity': {tiempo, espacio, notaciones},
                'recurrence_solutions': {métodos de resolución},
                'recursion_tree': {representación del árbol},
                'pattern': {patrón detectado},
                'diagrams': {diagramas generados},
                'summary': texto resumen,
                'optimizations': sugerencias
            }
        """
        # 1. Crear instancia del modelo Recursive
        self.algorithm = Recursive(algorithm_name, pseudocode)
        
        # 2. Parsear si es necesario
        if parsed_tree is None:
            try:
                self.algorithm.preprocess_code()
            except Exception as e:
                # Si falla el parsing, retornar análisis vacío
                return self._empty_analysis_result(f"Error al parsear: {str(e)}")

        # 3. Verificar que la estructura no esté vacía
        if not self.algorithm.structure or len(self.algorithm.structure) == 0:
            return self._empty_analysis_result("Estructura vacía o inválida")

        if structure is None:
            transformer = TreeToDict()
            structure = transformer.transform(parsed_tree)

        # 4. Extraer relación de recurrencia
        print(self.algorithm.structure)
        self.extract_recurrence()

        # 5. Detectar casos base y llamadas recursivas
        self.detect_base_cases()

        # 6. Calcular complejidad
        self.calculate_complexity()

        # 7. Resolver recurrencia con múltiples métodos
        solutions = self.solve_recurrence_with_methods()

        # 8. Construir árbol de recursión (se delega al modelo y se guarda)
        self.build_recursion_tree()

        # 9. Detectar patrón
        self.detect_pattern()

        # 10. Exportar resultados completos
        return self.export_results(solutions)

    def _empty_analysis_result(self, error_message: str = "") -> Dict[str, Any]:
        """
        Retorna un resultado de análisis vacío cuando no se puede analizar.
        
        Args:
            error_message: Mensaje de error opcional
            
        Returns:
            Dict con estructura de análisis vacía
        """
        return {
            "algorithm": {
                "name": self.algorithm.name if self.algorithm else "Unknown",
                "type": "Recursivo",
                "code": self.algorithm.pseudocode if self.algorithm else "",
                "language": "pseudocode",
            },
            "analysis": {
                "base_cases": 0,
                "base_case_details": [],
                "recursive_calls": 0,
                "recursive_call_details": [],
                "recursion_depth": 0,
                "recurrence_relation": "No disponible",
                "error": error_message,
            },
            "complexity": {
                "time": {
                    "worst_case": "No disponible",
                    "best_case": "No disponible",
                    "average_case": "No disponible",
                },
                "space": {
                    "worst_case": "No disponible",
                    "best_case": "No disponible",
                    "average_case": "No disponible",
                },
                "notation": {
                    "big_o": "",
                    "big_omega": "",
                    "big_theta": "",
                },
                "reasoning": error_message,
            },
        }

    def extract_recurrence(self) -> None:
        """
        Extrae la relación de recurrencia del algoritmo.

        Analiza el árbol sintáctico para encontrar:
        - Llamadas recursivas y sus argumentos
        - Patrones de reducción del problema (n/2, n-1, etc.)
        - Trabajo no recursivo (operaciones constantes, lineales, etc.)

        Args:
            structure: Estructura del código (dict, list o Tree)
        """
        if self.algorithm:
            self.recurrence_relation = self.algorithm.extract_recurrence()

    def detect_base_cases(self) -> None:
        """
        Detecta los casos base del algoritmo recursivo.

        Los casos base son condiciones que terminan la recursión,
        típicamente encontrados en estructuras if-return.

        Args:
            structure: Estructura del código
        """
        if self.algorithm:
            base_cases = self.algorithm.extract_base_case()
            self.base_cases = len(base_cases)
            self.base_case_details = base_cases

    def calculate_complexity(self) -> None:
        """
        Calcula la complejidad del algoritmo recursivo.

        Utiliza el modelo Recursive para estimar la complejidad
        basándose en la relación de recurrencia.
        """
        if self.algorithm:
            self.complexity = self.algorithm.estimate_complexity()

    def solve_recurrence(self, method: str) -> str:
        """
        Resuelve la recurrencia usando el método especificado.

        Este método es requerido por la interfaz ControlAlgorithm y actúa
        como wrapper para métodos específicos de resolución.

        Args:
            method: Método a utilizar ('substitution', 'master_theorem',
                   'recursion_tree', o 'all' para todos)

        Returns:
            String con la solución de la recurrencia
        """

        return f"Método desconocido: . Use: substitution, master_theorem, recursion_tree, o all"

    def solve_recurrence_with_methods(self) -> Dict[str, Any]:
        """
        Resuelve la recurrencia usando múltiples métodos.

        Returns:
            Dict con soluciones de cada método:
            {
                'substitution': resultado,
                'master_theorem': resultado,
                'recursion_tree': resultado
            }
        """
        solutions = {}

        if self.recurrence_relation:
            # Crear instancia del solver
            self.recurrence_solver = RecurrenceMethods(self.recurrence_relation)

            # Método de sustitución
            try:
                solutions["substitution"] = self.recurrence_solver.substitution_method()
            except Exception as e:
                solutions["substitution"] = f"No aplicable: {str(e)}"

            # Teorema maestro
            try:
                solutions["master_theorem"] = self.recurrence_solver.master_theorem()
            except Exception as e:
                solutions["master_theorem"] = f"No aplicable: {str(e)}"

            # Método del árbol de recursión
            try:
                solutions["recursion_tree_method"] = (
                    self.recurrence_solver.recursion_tree_method()
                )
            except Exception as e:
                solutions["recursion_tree_method"] = f"No aplicable: {str(e)}"

        return solutions

    def build_recursion_tree(self) -> None:
        """
        Construye la representación del árbol de recursión.
        """
        # Delegamos la construcción del árbol al modelo Recursive
        if self.algorithm:
            try:
                self.recursion_tree = self.algorithm.build_recursion_tree()
            except Exception:
                # En caso de error durante la construcción, mantener None
                self.recursion_tree = None

    def detect_pattern(self) -> None:
        """
        Detecta el patrón algorítmico recursivo.
        """
        if self.algorithm:
            pattern_detector = AlgorithmPatterns()

    def export_results(self, solutions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exporta todos los resultados del análisis.

        Args:
            solutions: Soluciones de la recurrencia

        Returns:
            Dict completo con todos los resultados
        """
        if not self.algorithm or not self.complexity:
            return {"error": "No se ha realizado el análisis"}

        return {
            "algorithm": {
                "name": self.algorithm.name,
                "type": "Recursivo",
                "code": self.algorithm.pseudocode,
                "language": "pseudocode",
            },
            "analysis": {
                "base_cases": self.base_cases,
                "base_case_details": self.base_case_details,
                "recursive_calls": self.algorithm.recursive_calls,
                "recursive_call_details": self.algorithm.recursive_call_nodes,
                "recursion_depth": self.recursion_depth,
                "recurrence_relation": self.recurrence_relation,
            },
            "recursion_summary": {
                "total_base_cases": self.base_cases,
                "total_recursive_calls": self.algorithm.recursive_calls,
                "recurrence_relation": self.recurrence_relation,
                "estimated_depth": str(self.recursion_depth),
                "base_cases_found": [
                    {
                        "condition": base.get('condition', 'N/A'),
                        "return_value": base.get('return_value', 'N/A'),
                        "line": base.get('line', 'N/A')
                    }
                    for base in self.base_case_details
                ],
                "recursive_calls_found": [
                    {
                        "function": call.get('function', 'N/A'),
                        "pattern": call.get('pattern', 'N/A'),
                        "depth": call.get('depth', 0),
                        "arguments": call.get('arguments', [])
                    }
                    for call in self.algorithm.recursive_call_nodes
                ]
            },
            "complexity": {
                "time": {
                    "worst_case": self.complexity.worst_case,
                    "best_case": self.complexity.best_case,
                    "average_case": self.complexity.average_case,
                },
                "space": {
                    "worst_case": self.complexity.space_complexity,
                    "best_case": getattr(self.complexity, "best_case", ""),
                    "average_case": getattr(self.complexity, "average_case", ""),
                },
                "notation": {
                    "big_o": getattr(self.complexity, "big_o", ""),
                    "big_omega": getattr(self.complexity, "big_omega", ""),
                    "big_theta": getattr(self.complexity, "big_theta", ""),
                },
                "reasoning": getattr(self.complexity, "reasoning", ""),
            },
            "recurrence_solutions": solutions,
            "Tree_diagram": self.recursion_tree
        }

    def _generate_summary(self) -> str:
        """Genera un resumen textual del análisis."""
        summary = f"Análisis de Algoritmo Recursivo\n"
        summary += f"{'=' * 40}\n\n"

        if self.algorithm:
            summary += f"Algoritmo: {self.algorithm.name}\n"

        summary += f"Casos Base: {self.base_cases}\n"
        summary += f"Llamadas Recursivas: {self.algorithm.recursive_calls if self.algorithm else 0}\n"
        summary += f"Relación de Recurrencia: {self.recurrence_relation}\n"
        summary += f"Profundidad de Recursión: {self.recursion_depth}\n\n"

        if self.complexity:
            summary += (
                f"Complejidad Temporal (Peor Caso): {self.complexity.worst_case}\n"
            )
            summary += f"Complejidad Espacial: {self.complexity.space_complexity}\n\n"

        if self.pattern:
            summary += f"Patrón Detectado: {self.pattern.get('name', 'Desconocido')}\n"

        return summary

    def _suggest_optimizations(self) -> List[str]:
        """Genera sugerencias de optimización."""
        suggestions = []

        if not self.algorithm:
            return suggestions

        # Memoización para recursión con subproblemas repetidos
        if "T(n-1) + T(n-2)" in self.recurrence_relation:
            suggestions.append(
                "⚡ Usar memoización o programación dinámica para evitar "
                "recalcular subproblemas (ej: Fibonacci)"
            )

        # Tail recursion
        if self.base_cases > 0 and self.algorithm.recursive_calls == 1:
            suggestions.append(
                "🔄 Considerar optimización de tail recursion "
                "(convertir a iterativo si el lenguaje no optimiza)"
            )

        # Profundidad alta
        if isinstance(self.recursion_depth, str) and "n" in self.recursion_depth:
            suggestions.append(
                "⚠️ Profundidad de recursión O(n) puede causar stack overflow "
                "con entradas grandes. Considerar versión iterativa."
            )

        # Divide y conquista sin combinar
        if self.algorithm.recursive_calls > 1 and "divide" in str(self.pattern).lower():
            suggestions.append(
                "✅ Algoritmo divide y conquista eficiente. "
                "Asegurar que la fase de combinación sea óptima."
            )

        return suggestions

    def get_complexity_report(self, format: str = "text") -> str:
        """
        Obtiene el reporte de complejidad en el formato especificado.

        Args:
            format: 'text', 'json' o 'markdown'

        Returns:
            String con el reporte formateado
        """
        if not self.complexity:
            return "No hay análisis de complejidad disponible"

        if format == "json":
            import json

            return json.dumps(
                {
                    "time_complexity": {
                        "worst_case": self.complexity.worst_case,
                        "best_case": self.complexity.best_case,
                        "average_case": self.complexity.average_case,
                    },
                    "space_complexity": self.complexity.space_complexity,
                    "recurrence": self.recurrence_relation,
                    "recursion_depth": str(self.recursion_depth),
                },
                indent=2,
            )

        elif format == "markdown":
            md = "# Análisis de Complejidad - Recursivo\n\n"
            md += f"## Complejidad Temporal\n"
            md += f"- **Peor Caso**: `{self.complexity.worst_case}`\n"
            md += f"- **Mejor Caso**: `{self.complexity.best_case}`\n"
            md += f"- **Caso Promedio**: `{self.complexity.average_case}`\n\n"
            md += f"## Complejidad Espacial\n"
            md += f"- **Peor Caso**: `{self.complexity.space_complexity}`\n\n"
            md += f"## Recursión\n"
            md += f"- **Relación**: `{self.recurrence_relation}`\n"
            md += f"- **Profundidad**: `{self.recursion_depth}`\n"
            md += f"- **Casos Base**: {self.base_cases}\n"
            md += f"- **Llamadas Recursivas**: {self.algorithm.recursive_calls if self.algorithm else 0}\n"
            return md

        else:  # text
            report = "=" * 50 + "\n"
            report += "  ANÁLISIS DE COMPLEJIDAD - RECURSIVO\n"
            report += "=" * 50 + "\n\n"
            report += (
                f"Complejidad Temporal (Peor Caso): {self.complexity.worst_case}\n"
            )
            report += (
                f"Complejidad Temporal (Mejor Caso): {self.complexity.best_case}\n"
            )
            report += f"Complejidad Espacial: {self.complexity.space_complexity}\n"
            report += f"\nRelación de Recurrencia: {self.recurrence_relation}\n"
            report += f"Profundidad de Recursión: {self.recursion_depth}\n"
            report += f"Casos Base: {self.base_cases}\n"
            report += f"Llamadas Recursivas: {self.algorithm.recursive_calls if self.algorithm else 0}\n"
            return report

    def get_recursion_summary(self) -> str:
        """
        Obtiene un resumen detallado de la recursión.

        Returns:
            String con el resumen de la estructura recursiva
        """
        summary = "\n" + "=" * 60 + "\n"
        summary += "  RESUMEN DE ESTRUCTURA RECURSIVA\n"
        summary += "=" * 60 + "\n\n"

        if not self.algorithm:
            return summary + "No hay algoritmo analizado\n"

        summary += f"Total de casos base: {self.base_cases}\n"
        summary += f"Total de llamadas recursivas: {self.algorithm.recursive_calls}\n"
        summary += f"Relación de recurrencia: {self.recurrence_relation}\n"
        summary += f"Profundidad estimada: {self.recursion_depth}\n\n"

        # Detalles de casos base
        if self.base_case_details:
            summary += "--- Casos Base Detectados ---\n"
            for i, base in enumerate(self.base_case_details, 1):
                summary += f"  {i}. Condición: {base.get('condition', 'N/A')}\n"
                summary += f"     Retorno: {base.get('return_value', 'N/A')}\n"

        # Detalles de llamadas recursivas
        if self.algorithm.recursive_calls:
            summary += "\n--- Llamadas Recursivas ---\n"
            for i, call in enumerate(self.algorithm.recursive_call_nodes, 1):
                summary += f"  {i}. Función: {call.get('function', 'N/A')}\n"
                summary += f"     Patrón: {call.get('pattern', 'N/A')}\n"
                summary += f"     Profundidad: {call.get('depth', 0)}\n"

        return summary

    def reset(self) -> None:
        """
        Reinicia el estado del controlador.

        Implementación del método abstracto que limpia todos los datos
        del análisis previo, incluyendo los atributos de la clase base.
        """
        # Reiniciar atributos de la clase base
        self.tree = None
        self.complexity = None

        # Reiniciar atributos específicos de ControlRecursive
        self.base_cases = 0
        self.recursion_depth = 0
        self.recurrence_relation = ""
        self.algorithm = None
        self.base_case_details = []
        self.pattern = {}
        self.recurrence_solver = None
        self.recursion_tree = None
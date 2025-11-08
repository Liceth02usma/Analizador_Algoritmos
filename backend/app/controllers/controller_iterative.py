"""
Controlador para el análisis de algoritmos iterativos.
Actúa como puente entre el parser Lark y los modelos de análisis.
"""

from typing import Dict, Any, List, Optional, Union
from lark import Tree as LarkTree

from app.controllers.control_algorithm import ControlAlgorithm
from app.models.iterative import Iterative
from app.models.complexity import Complexity
from app.models.flowdiagram import FlowDiagram
from app.models.algorithm_pattern import AlgorithmPatterns


class ControlIterative(ControlAlgorithm):
    """
    Controlador para análisis de algoritmos iterativos.

    Hereda de ControlAlgorithm e implementa la lógica específica para
    detectar y analizar ciclos (for, while, repeat) en algoritmos iterativos.

    Gestiona la detección de ciclos, cálculo de complejidad y exportación de resultados.
    """

    def __init__(self):
        """Inicializa el controlador iterativo."""
        super().__init__()  # Inicializa tree y complexity de la clase base
        self.algorithm: Optional[Iterative] = None
        self.pattern: Optional[AlgorithmPatterns] = None

    def analyze(self, tree: LarkTree, **kwargs) -> None:
        """
        Implementación del método abstracto analyze.

        Analiza el algoritmo iterativo a partir del árbol sintáctico.
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
        structure: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Analiza un algoritmo iterativo a partir del árbol parseado.

        Args:
            algorithm_name: Nombre del algoritmo
            pseudocode: Pseudocódigo original
            parsed_tree: Árbol de Lark (opcional)
            structure: Estructura AST transformada (opcional)

        Returns:
            Diccionario con los resultados del análisis
        """
        # Crear instancia del algoritmo iterativo
        self.algorithm = Iterative(algorithm_name, pseudocode)

        # Si se proporciona estructura ya parseada, usarla
        if structure is not None:
            self.algorithm.structure = structure
            self.algorithm.parsed_tree = parsed_tree
        else:
            # Si no, parsear el pseudocódigo
            self.algorithm.preprocess_code()


        print("Estructura generada por lark: ",self.algorithm.structure)
        print("Tokens de lark: ",self.algorithm.tokens)
        # Detectar ciclos en el algoritmo
        self.algorithm.detect_loops()

        # Calcular complejidad
        self.complexity = self.calculate_complexity()

        # Identificar patrón algorítmico
        self.pattern = self.algorithm.identify_pattern()

        # Exportar resultados
        return self.export_results()




    def calculate_complexity(self) -> Complexity:
        """
        Calcula la complejidad temporal y espacial del algoritmo iterativo.

        Returns:
            Objeto Complexity con el análisis completo
        """
        if not self.algorithm:
            raise ValueError(
                "No hay algoritmo para analizar. Llame primero a analyze_from_parsed_tree()"
            )

        # Usar el método del modelo Iterative (que ahora delega a Complexity)
        complexity = self.algorithm.estimate_complexity()

        # Ya no es necesario agregar información adicional aquí
        # porque compute_from_loops() ya lo hace

        self.complexity = complexity
        return complexity

    def export_results(self) -> Dict[str, Any]:
        """
        Exporta los resultados del análisis en formato de diccionario.

        Returns:
            Diccionario con todos los resultados del análisis
        """
        if not self.algorithm or not self.complexity:
            return {
                "error": "No se ha realizado el análisis. Llame primero a analyze_from_parsed_tree()"
            }

        # Generar diagrama de flujo
        try:
            flow_diagram = self.algorithm.generate_flow_diagram()
            diagram_mermaid = flow_diagram.export_diagram("mermaid")
            diagram_text = flow_diagram.export_diagram("text")
        except Exception as e:
            diagram_mermaid = f"Error al generar diagrama: {str(e)}"
            diagram_text = f"Error al generar diagrama: {str(e)}"

        # Construir resultado completo
        result = {
            "algorithm": {
                "name": self.algorithm.name,
                "type": self.algorithm.type,
                "pseudocode": self.algorithm.pseudocode,
            },
            "analysis": {
                "loops_detected": len(self.algorithm.loop_details),
                "nested_levels": self.algorithm.nested_loops,
                "loop_details": self.algorithm.loop_details,
                "operations_per_loop": self.algorithm.operations_per_loop,
            },
            "complexity": {
                "time": {
                    "best_case": self.complexity.best_case,
                    "worst_case": self.complexity.worst_case,
                    "average_case": self.complexity.average_case,
                    "dominant": self.complexity.time_complexity,
                },
                "space": self.complexity.space_complexity,
                "reasoning": self.complexity.reasoning,
            },
            "pattern": {
                "name": self.pattern.pattern_name if self.pattern else "No detectado",
                "description": self.pattern.description if self.pattern else "",
                "complexity_hint": self.pattern.complexity_hint if self.pattern else "",
                "examples": self.pattern.examples if self.pattern else [],
            },
            "diagrams": {
                "flowchart_mermaid": diagram_mermaid,
                "flowchart_text": diagram_text,
            },
            "summary": self.algorithm.summarize_analysis(),
        }

        # Agregar sugerencias de optimización si hay patrón detectado
        if self.pattern:
            try:
                result["optimizations"] = self.pattern.suggest_optimization_strategies()
            except Exception:
                result["optimizations"] = []

        return result

    def get_complexity_report(self, format: str = "text") -> str:
        """
        Genera un reporte de complejidad en el formato especificado.

        Args:
            format: Formato del reporte ('text', 'json', 'markdown')

        Returns:
            String con el reporte formateado
        """
        if not self.complexity:
            return "No hay análisis de complejidad disponible."

        return self.complexity.export_report(format)

    def get_loop_summary(self) -> str:
        """
        Genera un resumen textual de los ciclos detectados.

        Returns:
            String con el resumen de ciclos
        """
        if not self.loop_details:
            return "No se detectaron ciclos en el algoritmo."

        summary = []
        summary.append(f"=== Resumen de Ciclos ===\n")
        summary.append(f"Total de ciclos: {self.loops_detected}")
        summary.append(f"Nivel máximo de anidamiento: {self.nested_levels}\n")

        # Agrupar por nivel
        by_level: Dict[int, List[Dict]] = {}
        for loop in self.loop_details:
            level = loop["depth"]
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(loop)

        # Mostrar por nivel
        for level in sorted(by_level.keys()):
            summary.append(f"\nNivel {level}:")
            for loop in by_level[level]:
                summary.append(f"  - {loop['type'].upper()}")
                if loop["type"] == "for":
                    summary.append(f"    Variable: {loop['variable']}")
                    summary.append(f"    Rango: {loop['from']} hasta {loop['to']}")
                else:
                    summary.append(f"    Condición: {loop['condition']}")

        return "\n".join(summary)

    def reset(self) -> None:
        """
        Reinicia el estado del controlador.

        Implementación del método abstracto que limpia todos los datos
        del análisis previo, incluyendo los atributos de la clase base.
        """
        # Reiniciar atributos de la clase base
        self.tree = None
        self.complexity = None

        # Reiniciar atributos específicos de ControlIterative
        self.nested_levels = 0
        self.algorithm = None
        self.loop_details = []
        self.pattern = None

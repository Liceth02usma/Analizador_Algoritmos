from typing import Dict, Any, Optional
from lark import Tree as LarkTree

from app.controllers.control_algorithm import ControlAlgorithm
from ..models.iterative.iterative import Iterative
from ..models.complexity import Complexity
from app.models.algorithm_pattern import AlgorithmPatterns


class ControlIterative(ControlAlgorithm):

    def __init__(self):
        """Inicializa el controlador iterativo."""
        super().__init__()
        self.algorithm: Optional[Iterative] = None
        self.pattern: Optional[AlgorithmPatterns] = None

    def analyze(self, tree: LarkTree, **kwargs) -> None:

        algorithm_name = kwargs.get("algorithm_name", "UnknownAlgorithm")
        pseudocode = kwargs.get("pseudocode", "")
        structure = kwargs.get("structure", None)

        # Analizar que tipo de algoritmo es para ver si tiene MEJOR PEOR o PROMEDIO o si no APLICA (implementar Alghoritm pattern de models)

        self.tree = tree

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

        self.algorithm = Iterative(algorithm_name, pseudocode)

        if structure is not None:
            self.algorithm.structure = structure
            self.algorithm.parsed_tree = parsed_tree
        else:

            self.algorithm.preprocess_code()

        self.algorithm.detect_loops()

        self.calculate_complexity()

        self.pattern = self.algorithm.identify_pattern()

        return self.export_results()

    def calculate_complexity(self) -> Complexity:
        pass

    def export_results(self) -> Dict[str, Any]:

        flow_diagram = self.algorithm.generate_flow_diagram()

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
                    "best_case": None,
                    "worst_case": None,
                    "average_case": None,
                    "dominant": None,
                },
                "space": None,
                "reasoning": None,
            },
            "pattern": {
                "name": "No detectado",
                "description": "",
                "complexity_hint": "",
            },
            "diagrams": {
                "flowDiagram": flow_diagram,
            },
        }

        return result

    def reset(self) -> None:
        """
        Reinicia el estado del controlador.

        Implementación del método abstracto que limpia todos los datos
        del análisis previo, incluyendo los atributos de la clase base.
        """

        self.tree = None
        self.complexity = None

        self.nested_levels = 0
        self.algorithm = None
        self.loop_details = []
        self.pattern = None

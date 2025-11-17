"""
Controlador para el análisis de algoritmos recursivos.

Este módulo implementa ControlRecursive que orquesta el análisis completo
de algoritmos recursivos a partir del árbol sintáctico parseado.
"""

from typing import Dict, Any, Optional, List, Union
from lark import Tree as LarkTree

from app.controllers.control_algorithm import ControlAlgorithm
from ..models.recursive.recursive import Recursive


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
        self.recurrence_solver = None
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

        # Realizar el análisis
        solution = self.analyze_from_parsed_tree(
            algorithm_name=algorithm_name,
            pseudocode=pseudocode,
            parsed_tree=tree,
            structure=structure,
        )
        print(solution)

    def analyze_from_parsed_tree(
        self,
        algorithm_name: str,
        pseudocode: str,
        parsed_tree: Optional[LarkTree] = None,
        structure: Optional[Dict] = None,
    ) -> Dict[str, Any]:

        # 1. Crear instancia del modelo Recursive
        self.algorithm = Recursive(algorithm_name, pseudocode, True)
        
        # 2. Parsear si es necesario
        self.algorithm.preprocess_code()



        # 4. Extraer relación de recurrencia
        # 5. Detectar casos base y llamadas recursivas
        self.detect_base_cases()
        self.algorithm.extract_recurrence()
        result = self.get_recurrence_solver()
        # 10. Exportar resultados completos
        return result
    

    def get_recurrence_solver(self) -> None:
        """
        Obtiene las soluciones de la relación de recurrencia
        utilizando el agente RecurrenceAnalysis.
        """
        if self.algorithm:
            return self.algorithm.get_analysis_recurrence()


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



    def export_results(self) -> Dict[str, Any]:
        """
        Exporta todos los resultados del análisis.

        Args:
            solutions: Soluciones de la recurrencia

        Returns:
            Dict completo con todos los resultados
        """
        pass
    
    def calculate_complexity(self):
        """
        Calcula la complejidad del algoritmo analizado.
        
        Debe implementar la lógica específica para calcular las complejidades
        temporal y espacial según el tipo de algoritmo.
        
        Returns:
            Complexity: Objeto con análisis de complejidad completo
        
        Raises:
            NotImplementedError: Si no se implementa en la clase derivada
        """
        pass

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
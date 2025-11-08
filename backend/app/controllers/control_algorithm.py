from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from lark import Tree

from ..models.complexity import Complexity


class ControlAlgorithm(ABC):
    """
    Clase abstracta base para controladores de análisis de algoritmos.
    
    Define la interfaz común que todos los controladores deben implementar,
    siguiendo el patrón Template Method para el análisis de algoritmos.
    
    Attributes:
        tree (Optional[Tree]): Árbol sintáctico parseado del algoritmo
        complexity (Optional[Complexity]): Objeto con análisis de complejidad
    """
    
    def __init__(self):
        """Inicializa el controlador base."""
        self.tree: Optional[Tree] = None
        self.complexity: Optional[Complexity] = None
    
    @abstractmethod
    def analyze(self, tree: Tree, **kwargs) -> None:
        """
        Analiza el algoritmo a partir del árbol sintáctico.
        
        Este método debe ser implementado por cada controlador específico
        para realizar el análisis apropiado según el tipo de algoritmo.
        
        Args:
            tree: Árbol sintáctico del código parseado
            **kwargs: Argumentos adicionales específicos del controlador
        
        Raises:
            NotImplementedError: Si no se implementa en la clase derivada
        """
        pass
    
    @abstractmethod
    def calculate_complexity(self) -> Complexity:
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
    
    @abstractmethod
    def export_results(self) -> Dict[str, Any]:
        """
        Exporta los resultados del análisis en formato diccionario.
        
        Debe retornar un diccionario con toda la información del análisis
        incluyendo complejidad, patrones, diagramas y sugerencias.
        
        Returns:
            Dict con todos los resultados del análisis
        
        Raises:
            NotImplementedError: Si no se implementa en la clase derivada
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """
        Reinicia el estado del controlador.
        
        Limpia todos los datos del análisis previo para permitir un nuevo análisis.
        
        Raises:
            NotImplementedError: Si no se implementa en la clase derivada
        """
        pass

"""
Clase abstracta base para todos los controladores de análisis de algoritmos.

Este módulo define la interfaz común que deben implementar todos los
controladores de análisis (iterativo, recursivo, etc.).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from lark import Tree

from app.models.complexity import Complexity


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
    
    def get_complexity_report(self, format: str = "text") -> str:
        """
        Obtiene un reporte de complejidad en el formato especificado.
        
        Método de plantilla que puede ser sobrescrito por las clases derivadas
        para proporcionar reportes personalizados.
        
        Args:
            format: Formato del reporte ('text', 'json', 'markdown')
        
        Returns:
            String con el reporte formateado
        """
        if not self.complexity:
            return "No hay análisis de complejidad disponible"
        
        if format == "json":
            import json
            return json.dumps({
                'time_complexity': {
                    'worst_case': self.complexity.time_complexity.worst_case,
                    'best_case': self.complexity.time_complexity.best_case,
                    'average_case': self.complexity.time_complexity.average_case
                },
                'space_complexity': {
                    'worst_case': self.complexity.space_complexity.worst_case,
                    'best_case': self.complexity.space_complexity.best_case
                }
            }, indent=2)
        
        elif format == "markdown":
            md = "# Análisis de Complejidad\n\n"
            md += f"## Complejidad Temporal\n"
            md += f"- **Peor Caso**: `{self.complexity.time_complexity.worst_case}`\n"
            md += f"- **Mejor Caso**: `{self.complexity.time_complexity.best_case}`\n"
            md += f"- **Caso Promedio**: `{self.complexity.time_complexity.average_case}`\n\n"
            md += f"## Complejidad Espacial\n"
            md += f"- **Peor Caso**: `{self.complexity.space_complexity.worst_case}`\n"
            return md
        
        else:  # text
            report = "=" * 50 + "\n"
            report += "  ANÁLISIS DE COMPLEJIDAD\n"
            report += "=" * 50 + "\n\n"
            report += f"Complejidad Temporal (Peor Caso): {self.complexity.time_complexity.worst_case}\n"
            report += f"Complejidad Temporal (Mejor Caso): {self.complexity.time_complexity.best_case}\n"
            report += f"Complejidad Espacial: {self.complexity.space_complexity.worst_case}\n"
            return report
    
    def _validate_tree(self, tree: Tree) -> bool:
        """
        Valida que el árbol sintáctico sea válido.
        
        Args:
            tree: Árbol sintáctico a validar
        
        Returns:
            True si el árbol es válido, False en caso contrario
        """
        return tree is not None and isinstance(tree, Tree)
    
    def __str__(self) -> str:
        """Representación en string del controlador."""
        return f"{self.__class__.__name__}(complexity={self.complexity})"
    
    def __repr__(self) -> str:
        """Representación técnica del controlador."""
        return f"{self.__class__.__name__}(tree={self.tree is not None}, complexity={self.complexity is not None})"

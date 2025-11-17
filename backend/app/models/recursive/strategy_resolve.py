from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class RecurrenceStrategy(ABC):
    """Interfaz abstracta para estrategias de resolución de recurrencias.
    
    Define el contrato que deben cumplir todas las estrategias concretas
    de resolución de ecuaciones de recurrencia.
    
    Attributes:
        name (str): Nombre identificador de la estrategia
        description (str): Descripción breve del método
    """
    
    def __init__(self):
        self.name: str = ""
        self.description: str = ""
    
    
    @abstractmethod
    def solve(self, recurrenceEquation: str) -> Dict[str, Any]:
        """Resuelve la ecuación de recurrencia usando esta estrategia.
        
        Args:
            recurrenceEquation: Ecuación de recurrencia en formato string (ej: "T(n) = 2T(n/2) + n")
            
        Returns:
            Diccionario con la solución:
            {
                'complexity': str,           # Complejidad resultante (ej: 'O(n log n)')
                'steps': List[str],          # Pasos de la resolución
                'explanation': str,          # Explicación del proceso
                'applicable': bool,          # Si el método fue aplicable
                'method': str                # Nombre del método usado
            }
            
        Raises:
            ValueError: Si la recurrencia no puede ser resuelta por esta estrategia
        """
        pass
    


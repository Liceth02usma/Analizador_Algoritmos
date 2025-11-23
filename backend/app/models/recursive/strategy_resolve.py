from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class RecurrenceSolution(BaseModel):
    """Formato unificado de salida para las estrategias de recurrencia.

    Campos principales pensados para cubrir los distintos agentes:
    - `complexity`: resultado en notación Big-O (cuando aplique)
    - `steps`: lista de pasos legibles que describen la resolución
    - `explanation` / `detailed_explanation`: explicación textual completa
    - `applicable`: si la estrategia fue aplicable
    - `method`: nombre del método usado (ej: 'Teorema Maestro')
    - `details`: diccionario libre para información específica (árboles, raíces, etc.)
    """

    complexity: Optional[str] = None
    steps: Optional[List[str]] = None
    explanation: Optional[str] = None
    detailed_explanation: Optional[str] = None
    applicable: bool = True
    method: Optional[str] = None
    details: Dict[str, Any] = {}


class RecurrenceStrategy(ABC):
    """Interfaz abstracta para estrategias de resolución de recurrencias.

    Todas las estrategias concretas deben implementar `solve` y devolver
    un `RecurrenceSolution` (o un dict convertible a dicho modelo).
    """

    def __init__(self):
        self.name: str = ""
        self.description: str = ""

    @abstractmethod
    def solve(self, recurrenceEquation: str) -> RecurrenceSolution:
        """Resuelve la ecuación de recurrencia y retorna un `RecurrenceSolution`.

        Args:
            recurrenceEquation: Ecuación de recurrencia en formato string

        Returns:
            RecurrenceSolution

        Raises:
            ValueError: Si la recurrencia no puede ser resuelta por esta estrategia
        """
        raise NotImplementedError()
    


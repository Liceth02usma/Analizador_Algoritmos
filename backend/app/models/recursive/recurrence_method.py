"""
Módulo: recurrence_method

Cliente del patrón Strategy para resolver ecuaciones de recurrencia.
Permite seleccionar y cambiar dinámicamente entre diferentes estrategias
de resolución.
"""

from enum import Enum
from typing import Dict, Any, Optional

from .equation_characteristic import CharacteristicEquationStrategy
from .strategy_resolve import RecurrenceStrategy, RecurrenceSolution
from .master_theorem import MasterTheoremStrategy
from .tree_method import TreeMethodStrategy
from .intelligent_substitution import IntelligentSubstitutionStrategy
from .none_strategy import NoneStrategy


class StrategyType(Enum):
    """Enumeración de estrategias disponibles para resolver recurrencias."""

    TREE_METHOD = "tree_method"
    EQUATION_CHARACTERISTICS = "equation_characteristics"
    MASTER_THEOREM = "master_theorem"
    INTELLIGENT_SUBSTITUTION = "intelligent_substitution"
    NONE = "none"


class RecurrenceMethods:
    """Cliente del patrón Strategy para resolver ecuaciones de recurrencia.

    Esta clase actúa como contexto que mantiene una referencia a una estrategia
    de resolución y delega el trabajo a ella. Permite cambiar la estrategia
    en tiempo de ejecución.

    Attributes:
        recurrence: Ecuación de recurrencia a resolver
        _strategy: Estrategia actual de resolución
        _strategies: Diccionario de estrategias disponibles

    Example:
        >>> solver = RecurrenceMethods("T(n) = 2T(n/2) + n")
        >>> solver.set_strategy(StrategyType.MASTER_THEOREM)
        >>> result = solver.solve()
        >>> print(result['complexity'])
        'O(n log n)'
    """

    def __init__(self, recurrence: str, strategy: Optional[RecurrenceStrategy] = None):
        """Inicializa el solver con una ecuación de recurrencia.

        Args:
            recurrence: Ecuación de recurrencia en formato string (ej: "T(n) = 2T(n/2) + n")
            strategy: Estrategia inicial (opcional). Si no se proporciona, debe
                     configurarse antes de resolver.
        """
        self.recurrence: str = recurrence
        self._strategy: Optional[RecurrenceStrategy] = strategy

        # Inicializar estrategias disponibles
        self._strategies: Dict[StrategyType, RecurrenceStrategy] = {
            StrategyType.EQUATION_CHARACTERISTICS: CharacteristicEquationStrategy(),
            StrategyType.TREE_METHOD: TreeMethodStrategy(),
            StrategyType.MASTER_THEOREM: MasterTheoremStrategy(),
            StrategyType.INTELLIGENT_SUBSTITUTION: IntelligentSubstitutionStrategy(),
            StrategyType.NONE: NoneStrategy(),
        }

    def set_strategy(self, strategy_type: StrategyType) -> None:
        """Establece la estrategia de resolución usando el tipo enumerado.

        Args:
            strategy_type: Tipo de estrategia del enum StrategyType

        Raises:
            ValueError: Si el tipo de estrategia no existe
        """
        if strategy_type not in self._strategies:
            raise ValueError(f"Estrategia {strategy_type} no está disponible")

        self._strategy = self._strategies[strategy_type]

    def set_custom_strategy(self, strategy: RecurrenceStrategy) -> None:
        """Establece una estrategia personalizada.

        Args:
            strategy: Instancia de una estrategia concreta que implementa RecurrenceStrategy
        """
        self._strategy = strategy

    def solve(self) -> RecurrenceSolution:
        """Resuelve la ecuación de recurrencia usando la estrategia actual.

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
            ValueError: Si no hay estrategia configurada
        """
        if self._strategy is None:
            raise ValueError(
                "No se ha configurado ninguna estrategia. "
                "Use set_strategy() primero."
            )

        result = self._strategy.solve(self.recurrence)

        # Normalizar a RecurrenceSolution
        if isinstance(result, RecurrenceSolution):
            return result

        # Si la estrategia retorna un dict convertible, construir el modelo
        if isinstance(result, dict):
            return RecurrenceSolution(
                complexity=result.get("complexity"),
                steps=result.get("steps"),
                explanation=result.get("explanation")
                or result.get("detailed_explanation"),
                applicable=result.get("applicable", True),
                method=result.get("method") or getattr(self._strategy, "name", None),
                details=result,
            )

        # Si no es ninguno de los anteriores, intentar construir directamente
        try:
            return RecurrenceSolution(**result)  # type: ignore[arg-type]
        except Exception as e:
            raise ValueError(f"Resultado de la estrategia no convertible: {e}")

    def get_current_strategy(self) -> Optional[str]:
        """Retorna el nombre de la estrategia actual.

        Returns:
            Nombre de la estrategia o None si no hay ninguna configurada
        """
        return self._strategy.name if self._strategy else None

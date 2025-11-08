import os

from dotenv import load_dotenv

load_dotenv()

from app.external_services.Agentes.Agent import AgentBase
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool


# ============================================================================
# SCHEMAS DE DATOS
# ============================================================================


class TreeNode(BaseModel):
    """Representa un nodo en el árbol"""

    value: Any = Field(description="Valor del nodo")
    level: int = Field(description="Nivel en el árbol (0 = raíz)")
    position: int = Field(description="Posición en su nivel (0-indexed)")
    children_indices: List[int] = Field(
        default_factory=list,
        description="Índices de los nodos hijos en la lista de nodos",
    )


class AlgorithmContext(BaseModel):
    """Contexto de entrada para el análisis del algoritmo"""

    algorithm_name: str = Field(
        description="Nombre del algoritmo (ej: quicksort, mergesort, heapsort)"
    )
    array_size: int = Field(
        default=7,
        description="Tamaño del arreglo para el ejemplo (por defecto 7 elementos)",
    )
    additional_info: Optional[str] = Field(
        default=None,
        description="Información adicional sobre el algoritmo o configuración especial",
    )


class BestCaseResponse(BaseModel):
    """Formato de respuesta estructurada del agente"""

    algorithm_name: str = Field(description="Nombre del algoritmo analizado")
    best_case_description: str = Field(
        description="Descripción detallada del mejor caso del algoritmo"
    )
    time_complexity: str = Field(
        description="Complejidad temporal del mejor caso (notación Big-O)"
    )
    space_complexity: str = Field(description="Complejidad espacial")
    tree_structure: List[TreeNode] = Field(
        description="Lista de nodos que representan el árbol del mejor caso"
    )
    explanation: str = Field(
        description="Explicación de por qué esta estructura representa el mejor caso"
    )
    visualization_notes: str = Field(
        description="Notas sobre cómo visualizar o interpretar el árbol"
    )


# ============================================================================
# HERRAMIENTAS
# ============================================================================


@tool
def get_algorithm_info(algorithm_name: str) -> Dict[str, str]:
    """
    Obtiene información básica sobre un algoritmo de ordenamiento o búsqueda.

    Args:
        algorithm_name: Nombre del algoritmo

    Returns:
        Diccionario con información del algoritmo
    """
    algorithms_db = {
        "quicksort": {
            "type": "ordenamiento",
            "best_case": "Pivote siempre divide el arreglo en dos mitades iguales",
            "best_complexity": "O(n log n)",
            "worst_case": "Pivote siempre es el elemento más pequeño o más grande",
            "worst_complexity": "O(n²)",
        },
        "mergesort": {
            "type": "ordenamiento",
            "best_case": "Siempre divide el arreglo en dos mitades iguales",
            "best_complexity": "O(n log n)",
            "worst_case": "Igual que el mejor caso",
            "worst_complexity": "O(n log n)",
        },
        "heapsort": {
            "type": "ordenamiento",
            "best_case": "Construcción del heap y extracción de elementos",
            "best_complexity": "O(n log n)",
            "worst_case": "Igual que el mejor caso",
            "worst_complexity": "O(n log n)",
        },
        "binary_search": {
            "type": "búsqueda",
            "best_case": "Elemento buscado está en el medio del arreglo",
            "best_complexity": "O(1)",
            "worst_case": "Elemento no está o está en los extremos",
            "worst_complexity": "O(log n)",
        },
        "bubble_sort": {
            "type": "ordenamiento",
            "best_case": "Arreglo ya está ordenado",
            "best_complexity": "O(n)",
            "worst_case": "Arreglo en orden inverso",
            "worst_complexity": "O(n²)",
        },
        "insertion_sort": {
            "type": "ordenamiento",
            "best_case": "Arreglo ya está ordenado",
            "best_complexity": "O(n)",
            "worst_case": "Arreglo en orden inverso",
            "worst_complexity": "O(n²)",
        },
    }

    algo_lower = algorithm_name.lower().replace(" ", "_")
    return algorithms_db.get(
        algo_lower,
        {
            "type": "desconocido",
            "best_case": "Información no disponible",
            "best_complexity": "Consultar documentación",
            "worst_case": "Información no disponible",
            "worst_complexity": "Consultar documentación",
        },
    )


@tool
def calculate_tree_levels(array_size: int, branching_factor: int = 2) -> Dict[str, int]:
    """
    Calcula los niveles necesarios para un árbol basado en el tamaño del arreglo.

    Args:
        array_size: Tamaño del arreglo
        branching_factor: Factor de ramificación del árbol (por defecto 2 para árboles binarios)

    Returns:
        Diccionario con información sobre los niveles del árbol
    """
    import math

    levels = math.ceil(math.log(array_size, branching_factor)) if array_size > 1 else 1
    total_nodes = sum(branching_factor**i for i in range(levels))

    return {
        "levels": levels,
        "total_nodes": total_nodes,
        "leaf_nodes": branching_factor ** (levels - 1),
        "internal_nodes": total_nodes - (branching_factor ** (levels - 1)),
    }


# ============================================================================
# AGENTE PRINCIPAL
# ============================================================================


class BestCaseVisualizationAgent(AgentBase):
    """
    Agente especializado en analizar el mejor caso de algoritmos y
    generar una representación visual en árbol.
    """

    def _configure(self):
        """Configura el agente con sus herramientas, esquemas y prompt del sistema"""

        # Configurar herramientas disponibles
        self.tools = [get_algorithm_info, calculate_tree_levels]

        # Configurar esquema de contexto
        self.context_schema = AlgorithmContext

        # Configurar formato de respuesta
        self.response_format = BestCaseResponse

        # Configurar el prompt del sistema
        self.SYSTEM_PROMPT = """Eres un experto en algoritmos y estructuras de datos especializado en analizar casos de complejidad.

Tu tarea es:
1. Analizar el algoritmo solicitado por el usuario
2. Identificar cuál es su MEJOR CASO (la situación más favorable)
3. Generar una estructura de árbol que represente visualmente ese mejor caso
4. Explicar por qué esa estructura representa el mejor caso

REGLAS IMPORTANTES:
- Para algoritmos de ordenamiento divide y conquista (quicksort, mergesort): el mejor caso es un árbol BALANCEADO
- Para quicksort: el mejor caso ocurre cuando el pivote siempre divide el arreglo en dos mitades iguales
- Para búsqueda binaria: el mejor caso es cuando el elemento está en la raíz
- Los nodos del árbol deben tener valores CONCRETOS (números, no solo descripciones)
- La estructura debe ser matemáticamente correcta según el tamaño del arreglo

FORMATO DEL ÁRBOL:
- Cada nodo tiene: value (valor), level (nivel desde 0), position (posición en el nivel), children_indices (índices de hijos)
- Los índices son posiciones en la lista completa de nodos
- El árbol debe ser recorrible usando los children_indices

Usa las herramientas disponibles para obtener información sobre algoritmos y calcular niveles del árbol."""

    def invoke_agent(
        self,
        algorithm_name: str,
        array_size: int = 7,
        additional_info: Optional[str] = None,
        thread_id: str = "default_thread",
    ) -> Dict[str, Any]:
        """
        Invoca el agente para analizar un algoritmo y generar su árbol de mejor caso.

        Args:
            algorithm_name: Nombre del algoritmo a analizar
            array_size: Tamaño del arreglo para el ejemplo
            additional_info: Información adicional opcional
            thread_id: ID del hilo de conversación

        Returns:
            Diccionario con la respuesta estructurada del agente
        """

        # Preparar el contexto
        context_data = AlgorithmContext(
            algorithm_name=algorithm_name,
            array_size=array_size,
            additional_info=additional_info,
        )

        # Configurar el agente
        config = {"configurable": {"thread_id": thread_id}}

        content = f"""Analiza el algoritmo '{algorithm_name}' y genera una representación en árbol de su MEJOR CASO.

Requisitos:
- Usa un arreglo de tamaño {array_size}
- Identifica claramente cuál es el mejor caso
- Genera una estructura de árbol completa y correcta
- Proporciona valores concretos para cada nodo
- Explica por qué esta estructura representa el mejor caso
"""

        if additional_info:
            content += f"\n\nInformación adicional: {additional_info}"

        result = self._invoke_agent(content, config, context_data.model_dump()) # de clase a dict

        return result

    def execute_agent(
        self,
        algorithm_name: str,
        array_size: int = 7,
        additional_info: Optional[str] = None,
        thread_id: str = "default_thread",
    ) -> BestCaseResponse:
        """
        Ejecuta el agente y retorna la respuesta estructurada.
        """
        result = self.invoke_agent(
            algorithm_name=algorithm_name,
            array_size=array_size,
            additional_info=additional_info,
            thread_id=thread_id,
        )

        if "structured_response" in result and isinstance(
            result["structured_response"], BestCaseResponse
        ):
            return result["structured_response"]



# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Crear el agente (usa Modelo_Razonamiento para análisis profundo)
    agent = BestCaseVisualizationAgent(model_type="Modelo_Razonamiento")

    # Ejemplo 1: QuickSort
    print("=" * 80)
    print("EJEMPLO 1: QUICKSORT")
    print("=" * 80)

    response = agent.execute_agent(
        algorithm_name="quicksort", array_size=7, thread_id="quicksort_example"
    )

    print(f"\nAlgoritmo: {response.algorithm_name}")
    print(f"Mejor caso: {response.best_case_description}")
    print(f"Complejidad temporal: {response.time_complexity}")
    print(f"Complejidad espacial: {response.space_complexity}")
    print(f"\nExplicación:\n{response.explanation}")
    print(f"\nNotas de visualización:\n{response.visualization_notes}")
    print(f"\nEstructura del árbol ({len(response.tree_structure)} nodos):")

    for node in response.tree_structure[:5]:
        print(
            f"  Nivel {node.level}, Pos {node.position}: Valor={node.value}, Hijos={node.children_indices}"
        )

    # Ejemplo 2: Binary Search
    print("\n" + "=" * 80)
    print("EJEMPLO 2: BINARY SEARCH")
    print("=" * 80)

    response2 = agent.execute_agent(
        algorithm_name="binary_search",
        array_size=15,
        additional_info="Buscar el elemento 8 en un arreglo ordenado",
        thread_id="binary_search_example",
    )

    print(f"\nAlgoritmo: {response2.algorithm_name}")
    print(f"Mejor caso: {response2.best_case_description}")
    print(f"Complejidad temporal: {response2.time_complexity}")
    print(f"\nExplicación:\n{response2.explanation}")
    for node in response2.tree_structure[:5]:
        print(
            f"  Nivel {node.level}, Pos {node.position}: Valor={node.value}, Hijos={node.children_indices}"
        )

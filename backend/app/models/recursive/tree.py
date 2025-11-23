import math
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from ...external_services.Agentes.Agent import AgentBase

# ============================================================================
# SCHEMAS DE DATOS
# ============================================================================


class TreeNode(BaseModel):
    """Representa un nodo en el árbol de recursión (bosquejo)."""

    level: int = Field(description="Nivel en el árbol (0 = raíz).")
    position: int = Field(description="Posición en su nivel (0-indexed).")
    label: str = Field(
        description="Etiqueta del nodo (ej: 'T(n)', 'T(n/2)', 'T(n-1)')."
    )
    children_count: int = Field(description="Número de hijos directos de este nodo.")


class SingleTreeSketch(BaseModel):
    """Bosquejo de un único árbol de recursión."""

    case_type: str = Field(
        description="Tipo de caso: 'best', 'worst', 'average', o 'single' si no hay casos."
    )
    recurrence_equation: str = Field(
        description="Ecuación de recurrencia correspondiente."
    )
    tree_structure: List[TreeNode] = Field(
        description="Lista de nodos que representan el bosquejo del árbol."
    )
    tree_depth: int = Field(
        description="Profundidad aproximada del árbol (número de niveles)."
    )
    description: str = Field(
        description="Descripción breve del tipo de árbol (equilibrado, lineal, etc.)."
    )


class RecurrenceTreeResponse(BaseModel):
    """Formato de respuesta del agente para uno o múltiples árboles."""

    has_multiple_cases: bool = Field(
        description="True si hay mejor/peor/promedio caso, False si es un solo árbol."
    )
    trees: List[SingleTreeSketch] = Field(
        description="Lista de bosquejos de árboles generados."
    )
    summary: str = Field(description="Resumen general de los árboles generados.")


class RecurrenceInput(BaseModel):
    """Contexto de entrada para el análisis de árboles."""

    has_multiple_cases: bool = Field(
        description="Indica si hay múltiples casos (mejor/peor/promedio)."
    )
    best_case: Optional[str] = Field(
        None, description="Ecuación del mejor caso si existe."
    )
    worst_case: Optional[str] = Field(
        None, description="Ecuación del peor caso si existe."
    )
    average_case: Optional[str] = Field(
        None, description="Ecuación del caso promedio si existe."
    )
    single_equation: Optional[str] = Field(
        None, description="Ecuación única si no hay casos múltiples."
    )
    max_depth: int = Field(
        default=4, description="Profundidad máxima del bosquejo del árbol."
    )


# ============================================================================
# HERRAMIENTAS
# ============================================================================


@tool
def parse_recurrence_pattern(equation: str) -> Dict[str, Any]:
    """
    Identifica el patrón de una ecuación de recurrencia para determinar
    el tipo de árbol (divide y conquista, lineal, etc.).

    Args:
        equation: Ecuación de recurrencia (ej: 'T(n) = 2T(n/2) + n')

    Returns:
        Dict con: branching_factor (a), division_type, pattern_type
    """
    import re

    eq = equation.lower().strip()

    result = {
        "branching_factor": 1,
        "division_type": "none",  # "divide", "subtract", "none"
        "pattern_type": "unknown",  # "balanced", "linear", "fibonacci", "unknown"
    }

    # Detectar T(n/b) - División
    div_matches = re.findall(r"t\(n/(\d+)\)", eq)
    if div_matches:
        result["division_type"] = "divide"
        result["branching_factor"] = len(div_matches)

        # Verificar si todos son del mismo tamaño
        if len(set(div_matches)) == 1:
            result["pattern_type"] = "balanced"  # Árbol equilibrado
        else:
            result["pattern_type"] = "unbalanced"

        return result

    # Detectar T(n-k) - Resta
    sub_matches = re.findall(r"t\(n-(\d+)\)", eq)
    if sub_matches:
        result["division_type"] = "subtract"
        result["branching_factor"] = len(sub_matches)

        if len(sub_matches) == 1:
            result["pattern_type"] = "linear"  # Árbol lineal
        elif len(sub_matches) == 2 and "t(n-1)" in eq and "t(n-2)" in eq:
            result["pattern_type"] = "fibonacci"  # Árbol tipo Fibonacci
        else:
            result["pattern_type"] = "multi_branch"

        return result

    return result


@tool
def generate_tree_sketch(
    branching_factor: int, pattern_type: str, max_depth: int = 4
) -> List[TreeNode]:
    """
    Genera un bosquejo de árbol basado en el patrón identificado.

    Args:
        branching_factor: Número de hijos por nodo (a)
        pattern_type: Tipo de patrón ("balanced", "linear", "fibonacci", etc.)
        max_depth: Profundidad máxima del bosquejo

    Returns:
        Lista de TreeNode representando el bosquejo
    """
    nodes: List[TreeNode] = []

    if pattern_type == "linear":
        # Árbol lineal: cada nodo tiene 1 hijo
        for level in range(max_depth):
            node = TreeNode(
                level=level,
                position=0,
                label=f"T(n-{level})" if level > 0 else "T(n)",
                children_count=1 if level < max_depth - 1 else 0,
            )
            nodes.append(node)

    elif pattern_type == "balanced":
        # Árbol equilibrado: cada nodo tiene 'branching_factor' hijos
        node_count = 0
        for level in range(max_depth):
            nodes_in_level = branching_factor**level
            for pos in range(nodes_in_level):
                children = branching_factor if level < max_depth - 1 else 0
                node = TreeNode(
                    level=level,
                    position=pos,
                    label=f"T(n/{2**level})" if level > 0 else "T(n)",
                    children_count=children,
                )
                nodes.append(node)

    elif pattern_type == "fibonacci":
        # Árbol tipo Fibonacci: patrón exponencial con 2 ramas
        for level in range(max_depth):
            nodes_in_level = 2**level
            for pos in range(min(nodes_in_level, 16)):  # Limitar visualización
                children = 2 if level < max_depth - 1 else 0
                node = TreeNode(
                    level=level,
                    position=pos,
                    label=f"T(n-{level})",
                    children_count=children,
                )
                nodes.append(node)

    else:
        # Árbol genérico
        for level in range(max_depth):
            nodes_in_level = branching_factor**level
            for pos in range(min(nodes_in_level, 10)):
                children = branching_factor if level < max_depth - 1 else 0
                node = TreeNode(
                    level=level,
                    position=pos,
                    label=f"Level {level}, Node {pos}",
                    children_count=children,
                )
                nodes.append(node)

    return nodes


# ============================================================================
# AGENTE PRINCIPAL
# ============================================================================


class RecurrenceTreeAgent(AgentBase[RecurrenceTreeResponse]):
    """
    Agente especializado en generar bosquejos de árboles de recursión.
    No calcula costos, solo genera la estructura visual del árbol.
    """

    def __init__(self, model_type: str = "Modelo_Codigo", enable_verbose: bool = False):
        """
        Inicializa el agente de bosquejos de árboles.

        Args:
            model_type: Tipo de modelo a utilizar
            enable_verbose: Activar logs detallados
        """
        self.enable_verbose = enable_verbose
        super().__init__(model_type)

    def _configure(self) -> None:
        """Configura el agente con sus herramientas, esquemas y prompt del sistema."""

        self.tools = [parse_recurrence_pattern, generate_tree_sketch]
        self.context_schema = RecurrenceInput
        self.response_format = RecurrenceTreeResponse

        self.SYSTEM_PROMPT = """Eres un experto en generar bosquejos visuales de árboles de recursión.

**TU TAREA:** Generar bosquejos de árboles (NO calcular costos ni complejidades).

**IMPORTANTE:**
- SOLO generas la ESTRUCTURA del árbol (nodos y conexiones)
- NO calculas costos por nivel
- NO determinas complejidad Big-O
- SOLO identificas el patrón y generas el bosquejo visual

**PASOS:**
1. Para CADA ecuación recibida, identificar su patrón:
   - **Balanced (Equilibrado)**: T(n) = aT(n/b) + f(n) → árbol con 'a' hijos por nodo
   - **Linear (Lineal)**: T(n) = T(n-1) + f(n) → cadena de nodos (1 hijo por nodo)
   - **Fibonacci**: T(n) = T(n-1) + T(n-2) → árbol binario exponencial

2. Usar las herramientas para:
   - `parse_recurrence_pattern`: Identificar el patrón
   - `generate_tree_sketch`: Generar el bosquejo

3. Crear un `SingleTreeSketch` por cada ecuación con:
   - `case_type`: "best", "worst", "average", o "single"
   - `tree_structure`: Lista de TreeNode
   - `tree_depth`: Número de niveles
   - `description`: Tipo de árbol ("Árbol equilibrado binario", "Árbol lineal", etc.)

**EJEMPLOS:**

**Entrada:** T(n) = 2T(n/2) + n
**Salida:** Árbol equilibrado con 2 hijos por nodo, profundidad log₂(n)

**Entrada:** T(n) = T(n-1) + 1
**Salida:** Árbol lineal (cadena) con 1 hijo por nodo, profundidad n

**Entrada:** T(n) = T(n-1) + T(n-2)
**Salida:** Árbol binario tipo Fibonacci, crecimiento exponencial

**RESPONDE con RecurrenceTreeResponse.**"""

    def generate_tree_sketches(
        self,
        best_case: Optional[str] = None,
        worst_case: Optional[str] = None,
        average_case: Optional[str] = None,
        single_equation: Optional[str] = None,
        max_depth: int = 4,
        thread_id: Optional[str] = None,
    ) -> RecurrenceTreeResponse:
        """
        Genera bosquejos de árboles para una o múltiples ecuaciones.

        Args:
            best_case: Ecuación del mejor caso (opcional)
            worst_case: Ecuación del peor caso (opcional)
            average_case: Ecuación del caso promedio (opcional)
            single_equation: Ecuación única si no hay casos múltiples
            max_depth: Profundidad máxima del bosquejo
            thread_id: ID del hilo de conversación

        Returns:
            RecurrenceTreeResponse con los bosquejos generados
        """
        has_multiple_cases = any([best_case, worst_case, average_case])

        if thread_id is None:
            base = best_case or worst_case or average_case or single_equation or "tree"
            thread_id = f"tree_{abs(hash(base))}"

        try:
            if self.enable_verbose:
                print(f"\n[RecurrenceTreeAgent] ===== GENERANDO BOSQUEJOS =====")
                print(f"Múltiples casos: {has_multiple_cases}")
                if best_case:
                    print(f"Mejor caso: {best_case}")
                if worst_case:
                    print(f"Peor caso: {worst_case}")
                if average_case:
                    print(f"Caso promedio: {average_case}")
                if single_equation:
                    print(f"Ecuación única: {single_equation}")

            # Preparar el contexto
            context = RecurrenceInput(
                has_multiple_cases=has_multiple_cases,
                best_case=best_case,
                worst_case=worst_case,
                average_case=average_case,
                single_equation=single_equation,
                max_depth=max_depth,
            )

            # Construir el contenido del mensaje
            if has_multiple_cases:
                content = f"""Genera bosquejos de árboles de recursión para los siguientes casos:

"""
                if best_case:
                    content += f"**MEJOR CASO:** {best_case}\n"
                if worst_case:
                    content += f"**PEOR CASO:** {worst_case}\n"
                if average_case:
                    content += f"**CASO PROMEDIO:** {average_case}\n"

                content += f"""
Para cada caso:
1. Identifica el patrón (equilibrado, lineal, fibonacci)
2. Genera el bosquejo del árbol
3. Describe brevemente la estructura

**Profundidad máxima:** {max_depth} niveles
**IMPORTANTE:** Solo generar la estructura visual, NO calcular costos."""
            else:
                content = f"""Genera un bosquejo de árbol de recursión para:

**Ecuación:** {single_equation}

1. Identifica el patrón de recursión
2. Genera el bosquejo del árbol
3. Describe la estructura

**Profundidad máxima:** {max_depth} niveles
**IMPORTANTE:** Solo generar la estructura visual, NO calcular costos."""

            if self.enable_verbose:
                print(f"\n[RecurrenceTreeAgent] Enviando prompt al modelo...")

            # Invocar el agente
            result = self.invoke_simple(
                content=content,
                thread_id=thread_id,
                context=context.model_dump(),
            )

            # Extraer y validar la respuesta estructurada
            response = self.extract_response(result)

            if response is None:
                raise ValueError("No se pudo obtener una respuesta estructurada válida")

            if self.enable_verbose:
                print(f"\n[RecurrenceTreeAgent] ✅ Bosquejos generados:")
                print(f"  - Árboles generados: {len(response.trees)}")
                for tree in response.trees:
                    print(
                        f"    • {tree.case_type}: {tree.description} ({len(tree.tree_structure)} nodos)"
                    )

            return response

        except Exception as e:
            if self.enable_verbose:
                print(f"[RecurrenceTreeAgent] ❌ ERROR: {type(e).__name__}: {str(e)}")
                import traceback

                traceback.print_exc()

            raise ValueError(
                f"No se pudieron generar los bosquejos de árboles: {str(e)}"
            )

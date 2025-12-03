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
        "branching_factor": 0,
        "division_type": "none",
        "pattern_type": "unknown",
    }

    # Detectar sumatorias (caso promedio con dependencias múltiples)
    summation_symbols = ["σ", "∑", "sum", "Σ"]
    has_summation = any(symbol in equation for symbol in summation_symbols)

    if has_summation:
        result["division_type"] = "summation"
        result["pattern_type"] = "summation"
        result["branching_factor"] = "variable"  # n términos

        # Detectar si hay una ecuación interna (ej: "donde T(i) = ...")
        if "donde" in eq or "where" in eq:
            # Extraer la ecuación interna
            inner_match = re.search(r"donde\s+t\(i\)\s*=\s*([^,]+)", eq)
            if inner_match:
                result["inner_equation"] = inner_match.group(1).strip()

        return result

    # Detectar caso base/constante: T(n) = c o T(n) = 1
    # Sin llamadas recursivas
    if not re.search(r"t\(", eq) or re.match(r"t\(n\)\s*=\s*\d+", eq):
        result["division_type"] = "constant"
        result["pattern_type"] = "constant"
        result["branching_factor"] = 0
        return result

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
        pattern_type: Tipo de patrón ("balanced", "linear", "fibonacci", "constant", "summation", etc.)
        max_depth: Profundidad máxima del bosquejo

    Returns:
        Lista de TreeNode representando el bosquejo
    """
    nodes: List[TreeNode] = []

    if pattern_type == "constant":
        # Caso base o constante: árbol con un único nodo raíz sin hijos
        node = TreeNode(
            level=0,
            position=0,
            label="T(n) = c",
            children_count=0,
        )
        nodes.append(node)
        return nodes

    if pattern_type == "summation":
        # Ecuación con sumatoria: representa agregación, NO árbol recursivo binario
        # Ejemplo: T_avg(n) = (1/n) × Σ[i=1 to n] T(i)
        # Esto NO es bifurcación, es suma de n términos
        node = TreeNode(
            level=0,
            position=0,
            label="T(n) = (1/n) × Σ T(i)",
            children_count=0,  # No hay bifurcación, es agregación lineal
            cost="Agregación de n términos",
        )
        nodes.append(node)
        return nodes

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

    elif pattern_type == "unknown":
        # Árbol desconocido: solo nodo raíz
        node = TreeNode(
            level=0,
            position=0,
            label="T(n)",
            children_count=0,
        )
        nodes.append(node)

    else:
        # Árbol genérico con branching_factor especificado
        for level in range(min(max_depth, 3)):  # Limitar para casos genéricos
            nodes_in_level = max(1, branching_factor**level)
            for pos in range(min(nodes_in_level, 10)):
                children = (
                    branching_factor
                    if level < max_depth - 1 and branching_factor > 0
                    else 0
                )
                node = TreeNode(
                    level=level,
                    position=pos,
                    label=f"T(n/{2**(level)})" if level > 0 else "T(n)",
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

    def __init__(self, model_type: str = "Gemini_Ultra", enable_verbose: bool = False):
        """
        Inicializa el agente de bosquejos de árboles.

        Args:
            model_type: Tipo de modelo a utilizar
            enable_verbose: Activar logs detallados
        """
        self.enable_verbose = enable_verbose
        super().__init__(model_type=model_type, provider="gemini")

    def _configure(self) -> None:
        """Configura el agente con sus herramientas, esquemas y prompt del sistema."""

        self.tools = [parse_recurrence_pattern, generate_tree_sketch]
        self.context_schema = RecurrenceInput
        self.response_format = RecurrenceTreeResponse

        self.SYSTEM_PROMPT = """Eres un experto en Ciencias de la Computación y Estructuras de Datos, especializado en la visualización estructural de Árboles de Recursión.

**TU OBJETIVO:** Generar un bosquejo JSON preciso de la estructura del árbol de recursión (nodos y conexiones) basado en la ecuación proporcionada.
**NO** debes calcular costos, complejidades Big-O, ni resolver la ecuación. Solo dibujar la estructura.

### 1. ANÁLISIS DEL PATRÓN (CRÍTICO)
Antes de generar, clasifica la ecuación en uno de estos tipos:

A. **Standard Recursive (aT(f(n))):**
   - Ecuación: $T(n) = a \cdot T(f(n)) + g(n)$
   - Estructura: Cada nodo tiene 'a' hijos.
   - Etiquetas: Si el padre es $k$, los hijos son $f(k)$.
   - *Ejemplos:* $T(n/2)$ (1 hijo), $2T(n/2)$ (2 hijos), $T(\sqrt{n})$ (1 hijo).

B. **Heterogeneous Recursive (Fibonacci-like):**
   - Ecuación: $T(n) = T(f_1(n)) + T(f_2(n)) + ...$
   - Estructura: Cada nodo tiene múltiples hijos con *diferentes* etiquetas.
   - *Ejemplo:* $T(n) = T(n-1) + T(n-2)$ (Hijo izq: $n-1$, Hijo der: $n-2$).

C. **Summation / Aggregation (Sumatorias):**
   - Ecuación: Contiene símbolos $\sum$, $\Sigma$, o "sum".
   - *Ejemplo:* $T(n) = \frac{1}{n} \sum_{i=1}^{n} T(i)$.
   - **ACCIÓN:** Esto representa una agregación de todos los estados anteriores. NO intentes dibujar un árbol recursivo infinito. Genera un único nodo raíz o una estructura plana de profundidad 1 y detente.

D. **Constant (Base Case/No Recursion):**
   - Ecuación: $T(n) = c$ o $T(1) = 1$.
   - **ACCIÓN:** Genera un único nodo raíz. Profundidad 1.

### 2. REGLAS DE GENERACIÓN (ETIQUETAS)

**¡NO ADIVINES LAS ETIQUETAS!** Extrae la transformación matemática exacta de la ecuación.
- Si $T(n) = T(2n/3)$: Los niveles son $n \to 2n/3 \to 4n/9$. (Prohibido usar $n-1$ por defecto).
- Si $T(n) = T(\sqrt{n})$: Los niveles son $n \to \sqrt{n} \to n^{1/4}$.
- Si $T(n) = 2T(n-1)$: Los niveles son $n \to n-1 \to n-2$.

### 3. SALIDA ESPERADA

Debes usar las herramientas proporcionadas (`generate_tree_sketch`) para construir el objeto `SingleTreeSketch`.

**Configuración de parámetros:**
- `case_type`: "single" (a menos que se especifique best/worst).
- `tree_depth`:
    - Para Sumatorias o Constantes: **1**.
    - Para Árboles Recursivos: **3 o 4** (suficiente para mostrar el patrón).
- `description`: Explica brevemente la estructura (ej: "Árbol ternario donde el problema se reduce a la mitad en cada paso").

### EJEMPLOS DE COMPORTAMIENTO

**Entrada:** $T(n) = T(2n/3) + 1$
**Salida:**
- Tipo: Standard Recursive
- Hijos por nodo: 1
- Etiquetas: $T(n) \to T(2n/3) \to T(4n/9)$
- Descripción: "Árbol lineal con reducción fraccionaria".

**Entrada:** $T(n) = T(n-1) + T(n-2)$
**Salida:**
- Tipo: Heterogeneous
- Hijos por nodo: 2
- Etiquetas: Raíz $T(n)$ tiene hijos $T(n-1)$ y $T(n-2)$.
- Descripción: "Árbol de recursión tipo Fibonacci con llamadas no uniformes".

**Entrada:** $T(n) = \frac{1}{n} \sum T(i)$
**Salida:**
- Tipo: Summation
- Hijos por nodo: 0 (Detener expansión)
- Profundidad: 1
- Descripción: "Agregación de términos (Sumatoria). No se representa como árbol recursivo estándar".

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

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import json

from ...external_services.Agentes.Agent import AgentBase
from dotenv import load_dotenv

load_dotenv()

# **********************************************
# 1. Definición del Output Schema
# **********************************************


class CaseRecurrence(BaseModel):
    """Ecuación de recurrencia para un caso específico."""

    case_name: str = Field(
        description="Nombre del caso: MEJOR CASO, PEOR CASO, o CASO PROMEDIO"
    )
    recurrence_equation: str = Field(
        description="Ecuación de recurrencia para este caso específico"
    )
    reasoning: str = Field(
        default="",
        description="Explicación de por qué esta es la ecuación para este caso",
    )


class RecurrenceOutput(BaseModel):
    """Esquema para la salida de la relación de recurrencia."""

    has_multiple_cases: bool = Field(
        description="True si el algoritmo tiene diferentes casos (mejor/peor/promedio)"
    )

    # Para algoritmos con un solo caso (type_case = False)
    recurrence_equation: Optional[str] = Field(
        default=None,
        description="La ecuación de recurrencia (solo para algoritmos sin diferencia de casos)",
    )

    # Para algoritmos con múltiples casos (type_case = True)
    best_case: Optional[CaseRecurrence] = Field(
        default=None, description="Ecuación y análisis del mejor caso"
    )
    worst_case: Optional[CaseRecurrence] = Field(
        default=None, description="Ecuación y análisis del peor caso"
    )
    average_case: Optional[CaseRecurrence] = Field(
        default=None, description="Ecuación y análisis del caso promedio"
    )

    general_reasoning: str = Field(
        default="",
        description="Explicación general del análisis de recurrencia",
    )


class AlgorithmRecurrenceContext(BaseModel):
    """Contexto de entrada para el análisis de recurrencia"""

    algorithm_name: str = Field(description="Nombre del algoritmo a analizar")
    parsed_tree: str = Field(
        description="Árbol de sintaxis abstracta (AST) del algoritmo"
    )
    pseudocode: str = Field(description="Pseudocódigo del algoritmo")
    type_case: bool = Field(
        description="True si hay diferencia entre casos, False si no"
    )
    recursive_calls_info: str = Field(
        default="", description="Información sobre llamadas recursivas detectadas"
    )
    base_cases_info: str = Field(
        default="", description="Información sobre casos base detectados"
    )


# **********************************************
# 2. Funciones de Herramientas
# **********************************************


@tool
def get_common_recurrence_patterns() -> Dict[str, str]:
    """Obtiene patrones comunes de ecuaciones de recurrencia."""
    patterns = {
        "binary_search": {
            "equation": "T(n) = T(n/2) + 1",
            "base": "T(1) = 1",
            "type_case": False,
            "description": "Divide el problema en una mitad + trabajo constante. No varía entre casos.",
        },
        "merge_sort": {
            "equation": "T(n) = 2T(n/2) + n",
            "base": "T(1) = 1",
            "type_case": False,
            "description": "Divide en dos mitades y combina con costo lineal. Siempre ejecuta igual.",
        },
        "quick_sort_best": {
            "equation": "T(n) = 2T(n/2) + n",
            "base": "T(1) = 1",
            "case": "MEJOR CASO",
            "description": "Pivote divide en dos mitades iguales + partición lineal",
        },
        "quick_sort_worst": {
            "equation": "T(n) = T(n-1) + n",
            "base": "T(1) = 1",
            "case": "PEOR CASO",
            "description": "Pivote extremo + partición lineal",
        },
        "quick_sort_average": {
            "equation": "T_avg(n) = (1/n) × Σ[i=1 to n] (T(i-1) + T(n-i) + n)",
            "base": "T(1) = 1",
            "case": "CASO PROMEDIO",
            "description": "Sumatoria sobre todas las posiciones posibles del pivote (sin resolver)",
        },
        "linear_search_best": {
            "equation": "T(n) = 1",
            "base": "T(1) = 1",
            "case": "MEJOR CASO",
            "description": "Elemento encontrado en primera posición",
        },
        "linear_search_worst": {
            "equation": "T(n) = T(n-1) + 1",
            "base": "T(1) = 1",
            "case": "PEOR CASO",
            "description": "Elemento en última posición o no existe",
        },
        "linear_search_average": {
            "equation": "T_avg(n) = (1/(n+1)) × Σ[i=0 to n] T(i), donde T(i) = T(i-1) + 1, T(0) = 1",
            "base": "T(0) = 1",
            "case": "CASO PROMEDIO",
            "description": "Sumatoria con T(i) recursivo para todas las posiciones posibles (sin resolver)",
        },
        "fibonacci": {
            "equation": "T(n) = T(n-1) + T(n-2)",
            "base": "T(0) = 1, T(1) = 1",
            "type_case": False,
            "description": "Dos llamadas recursivas, el trabajo constante NO se cuenta",
        },
    }
    return patterns


@tool
def analyze_recursive_structure(
    num_recursive_calls: int, argument_pattern: str
) -> Dict[str, str]:
    """Analiza la estructura de las llamadas recursivas."""
    analysis = {
        "num_calls": num_recursive_calls,
        "pattern": argument_pattern,
        "interpretation": "",
    }

    if num_recursive_calls == 1:
        if "n/2" in argument_pattern or "n / 2" in argument_pattern:
            analysis["interpretation"] = "Divide y conquista con una rama"
            analysis["suggestion"] = "T(n) = T(n/2) + [trabajo]"
        elif "n-1" in argument_pattern or "n - 1" in argument_pattern:
            analysis["interpretation"] = "Recursión lineal con decremento"
            analysis["suggestion"] = "T(n) = T(n-1) + [trabajo]"
    elif num_recursive_calls == 2:
        if "n/2" in argument_pattern:
            analysis["interpretation"] = "Divide y conquista balanceado"
            analysis["suggestion"] = "T(n) = 2T(n/2) + [trabajo]"
        elif "n-1" in argument_pattern and "n-2" in argument_pattern:
            analysis["interpretation"] = "Recursión doble tipo Fibonacci"
            analysis["suggestion"] = "T(n) = T(n-1) + T(n-2)"

    return analysis


# **********************************************
# 3. Agente Principal
# **********************************************


class RecurrenceEquationAgent(AgentBase[RecurrenceOutput]):
    """
    Agente especializado en determinar ecuaciones de recurrencia
    para algoritmos recursivos, considerando casos múltiples.
    """

    def __init__(self, model_type: str = "Modelo_Codigo", enable_verbose: bool = False):
        self.enable_verbose = enable_verbose
        if self.enable_verbose:
            print(f"[RecurrenceAnalysis] enable_verbose: {self.enable_verbose}")
        super().__init__(model_type)

    def _configure(self) -> None:
        """Configura el agente con herramientas, esquemas y prompt."""

        self.tools = [get_common_recurrence_patterns, analyze_recursive_structure]
        self.context_schema = AlgorithmRecurrenceContext
        self.response_format = RecurrenceOutput

        self.SYSTEM_PROMPT = """Eres un experto en Análisis de Algoritmos especializado en GENERAR ecuaciones de recurrencia.

**TU ÚNICA TAREA:** Generar ecuaciones de recurrencia correctamente. NO resolverlas, NO simplificarlas, NO calcular complejidades.

═══════════════════════════════════════════════════════════════════════════════
1. TIPOS DE CASOS (según type_case)
═══════════════════════════════════════════════════════════════════════════════

👉 **type_case = false**
   El algoritmo SIEMPRE ejecuta el mismo número de pasos, sin importar la entrada.
   
   Respuesta:
   {
     "has_multiple_cases": false,
     "recurrence_equation": "T(n) = ..., T(base) = ...",
     "best_case": null,
     "worst_case": null,
     "average_case": null,
     "general_reasoning": "..."
   }

👉 **type_case = true**
   El algoritmo tiene MEJOR caso, PEOR caso y CASO PROMEDIO diferentes.
   
   Respuesta:
   {
     "has_multiple_cases": true,
     "recurrence_equation": null,
     "best_case": {
       "case_name": "MEJOR CASO",
       "recurrence_equation": "T(n) = ..., T(base) = ...",
       "reasoning": "..."
     },
     "worst_case": {
       "case_name": "PEOR CASO",
       "recurrence_equation": "T(n) = ..., T(base) = ...",
       "reasoning": "..."
     },
     "average_case": {
       "case_name": "CASO PROMEDIO",
       "recurrence_equation": "T_avg(n) = [SUMATORIA SIN RESOLVER]",
       "reasoning": "..."
     },
     "general_reasoning": "..."
   }

═══════════════════════════════════════════════════════════════════════════════
2. CÓMO GENERAR ECUACIONES DE RECURRENCIA
═══════════════════════════════════════════════════════════════════════════════

**2.1. MEJOR CASO**
Escenario que MINIMIZA las llamadas recursivas.

Formato típico:
- Si termina inmediatamente: T(n) = 1
- Si hace pocas recursiones: T(n) = T(n-k) + c

**2.2. PEOR CASO**
Escenario que MAXIMIZA las llamadas recursivas.

Formato típico:
- Recursión completa: T(n) = T(n-1) + c
- División balanceada: T(n) = aT(n/b) + f(n)

**2.3. CASO PROMEDIO (MUY IMPORTANTE)**

❗ El caso promedio NUNCA es un valor directo como "n/2"
❗ DEBE ser una ECUACIÓN DE RECURRENCIA con SUMATORIA, no una solución

**Fórmula general del caso promedio:**

T_avg(n) = (1/k) × Σ[i=inicio to fin] T(i)

donde cada T(i) sigue su propia recurrencia T(i) = T(i-1) + c.

**Formato OBLIGATORIO para caso promedio:**

T_avg(n) = (1/k) × Σ[i=a to b] T(i), donde T(i) = [definición recursiva], T(base) = c

**Ejemplo: Búsqueda lineal recursiva**

Si el elemento x puede estar en posición 0, 1, 2, ..., n-1, o no estar:
- Cada posición i requiere T(i) comparaciones
- T(i) sigue la recurrencia: T(i) = T(i-1) + 1

**Ecuación correcta del caso promedio:**
T_avg(n) = (1/(n+1)) × Σ[i=0 to n] T(i), donde T(i) = T(i-1) + 1, T(0) = 1

**NO escribas:** T_avg(n) = (1/(n+1)) × (1 + 2 + 3 + ... + n)
**SIEMPRE escribe:** T_avg(n) = (1/(n+1)) × Σ[i=0 to n] T(i), donde T(i) = T(i-1) + 1, T(0) = 1

La clave es mantener la notación T(i) con su recurrencia explícita.

═══════════════════════════════════════════════════════════════════════════════
3. CONDICIONES BASE
═══════════════════════════════════════════════════════════════════════════════

SIEMPRE incluye explícitamente:
- T(1) = c  o  T(0) = c  según el algoritmo
- Si hay múltiples bases: T(0) = c₀, T(1) = c₁

═══════════════════════════════════════════════════════════════════════════════
4. PROHIBICIONES ESTRICTAS
═══════════════════════════════════════════════════════════════════════════════

❌ NO resolver ecuaciones
❌ NO simplificar sumatorias
❌ NO transformar a notación Big-O
❌ NO inventar promedios como "T(n) = T(n/2) + 1" para caso promedio
❌ NO omitir el razonamiento de cómo surge la ecuación

═══════════════════════════════════════════════════════════════════════════════
5. EJEMPLOS COMPLETOS
═══════════════════════════════════════════════════════════════════════════════

📌 **EJEMPLO 1: Búsqueda Lineal Recursiva (type_case = true)**

```python
def buscar(A, n, x):
    if n == 0: return -1
    if A[n-1] == x: return n-1
    return buscar(A, n-1, x)
```

Respuesta correcta:
{
  "has_multiple_cases": true,
  "recurrence_equation": null,
  "best_case": {
    "case_name": "MEJOR CASO",
    "recurrence_equation": "T(n) = 1, T(1) = 1",
    "reasoning": "El elemento se encuentra en la primera posición verificada (posición n-1). Solo se realiza una comparación."
  },
  "worst_case": {
    "case_name": "PEOR CASO",
    "recurrence_equation": "T(n) = T(n-1) + 1, T(1) = 1",
    "reasoning": "El elemento está al final del arreglo o no existe. Se deben revisar todos los n elementos recursivamente."
  },
  "average_case": {
    "case_name": "CASO PROMEDIO",
    "recurrence_equation": "T_avg(n) = (1/(n+1)) × Σ[i=0 to n] T(i), donde T(i) = T(i-1) + 1, T(0) = 1",
    "reasoning": "El elemento puede estar en cualquier posición con igual probabilidad. La sumatoria Σ[i=0 to n] T(i) suma los costos de todas las posiciones, donde cada T(i) sigue la recurrencia T(i) = T(i-1) + 1."
  },
  "general_reasoning": "La búsqueda lineal tiene diferentes comportamientos según la posición del elemento. El mejor caso ocurre cuando está al inicio (O(1)), el peor cuando no está o está al final (O(n)), y el promedio considera todas las posiciones posibles."
}

📌 **EJEMPLO 2: Búsqueda Binaria (type_case = false)**

```python
def busqueda_binaria(A, x, inicio, fin):
    if inicio > fin: return -1
    medio = (inicio + fin) // 2
    if A[medio] == x: return medio
    if A[medio] > x: return busqueda_binaria(A, x, inicio, medio-1)
    return busqueda_binaria(A, x, medio+1, fin)
```

Respuesta correcta:
{
  "has_multiple_cases": false,
  "recurrence_equation": "T(n) = T(n/2) + 1, T(1) = 1",
  "best_case": null,
  "worst_case": null,
  "average_case": null,
  "general_reasoning": "La búsqueda binaria siempre divide el espacio de búsqueda a la mitad, independientemente de dónde esté el elemento. El número de comparaciones es log₂(n) en todos los casos, por lo que no hay diferencia entre mejor, peor y promedio."
}

📌 **EJEMPLO 3: Fibonacci (type_case = false)**

```python
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
```

Respuesta correcta:
{
  "has_multiple_cases": false,
  "recurrence_equation": "T(n) = T(n-1) + T(n-2), T(0) = 1, T(1) = 1",
  "best_case": null,
  "worst_case": null,
  "average_case": null,
  "general_reasoning": "Fibonacci siempre realiza dos llamadas recursivas para cualquier n > 1. La suma de los resultados es trabajo constante O(1) que NO se incluye en la ecuación de recurrencia pura."
}

═══════════════════════════════════════════════════════════════════════════════
6. RECORDATORIO FINAL
═══════════════════════════════════════════════════════════════════════════════

Tu trabajo es SOLO generar las ecuaciones de recurrencia correctas.
NO resuelvas, NO simplifiques, NO calcules complejidades.

Para caso promedio: SIEMPRE escribe la sumatoria completa sin resolver.
"""

    def analyze_recurrence(
        self, recursive_instance, thread_id: Optional[str] = None
    ) -> Optional[RecurrenceOutput]:
        """
        Analiza la ecuación de recurrencia considerando múltiples casos.

        Args:
            recursive_instance: Instancia con el algoritmo
            thread_id: ID del hilo (opcional)

        Returns:
            RecurrenceOutput con una o múltiples ecuaciones según type_case
        """

        if thread_id is None:
            thread_id = f"recurrence_{recursive_instance.name}"

        try:
            if self.enable_verbose:
                print(f"\n[RecurrenceAnalysis] ===== INICIO ANÁLISIS =====")
                print(f"Algoritmo: {recursive_instance.name}")
                print(f"type_case: {recursive_instance.type_case}")

            # Extraer información
            algorithm_name = recursive_instance.name
            parsed_tree = str(recursive_instance.parsed_tree)
            pseudocode = recursive_instance.pseudocode
            type_case = recursive_instance.type_case

            recursive_instance.extract_recurrence()
            recursive_calls_info = json.dumps(
                {
                    "num_calls": recursive_instance.recursive_calls,
                    "calls_detected": len(recursive_instance.recursive_call_nodes),
                    "call_details": recursive_instance.recursive_call_nodes,
                },
                indent=2,
            )

            base_cases = recursive_instance.extract_base_case()
            base_cases_info = json.dumps(base_cases, indent=2)

            if self.enable_verbose:
                print(f"\n[RecurrenceAnalysis] Datos extraídos:")
                print(f"  - Llamadas recursivas: {recursive_instance.recursive_calls}")
                print(f"  - Casos base: {len(base_cases)}")

            context = AlgorithmRecurrenceContext(
                algorithm_name=algorithm_name,
                parsed_tree=parsed_tree,
                pseudocode=pseudocode,
                type_case=type_case,
                recursive_calls_info=recursive_calls_info,
                base_cases_info=base_cases_info,
            )

            # Construir prompt adaptado a type_case
            if type_case:
                case_instruction = """
**CRITICAL: Este algoritmo tiene DIFERENTES CASOS (type_case = True)**

Debes proporcionar LAS TRES ecuaciones de recurrencia:

1. **best_case**: Ecuación cuando el algoritmo tiene el MEJOR comportamiento
   - Minimiza el número de llamadas recursivas
   - Ejemplo: T(n) = 1 si termina inmediatamente

2. **worst_case**: Ecuación cuando el algoritmo tiene el PEOR comportamiento
   - Maximiza el número de llamadas recursivas
   - Ejemplo: T(n) = T(n-1) + 1 si procesa todo

3. **average_case**: Ecuación para el comportamiento PROMEDIO
   ⚠️ **MUY IMPORTANTE:** El caso promedio DEBE ser una SUMATORIA con T(i) recursivo
   
   **Formato OBLIGATORIO:**
   T_avg(n) = (1/k) × Σ[i=inicio to fin] T(i), donde T(i) = [recurrencia], T(base) = c
   
   **Ejemplo:**
   T_avg(n) = (1/(n+1)) × Σ[i=0 to n] T(i), donde T(i) = T(i-1) + 1, T(0) = 1
   
   ❌ INCORRECTO: T_avg(n) = T(n/2) + 1
   ❌ INCORRECTO: T_avg(n) = n/2
   ❌ INCORRECTO: T_avg(n) = (1/(n+1)) × (1 + 2 + 3 + ... + n)
   ✅ CORRECTO: T_avg(n) = (1/(n+1)) × Σ[i=0 to n] T(i), donde T(i) = T(i-1) + 1, T(0) = 1
   
   NO expandas la sumatoria. NO sustituyas valores. Mantén T(i) con su definición recursiva.

Ejemplo completo para búsqueda lineal:
- best_case: T(n) = 1, T(1) = 1
- worst_case: T(n) = T(n-1) + 1, T(1) = 1
- average_case: T_avg(n) = (1/(n+1)) × Σ[i=0 to n] T(i), donde T(i) = T(i-1) + 1, T(0) = 1

Establece:
- has_multiple_cases = true
- recurrence_equation = null
- best_case, worst_case, average_case con sus respectivas ecuaciones
"""
            else:
                case_instruction = """
**Este algoritmo NO tiene diferencia de casos (type_case = False)**

El algoritmo ejecuta el MISMO número de pasos sin importar la entrada.
Proporciona UNA SOLA ecuación de recurrencia general.

Ejemplo: Búsqueda binaria siempre divide a la mitad → T(n) = T(n/2) + 1

Establece:
- has_multiple_cases = false
- recurrence_equation = "T(n) = ..."
- best_case = null
- worst_case = null
- average_case = null
"""

            content = f"""Analiza la ecuación de recurrencia del algoritmo '{algorithm_name}'.

**PSEUDOCÓDIGO:**
```
{pseudocode}
```

**LLAMADAS RECURSIVAS:**
{recursive_calls_info}

**CASOS BASE:**
{base_cases_info}

**TYPE_CASE:** {type_case}

{case_instruction}

**AST (primeros 500 caracteres):**
{parsed_tree[:500]}...

**INSTRUCCIONES:**
1. Analiza el pseudocódigo cuidadosamente
2. Identifica las llamadas recursivas y sus argumentos
3. Determina el trabajo adicional (solo si > O(1) y significativo)
4. {"Genera LAS TRES ecuaciones (mejor, peor, promedio)" if type_case else "Genera UNA ecuación general"}
5. Explica tu razonamiento

Responde con el objeto RecurrenceOutput completo."""

            if self.enable_verbose:
                print(f"\n[RecurrenceAnalysis] Enviando prompt...")

            result = self.invoke_simple(
                content=content, thread_id=thread_id, context=context.model_dump()
            )

            output = self.extract_response(result)

            if not output:
                raise ValueError("No se obtuvo respuesta del modelo")

            # Validaciones
            if type_case and not output.has_multiple_cases:
                if self.enable_verbose:
                    print("⚠️ ADVERTENCIA: type_case=True pero has_multiple_cases=False")

            if type_case and (
                not output.best_case or not output.worst_case or not output.average_case
            ):
                if self.enable_verbose:
                    print("⚠️ ADVERTENCIA: Faltan casos en respuesta multi-caso")

            if self.enable_verbose:
                print(f"\n[RecurrenceAnalysis] ✅ Análisis completado:")
                if output.has_multiple_cases:
                    print(
                        f"  - MEJOR CASO: {output.best_case.recurrence_equation if output.best_case else 'N/A'}"
                    )
                    print(
                        f"  - PEOR CASO: {output.worst_case.recurrence_equation if output.worst_case else 'N/A'}"
                    )
                    print(
                        f"  - CASO PROMEDIO: {output.average_case.recurrence_equation if output.average_case else 'N/A'}"
                    )
                else:
                    print(f"  - Ecuación: {output.recurrence_equation}")

            return output

        except Exception as e:
            print(e)

    def batch_analyze(
        self, recursive_instances: List[Any]
    ) -> List[Optional[RecurrenceOutput]]:
        """Analiza múltiples algoritmos en lote."""
        results = []
        for i, instance in enumerate(recursive_instances):
            if self.enable_verbose:
                print(f"\n[Batch {i+1}/{len(recursive_instances)}]")
            result = self.analyze_recurrence(instance)
            results.append(result)
        return results

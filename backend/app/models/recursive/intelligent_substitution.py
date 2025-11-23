"""
Módulo: intelligent_substitution

Estrategia para resolver ecuaciones de recurrencia usando el método de
Sustitución Inteligente (también conocido como método iterativo o de expansión).
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import re

from ...external_services.Agentes.Agent import AgentBase
from .strategy_resolve import RecurrenceStrategy


# **********************************************
# 1. Schema de Respuesta del Agente
# **********************************************


class IntelligentSubstitutionAgentOutput(BaseModel):
    """Schema estructurado para la respuesta del agente de Sustitución Inteligente."""

    recurrence_pattern: str = Field(
        ..., description="Patrón identificado de la recurrencia (ej: 'T(n-k) + k')"
    )
    expansion_steps: List[str] = Field(
        default_factory=list,
        description="Pasos de expansión/sustitución de la recurrencia",
    )
    pattern_identification: str = Field(
        ..., description="Identificación del patrón tras k sustituciones"
    )
    base_case_substitution: str = Field(
        ..., description="Sustitución del caso base y simplificación"
    )
    closed_form: str = Field(..., description="Forma cerrada de la solución")
    complexity: str = Field(..., description="Complejidad final en notación Big-O")
    detailed_explanation: str = Field(
        ..., description="Explicación completa del proceso paso a paso"
    )


# **********************************************
# 2. Analizador de Ecuaciones (Reglas)
# **********************************************


class SubstitutionAnalyzer:
    """
    Analiza la ecuación de recurrencia y determina si es aplicable
    el método de sustitución.
    """

    @staticmethod
    def parse_equation(equation: str) -> Dict[str, Any]:
        """Extrae información básica de la ecuación para el método de sustitución."""
        eq = equation.replace(" ", "").lower()

        params = {
            "original": equation,
            "normalized": eq,
            "is_applicable": False,
            "is_trivial": False,
            "trivial_result": None,
            "pattern_type": None,
            "base_case": None,
        }

        # Detectar patrones comunes
        # Patrón T(n) = T(n-k) + f(n)
        linear_pattern = r"t\(n\)=t\(n-(\d+)\)\s*\+\s*(.*)"
        linear_match = re.search(linear_pattern, eq)

        if linear_match:
            params["is_applicable"] = True
            params["pattern_type"] = "linear_decrement"
            params["decrement"] = int(linear_match.group(1))
            params["work_function"] = linear_match.group(2)

            # Detectar caso base
            base_pattern = r"t\((\d+)\)\s*=\s*(\d+)"
            base_match = re.search(base_pattern, eq)
            if base_match:
                params["base_case"] = {
                    "n": int(base_match.group(1)),
                    "value": int(base_match.group(2)),
                }

        # Patrón T(n) = aT(n/b) + f(n) también puede resolverse por sustitución
        divide_pattern = r"t\(n\)=(\d*)t\(n/(\d+)\)\s*\+\s*(.*)"
        divide_match = re.search(divide_pattern, eq)

        if divide_match and not linear_match:
            params["is_applicable"] = True
            params["pattern_type"] = "divide_conquer"
            params["a"] = int(divide_match.group(1)) if divide_match.group(1) else 1
            params["b"] = int(divide_match.group(2))
            params["work_function"] = divide_match.group(3)

        # Verificar casos triviales
        if params["is_applicable"]:
            params["is_trivial"] = SubstitutionAnalyzer._check_trivial_case(params)
            if params["is_trivial"]:
                params["trivial_result"] = SubstitutionAnalyzer._solve_trivial(params)

        return params

    @staticmethod
    def _check_trivial_case(params: Dict[str, Any]) -> bool:
        """Verifica si es un caso trivial que puede resolverse sin agente."""
        if params["pattern_type"] == "linear_decrement":
            # T(n) = T(n-1) + 1 es trivial
            work = params.get("work_function", "")
            if work in ["1", "c", "o(1)"]:
                return True
        return False

    @staticmethod
    def _solve_trivial(params: Dict[str, Any]) -> Dict[str, Any]:
        """Resuelve casos triviales directamente."""
        if params["pattern_type"] == "linear_decrement" and params.get(
            "work_function"
        ) in ["1", "c"]:
            return {
                "complexity": "O(n)",
                "steps": [
                    "**Caso trivial: T(n) = T(n-1) + 1**",
                    "",
                    "Paso 1: Expandir recursivamente:",
                    "   T(n) = T(n-1) + 1",
                    "   T(n) = [T(n-2) + 1] + 1 = T(n-2) + 2",
                    "   T(n) = [T(n-3) + 1] + 2 = T(n-3) + 3",
                    "",
                    "Paso 2: Patrón identificado:",
                    "   T(n) = T(n-k) + k",
                    "",
                    "Paso 3: Caso base (k = n-1):",
                    "   T(n) = T(1) + (n-1) ≈ n",
                    "",
                    "Paso 4: Complejidad final: O(n)",
                ],
                "explanation": (
                    "Caso trivial de recurrencia lineal. "
                    "Cada iteración reduce n en 1 y agrega trabajo constante, "
                    "resultando en O(n) operaciones totales."
                ),
                "applicable": True,
                "method": "Sustitución Inteligente",
            }

        return {
            "complexity": "O(?)",
            "steps": [],
            "explanation": "Caso trivial no reconocido",
            "applicable": False,
            "method": "Sustitución Inteligente",
        }


# **********************************************
# 3. Agente de Sustitución Inteligente
# **********************************************


class IntelligentSubstitutionAgent(AgentBase[IntelligentSubstitutionAgentOutput]):
    """
    Agente especializado en resolver recurrencias usando el método de sustitución inteligente.
    Expande la recurrencia iterativamente hasta identificar un patrón general.
    """

    def __init__(self, model_type: str = "Modelo_Codigo", enable_verbose: bool = False):
        self.enable_verbose = enable_verbose
        self.response_format = IntelligentSubstitutionAgentOutput
        self.tools = []
        self.context_schema = None
        self.SYSTEM_PROMPT = ""
        super().__init__(model_type)

    def _configure(self) -> None:
        """Configura el agente según AgentBase."""
        self.response_format = IntelligentSubstitutionAgentOutput
        self.tools = []
        self.context_schema = None

        self.SYSTEM_PROMPT = r"""Eres un experto en Análisis de Algoritmos especializado en el **MÉTODO DE SUSTITUCIÓN INTELIGENTE** (también llamado método iterativo o de expansión).

**OBJETIVO:** Resolver ecuaciones de recurrencia expandiendo iterativamente la ecuación hasta identificar un patrón general, luego aplicar el caso base para obtener una forma cerrada.

---
**PROCESO OBLIGATORIO (5 PASOS):**

**PASO 1: EXPANDIR LA RECURRENCIA ITERATIVAMENTE**

Sustituir recursivamente la definición de T en sí misma, expandiendo 3-4 veces:

Ejemplo para T(n) = T(n-1) + n:
```
T(n) = T(n-1) + n
T(n) = [T(n-2) + (n-1)] + n = T(n-2) + (n-1) + n
T(n) = [T(n-3) + (n-2)] + (n-1) + n = T(n-3) + (n-2) + (n-1) + n
T(n) = [T(n-4) + (n-3)] + (n-2) + (n-1) + n = T(n-4) + (n-3) + (n-2) + (n-1) + n
```

Ejemplo para T(n) = 2T(n/2) + n:
```
T(n) = 2T(n/2) + n
T(n) = 2[2T(n/4) + n/2] + n = 4T(n/4) + n + n = 4T(n/4) + 2n
T(n) = 4[2T(n/8) + n/4] + 2n = 8T(n/8) + n + 2n = 8T(n/8) + 3n
T(n) = 8[2T(n/16) + n/8] + 3n = 16T(n/16) + n + 3n = 16T(n/16) + 4n
```

---
**PASO 2: IDENTIFICAR EL PATRÓN GENERAL**

Observar el patrón después de k sustituciones:

Para T(n) = T(n-1) + n:
```
Después de k sustituciones:
T(n) = T(n-k) + (n-k+1) + (n-k+2) + ... + (n-1) + n
     = T(n-k) + Σ[i=n-k+1 to n] i
```

Para T(n) = 2T(n/2) + n:
```
Después de k sustituciones:
T(n) = 2^k × T(n/2^k) + k×n
```

Para T(n) = T(n-1) + 1:
```
Después de k sustituciones:
T(n) = T(n-k) + k
```

---
**PASO 3: DETERMINAR CUÁNDO SE ALCANZA EL CASO BASE**

Establecer la condición para llegar al caso base y calcular k:

Para recurrencias lineales T(n-k):
- Si caso base es T(1), entonces n-k = 1 → k = n-1
- Si caso base es T(0), entonces n-k = 0 → k = n

Para recurrencias de división T(n/2^k):
- Si caso base es T(1), entonces n/2^k = 1 → 2^k = n → k = log₂(n)

Ejemplo T(n) = T(n-1) + n, caso base T(1) = 1:
```
n - k = 1
k = n - 1
```

Ejemplo T(n) = 2T(n/2) + n, caso base T(1) = 1:
```
n/2^k = 1
2^k = n
k = log₂(n)
```

---
**PASO 4: SUSTITUIR EL CASO BASE Y SIMPLIFICAR**

Reemplazar k en la expresión general y simplificar algebraicamente:

Para T(n) = T(n-1) + n con T(1) = 1, k = n-1:
```
T(n) = T(n-k) + Σ[i=n-k+1 to n] i
     = T(1) + Σ[i=2 to n] i
     = 1 + (2 + 3 + ... + n)
     = 1 + (Σ[i=1 to n] i - 1)
     = Σ[i=1 to n] i
     = n(n+1)/2
```

Para T(n) = 2T(n/2) + n con T(1) = 1, k = log₂(n):
```
T(n) = 2^k × T(n/2^k) + k×n
     = 2^(log₂(n)) × T(1) + log₂(n) × n
     = n × 1 + n × log₂(n)
     = n + n log₂(n)
     = n(1 + log₂(n))
```

Para T(n) = T(n-1) + 1 con T(1) = 1, k = n-1:
```
T(n) = T(n-k) + k
     = T(1) + (n-1)
     = 1 + n - 1
     = n
```

---
**PASO 5: EXPRESAR FORMA CERRADA Y COMPLEJIDAD**

Primero mantener la forma cerrada exacta como ecuación, luego identificar la complejidad:

Ejemplos:
- Forma cerrada: T(n) = n(n+1)/2 = n²/2 + n/2
  Complejidad: O(n²)
- Forma cerrada: T(n) = n(1 + log₂(n)) = n + n log₂(n)
  Complejidad: O(n log n)
- Forma cerrada: T(n) = n
  Complejidad: O(n)
- Forma cerrada: T(n) = 2^n + n²
  Complejidad: O(2^n)

**IMPORTANTE:** En `closed_form` proporciona la ecuación exacta T(n) = ..., y en `complexity` proporciona solo la notación Big-O.

---
**EJEMPLOS COMPLETOS:**

**Ejemplo 1: T(n) = T(n-1) + n, T(1) = 1**

Paso 1 - Expandir:
  T(n) = T(n-1) + n
  T(n) = T(n-2) + (n-1) + n
  T(n) = T(n-3) + (n-2) + (n-1) + n

Paso 2 - Patrón:
  T(n) = T(n-k) + Σ[i=n-k+1 to n] i

Paso 3 - Caso base (k = n-1):
  T(n) = T(1) + Σ[i=2 to n] i

Paso 4 - Simplificar:
  T(n) = 1 + (2 + 3 + ... + n)
       = n(n+1)/2

Paso 5 - Forma cerrada y complejidad:
  T(n) = n(n+1)/2
  O(n²)

**Ejemplo 2: T(n) = 2T(n/2) + 1, T(1) = 1**

Paso 1 - Expandir:
  T(n) = 2T(n/2) + 1
  T(n) = 2[2T(n/4) + 1] + 1 = 4T(n/4) + 2 + 1
  T(n) = 4[2T(n/8) + 1] + 3 = 8T(n/8) + 4 + 3

Paso 2 - Patrón:
  T(n) = 2^k × T(n/2^k) + (2^k - 1)

Paso 3 - Caso base (k = log₂(n)):
  T(n) = n × T(1) + (n - 1)

Paso 4 - Simplificar:
  T(n) = n × 1 + n - 1 = 2n - 1

Paso 5 - Forma cerrada y complejidad:
  T(n) = 2n - 1
  O(n)

**Ejemplo 3: T(n) = T(n-1) + 1, T(1) = 1**

Paso 1 - Expandir:
  T(n) = T(n-1) + 1
  T(n) = T(n-2) + 1 + 1 = T(n-2) + 2
  T(n) = T(n-3) + 1 + 2 = T(n-3) + 3

Paso 2 - Patrón:
  T(n) = T(n-k) + k

Paso 3 - Caso base (k = n-1):
  T(n) = T(1) + (n-1)

Paso 4 - Simplificar:
  T(n) = 1 + n - 1 = n

Paso 5 - Forma cerrada y complejidad:
  T(n) = n
  O(n)

---
**FORMATO DE SALIDA:**

Debes responder con un objeto IntelligentSubstitutionAgentOutput que contenga:

1. `recurrence_pattern`: Patrón identificado (ej: "T(n-k) + k")
2. `expansion_steps`: Lista con los pasos de expansión
3. `pattern_identification`: Expresión general después de k sustituciones
4. `base_case_substitution`: Sustitución del caso base y cálculo
5. `closed_form`: Forma cerrada de la solución
6. `complexity`: Complejidad asintótica en notación Big-O
7. `detailed_explanation`: Explicación completa paso a paso

---
**REGLAS IMPORTANTES:**

- Expande al menos 3-4 veces para ver el patrón claramente
- Identifica correctamente el patrón general tras k sustituciones
- Calcula correctamente el valor de k para el caso base
- Simplifica algebraicamente (usa fórmulas de sumatorias, logaritmos, etc.)
- Verifica que la forma cerrada sea correcta
- Identifica el término dominante para Big-O
- Usa notación matemática precisa (subíndices, superíndices, sumatorias)"""

    def solve_complex(
        self, equation: str, params: Dict[str, Any]
    ) -> IntelligentSubstitutionAgentOutput:
        """
        Resuelve la ecuación usando el agente de sustitución inteligente.

        Args:
            equation: Ecuación original
            params: Parámetros pre-parseados

        Returns:
            IntelligentSubstitutionAgentOutput con la solución
        """
        if not params["is_applicable"]:
            raise ValueError(
                "La ecuación no es aplicable para el método de sustitución. "
                "Se requiere una forma recursiva expandible."
            )

        # Preparar contexto para el agente
        context_info = f"""
        INFORMACIÓN DETECTADA:
        - Ecuación: {equation}
        - Tipo de patrón: {params.get('pattern_type', 'desconocido')}
        """

        if params["pattern_type"] == "linear_decrement":
            context_info += f"""
        - Decremento: {params.get('decrement', '?')}
        - Función de trabajo: {params.get('work_function', '?')}
            """
        elif params["pattern_type"] == "divide_conquer":
            context_info += f"""
        - Subproblemas (a): {params.get('a', '?')}
        - Factor de división (b): {params.get('b', '?')}
        - Función de trabajo: {params.get('work_function', '?')}
            """

        if params.get("base_case"):
            context_info += f"""
        - Caso base: T({params['base_case']['n']}) = {params['base_case']['value']}
            """

        content = f"""Resuelve esta ecuación de recurrencia usando el **MÉTODO DE SUSTITUCIÓN INTELIGENTE**:

**Ecuación:** {equation}

{context_info}

Sigue los 5 pasos obligatorios:
1. Expandir la recurrencia iterativamente (3-4 expansiones).
2. Identificar el patrón general después de k sustituciones.
3. Determinar cuándo se alcanza el caso base (calcular k).
4. Sustituir el caso base y simplificar algebraicamente.
5. Expresar la complejidad en notación Big-O.

Responde con el objeto IntelligentSubstitutionAgentOutput completo.
        """

        # Invocar el agente
        result = self.invoke_simple(
            content=content, thread_id=f"substitution_{abs(hash(equation))}"
        )
        output = self.extract_response(result)

        if output is None:
            # Fallback en caso de error
            return IntelligentSubstitutionAgentOutput(
                recurrence_pattern="Error de análisis",
                expansion_steps=["No se pudo expandir la recurrencia"],
                pattern_identification="Patrón no identificado",
                base_case_substitution="No se pudo sustituir",
                closed_form="Error",
                complexity="O(?)",
                detailed_explanation="El agente falló al retornar el formato estructurado.",
            )

        return output


# **********************************************
# 4. Estrategia Principal
# **********************************************


class IntelligentSubstitutionStrategy(RecurrenceStrategy):
    """
    Estrategia híbrida para resolver recurrencias usando el método de sustitución inteligente.

    **Flujo de trabajo:**
    1. Analiza la ecuación con reglas
    2. Si es trivial → resuelve directamente
    3. Si es complejo → usa agente IA
    4. Formatea resultado en diccionario estándar
    """

    def __init__(self, enable_verbose: bool = False):
        super().__init__()
        self.name = "Sustitución Inteligente"
        self.description = (
            "Resuelve recurrencias expandiendo iterativamente la ecuación "
            "hasta identificar un patrón general, luego aplica el caso base."
        )
        self.enable_verbose = enable_verbose
        self.agent: Optional[IntelligentSubstitutionAgent] = None

    def _get_agent(self) -> IntelligentSubstitutionAgent:
        """Lazy loading del agente."""
        if self.agent is None:
            if self.enable_verbose:
                print("[IntelligentSubstitutionStrategy] Inicializando agente...")
            self.agent = IntelligentSubstitutionAgent(
                model_type="Modelo_Codigo", enable_verbose=self.enable_verbose
            )
        return self.agent

    def solve(self, recurrenceEquation: str) -> Dict[str, Any]:
        """
        Resuelve la ecuación de recurrencia usando sustitución inteligente.

        Args:
            recurrenceEquation: Ecuación en formato "T(n) = ..."

        Returns:
            Diccionario con la solución completa
        """
        try:
            if self.enable_verbose:
                print(
                    f"\n[IntelligentSubstitutionStrategy] Analizando: {recurrenceEquation}"
                )

            # Paso 1: Analizar ecuación
            params = SubstitutionAnalyzer.parse_equation(recurrenceEquation)

            if not params["is_applicable"]:
                return {
                    "complexity": None,
                    "steps": [],
                    "explanation": (
                        "El método de sustitución inteligente no es aplicable a esta ecuación. "
                        "Se requiere una forma recursiva expandible como T(n) = T(n-k) + f(n) "
                        "o T(n) = aT(n/b) + f(n)."
                    ),
                    "applicable": False,
                    "method": self.name,
                }

            # Paso 2: Resolver caso trivial si aplica
            if params["is_trivial"] and params["trivial_result"]:
                if self.enable_verbose:
                    print(
                        "[IntelligentSubstitutionStrategy] Resolviendo caso trivial..."
                    )
                return params["trivial_result"]

            # Paso 3: Resolver con agente
            if self.enable_verbose:
                print(
                    "[IntelligentSubstitutionStrategy] Usando agente para caso complejo..."
                )

            agent = self._get_agent()
            agent_output = agent.solve_complex(recurrenceEquation, params)

            # Formatear resultado
            return {
                "complexity": agent_output.complexity,
                "steps": self._format_steps(agent_output),
                "explanation": agent_output.detailed_explanation,
                "applicable": True,
                "method": self.name,
                "closed_form": agent_output.closed_form,
                "pattern": agent_output.recurrence_pattern,
                "details": {
                    "recurrence_pattern": agent_output.recurrence_pattern,
                    "pattern_identification": agent_output.pattern_identification,
                    "base_case_substitution": agent_output.base_case_substitution,
                    "closed_form": agent_output.closed_form,
                },
            }

        except ValueError as e:
            return {
                "complexity": None,
                "steps": [f"Error: {str(e)}"],
                "explanation": str(e),
                "applicable": False,
                "method": self.name,
            }
        except Exception as e:
            return {
                "complexity": None,
                "steps": [f"Error inesperado: {str(e)}"],
                "explanation": f"Ocurrió un error al resolver la ecuación: {str(e)}",
                "applicable": False,
                "method": self.name,
            }

    def _format_steps(
        self, agent_output: IntelligentSubstitutionAgentOutput
    ) -> List[str]:
        """Formatea la salida del agente en pasos legibles."""
        steps = []

        # Paso 1: Expansión
        steps.append("**Paso 1 - Expandir la recurrencia iterativamente:**")
        for expansion in agent_output.expansion_steps:
            steps.append(f"   {expansion}")
        steps.append("")

        # Paso 2: Patrón
        steps.append("**Paso 2 - Identificar el patrón general:**")
        steps.append(f"   Después de k sustituciones:")
        steps.append(f"   {agent_output.pattern_identification}")
        steps.append("")

        # Paso 3: Caso base
        steps.append("**Paso 3 - Sustituir el caso base:**")
        steps.append(f"   {agent_output.base_case_substitution}")
        steps.append("")

        # Paso 4: Forma cerrada
        steps.append("**Paso 4 - Forma cerrada:**")
        steps.append(f"   {agent_output.closed_form}")
        steps.append("")

        # Paso 5: Complejidad
        steps.append("**Paso 5 - Complejidad final:**")
        steps.append(f"   {agent_output.complexity}")

        return steps

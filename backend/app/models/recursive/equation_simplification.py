"""
Módulo: equation_simplification

Agente especializado en simplificar ecuaciones de recurrencia complejas
(con sumatorias, promedios, etc.) a formas recursivas estándar.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import re
import json

# Asumiendo que esta es la ruta correcta a tu clase base
from ...external_services.Agentes.Agent import AgentBase

# **********************************************
# 1. Schema de Respuesta del Agente
# **********************************************


class SimplifiedEquationOutput(BaseModel):
    """Schema estructurado para la respuesta del agente de simplificación."""

    original_equation: str = Field(
        ..., description="Ecuación original tal cual fue recibida"
    )
    simplified_equation: str = Field(
        ..., description="Ecuación final simplificada: T(n) = T(f'(n)) + g'(n)"
    )
    simplification_steps: List[str] = Field(
        ...,
        description="Lista de 4 pasos detallados con el desarrollo matemático explícito",
    )
    explicit_form: str = Field(
        ..., description="Forma cerrada explícita de T(n) (NO de T_int)"
    )
    contains_summation: bool = Field(
        default=False, description="True si la ecuación original tenía sumatorias"
    )
    summation_resolved: Optional[str] = Field(
        default=None,
        description="La expresión algebraica resultante de evaluar la sumatoria S(n)",
    )
    confidence: float = Field(
        default=0.0, description="Nivel de confianza (0.0 a 1.0)", ge=0.0, le=1.0
    )
    pattern_type: str = Field(
        default="unknown",
        description="Tipo de patrón matemático (linear, quadratic, exponential, divide_conquer)",
    )


# **********************************************
# 2. Analizador Preliminar
# **********************************************


class EquationAnalyzer:
    """Analiza ecuaciones antes de enviarlas al agente para determinar si necesitan procesamiento."""

    @staticmethod
    def quick_check(equation: str) -> dict:
        """Análisis rápido de la ecuación."""
        eq_normalized = equation.replace(" ", "").lower()

        info = {
            "has_summation": False,
            "has_avg": False,
            "has_donde": False,
            "is_standard_form": False,
            "needs_simplification": True,
        }

        # Detectar sumatorias
        summation_symbols = ["σ", "∑", "sum", "Σ"]
        info["has_summation"] = any(symbol in equation for symbol in summation_symbols)

        # Detectar promedios
        info["has_avg"] = (
            "avg" in eq_normalized
            or "(1/n)" in eq_normalized
            or "(1/(n" in eq_normalized
        )

        # Detectar cláusulas "donde"
        info["has_donde"] = "donde" in eq_normalized or "where" in eq_normalized

        # Detectar si ya está en forma estándar (T(n) = aT(n-b) + g(n))
        # Simple heurística para evitar llamadas innecesarias
        standard_patterns = [
            r"t\(n\)\s*=\s*t\(n-\d+\)\s*\+",  # T(n) = T(n-1) + ...
            r"t\(n\)\s*=\s*\d*t\(n/\d+\)\s*\+",  # T(n) = 2T(n/2) + ...
        ]

        # Si tiene sumatoria, SIEMPRE necesita simplificación, ignorando patrones estándar
        if info["has_summation"]:
            info["needs_simplification"] = True
            return info

        for pattern in standard_patterns:
            if re.search(pattern, eq_normalized):
                info["is_standard_form"] = True
                info["needs_simplification"] = False
                break

        return info


# **********************************************
# 3. Agente de Simplificación
# **********************************************


class EquationSimplificationAgent(AgentBase[SimplifiedEquationOutput]):
    """
    Agente especializado en simplificar ecuaciones de recurrencia complejas.
    Utiliza un proceso estricto de 4 pasos para evitar alucinaciones algebraicas.
    """

    def __init__(self, model_type: str = "Gemini_Rapido", enable_verbose: bool = False):
        self.enable_verbose = enable_verbose
        super().__init__(model_type=model_type)

    def _configure(self) -> None:
        """Configura el Prompt del Sistema y las herramientas."""
        self.tools = []
        self.context_schema = None
        self.response_format = SimplifiedEquationOutput

        self.SYSTEM_PROMPT = r"""
Eres un matemático experto y riguroso especializado en SIMPLIFICACIÓN DE ECUACIONES DE RECURRENCIA CON PROMEDIOS.

**OBJETIVO:** Convertir una ecuación de la forma $T(n) = \frac{1}{k} \sum T_{int}(i)$ a una forma recursiva estándar $T(n) = T(n-1) + g'(n)$.

### ⚠️ REGLAS INVIOLABLES (CRÍTICO)
1. **DISTINCIÓN DE VARIABLES:**
   - $T_{int}(i)$: Es la recurrencia interna (dentro de la sumatoria).
   - $T(n)$: Es la función promedio resultante.
   - **NUNCA** confundas $T_{int}$ con $T(n)$.

2. **PROHIBIDO EL "PATRÓN VISUAL":**
   - El término $g'(n)$ **NO** es igual a $T_{int}(n) - T_{int}(n-1)$.
   - El término $g'(n)$ **DEBE** calcularse restando algebraicamente $T(n) - T(n-1)$.

3. **SIN NOTACIÓN ASINTÓTICA:**
   - $g'(n)$ debe ser una expresión exacta (ej: $1/2$, $n/2$, $2^n$). NO uses O(n).

4. **USO DE FÓRMULAS:**
   Usa estas fórmulas cerradas para evaluar sumatorias (S(n)):
   - $\sum_{i=0}^n c = c(n+1)$
   - $\sum_{i=0}^n i = \frac{n(n+1)}{2}$
   - $\sum_{i=0}^n i^2 = \frac{n(n+1)(2n+1)}{6}$
   - $\sum_{i=0}^n 2^i = 2^{n+1} - 1$

### 📝 PROCESO OBLIGATORIO DE 4 PASOS

**PASO 1: Resolver Recurrencia Interna $T_{int}(i)$**
Obtén la forma cerrada de la ecuación dentro del "donde".
*Ej: Si $T(i) = T(i-1) + 1, T(0)=1 \rightarrow T_{int}(i) = i+1$.*

**PASO 2: Evaluar Sumatoria $S(n)$**
Calcula $\sum_{i=0}^n T_{int}(i)$ sustituyendo el resultado del Paso 1.
*Importante:* Si $T_{int}(i)$ es una suma (ej. suma de cuadrados), $S(n)$ será una suma de sumas.
*Ej: $S(n) = \sum (i+1) = \frac{n(n+1)}{2} + (n+1) = \frac{(n+1)(n+2)}{2}$.*

**PASO 3: Forma Explícita de $T(n)$**
Aplica el factor de promedio a $S(n)$.
*Ej: $T(n) = \frac{1}{n+1} \cdot \frac{(n+1)(n+2)}{2} = \frac{n+2}{2}$.*
**Nota:** Esta es la fórmula de $T(n)$, NO de $T_{int}$.

**PASO 4: Derivar Recurrencia Final $g'(n)$**
Calcula $g'(n) = T(n) - T(n-1)$ algebraicamente.
1. Escribe $T(n)$.
2. Escribe $T(n-1)$ sustituyendo $n$ por $n-1$.
3. Resta las dos expresiones buscando denominador común.
4. Simplifica al máximo.

### EJEMPLO DE SALIDA JSON
```json
{
  "original_equation": "T(n) = (1/(n+1)) * sum(T(i)), donde T(i)=T(i-1)+1",
  "simplified_equation": "T(n) = T(n-1) + 1/2",
  "explicit_form": "T(n) = (n+2)/2",
  "summation_resolved": "(n+1)(n+2)/2",
  "simplification_steps": [
    "Paso 1: Resolvemos T_int. T(i) = i + 1.",
    "Paso 2: Evaluamos S(n) = sum(i+1) = n(n+1)/2 + (n+1) = (n+1)(n+2)/2.",
    "Paso 3: T(n) = S(n)/(n+1) = (n+2)/2.",
    "Paso 4: T(n-1) = (n+1)/2. Restamos: (n+2)/2 - (n+1)/2 = 1/2."
  "confidence": 1.0,
  "pattern_type": "linear",
  "contains_summation": true
}
```
"""

    def simplify_equation(
        self, equation: str, thread_id: str = "simplification"
    ) -> SimplifiedEquationOutput:
        """Ejecuta el proceso de simplificación."""
        if self.enable_verbose:
            print(f"\n[Agente] Simplificando: {equation}...")

        try:
            # Llamada al agente usando invoke_simple
            result = self.invoke_simple(content=equation, thread_id=thread_id)

            # Extraer la respuesta estructurada
            response = self.extract_response(result)

            if self.enable_verbose:
                if response:
                    print(f"✅ Resultado: {response.simplified_equation}")
                    print("📝 Pasos:")
                    for step in response.simplification_steps:
                        print(f"  - {step}")
                else:
                    print("⚠️ No se pudo extraer la respuesta")

            return response

        except Exception as e:
            if self.enable_verbose:
                print(f"❌ Error en simplificación: {str(e)}")

            # Retorno de fallo seguro
            return SimplifiedEquationOutput(
                original_equation=equation,
                simplified_equation="Error en simplificación",
                simplification_steps=[f"Error interno: {str(e)}"],
                explicit_form="Desconocido",
                confidence=0.0,
            )


# **********************************************
# 4. Función de Conveniencia
# **********************************************
def simplify_recurrence_equation(
    equation: str,
    model_type: str = "Gemini_Rapido",
    enable_verbose: bool = True,
    thread_id: str = "simplification_task",
) -> SimplifiedEquationOutput:
    """Función helper para usar el agente directamente."""

    # Pre-chequeo rápido para no gastar tokens si no es necesario
    analyzer = EquationAnalyzer()
    check = analyzer.quick_check(equation)

    if not check["needs_simplification"]:
        if enable_verbose:
            print(f"La ecuación '{equation}' ya parece estar en forma estándar.")
        # Retornar un objeto dummy o la misma ecuación
        return SimplifiedEquationOutput(
            original_equation=equation,
            simplified_equation=equation,
            simplification_steps=["La ecuación ya estaba en formato estándar."],
            explicit_form="N/A",
            confidence=1.0,
            pattern_type="standard",
        )

    # Crear el agente y ejecutar simplificación
    agent = EquationSimplificationAgent(
        model_type=model_type, enable_verbose=enable_verbose
    )
    return agent.simplify_equation(equation, thread_id=thread_id)


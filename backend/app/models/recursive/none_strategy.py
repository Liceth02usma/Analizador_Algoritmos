from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import re
import math

from ...external_services.Agentes.Agent import AgentBase
from .strategy_resolve import RecurrenceStrategy


class NoneStrategyAgentOutput(BaseModel):
    """Schema estructurado para ecuaciones sin recursión."""

    expression: str = Field(
        ..., description="La expresión T(n) analizada (ej: 'T(n) = n²', 'T(n) = 1')."
    )
    expression_type: str = Field(
        ...,
        description="Tipo de expresión (Constante, Lineal, Cuadrática, Polinomial, Logarítmica, etc.).",
    )
    dominant_term: str = Field(
        ...,
        description="Término dominante que determina la complejidad (ej: 'n²', '1', 'n log n').",
    )
    complexity: str = Field(
        ..., description="Complejidad en notación Big-O (ej: 'O(1)', 'O(n)', 'O(n²)')."
    )
    detailed_explanation: str = Field(
        ..., description="Explicación detallada de cómo se determinó la complejidad."
    )
    simplification_steps: List[str] = Field(
        default_factory=list,
        description="Pasos de simplificación si la expresión es compleja.",
    )


class DirectExpressionAnalyzer:
    """
    Analiza expresiones T(n) sin recursión para determinar su complejidad directamente.
    """

    @staticmethod
    def parse_expression(equation: str) -> Dict[str, Any]:
        """Extrae información de expresiones no recursivas y determina sus propiedades."""

        eq = equation.replace(" ", "").lower()

        params = {
            "original": equation,
            "normalized": eq,
            "has_recursion": False,
            "is_constant": False,
            "is_polynomial": False,
            "is_logarithmic": False,
            "is_exponential": False,
            "degree": None,
            "expression": None,
        }

        if "," in eq:
            main_equation = eq.split(",")[0].strip()
        else:
            main_equation = eq

        parts = main_equation.split("=")

        right_side = parts[1].strip() if len(parts) == 2 else main_equation

        all_t_calls = re.findall(r"t\(([^\)]+)\)", right_side)

        recursive_calls = [call for call in all_t_calls if "n" in call]

        if recursive_calls:

            params["has_recursion"] = True
            return params

        if len(parts) == 2:
            expr = right_side
            params["expression"] = expr

            if re.match(r"^\d+$", expr):
                params["is_constant"] = True
                params["degree"] = 0

            elif re.search(r"\d+\*\*n", expr):
                params["is_exponential"] = True

            elif re.search(r"n", expr):

                exp_matches = re.findall(r"n\*\*(\d+)", expr)

                if re.search(r"(?<!\*\*)\s*n(?!(\*\*|\w))", expr):

                    current_degree = 1
                else:
                    current_degree = 0

                if exp_matches:

                    max_degree = max([int(x) for x in exp_matches] + [current_degree])
                else:
                    max_degree = current_degree

                if max_degree > 0:
                    params["is_polynomial"] = True
                    params["degree"] = max_degree

                if "log" in expr:
                    params["is_logarithmic"] = True

        if "log" in right_side and not params["is_polynomial"]:
            params["is_logarithmic"] = True

        return params

    @staticmethod
    def determine_complexity_type(params: Dict[str, Any]) -> str:
        """Determina el tipo de complejidad basándose en los parámetros."""
        if params["is_constant"]:
            return "Constante"
        elif params["is_exponential"]:
            return "Exponencial"
        elif params["is_logarithmic"] and params["is_polynomial"]:
            return "Logarítmico-Polinomial"
        elif params["is_logarithmic"]:
            return "Logarítmica"
        elif params["is_polynomial"]:
            degree = params.get("degree", 1)
            if degree == 1:
                return "Lineal"
            elif degree == 2:
                return "Cuadrática"
            elif degree == 3:
                return "Cúbica"
            else:
                return f"Polinomial (grado {degree})"
        else:
            return "Desconocida"


class NoneStrategyAgent(AgentBase[NoneStrategyAgentOutput]):
    """
    Agente especializado en analizar ecuaciones SIN recursión.
    Determina la complejidad directamente de la expresión T(n) = f(n).
    """

    def __init__(self, model_type: str = "Modelo_Codigo", enable_verbose: bool = False):
        self.enable_verbose = enable_verbose
        super().__init__(model_type)

    def _configure(self) -> None:
        """Configura el agente según AgentBase."""
        self.response_format = NoneStrategyAgentOutput
        self.tools = []
        self.context_schema = None

        self.SYSTEM_PROMPT = """Eres un experto en Análisis de Algoritmos especializado en determinar la complejidad temporal de funciones directas (sin recursión).

**OBJETIVO:** Analizar expresiones de la forma T(n) = f(n) donde NO hay llamadas recursivas, y determinar su complejidad en notación Big-O.

---
**TIPOS DE COMPLEJIDAD COMÚN:**

1. **Constante - O(1):**
   - T(n) = 1, T(n) = 5, T(n) = 100
   - Cualquier valor que no dependa de n

2. **Logarítmica - O(log n):**
   - T(n) = log n, T(n) = log₂ n, T(n) = 3 log n

3. **Lineal - O(n):**
   - T(n) = n, T(n) = 2n, T(n) = n + 5

4. **Logarítmico-Lineal - O(n log n):**
   - T(n) = n log n, T(n) = n log₂ n

5. **Cuadrática - O(n²):**
   - T(n) = n², T(n) = n² + n, T(n) = 3n² + 2n + 1

6. **Cúbica - O(n³):**
   - T(n) = n³, T(n) = 2n³ + n²

7. **Polinomial - O(n^k):**
   - T(n) = n⁴, T(n) = n⁵

8. **Exponencial - O(2^n), O(k^n):**
   - T(n) = 2^n, T(n) = 3^n

---
**PROCESO DE ANÁLISIS (4 PASOS):**

**PASO 1: IDENTIFICAR LA EXPRESIÓN**
Extraer la función f(n) de T(n) = f(n).

**PASO 2: IDENTIFICAR EL TÉRMINO DOMINANTE**
En expresiones con múltiples términos (ej: n² + 3n + 5), identificar el término de mayor orden.
Regla: En Big-O, solo importa el término de crecimiento más rápido.

**PASO 3: APLICAR REGLAS DE SIMPLIFICACIÓN**
- Eliminar constantes multiplicativas: 5n → n
- Eliminar términos de menor orden: n² + n → n²
- Mantener la base en exponenciales y logaritmos cuando sea relevante

**PASO 4: DETERMINAR COMPLEJIDAD BIG-O**
Expresar el resultado en notación O(...) basándose en el término dominante.

---
**REGLAS DE DOMINANCIA (De menor a mayor):**
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(n³) < O(2^n) < O(n!)

---
**EJEMPLOS:**

🔹 **Ejemplo 1: T(n) = 5**
- Tipo: Constante
- Término dominante: 5 (constante)
- Complejidad: O(1)
- Explicación: No depende de n, por lo tanto es tiempo constante.

🔹 **Ejemplo 2: T(n) = 3n + 10**
- Tipo: Lineal
- Término dominante: 3n
- Complejidad: O(n)
- Explicación: El término 3n domina sobre la constante 10. Las constantes se eliminan en Big-O.

🔹 **Ejemplo 3: T(n) = n² + 5n + 3**
- Tipo: Cuadrática
- Término dominante: n²
- Complejidad: O(n²)
- Explicación: n² crece más rápido que 5n y 3, por lo tanto domina.

🔹 **Ejemplo 4: T(n) = 2n log n + n**
- Tipo: Logarítmico-Lineal
- Término dominante: n log n
- Complejidad: O(n log n)
- Explicación: n log n domina sobre n lineal.

🔹 **Ejemplo 5: T(n) = 2^n + n³**
- Tipo: Exponencial
- Término dominante: 2^n
- Complejidad: O(2^n)
- Explicación: El crecimiento exponencial domina completamente sobre el polinomial.

---
**FORMATO DE SALIDA:**
Debes responder con un objeto NoneStrategyAgentOutput que contenga:
- expression: La expresión T(n) analizada
- expression_type: Tipo de complejidad (Constante, Lineal, Cuadrática, etc.)
- dominant_term: El término que domina
- complexity: Resultado en notación Big-O
- detailed_explanation: Explicación paso a paso
- simplification_steps: Lista de pasos si hubo simplificación

**IMPORTANTE:** No uses recursión ni ecuaciones de recurrencia. Solo analiza la expresión directa."""

    def analyze_direct(
        self, equation: str, params: Dict[str, Any]
    ) -> NoneStrategyAgentOutput:
        """
        Analiza una expresión directa sin recursión usando el agente.
        """
        if params["has_recursion"]:
            raise ValueError(
                "Esta ecuación contiene términos recursivos. Use otra estrategia."
            )

        complexity_type = DirectExpressionAnalyzer.determine_complexity_type(params)

        context_info = f"""
INFORMACIÓN DETECTADA:
- Ecuación: {equation}
- Expresión normalizada: {params.get('normalized', '?')}
- Expresión extraída: {params.get('expression', '?')}
- Tipo detectado: {complexity_type}
- Es constante: {params.get('is_constant', False)}
- Es polinomial: {params.get('is_polynomial', False)}
- Grado (si aplica): {params.get('degree', 'N/A')}
- Tiene logaritmos: {params.get('is_logarithmic', False)}
- Es exponencial: {params.get('is_exponential', False)}
"""

        content = f"""Analiza esta expresión SIN RECURSIÓN para determinar su complejidad:

**Ecuación:** {equation}

{context_info}

Sigue los 4 pasos obligatorios:
1. Identificar la expresión f(n).
2. Identificar el término dominante.
3. Aplicar reglas de simplificación Big-O.
4. Determinar la complejidad final.

Responde con el objeto NoneStrategyAgentOutput completo."""

        try:
            result = self.invoke_simple(
                content=content, thread_id=f"none_{abs(hash(equation))}"
            )
            output = self.extract_response(result)

            if output is None:

                return self._create_fallback_output(equation, params, complexity_type)

            return output

        except Exception as e:
            if self.enable_verbose:
                print(f"[NoneStrategyAgent] Error: {e}")
            return self._create_fallback_output(equation, params, complexity_type)

    def _create_fallback_output(
        self, equation: str, params: Dict[str, Any], complexity_type: str
    ) -> NoneStrategyAgentOutput:
        """Crea una salida de respaldo cuando el agente falla."""
        expr = params.get("expression", "desconocida")

        if params.get("is_constant"):
            complexity = "O(1)"
            dominant = "constante"
        elif params.get("is_exponential"):
            complexity = "O(2^n)"
            dominant = "2^n"
        elif params.get("is_polynomial"):
            degree = params.get("degree", 1)
            if degree == 1:
                complexity = "O(n)"
                dominant = "n"
            elif degree == 2:
                complexity = "O(n²)"
                dominant = "n²"
            else:
                complexity = f"O(n^{degree})"
                dominant = f"n^{degree}"
        else:
            complexity = "O(?)"
            dominant = "desconocido"

        return NoneStrategyAgentOutput(
            expression=equation,
            expression_type=complexity_type,
            dominant_term=dominant,
            complexity=complexity,
            detailed_explanation=(
                f"Análisis directo de la expresión {equation}. "
                f"Tipo: {complexity_type}. "
                f"Complejidad determinada: {complexity}."
            ),
            simplification_steps=[
                "Expresión analizada directamente (sin recursión)",
                f"Término dominante identificado: {dominant}",
                f"Complejidad resultante: {complexity}",
            ],
        )


class NoneStrategy(RecurrenceStrategy):
    """
    Estrategia para analizar expresiones T(n) = f(n) SIN recursión.
    Determina la complejidad directamente de la expresión.
    """

    def __init__(self, enable_verbose: bool = False):
        super().__init__()
        self.name = "Análisis Directo (Sin Recursión)"
        self.description = (
            "Analiza expresiones T(n) = f(n) donde NO hay llamadas recursivas. "
            "Determina la complejidad directamente identificando el término dominante."
        )
        self.enable_verbose = enable_verbose
        self.agent: Optional[NoneStrategyAgent] = None

    def _get_agent(self) -> NoneStrategyAgent:
        """Lazy loading del agente."""
        if self.agent is None:
            if self.enable_verbose:
                print("[NoneStrategy] Inicializando agente...")
            self.agent = NoneStrategyAgent(
                model_type="Modelo_Codigo", enable_verbose=self.enable_verbose
            )
        return self.agent

    def solve(self, recurrenceEquation: str) -> Dict[str, Any]:
        """
        Analiza la expresión sin recursión para determinar su complejidad.
        """
        try:
            if self.enable_verbose:
                print(f"[NoneStrategy] Analizando: {recurrenceEquation}")

            params = DirectExpressionAnalyzer.parse_expression(recurrenceEquation)

            if params["has_recursion"]:
                raise ValueError(
                    "La ecuación contiene términos recursivos T(...). "
                    "Esta estrategia solo aplica a expresiones directas sin recursión."
                )

            if params["is_constant"]:
                return self._solve_constant(recurrenceEquation, params)

            if params["is_polynomial"] and not params["is_logarithmic"]:
                simple_result = self._try_simple_polynomial(recurrenceEquation, params)
                if simple_result:
                    return simple_result

            agent = self._get_agent()
            agent_output = agent.analyze_direct(recurrenceEquation, params)

            result = {
                "complexity": agent_output.complexity,
                "steps": self._format_steps(agent_output),
                "explanation": agent_output.detailed_explanation,
                "applicable": True,
                "method": self.name,
                "expression_type": agent_output.expression_type,
                "dominant_term": agent_output.dominant_term,
            }

            return result

        except ValueError as e:
            return {
                "complexity": "O(?)",
                "steps": [str(e)],
                "explanation": f"Esta estrategia no aplica. Razón: {str(e)}",
                "applicable": False,
                "method": self.name,
            }
        except Exception as e:
            if self.enable_verbose:
                print(f"[NoneStrategy] Error: {e}")
            return {
                "complexity": "O(?)",
                "steps": [f"Error: {str(e)}"],
                "explanation": f"Error durante el análisis: {str(e)}",
                "applicable": False,
                "method": self.name,
            }

    def _solve_constant(self, equation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resuelve casos constantes triviales sin agente."""
        return {
            "complexity": "O(1)",
            "steps": [
                "**Paso 1 - Identificar expresión:**",
                f"   {equation}",
                "",
                "**Paso 2 - Término dominante:**",
                "   Constante (no depende de n)",
                "",
                "**Paso 3 - Simplificación:**",
                "   Cualquier constante → O(1)",
                "",
                "**Paso 4 - Complejidad final:**",
                "   O(1) - Tiempo constante",
            ],
            "explanation": (
                f"La expresión {equation} es una constante que no depende de n. "
                "Por lo tanto, la complejidad es O(1) - tiempo constante."
            ),
            "applicable": True,
            "method": self.name,
            "expression_type": "Constante",
            "dominant_term": "constante",
        }

    def _try_simple_polynomial(
        self, equation: str, params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Intenta resolver polinomios simples sin agente."""
        degree = params.get("degree")

        if degree is None:
            return None

        if degree == 1:
            complexity_str = "O(n)"
            type_str = "Lineal"
        elif degree == 2:
            complexity_str = "O(n²)"
            type_str = "Cuadrática"
        elif degree == 3:
            complexity_str = "O(n³)"
            type_str = "Cúbica"
        else:
            complexity_str = f"O(n^{degree})"
            type_str = f"Polinomial (grado {degree})"

        return {
            "complexity": complexity_str,
            "steps": [
                "**Paso 1 - Identificar expresión:**",
                f"   {equation}",
                "",
                "**Paso 2 - Término dominante:**",
                f"   n^{degree}",
                "",
                "**Paso 3 - Simplificación:**",
                f"   En Big-O, los términos de menor grado se eliminan",
                f"   Las constantes se eliminan",
                "",
                "**Paso 4 - Complejidad final:**",
                f"   {complexity_str}",
            ],
            "explanation": (
                f"La expresión {equation} es {type_str.lower()}. "
                f"El término dominante es n^{degree}, por lo que la complejidad es {complexity_str}."
            ),
            "applicable": True,
            "method": self.name,
            "expression_type": type_str,
            "dominant_term": f"n^{degree}",
        }

    def _format_steps(self, agent_output: NoneStrategyAgentOutput) -> List[str]:
        """Formatea la salida del agente en pasos legibles."""
        steps = []

        steps.append("**Paso 1 - Identificar Expresión:**")
        steps.append(f"   {agent_output.expression}")
        steps.append("")

        steps.append("**Paso 2 - Término Dominante:**")
        steps.append(f"   {agent_output.dominant_term}")
        steps.append("")

        if agent_output.simplification_steps:
            steps.append("**Paso 3 - Simplificación:**")
            for step in agent_output.simplification_steps:
                steps.append(f"   {step}")
            steps.append("")

        steps.append("**Paso 4 - Complejidad Final:**")
        steps.append(f"   Tipo: {agent_output.expression_type}")
        steps.append(f"   Complejidad: {agent_output.complexity}")

        return steps

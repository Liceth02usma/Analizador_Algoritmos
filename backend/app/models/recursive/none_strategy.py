from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import re
import math

from ...external_services.Agentes.Agent import AgentBase
from .strategy_resolve import RecurrenceStrategy

# **********************************************
# 1. Schema de Respuesta (Sin Notación Asintótica)
# **********************************************


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
        description="Término dominante matemático (ej: 'n²', '1', 'n log n').",
    )
    complexity: str = Field(
        ...,
        description="Función de crecimiento dominante SIN notación Big-O (ej: '1', 'n', 'n^2').",
    )
    detailed_explanation: str = Field(
        ..., description="Explicación detallada de cómo se determinó la dominancia."
    )
    simplification_steps: List[str] = Field(
        default_factory=list,
        description="Pasos de simplificación algebraicos.",
    )


# **********************************************
# 2. Analizador de Expresiones (Reglas)
# **********************************************


class DirectExpressionAnalyzer:
    """
    Analiza expresiones T(n) sin recursión.
    """

    @staticmethod
    def parse_expression(equation: str) -> Dict[str, Any]:
        """Extrae información de expresiones no recursivas."""
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

        # Limpieza básica
        if "," in eq:
            main_equation = eq.split(",")[0].strip()
        else:
            main_equation = eq

        parts = main_equation.split("=")
        right_side = parts[1].strip() if len(parts) == 2 else main_equation

        # Detección de recursión (Safety Check)
        all_t_calls = re.findall(r"t\(([^\)]+)\)", right_side)
        recursive_calls = [call for call in all_t_calls if "n" in call]
        if recursive_calls:
            params["has_recursion"] = True
            return params

        # Análisis de la expresión
        if len(parts) >= 1:  # Flexibilidad si no hay "="
            expr = right_side
            params["expression"] = expr

            # Constante
            if re.match(r"^\d+$", expr):
                params["is_constant"] = True
                params["degree"] = 0

            # Exponencial (base^n)
            elif re.search(r"\d+\*\*n", expr):
                params["is_exponential"] = True

            # Polinomial
            elif re.search(r"n", expr):
                exp_matches = re.findall(r"n\*\*(\d+)", expr)

                # Check término lineal 'n' sin exponente
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
        if params["is_constant"]:
            return "Constante"
        elif params["is_exponential"]:
            return "Exponencial"
        elif params["is_logarithmic"] and params["is_polynomial"]:
            return "Logarítmico-Polinomial"
        elif params["is_logarithmic"]:
            return "Logarítmica"
        elif params["is_polynomial"]:
            d = params.get("degree", 1)
            if d == 1:
                return "Lineal"
            elif d == 2:
                return "Cuadrática"
            elif d == 3:
                return "Cúbica"
            return f"Polinomial (grado {d})"
        else:
            return "Desconocida"


# **********************************************
# 3. Agente de Resolución (Prompt Actualizado)
# **********************************************


class NoneStrategyAgent(AgentBase[NoneStrategyAgentOutput]):

    def __init__(self, model_type: str = "Modelo_Codigo", enable_verbose: bool = False):
        self.enable_verbose = enable_verbose
        super().__init__(model_type, provider="gemini")

    def _configure(self) -> None:
        self.response_format = NoneStrategyAgentOutput
        self.tools = []
        self.context_schema = None

        # PROMPT REESCRITO PARA EVITAR BIG-O
        self.SYSTEM_PROMPT = """Eres un experto en Análisis de Algoritmos.

**OBJETIVO:** Analizar expresiones directas $T(n) = f(n)$ y extraer la **FUNCIÓN DE CRECIMIENTO DOMINANTE**.

**REGLA DE ORO (FORMATO):**
1. En el campo `complexity`, **NO USES notación asintótica (O, Theta, Omega)**.
2. Escribe ÚNICAMENTE el término matemático simplificado.
3. Si el resultado es constante, escribe "1".

**EJEMPLOS DE RESPUESTA ESPERADA:**
- T(n) = 5        -> complexity: "1"
- T(n) = 3n + 10  -> complexity: "n"
- T(n) = 2n^2 + n -> complexity: "n^2"
- T(n) = n log n  -> complexity: "n log n"
- T(n) = 2^n + n³ -> complexity: "2^n"

**PROCESO:**
1. Identifica la expresión.
2. Encuentra el término que crece más rápido (dominante).
3. Elimina constantes multiplicativas y términos de menor orden.
4. Devuelve el término limpio.
"""

    def analyze_direct(
        self, equation: str, params: Dict[str, Any]
    ) -> NoneStrategyAgentOutput:

        if params["has_recursion"]:
            raise ValueError("Ecuación recursiva detectada. Estrategia incorrecta.")

        complexity_type = DirectExpressionAnalyzer.determine_complexity_type(params)

        context_info = f"""
DATOS:
- Ecuación: {equation}
- Expresión parseada: {params.get('expression', '?')}
- Tipo preliminar: {complexity_type}
- Grado polinomial: {params.get('degree', 'N/A')}
"""

        content = f"""Extrae el término dominante de: {equation}

{context_info}

Recuerda: Solo devuelve la función matemática (ej: "n^2"), SIN "O(...)". Si es constante devuelve "1".
"""

        try:
            result = self.invoke_simple(
                content=content, thread_id=f"none_{abs(hash(equation))}"
            )
            output = self.extract_response(result)

            if output is None:
                return self._create_fallback_output(equation, params, complexity_type)

            # Guardrail: Limpieza forzosa por si el LLM alucina
            output.complexity = (
                output.complexity.replace("O(", "").replace(")", "").strip()
            )

            return output

        except Exception as e:
            if self.enable_verbose:
                print(f"[NoneStrategyAgent] Error: {e}")
            return self._create_fallback_output(equation, params, complexity_type)

    def _create_fallback_output(
        self, equation: str, params: Dict[str, Any], complexity_type: str
    ) -> NoneStrategyAgentOutput:
        """Crea salida de respaldo SIN notación O()."""

        if params.get("is_constant"):
            complexity = "1"
            dominant = "1"
        elif params.get("is_exponential"):
            complexity = "2^n"
            dominant = "2^n"
        elif params.get("is_polynomial"):
            d = params.get("degree", 1)
            complexity = "n" if d == 1 else f"n^{d}"
            dominant = complexity
        else:
            complexity = "?"
            dominant = "?"

        return NoneStrategyAgentOutput(
            expression=equation,
            expression_type=complexity_type,
            dominant_term=dominant,
            complexity=complexity,  # Sin O()
            detailed_explanation="Análisis por reglas de respaldo.",
            simplification_steps=["Extracción directa de término dominante"],
        )


# **********************************************
# 4. Estrategia Principal
# **********************************************


class NoneStrategy(RecurrenceStrategy):
    """
    Estrategia para analizar expresiones directas SIN recursión.
    Devuelve la función de complejidad pura (sin O).
    """

    def __init__(self, enable_verbose: bool = False):
        super().__init__()
        self.name = "Análisis Directo"
        self.description = "Determina la función de complejidad dominante."
        self.enable_verbose = enable_verbose
        self.agent: Optional[NoneStrategyAgent] = None

    def _get_agent(self) -> NoneStrategyAgent:
        if self.agent is None:
            self.agent = NoneStrategyAgent(
                model_type="Gemini_Rapido", enable_verbose=self.enable_verbose
            )
        return self.agent

    def solve(self, recurrenceEquation: str) -> Dict[str, Any]:
        try:
            if self.enable_verbose:
                print(f"[NoneStrategy] Analizando: {recurrenceEquation}")

            params = DirectExpressionAnalyzer.parse_expression(recurrenceEquation)

            if params["has_recursion"]:
                raise ValueError("Contiene recursión, usar otra estrategia.")

            # Intentar resolver determinísticamente primero
            if params["is_constant"]:
                return self._solve_constant(recurrenceEquation, params)

            if params["is_polynomial"] and not params["is_logarithmic"]:
                simple_result = self._try_simple_polynomial(recurrenceEquation, params)
                if simple_result:
                    return simple_result

            # Usar agente
            agent = self._get_agent()
            agent_output = agent.analyze_direct(recurrenceEquation, params)

            return {
                "complexity": agent_output.complexity,  # Sin O()
                "steps": self._format_steps(agent_output),
                "explanation": agent_output.detailed_explanation,
                "applicable": True,
                "method": self.name,
                "expression_type": agent_output.expression_type,
            }

        except ValueError as e:
            return {"applicable": False, "explanation": str(e), "complexity": "N/A"}
        except Exception as e:
            return {
                "applicable": False,
                "explanation": f"Error: {str(e)}",
                "complexity": "Error",
            }

    def _solve_constant(self, equation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resuelve casos constantes determinísticamente sin O()."""
        return {
            "complexity": "1",  # Antes O(1)
            "steps": [
                f"Expresión: {equation}",
                "Término dominante: Constante",
                "Simplificación: 1",
            ],
            "explanation": "La expresión es constante, no depende de n.",
            "applicable": True,
            "method": self.name,
            "expression_type": "Constante",
            "dominant_term": "1",
        }

    def _try_simple_polynomial(
        self, equation: str, params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Resuelve polinomios simples sin O()."""
        degree = params.get("degree")
        if degree is None:
            return None

        # Definir strings sin O()
        if degree == 1:
            comp_str = "n"
            type_str = "Lineal"
        elif degree == 2:
            comp_str = "n^2"
            type_str = "Cuadrática"
        elif degree == 3:
            comp_str = "n^3"
            type_str = "Cúbica"
        else:
            comp_str = f"n^{degree}"
            type_str = f"Polinomial (grado {degree})"

        return {
            "complexity": comp_str,  # Sin O()
            "steps": [
                f"Expresión: {equation}",
                f"Término dominante: n^{degree}",
                f"Resultado: {comp_str}",
            ],
            "explanation": f"Expresión {type_str.lower()} dominada por n^{degree}.",
            "applicable": True,
            "method": self.name,
            "expression_type": type_str,
            "dominant_term": f"n^{degree}",
        }

    def _format_steps(self, out: NoneStrategyAgentOutput) -> List[str]:
        steps = []
        steps.append(f"**Expresión:** {out.expression}")
        steps.append(f"**Término Dominante:** {out.dominant_term}")
        if out.simplification_steps:
            steps.append("**Simplificación:**")
            steps.extend([f" - {s}" for s in out.simplification_steps])
        steps.append(f"**Resultado Final:** {out.complexity}")
        return steps

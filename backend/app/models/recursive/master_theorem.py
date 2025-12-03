from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import re
import math

# Importación segura de SymPy
try:
    from sympy import symbols, limit, oo, log, sympify, zoo, Function, Symbol

    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

from ...external_services.Agentes.Agent import AgentBase
from .strategy_resolve import RecurrenceStrategy


# **********************************************
# 1. Schema de Respuesta (Sin Notación Asintótica)
# **********************************************


class MasterTheoremAgentOutput(BaseModel):
    """Schema estructurado para la respuesta del agente del Teorema Maestro."""

    a: int = Field(..., description="Parámetro 'a': número de subproblemas.")
    b: int = Field(..., description="Parámetro 'b': factor de división de n.")
    f_n: str = Field(..., description="Función de trabajo adicional f(n).")
    log_b_a: str = Field(..., description="Valor calculado de n^(log_b(a)).")
    comparison: str = Field(
        ...,
        description="Explicación de la comparación del límite (ej: 'f(n) crece más lento que n^E').",
    )
    case_id: str = Field(
        ...,
        description="Caso del Teorema Maestro identificado (Caso 1, Caso 2 o Caso 3).",
    )
    complexity: str = Field(
        ...,
        description="Término dominante final SIN notación O/Theta (ej: 'n log n', 'n^2'). NO escribir 'O(...)'.",
    )
    detailed_explanation: str = Field(
        ...,
        description="Explicación pedagógica paso a paso justificando el cálculo de SymPy.",
    )


# **********************************************
# 2. Analizador de Ecuaciones
# **********************************************


class MasterEquationAnalyzer:
    """
    Analiza la ecuación y extrae los parámetros a, b, f(n).
    """

    @staticmethod
    def parse_equation(equation: str) -> Dict[str, Any]:
        """Extrae a, b, y f(n) de ecuaciones de la forma T(n) = aT(n/b) + f(n)."""
        eq = equation.replace(" ", "").lower()

        params = {
            "original": equation,
            "normalized": eq,
            "a": None,
            "b": None,
            "f_n": None,
            "is_master_form": False,
        }

        # Regex mejorado para capturar T(n) = a T(n/b) + f(n)
        # Maneja casos donde 'a' no está presente (implícito 1)
        master_pattern = r"t\(n\)=(\d*)t\(n/(\d+)\)\s*(?:\+)?\s*(.*)"
        master_matches = re.findall(master_pattern, eq)

        if master_matches:
            match = master_matches[0]
            a_str, b_str, f_n_raw = match

            params["a"] = int(a_str) if a_str else 1
            params["b"] = int(b_str)

            # Limpieza de f(n)
            f_n = f_n_raw.replace("t(n)=", "").replace("+", "").strip()
            params["f_n"] = f_n if f_n else "0"  # f(n) no debería ser vacío

            if params["a"] >= 1 and params["b"] > 1:
                params["is_master_form"] = True

        return params


# **********************************************
# 3. Agente de Resolución (Con SymPy)
# **********************************************


class MasterTheoremAgent(AgentBase[MasterTheoremAgentOutput]):
    """
    Agente especializado en Teorema Maestro asistido por cálculo simbólico (SymPy).
    """

    def __init__(self, model_type: str = "Gemini_Rapido", enable_verbose: bool = False):
        self.enable_verbose = enable_verbose
        super().__init__(model_type, provider="gemini")

    def _configure(self) -> None:
        self.response_format = MasterTheoremAgentOutput
        self.tools = []
        self.context_schema = None

        # PROMPT ACTUALIZADO: Enfocado en interpretación y prohibiendo Big-O en salida
        self.SYSTEM_PROMPT = """Eres un experto en Análisis de Algoritmos. Tu tarea es interpretar los cálculos matemáticos del Teorema Maestro proporcionados por SymPy y generar una explicación pedagógica.

**OBJETIVO:** Validar y explicar el análisis del Teorema Maestro para $T(n) = aT(n/b) + f(n)$.

**TU FUENTE DE VERDAD (SymPy):**
Recibirás el cálculo del límite $\lim_{n \to \infty} \frac{f(n)}{n^{\log_b a}}$.
- Si Límite = 0 $\to$ Domina $n^{\log_b a}$ (Caso 1).
- Si Límite = Constante $\to$ Son iguales (Caso 2).
- Si Límite = $\infty$ $\to$ Domina $f(n)$ (Caso 3).

**REGLA DE ORO (FORMATO):**
En el campo `complexity`, **NO USES NOTACIÓN ASINTÓTICA (O, Theta, Omega)**.
- INCORRECTO: "O(n^2)", "Theta(n log n)"
- CORRECTO: "n^2", "n log n", "n^2.58"

**PROCESO DE EXPLICACIÓN:**
1. Confirma los parámetros $a, b, f(n)$.
2. Explica el cálculo de $E = \log_b a$ (exponente crítico).
3. Interpreta el límite calculado por SymPy para comparar $f(n)$ vs $n^E$.
4. Concluye con el Caso y la complejidad final (solo el término).
"""

    def _analyze_with_sympy(self, a: int, b: int, f_n_str: str) -> Dict[str, Any]:
        """
        Usa SymPy para calcular el límite y determinar el caso científicamente.
        Comparación: L = lim(n->oo) f(n) / n^(log_b a)
        """
        if not SYMPY_AVAILABLE:
            return {"status": "error", "reason": "SymPy no instalado"}

        try:
            n = Symbol("n", positive=True, real=True)

            # 1. Calcular exponente crítico E = log_b(a)
            # log(a, b) en SymPy es logaritmo base b de a
            critical_exponent = log(a, b)
            critical_term = n**critical_exponent

            # 2. Parsear f(n)
            # Limpieza para SymPy: 'log' suele ser base e, para CS usamos base 2 o 10,
            # pero para límites al infinito la base del logaritmo es una constante que no afecta el 0 o inf.
            # Reemplazamos ^ por ** para sintaxis python
            f_n_clean = f_n_str.replace("^", "**").replace("log", "log")
            f_n_expr = sympify(f_n_clean)

            # 3. Calcular Límite: Ratio = f(n) / n^E
            ratio = f_n_expr / critical_term
            limit_val = limit(ratio, n, oo)

            # 4. Determinar Caso basado en el límite
            case_detected = "Desconocido"
            explanation = ""

            if limit_val == 0:
                case_detected = "Caso 1"
                explanation = f"El límite es 0, lo que significa que el término crítico n^{critical_exponent} crece más rápido que f(n)."
            elif limit_val == oo:  # Infinito
                case_detected = "Caso 3"
                explanation = f"El límite es infinito, lo que significa que f(n) crece más rápido que n^{critical_exponent}."
                # Nota: Aquí faltaría chequear condición de regularidad, se lo dejamos al Agente explicar.
            elif limit_val.is_constant() and limit_val != 0:
                case_detected = "Caso 2"
                explanation = f"El límite es una constante ({limit_val}), lo que significa que f(n) y n^{critical_exponent} crecen a la misma velocidad."
            else:
                # Caso logarítmico especial del Caso 2 (n^E log^k n)
                # Si el limite es raro, SymPy podría devolver una expresión
                case_detected = "Caso 2 (Extendido)"
                explanation = "Comparación compleja, posible factor logarítmico extra."

            return {
                "status": "success",
                "limit_value": str(limit_val),
                "critical_exponent": str(
                    critical_exponent.evalf(3)
                ),  # Valor numérico aprox
                "case_detected": case_detected,
                "sympy_explanation": explanation,
            }

        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def solve_complex(
        self, equation: str, params: Dict[str, Any]
    ) -> MasterTheoremAgentOutput:

        # 1. Ejecutar Análisis Matemático (SymPy)
        sympy_analysis = self._analyze_with_sympy(
            params["a"], params["b"], params["f_n"]
        )

        if self.enable_verbose and sympy_analysis.get("status") == "success":
            print(
                f"[MasterTheoremAgent] 🧮 SymPy Límite: {sympy_analysis['limit_value']} -> {sympy_analysis['case_detected']}"
            )

        # 2. Construir Contexto Rico para el Agente
        context_info = f"""
DATOS EXTRAÍDOS:
- a = {params['a']}
- b = {params['b']}
- f(n) = {params['f_n']}

ANÁLISIS MATEMÁTICO (SymPy):
- Exponente crítico (log_b a): {sympy_analysis.get('critical_exponent', '?')}
- Límite calculado (f(n) / n^E): {sympy_analysis.get('limit_value', '?')}
- Caso Sugerido: {sympy_analysis.get('case_detected', '?')}
- Interpretación: {sympy_analysis.get('sympy_explanation', '')}
"""

        content = f"""Analiza la recurrencia: {equation}
        
{context_info}

Recuerda: NO uses O() en el campo 'complexity'. Solo la función."""

        # 3. Invocar al LLM
        thread_id = f"master_{abs(hash(equation))}"
        result = self.invoke_simple(content=content, thread_id=thread_id)
        output = self.extract_response(result)

        if output is None:
            # Fallback en caso de error grave
            return MasterTheoremAgentOutput(
                a=params["a"],
                b=params["b"],
                f_n=params["f_n"],
                log_b_a="?",
                comparison="Error",
                case_id="Error",
                complexity="Error",
                detailed_explanation="El agente no respondió.",
            )

        # Guardrail final: Limpiar O() si el agente alucinó
        clean_complexity = (
            output.complexity.replace("O(", "")
            .replace("Theta(", "")
            .replace(")", "")
            .strip()
        )
        output.complexity = clean_complexity

        return output


# **********************************************
# 4. Estrategia Principal
# **********************************************


class MasterTheoremStrategy(RecurrenceStrategy):
    """
    Estrategia híbrida para resolver recurrencias usando el Teorema Maestro + SymPy.
    """

    def __init__(self, enable_verbose: bool = False):
        super().__init__()
        self.name = "Teorema Maestro"
        self.description = "Resuelve T(n) = aT(n/b) + f(n) usando límites con SymPy."
        self.enable_verbose = enable_verbose
        self.agent: Optional[MasterTheoremAgent] = None

    def _get_agent(self) -> MasterTheoremAgent:
        if self.agent is None:
            if self.enable_verbose:
                print("[MasterTheoremStrategy] Inicializando agente...")
            self.agent = MasterTheoremAgent(
                model_type="Gemini_Rapido", enable_verbose=self.enable_verbose
            )
        return self.agent

    def solve(self, recurrenceEquation: str) -> Dict[str, Any]:
        try:
            if self.enable_verbose:
                print(f"\n[MasterTheoremStrategy] Analizando: {recurrenceEquation}")

            params = MasterEquationAnalyzer.parse_equation(recurrenceEquation)

            if not params["is_master_form"]:
                raise ValueError(
                    "La ecuación no sigue el formato T(n) = aT(n/b) + f(n) requerido."
                )

            agent = self._get_agent()
            agent_output = agent.solve_complex(recurrenceEquation, params)

            # Construir respuesta final
            # Nota: 'complexity' aquí viene SIN O(). Si el frontend necesita O(),
            # se puede agregar en la visualización, pero cumplimos el requisito de "no dar la respuesta en ninguna cota"
            # en el campo raw.

            result = {
                "complexity": agent_output.complexity,  # Solo "n^2"
                "steps": self._format_steps(agent_output),
                "explanation": agent_output.detailed_explanation,
                "applicable": True,
                "method": self.name,
                "case": agent_output.case_id,
                # Metadata útil
                "a": agent_output.a,
                "b": agent_output.b,
                "log_b_a": agent_output.log_b_a,
            }

            return result

        except ValueError as e:
            return {
                "complexity": "N/A",
                "steps": [],
                "explanation": f"No aplicable: {str(e)}",
                "applicable": False,
                "method": self.name,
            }
        except Exception as e:
            return {
                "complexity": "Error",
                "steps": [],
                "explanation": f"Error interno: {str(e)}",
                "applicable": False,
                "method": self.name,
            }

    def _format_steps(self, out: MasterTheoremAgentOutput) -> List[str]:
        steps = []
        steps.append("**Paso 1 - Parámetros:**")
        steps.append(f" a = {out.a}, b = {out.b}")
        steps.append(f" f(n) = {out.f_n}")
        steps.append("")
        steps.append(f"**Paso 2 - Exponente Crítico:**")
        steps.append(f" log_{out.b}({out.a}) ≈ {out.log_b_a}")
        steps.append("")
        steps.append("**Paso 3 - Análisis de Límite (SymPy):**")
        steps.append(f" {out.comparison}")
        steps.append("")
        steps.append(f"**Paso 4 - Conclusión:**")
        steps.append(f" Aplica **{out.case_id}**")
        steps.append(f" Término dominante: {out.complexity}")  # Sin O()
        return steps

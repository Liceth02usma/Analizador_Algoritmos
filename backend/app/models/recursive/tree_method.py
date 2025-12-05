from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import re
import math

# Importación segura de SymPy
try:
    from sympy import symbols, summation, log, simplify, sympify, oo, Function, Symbol
    from sympy.abc import i, n, k

    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

from ...external_services.Agentes.Agent import AgentBase
from .strategy_resolve import RecurrenceStrategy

# **********************************************
# 1. Schema de Respuesta del Agente
# **********************************************


class TreeMethodAgentOutput(BaseModel):
    """Schema estructurado para la respuesta del agente."""

    tree_depth: str = Field(
        ..., description="Profundidad del árbol (ej: 'log_2(n)', 'n')"
    )
    levels_expansion: List[str] = Field(
        default_factory=list, description="Expansión nivel por nivel del árbol"
    )
    work_per_level: List[str] = Field(
        default_factory=list, description="Trabajo calculado en cada nivel"
    )
    total_sum: str = Field(..., description="Suma total de todos los niveles (fórmula)")
    sum_simplification: str = Field(
        ...,
        description="Resultado simplificado de la suma (calculado por SymPy si es posible)",
    )
    complexity: str = Field(
        ...,
        description="Término dominante final SIN notación Big-O (ej: 'n log n', 'n^2').",
    )
    detailed_explanation: str = Field(
        ..., description="Explicación completa del proceso paso a paso"
    )


# **********************************************
# 2. Analizador de Ecuaciones (Reglas Rápidas)
# **********************************************


class EquationAnalyzer:
    """
    Analiza la ecuación y extrae parámetros básicos usando reglas.
    Identifica casos triviales que no necesitan agente.
    """

    @staticmethod
    def parse_equation(equation: str) -> Dict[str, Any]:
        """Extrae componentes básicos de la ecuación."""
        eq = equation.replace(" ", "").lower()

        params = {
            "original": equation,
            "normalized": eq,
            "a": None,
            "b": None,
            "k": None,
            "f_n": None,
            "type": None,
            "is_trivial": False,
            "trivial_result": None,
            "has_summation": False,
            "summation_params": {},
        }

        # Detectar sumatorias
        summation_symbols = ["σ", "∑", "sum", "Σ"]
        has_summation = any(symbol in equation for symbol in summation_symbols)

        if has_summation:
            params["has_summation"] = True
            params["type"] = "summation"
            summation_result = EquationAnalyzer._parse_summation(equation)
            if summation_result:
                params["summation_params"] = summation_result
                params["is_trivial"] = False
                return params

        # Detectar T(n) = aT(n/b) + f(n)
        div_pattern = r"(\d*)t\(n/(\d+)\)"
        div_matches = re.findall(div_pattern, eq)

        if div_matches:
            params["type"] = "divide_conquer"
            coef = div_matches[0][0]
            params["a"] = int(coef) if coef else 1
            if not coef and len(div_matches) > 1:  # Caso T(n/3) + T(n/3)
                params["a"] = len(div_matches)

            params["b"] = int(div_matches[0][1])

            work = re.sub(r"\d*t\([^)]+\)", "", eq)
            work = (
                work.replace("t(n)=", "")
                .replace("=", "")
                .replace("+", "")
                .replace("-", "")
                .strip()
            )
            params["f_n"] = work if work else "1"

        # Detectar T(n) = T(n-k) + f(n)
        sub_pattern = r"t\(n-(\d+)\)"
        sub_matches = re.findall(sub_pattern, eq)

        if sub_matches and not div_matches:
            params["type"] = "linear"
            params["k"] = int(sub_matches[0])
            work = re.sub(r"t\([^)]+\)", "", eq)
            work = work.replace("t(n)=", "").replace("=", "").replace("+", "").strip()
            params["f_n"] = work if work else "1"

        # Detectar casos TRIVIALES
        params["is_trivial"] = EquationAnalyzer._check_trivial_case(params)
        if params["is_trivial"]:
            params["trivial_result"] = EquationAnalyzer._solve_trivial(params)

        return params

    @staticmethod
    def _parse_summation(equation: str) -> Optional[Dict[str, Any]]:
        # (Lógica de parseo idéntica a la anterior, se mantiene igual)
        try:
            factor_pattern = r"\(1/\(?([^)]+)\)?\)"
            factor_match = re.search(factor_pattern, equation)
            multiplicative_factor = (
                factor_match.group(1).strip() if factor_match else None
            )

            summation_pattern = r"[Σ∑σsum]\s*\[i=(\d+)\s+to\s+([^\]]+)\]"
            summation_match = re.search(summation_pattern, equation, re.IGNORECASE)

            if not summation_match:
                return None
            lower_bound, upper_bound = (
                summation_match.group(1).strip(),
                summation_match.group(2).strip(),
            )

            inner_pattern = r"donde\s+t\(i\)\s*=\s*([^,]+)"
            inner_match = re.search(inner_pattern, equation, re.IGNORECASE)
            inner_recurrence = inner_match.group(1).strip() if inner_match else None

            base_pattern = r"t\((\d+)\)\s*=\s*(\d+)"
            base_match = re.search(base_pattern, equation, re.IGNORECASE)
            base_case = base_match.group(1) if base_match else None
            base_value = base_match.group(2) if base_match else None

            return {
                "original": equation,
                "multiplicative_factor": multiplicative_factor,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "inner_recurrence": inner_recurrence,
                "base_case": base_case,
                "base_value": base_value,
            }
        except Exception:
            return None

    @staticmethod
    def _check_trivial_case(params: Dict[str, Any]) -> bool:
        # Caso 1: T(n) = T(n-1) + c (trabajo constante)
        if (
            params["type"] == "linear"
            and params["k"] == 1
            and params["f_n"] in ["1", "c", ""]
        ):
            return True
        return False

    @staticmethod
    def _solve_trivial(params: Dict[str, Any]) -> Dict[str, Any]:
        """Resuelve casos triviales. CORREGIDO: Retorna 'n' sin O()."""
        if params["type"] == "linear" and params["k"] == 1:
            # T(n) = T(n-1) + c
            return {
                "complexity": "n",  # CORREGIDO: Sin O()
                "steps": [
                    f"Nivel 0: T(n) -> Trabajo: {params['f_n']}",
                    f"Nivel 1: T(n-1) -> Trabajo: {params['f_n']}",
                    "...",
                    f"Nivel n: T(0) -> Trabajo: {params['f_n']}",
                    f"Total: {params['f_n']} × n niveles = n",
                ],
                "explanation": "Recurrencia lineal simple con trabajo constante por nivel. Profundidad n.",
                "applicable": True,
                "method": "Método del Árbol (trivial)",
            }
        return None


# **********************************************
# 3. Agente de Resolución Compleja
# **********************************************


class TreeMethodAgent(AgentBase[TreeMethodAgentOutput]):

    def __init__(self, model_type: str = "Modelo_Codigo", enable_verbose: bool = False):
        self.enable_verbose = enable_verbose
        super().__init__(model_type, provider="gemini")

    def _configure(self) -> None:
        self.response_format = TreeMethodAgentOutput
        self.tools = []
        self.context_schema = None

        self.SYSTEM_PROMPT = """Eres un experto en Análisis de Algoritmos y el Método del Árbol.

**OBJETIVO:** Explicar el desarrollo del árbol de recursión basándote en la SUMA EXACTA calculada matemáticamente (SymPy) que te será proporcionada.

**REGLA DE ORO (FORMATO):**
1. En el campo `complexity`, **NO uses notación asintótica (O, Theta, Omega)**.
2. Escribe solo el término dominante.
   - CORRECTO: "n log n", "n^2", "2^n"
   - INCORRECTO: "O(n log n)", "Theta(n^2)"

**TU TAREA:**
1. Recibirás los datos del árbol (profundidad, trabajo por nivel) calculados por SymPy.
2. Tu trabajo es generar la explicación pedagógica y llenar los campos del schema.
3. Debes detallar la expansión del árbol nivel por nivel para que el estudiante entienda de dónde sale la suma.

**FLUJO DE PENSAMIENTO:**
1. ¿Cuál es la profundidad del árbol? (Dada por contexto o calculada: log_b n).
2. ¿Cuál es el trabajo en el nivel i? (Dado por contexto: a^i * f(n/b^i)).
3. ¿Cuál es la suma total? (Dada por SymPy).
4. ¿Cuál es el término dominante? (Simplificación final).
"""

    def _compute_tree_summation(self, params: Dict[str, Any]) -> Dict[str, str]:
        """
        Usa SymPy para calcular la suma exacta de los niveles del árbol.
        Suma = Sigma(i=0 to h) [Nodos_i * Costo_Nodo_i]
        """
        if not SYMPY_AVAILABLE:
            return {"status": "error", "reason": "SymPy no instalado"}

        try:
            n_sym = Symbol("n", positive=True, real=True)
            i = Symbol("i", integer=True, nonnegative=True)

            # Extraer f(n)
            f_n_str = params.get("f_n", "1").replace("^", "**")
            try:
                f_n_expr = sympify(f_n_str)
            except:
                f_n_expr = 1  # Fallback seguro

            sum_expr = None
            depth_expr = None
            work_i_expr = None

            # CASO 1: Divide y Vencerás (T(n) = aT(n/b) + f(n))
            if params.get("type") == "divide_conquer":
                a = params.get("a", 1)
                b = params.get("b", 2)

                # Altura h = log_b(n)
                h = log(n_sym, b)
                depth_expr = h

                # Nodos en nivel i: a^i
                nodes_i = a**i

                # Tamaño de problema en nivel i: n / b^i
                size_i = n_sym / (b**i)

                # Trabajo por nodo: f(size_i)
                # Sustituimos 'n' en f(n) por 'size_i'
                cost_node_i = f_n_expr.subs(n_sym, size_i)

                # Trabajo total nivel i
                work_i_expr = nodes_i * cost_node_i

                # Sumatoria
                sum_expr = summation(work_i_expr, (i, 0, h))

            # CASO 2: Decremento Lineal (T(n) = T(n-k) + f(n))
            elif params.get("type") == "linear":
                k_val = params.get("k", 1)

                # Altura h = n / k
                h = n_sym / k_val
                depth_expr = h

                # En lineal puro (T(n-k)), usualmente hay 1 nodo por nivel
                # Trabajo total nivel i = f(n - i*k)
                size_i = n_sym - i * k_val
                work_i_expr = f_n_expr.subs(n_sym, size_i)

                sum_expr = summation(work_i_expr, (i, 0, h))

            else:
                return {
                    "status": "skipped",
                    "reason": "Tipo no soportado por SymPy auto",
                }

            # Simplificar resultados
            total_sum_simplified = simplify(sum_expr)

            # Intentar obtener el término dominante (heurística simple para contexto)
            # Para el agente, le damos la expresión simplificada

            return {
                "status": "success",
                "depth": str(depth_expr),
                "work_per_level_formula": str(work_i_expr),
                "total_sum": str(total_sum_simplified),
                "simplified": str(
                    total_sum_simplified
                ),  # SymPy a veces deja la Sum(...) si no puede cerrar
            }

        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def solve_complex(
        self, equation: str, params: Dict[str, Any]
    ) -> TreeMethodAgentOutput:

        # 1. CÁLCULO SIMBÓLICO CON SYMPY
        sympy_data = self._compute_tree_summation(params)

        if self.enable_verbose:
            print(f"[TreeMethodAgent] 🧮 SymPy Calc: {sympy_data.get('status')}")
            if sympy_data.get("status") == "success":
                print(f"   Suma Total: {sympy_data.get('total_sum')}")

        # 2. INYECCIÓN DE CONTEXTO
        context_info = f"""
ANÁLISIS MATEMÁTICO (SYMPY):
- Profundidad (h): {sympy_data.get('depth', 'A determinar')}
- Fórmula de trabajo en nivel i: {sympy_data.get('work_per_level_formula', 'A determinar')}
- SUMA TOTAL EXACTA: {sympy_data.get('total_sum', 'A determinar')}
"""

        # Agregar contexto específico del tipo
        if params.get("type") == "summation":
            summation_params = params.get("summation_params", {})
            context_info += f"""
INFO ADICIONAL (SUMATORIA):
- Factor: 1/{summation_params.get('multiplicative_factor')}
- Límites: {summation_params.get('lower_bound')} a {summation_params.get('upper_bound')}
"""

        content = f"""Resuelve por Método del Árbol: {equation}

{context_info}

Recuerda: NO USES Big-O en 'complexity'. Solo la función."""

        # 3. LLAMADA AL AGENTE
        thread_id = f"tree_{abs(hash(equation))}"
        try:
            result = self.invoke_simple(content=content, thread_id=thread_id)
            output = self.extract_response(result)

            if output is None:
                raise ValueError("Agente retornó None")

            # Guardrail final
            output.complexity = (
                output.complexity.replace("O(", "")
                .replace("Theta(", "")
                .replace(")", "")
                .strip()
            )

            return output

        except Exception as e:
            # Fallback
            return TreeMethodAgentOutput(
                tree_depth="?",
                levels_expansion=[],
                work_per_level=[],
                total_sum="?",
                sum_simplification="?",
                complexity="Error",
                detailed_explanation=str(e),
            )


# **********************************************
# 4. Estrategia Principal
# **********************************************


class TreeMethodStrategy(RecurrenceStrategy):

    def __init__(self, enable_verbose: bool = False):
        super().__init__()
        self.name = "Método del Árbol"
        self.description = "Expansión del árbol de recursión asistida por SymPy."
        self.enable_verbose = enable_verbose
        self.agent: Optional[TreeMethodAgent] = None

    def _get_agent(self) -> TreeMethodAgent:
        if self.agent is None:
            self.agent = TreeMethodAgent(
                model_type="Gemini_Rapido", enable_verbose=self.enable_verbose
            )
        return self.agent

    def solve(self, recurrenceEquation: str) -> Dict[str, Any]:
        try:
            if self.enable_verbose:
                print(f"\n[TreeMethodStrategy] Analizando: {recurrenceEquation}")

            # Paso 1: Analizar
            params = EquationAnalyzer.parse_equation(recurrenceEquation)

            # Paso 2: Trivial
            if params["is_trivial"] and params["trivial_result"]:
                if self.enable_verbose:
                    print("[TreeMethodStrategy] Caso trivial detectado.")
                return params["trivial_result"]

            # Paso 3: Agente + SymPy
            agent = self._get_agent()
            agent_output = agent.solve_complex(recurrenceEquation, params)

            result = {
                "complexity": agent_output.complexity,  # Sin O()
                "steps": self._format_steps(agent_output),
                "explanation": agent_output.detailed_explanation,
                "applicable": True,
                "method": self.name,
                "tree_depth": agent_output.tree_depth,
                "levels_detail": agent_output.levels_expansion,
                "work_per_level": agent_output.work_per_level,
                "sum_formula": agent_output.total_sum,
                "sum_simplification": agent_output.sum_simplification,
            }

            return result

        except Exception as e:
            return {
                "complexity": "Error",
                "steps": [str(e)],
                "explanation": f"Fallo en estrategia: {str(e)}",
                "applicable": False,
                "method": self.name,
            }

    def _format_steps(self, out: TreeMethodAgentOutput) -> List[str]:
        steps = []
        steps.append(f"**Profundidad:** {out.tree_depth}")
        steps.append("**Expansión por niveles:**")
        steps.extend(
            [f"  {l}" for l in out.levels_expansion[:3]]
        )  # Solo primeros 3 para resumen
        steps.append("  ...")
        steps.append(f"**Suma Total (SymPy):** {out.total_sum}")
        steps.append(f"**Complejidad:** {out.complexity}")
        return steps

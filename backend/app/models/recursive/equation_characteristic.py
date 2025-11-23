from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field
import re
import math
import cmath

from ...external_services.Agentes.Agent import AgentBase
from .strategy_resolve import RecurrenceStrategy

# **********************************************
# 1. Schema de Respuesta del Agente
# **********************************************


class CharacteristicEquationAgentOutput(BaseModel):
    """Schema estructurado para la respuesta del agente."""

    recurrence_form: str = Field(
        ..., description="Forma de la recurrencia identificada"
    )
    coefficients: List[str] = Field(
        default_factory=list, description="Coeficientes de la recurrencia lineal"
    )
    characteristic_equation: str = Field(
        ..., description="Ecuación característica formada"
    )
    roots: List[str] = Field(
        default_factory=list, description="Raíces de la ecuación característica"
    )
    general_solution: str = Field(
        ..., description="Solución general en términos de constantes"
    )
    particular_solution: Optional[str] = Field(
        None, description="Solución particular si hay término no homogéneo"
    )
    final_solution: str = Field(..., description="Solución final de la recurrencia")
    complexity: str = Field(..., description="Complejidad asintótica en notación Big-O")
    detailed_explanation: str = Field(
        ..., description="Explicación completa paso a paso"
    )


# **********************************************
# 2. Analizador de Ecuaciones Características (Reglas)
# **********************************************


class CharacteristicAnalyzer:
    """
    Analiza ecuaciones lineales con coeficientes constantes.
    Resuelve casos estándar sin necesidad de agente.
    """

    @staticmethod
    def parse_equation(equation: str) -> Dict[str, Any]:
        """
        Extrae parámetros de la ecuación lineal.
        Formas esperadas:
        - T(n) = aT(n-1) + bT(n-2) + ... + g(n)
        - T(n) = T(n-1) + T(n-2) + c
        - T_avg(n) = (1/k) × Σ[i=a to b] T(i), donde T(i) = T(i-1) + c
        """
        eq = equation.replace(" ", "").lower()

        params = {
            "original": equation,
            "normalized": eq,
            "order": 0,  # Orden de la recurrencia
            "coefficients": [],  # Coeficientes [c1, c2, ..., ck]
            "delays": [],  # Retrasos [1, 2, ..., k]
            "non_homogeneous": None,  # Término no homogéneo g(n)
            "is_homogeneous": True,  # Si es homogénea
            "is_constant_coef": True,  # Si tiene coeficientes constantes
            "is_applicable": False,  # Si la ecuación característica aplica
            "is_standard": False,  # Si es caso estándar (resolvible con reglas)
            "standard_result": None,  # Resultado directo
            "has_summation": False,  # Si contiene sumatoria
            "summation_params": {},  # Parámetros de la sumatoria
        }

        # Detectar sumatorias
        summation_symbols = ["σ", "∑", "sum", "Σ"]
        has_summation = any(symbol in equation for symbol in summation_symbols)

        if has_summation:
            params["has_summation"] = True
            params["is_applicable"] = True
            summation_result = CharacteristicAnalyzer._parse_summation(equation)
            if summation_result:
                params["summation_params"] = summation_result
                params["is_standard"] = True
                params["standard_result"] = CharacteristicAnalyzer._solve_summation(
                    summation_result
                )
                return params

        # Detectar términos T(n-k)
        # Patrón: coeficiente opcional + t(n-delay)
        term_pattern = r"(\d*)t\(n-(\d+)\)"
        matches = re.findall(term_pattern, eq)

        if not matches:
            params["is_applicable"] = False
            return params

        # Extraer coeficientes y delays
        coef_delay_pairs = []
        for coef_str, delay_str in matches:
            coef = int(coef_str) if coef_str else 1
            delay = int(delay_str)
            coef_delay_pairs.append((coef, delay))

        # Ordenar por delay (menor a mayor)
        coef_delay_pairs.sort(key=lambda x: x[1])

        params["coefficients"] = [pair[0] for pair in coef_delay_pairs]
        params["delays"] = [pair[1] for pair in coef_delay_pairs]
        params["order"] = max(params["delays"]) if params["delays"] else 0

        # Extraer término no homogéneo g(n)
        work = re.sub(r"\d*t\([^)]+\)", "", eq)
        work = work.replace("t(n)=", "").replace("+", "").replace("-", "").strip()

        if work and work not in ["0", ""]:
            params["non_homogeneous"] = work
            params["is_homogeneous"] = False

        params["is_applicable"] = True

        # Verificar si es caso estándar
        if params["is_homogeneous"] and params["order"] <= 2:
            params["is_standard"] = True
            params["standard_result"] = CharacteristicAnalyzer._solve_standard(params)

        return params

    @staticmethod
    def _parse_summation(equation: str) -> Optional[Dict[str, Any]]:
        """
        Parsea ecuaciones con sumatorias.
        Formato esperado: T_avg(n) = (1/k) × Σ[i=a to b] T(i), donde T(i) = T(i-1) + c, T(base) = c
        También acepta: T_avg(n) = (1/k) × σ[i=aton] T(i), donde t(i) = t(i-1) + c
        """
        try:
            # Buscar factor multiplicativo (1/k) o (1/(k))
            factor_pattern = r"\(1/\(?([^)]+)\)?\)"
            factor_match = re.search(factor_pattern, equation)
            multiplicative_factor = None
            if factor_match:
                multiplicative_factor = factor_match.group(1).strip()

            # Buscar límites de la sumatoria con múltiples formatos:
            # Formato 1: Σ[i=a to b] (con espacios y "to")
            # Formato 2: σ[i=aton] (sin espacios)
            summation_pattern = r"[Σ∑σsum]\s*\[i=(\d+)\s*(?:to|TO)?\s*([^\]]+)\]"
            summation_match = re.search(summation_pattern, equation, re.IGNORECASE)

            if not summation_match:
                return None

            lower_bound = summation_match.group(1).strip()
            upper_bound = summation_match.group(2).strip()

            # Limpiar upper_bound: remover "to" si quedó pegado (ej: "ton" -> "n")
            if upper_bound.startswith("to"):
                upper_bound = upper_bound[2:].strip()
            # Extraer solo la variable si hay otros caracteres
            var_match = re.search(r"([a-zA-Z]+)", upper_bound)
            if var_match:
                upper_bound = var_match.group(1)

            # Buscar la recurrencia interna T(i) = ... o t(i) = ...
            # Formato 1: "donde T(i) = T(i-1) + c"
            # Formato 2: "dondet(i)=t(i-1)+c" (sin espacios)
            # Formato 3: ",dondet(i)=t(i-1)+c"
            inner_pattern = r"(?:,\s*)?donde\s*t\(i\)\s*=\s*([^,]+)"
            inner_match = re.search(inner_pattern, equation, re.IGNORECASE)

            inner_recurrence = None
            if inner_match:
                inner_recurrence = inner_match.group(1).strip()

            # Buscar caso base: T(base) = c
            base_pattern = r"t\((\d+)\)\s*=\s*(\d+)"
            base_match = re.search(base_pattern, equation, re.IGNORECASE)

            base_case = None
            base_value = None
            if base_match:
                base_case = base_match.group(1)
                base_value = base_match.group(2)

            return {
                "original": equation,
                "multiplicative_factor": multiplicative_factor,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "inner_recurrence": inner_recurrence,
                "base_case": base_case,
                "base_value": base_value,
            }
        except Exception as e:
            return None

    @staticmethod
    def _solve_summation(summation_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resuelve sumatorias del tipo T_avg(n) = (1/k) × Σ[i=a to b] T(i).
        Donde T(i) sigue una recurrencia lineal simple.
        """
        steps = []

        # Paso 1: Identificar la estructura
        steps.append("**Paso 1 - Identificar estructura de sumatoria:**")
        steps.append(f"   Ecuación: {summation_params['original']}")
        steps.append(
            f"   Factor multiplicativo: 1/{summation_params['multiplicative_factor']}"
        )
        steps.append(
            f"   Límites de sumatoria: i = {summation_params['lower_bound']} hasta {summation_params['upper_bound']}"
        )

        if summation_params["inner_recurrence"]:
            steps.append(
                f"   Recurrencia interna: T(i) = {summation_params['inner_recurrence']}"
            )
        if summation_params["base_case"]:
            steps.append(
                f"   Caso base: T({summation_params['base_case']}) = {summation_params['base_value']}"
            )
        steps.append("")

        # Paso 2: Expandir la recurrencia interna
        steps.append("**Paso 2 - Expandir recurrencia interna T(i):**")

        # Detectar patrón de la recurrencia interna
        inner_rec = summation_params.get("inner_recurrence", "").lower()

        # Caso común: T(i) = T(i-1) + c
        if "t(i-1)" in inner_rec:
            # Extraer constante c
            const_match = re.search(r"\+\s*(\d+)", inner_rec)
            c = int(const_match.group(1)) if const_match else 1
            base_val = int(summation_params.get("base_value", 0))
            base_idx = int(summation_params.get("base_case", 0))

            steps.append(f"   T(i) = T(i-1) + {c}")
            steps.append(f"   Expandiendo desde T({base_idx}) = {base_val}:")
            steps.append(f"      T({base_idx}) = {base_val}")
            steps.append(
                f"      T({base_idx+1}) = T({base_idx}) + {c} = {base_val + c}"
            )
            steps.append(
                f"      T({base_idx+2}) = T({base_idx+1}) + {c} = {base_val + 2*c}"
            )
            steps.append(f"      ...")
            steps.append(f"      T(i) = {base_val} + {c}·(i - {base_idx})")
            if base_idx == 0 and base_val == c:
                steps.append(f"      T(i) = {c}·(i + 1)")
            steps.append("")

            # Paso 3: Aplicar la sumatoria
            steps.append("**Paso 3 - Calcular Σ[i=a to b] T(i):**")
            lower = summation_params["lower_bound"]
            upper = summation_params["upper_bound"]

            if base_idx == 0 and base_val == c:
                # Caso simple: T(i) = c(i+1), Σ[i=0 to n] c(i+1)
                steps.append(f"   Σ[i={lower} to {upper}] {c}(i+1)")
                steps.append(f"   = {c} × Σ[i={lower} to {upper}] (i+1)")
                steps.append(f"   = {c} × (1 + 2 + 3 + ... + ({upper}+1))")
                steps.append(f"   = {c} × ({upper}+1)({upper}+2)/2")

                # Paso 4: Aplicar factor multiplicativo
                steps.append("")
                steps.append("**Paso 4 - Aplicar factor multiplicativo:**")
                factor = summation_params["multiplicative_factor"]
                steps.append(f"   T_avg(n) = (1/{factor}) × {c} × (n+1)(n+2)/2")

                # Simplificar si factor = n+1
                if factor == "n+1" or factor == "(n+1)":
                    steps.append(f"   T_avg(n) = {c} × (n+2)/2")
                    steps.append(f"   T_avg(n) = {c}n/2 + {c}")
                    complexity = "O(n)"
                elif factor == "n":
                    steps.append(f"   T_avg(n) = {c} × (n+1)(n+2)/(2n)")
                    steps.append(f"   T_avg(n) ≈ {c}n/2 (para n grande)")
                    complexity = "O(n)"
                else:
                    complexity = "O(n²)" if "n" not in factor else "O(n)"

                steps.append("")
                steps.append("**Paso 5 - Determinar complejidad:**")
                steps.append(f"   El término dominante es lineal en n")
                steps.append(f"   Complejidad: {complexity}")

                explanation = (
                    f"Sumatoria con recurrencia lineal T(i) = T(i-1) + {c}. "
                    f"La expansión de T(i) resulta en {c}(i+1). "
                    f"La suma Σ[i=0 to n] {c}(i+1) = {c}(n+1)(n+2)/2. "
                    f"Aplicando el factor (1/{factor}), obtenemos complejidad {complexity}."
                )

                return {
                    "complexity": complexity,
                    "steps": steps,
                    "explanation": explanation,
                    "applicable": True,
                    "method": "Ecuación Característica (Sumatoria)",
                    "summation_form": f"Σ[i={lower} to {upper}] T(i)",
                    "expanded_form": f"{c}(i+1)",
                    "sum_result": f"{c}(n+1)(n+2)/2",
                    "final_result": f"T_avg(n) = {complexity}",
                }
            else:
                # Caso general: serie aritmética
                complexity = "O(n)"
                explanation = (
                    f"Sumatoria con recurrencia lineal simple. "
                    f"La suma de una progresión aritmética resulta en complejidad {complexity}."
                )

                return {
                    "complexity": complexity,
                    "steps": steps,
                    "explanation": explanation,
                    "applicable": True,
                    "method": "Ecuación Característica (Sumatoria)",
                }

        # Si no se reconoce el patrón, devolver respuesta genérica
        return {
            "complexity": "O(n)",
            "steps": steps,
            "explanation": "Sumatoria detectada. Análisis detallado requiere más contexto.",
            "applicable": True,
            "method": "Ecuación Característica (Sumatoria)",
        }

    @staticmethod
    def _solve_standard(params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Resuelve casos estándar de ecuaciones características.
        Solo homogéneas de orden 1 o 2.
        """
        order = params["order"]
        coefficients = params["coefficients"]

        steps = []
        explanation_parts = []

        # Paso 1: Identificar forma
        steps.append(f"**Paso 1 - Identificar la forma de la recurrencia:**")
        steps.append(f"   Ecuación: {params['original']}")
        steps.append(f"   Orden: {order}")
        steps.append(f"   Coeficientes: {coefficients}")
        steps.append(f"   Tipo: Homogénea con coeficientes constantes")
        steps.append("")

        # Paso 2: Formar ecuación característica
        steps.append(f"**Paso 2 - Formar ecuación característica:**")

        if order == 1:
            # T(n) = cT(n-1)
            # Ecuación característica: r - c = 0 → r = c
            c = coefficients[0]
            char_eq = f"r - {c} = 0"
            root = c

            steps.append(f"   Sustitución: T(n) = r^n")
            steps.append(f"   r^n = {c}·r^(n-1)")
            steps.append(f"   r = {c}")
            steps.append(f"   Ecuación característica: {char_eq}")
            steps.append("")

            # Paso 3: Resolver raíces
            steps.append(f"**Paso 3 - Resolver para r:**")
            steps.append(f"   r = {root}")
            steps.append("")

            # Paso 4: Solución general
            steps.append(f"**Paso 4 - Formar solución general:**")
            steps.append(f"   T(n) = C·{root}^n")
            steps.append("")

            # Paso 5: Complejidad
            steps.append(f"**Paso 5 - Determinar complejidad:**")
            if root == 1:
                complexity = "O(1)"
                steps.append(f"   r = 1 → T(n) = C (constante)")
            elif root > 1:
                complexity = f"O({root}^n)"
                steps.append(f"   r = {root} > 1 → Crecimiento exponencial")
            else:
                complexity = f"O({root}^n)"
                steps.append(f"   r = {root} < 1 → Decrecimiento exponencial")
            steps.append(f"   Complejidad: {complexity}")

            explanation = (
                f"Recurrencia lineal de primer orden con coeficiente constante {c}. "
                f"La ecuación característica r = {c} tiene raíz única r = {root}. "
                f"La solución general es T(n) = C·{root}^n, con complejidad {complexity}."
            )

            return {
                "complexity": complexity,
                "steps": steps,
                "explanation": explanation,
                "applicable": True,
                "method": "Ecuación Característica",
                "characteristic_equation": char_eq,
                "roots": [str(root)],
                "general_solution": f"T(n) = C·{root}^n",
            }

        elif order == 2:
            # T(n) = c1·T(n-1) + c2·T(n-2)
            # Ecuación característica: r² - c1·r - c2 = 0

            # Verificar que tengamos coeficientes para n-1 y n-2
            if len(coefficients) < 2:
                return None

            c1, c2 = coefficients[0], coefficients[1]

            steps.append(f"   Sustitución: T(n) = r^n")
            steps.append(f"   r^n = {c1}·r^(n-1) + {c2}·r^(n-2)")
            steps.append(f"   Dividiendo por r^(n-2):")
            steps.append(f"   r² = {c1}·r + {c2}")
            steps.append(f"   r² - {c1}·r - {c2} = 0")
            char_eq = f"r² - {c1}r - {c2} = 0"
            steps.append("")

            # Paso 3: Resolver usando fórmula cuadrática
            steps.append(f"**Paso 3 - Resolver ecuación cuadrática:**")
            steps.append(f"   Usando fórmula: r = ({c1} ± √({c1}² + 4·{c2})) / 2")

            # Calcular discriminante
            a_coef = 1
            b_coef = -c1
            c_coef = -c2
            discriminant = b_coef**2 - 4 * a_coef * c_coef

            steps.append(f"   Discriminante: Δ = {c1}² + 4·{c2} = {discriminant}")

            if discriminant >= 0:
                # Raíces reales
                sqrt_disc = math.sqrt(discriminant)
                r1 = (-b_coef + sqrt_disc) / (2 * a_coef)
                r2 = (-b_coef - sqrt_disc) / (2 * a_coef)

                steps.append(f"   r₁ = {r1:.4f}")
                steps.append(f"   r₂ = {r2:.4f}")
                steps.append("")

                # Paso 4: Solución general
                steps.append(f"**Paso 4 - Formar solución general:**")

                if abs(r1 - r2) < 0.0001:
                    # Raíces repetidas
                    steps.append(f"   Raíces repetidas: r₁ = r₂ = {r1:.4f}")
                    steps.append(f"   T(n) = (C₁ + C₂·n)·{r1:.4f}^n")
                    gen_solution = f"(C₁ + C₂·n)·{r1:.4f}^n"
                else:
                    # Raíces distintas
                    steps.append(f"   Raíces distintas")
                    steps.append(f"   T(n) = C₁·{r1:.4f}^n + C₂·{r2:.4f}^n")
                    gen_solution = f"C₁·{r1:.4f}^n + C₂·{r2:.4f}^n"

                steps.append("")

                # Paso 5: Complejidad (dominada por raíz mayor)
                steps.append(f"**Paso 5 - Determinar complejidad:**")
                max_root = max(abs(r1), abs(r2))

                if max_root < 1.0001 and max_root > 0.9999:
                    complexity = "O(n)"
                    steps.append(f"   Raíz dominante ≈ 1 → Crecimiento lineal")
                elif max_root > 1:
                    # Representar con φ si es Fibonacci (raíz dorada)
                    if abs(max_root - 1.618) < 0.01:
                        complexity = "O(φ^n)"
                        steps.append(
                            f"   Raíz dominante ≈ φ = 1.618 (proporción áurea)"
                        )
                    else:
                        complexity = f"O({max_root:.3f}^n)"
                        steps.append(f"   Raíz dominante = {max_root:.4f} > 1")
                    steps.append(f"   → Crecimiento exponencial")
                else:
                    complexity = f"O({max_root:.3f}^n)"
                    steps.append(f"   Raíz dominante = {max_root:.4f} < 1")

                steps.append(f"   Complejidad: {complexity}")

                explanation = (
                    f"Recurrencia lineal de segundo orden homogénea. "
                    f"La ecuación característica r² - {c1}r - {c2} = 0 tiene raíces "
                    f"r₁ = {r1:.4f} y r₂ = {r2:.4f}. "
                    f"La solución general es T(n) = {gen_solution}. "
                    f"La raíz dominante determina la complejidad: {complexity}."
                )

                return {
                    "complexity": complexity,
                    "steps": steps,
                    "explanation": explanation,
                    "applicable": True,
                    "method": "Ecuación Característica",
                    "characteristic_equation": char_eq,
                    "roots": [f"{r1:.4f}", f"{r2:.4f}"],
                    "general_solution": f"T(n) = {gen_solution}",
                }

            else:
                # Raíces complejas - delegar al agente
                return None

        # Orden > 2: delegar al agente
        return None


# **********************************************
# 3. Agente de Ecuación Característica
# **********************************************


class CharacteristicEquationAgent(AgentBase[CharacteristicEquationAgentOutput]):
    """
    Agente especializado en resolver recurrencias lineales con la ecuación característica.
    Maneja casos complejos: orden > 2, raíces complejas, términos no homogéneos.
    """

    def __init__(self, model_type: str = "Modelo_Codigo", enable_verbose: bool = False):
        self.enable_verbose = enable_verbose
        super().__init__(model_type)

    def _configure(self) -> None:
        """Configura el agente según AgentBase."""
        self.response_format = CharacteristicEquationAgentOutput
        self.tools = []
        self.context_schema = None

        self.SYSTEM_PROMPT = """Eres un experto en Análisis de Algoritmos especializado en resolver recurrencias lineales usando el MÉTODO DE LA ECUACIÓN CARACTERÍSTICA.

**OBJETIVO:** Resolver ecuaciones de recurrencia lineales con coeficientes constantes.

**TIPOS DE RECURRENCIAS APLICABLES:**

1. **Homogéneas:** T(n) = c₁T(n-1) + c₂T(n-2) + ... + cₖT(n-k)
2. **No Homogéneas:** T(n) = c₁T(n-1) + ... + cₖT(n-k) + g(n)

---
**MÉTODO DE ECUACIÓN CARACTERÍSTICA (5 PASOS):**

**PASO 1: IDENTIFICAR LA FORMA**

Verificar que sea una recurrencia lineal con coeficientes constantes:
- T(n) depende linealmente de T(n-1), T(n-2), etc.
- Los coeficientes c₁, c₂, ... son constantes
- Identificar si es homogénea o tiene término g(n)

Ejemplo: T(n) = T(n-1) + T(n-2)
- Homogénea, orden 2, coeficientes: [1, 1]

---
**PASO 2: FORMAR LA ECUACIÓN CARACTERÍSTICA**

**Para recurrencia homogénea:**
Sustituir T(n) = r^n y dividir por r^(n-k):

T(n) = c₁T(n-1) + c₂T(n-2) + ... + cₖT(n-k)
→ r^n = c₁r^(n-1) + c₂r^(n-2) + ... + cₖr^(n-k)
→ r^k = c₁r^(k-1) + c₂r^(k-2) + ... + cₖ
→ r^k - c₁r^(k-1) - c₂r^(k-2) - ... - cₖ = 0

Ejemplo Fibonacci: T(n) = T(n-1) + T(n-2)
→ r² = r + 1
→ r² - r - 1 = 0

---
**PASO 3: RESOLVER PARA LAS RAÍCES**

Resolver la ecuación característica para encontrar r₁, r₂, ..., rₖ

**Para ecuaciones cuadráticas (orden 2):**
r² + br + c = 0
→ r = (-b ± √(b² - 4c)) / 2

**Casos especiales:**
- Raíces reales distintas: r₁ ≠ r₂
- Raíces repetidas: r₁ = r₂
- Raíces complejas: r = α ± βi

Ejemplo Fibonacci:
r² - r - 1 = 0
→ r = (1 ± √5) / 2
→ r₁ = φ ≈ 1.618 (proporción áurea)
→ r₂ = (1 - √5)/2 ≈ -0.618

---
**PASO 4: FORMAR LA SOLUCIÓN GENERAL**

**Caso 1: Raíces reales distintas**
T(n) = C₁r₁^n + C₂r₂^n + ... + Cₖrₖ^n

**Caso 2: Raíces repetidas (multiplicidad m)**
Si r aparece m veces:
T(n) = (C₁ + C₂n + C₃n² + ... + Cₘn^(m-1))·r^n

**Caso 3: Raíces complejas (r = α ± βi)**
T(n) = ρ^n(C₁cos(θn) + C₂sin(θn))
donde ρ = √(α² + β²), θ = arctan(β/α)

Ejemplo Fibonacci:
T(n) = C₁φ^n + C₂((1-√5)/2)^n

---
**PASO 5: SOLUCIÓN PARTICULAR (Si hay término g(n))**

Para recurrencias no homogéneas: T(n) = [parte homogénea] + g(n)

Buscar solución particular T_p(n) según la forma de g(n):
- g(n) = constante c → probar T_p(n) = A
- g(n) = n → probar T_p(n) = An + B
- g(n) = n² → probar T_p(n) = An² + Bn + C
- g(n) = 2^n → probar T_p(n) = A·2^n

Solución completa: T(n) = T_h(n) + T_p(n)

---
**PASO 6: DETERMINAR COMPLEJIDAD ASINTÓTICA**

La complejidad está dominada por la raíz de mayor magnitud:

- |r| < 1 → O(1) (decreciente)
- |r| = 1 → O(n^k) donde k es la multiplicidad
- |r| > 1 → O(r^n) (exponencial)

Para múltiples raíces: tomar la de mayor valor absoluto

Ejemplo Fibonacci: r₁ = φ ≈ 1.618
→ T(n) = O(φ^n) = O(1.618^n)

---
**EJEMPLOS COMPLETOS:**

**Ejemplo 1: T(n) = 2T(n-1) + 3T(n-2)**
1. Forma: Homogénea, orden 2
2. Ecuación: r² - 2r - 3 = 0
3. Raíces: r₁ = 3, r₂ = -1
4. Solución: T(n) = C₁·3^n + C₂·(-1)^n
5. Complejidad: O(3^n)

**Ejemplo 2: T(n) = 2T(n-1) - T(n-2)**
1. Forma: Homogénea, orden 2
2. Ecuación: r² - 2r + 1 = 0
3. Raíces: r₁ = r₂ = 1 (repetida)
4. Solución: T(n) = (C₁ + C₂n)·1^n = C₁ + C₂n
5. Complejidad: O(n)

**Ejemplo 3: T(n) = T(n-1) + 1**
1. Forma: No homogénea, orden 1
2. Homogénea: r - 1 = 0 → r = 1
3. T_h(n) = C·1^n = C
4. Particular: Probar T_p(n) = An → A = 1 → T_p(n) = n
5. Solución: T(n) = C + n
6. Complejidad: O(n)

---
**FORMATO DE SALIDA:**

Debes responder con un objeto CharacteristicEquationAgentOutput que contenga:

1. `recurrence_form`: Descripción de la forma (homogénea/no homogénea, orden)
2. `coefficients`: Lista de coeficientes
3. `characteristic_equation`: Ecuación característica formada
4. `roots`: Lista de raíces (reales o complejas)
5. `general_solution`: Solución general con constantes
6. `particular_solution`: Solución particular si hay g(n)
7. `final_solution`: Solución completa
8. `complexity`: Complejidad asintótica
9. `detailed_explanation`: Explicación paso a paso completa

---
**REGLAS IMPORTANTES:**

- Verifica que la recurrencia sea lineal con coeficientes constantes
- Resuelve algebraicamente la ecuación característica
- Para raíces complejas, usa forma polar
- Identifica correctamente la raíz dominante
- Justifica cada paso del proceso
- Usa notación matemática precisa (subíndices, exponentes)"""

    def solve_complex(
        self, equation: str, params: Dict[str, Any]
    ) -> CharacteristicEquationAgentOutput:
        """
        Resuelve ecuaciones complejas usando el agente.

        Args:
            equation: Ecuación original
            params: Parámetros pre-parseados

        Returns:
            CharacteristicEquationAgentOutput con la solución
        """
        try:
            if self.enable_verbose:
                print(f"\n[CharacteristicEquationAgent] 📐 Resolviendo con agente...")
                print(f"Ecuación: {equation}")

            # Preparar contexto
            context_info = f"""
INFORMACIÓN DETECTADA:
- Orden: {params.get('order', '?')}
- Coeficientes: {params.get('coefficients', [])}
- Delays: {params.get('delays', [])}
- Homogénea: {'Sí' if params.get('is_homogeneous') else 'No'}
- Término no homogéneo: {params.get('non_homogeneous', 'Ninguno')}
"""

            content = f"""Resuelve esta ecuación de recurrencia usando el MÉTODO DE LA ECUACIÓN CARACTERÍSTICA:

**Ecuación:** {equation}

{context_info}

Sigue el proceso completo:
1. Identificar la forma de la recurrencia
2. Formar la ecuación característica
3. Resolver para las raíces
4. Formar la solución general
5. Encontrar solución particular si es necesario
6. Determinar complejidad asintótica

Responde con el objeto CharacteristicEquationAgentOutput completo."""

            thread_id = f"char_eq_{abs(hash(equation))}"
            result = self.invoke_simple(content=content, thread_id=thread_id)
            output = self.extract_response(result)

            if output is None:
                raise ValueError("El agente no retornó una solución válida")

            if self.enable_verbose:
                print(f"[CharacteristicEquationAgent] ✅ Solución obtenida")
                print(f"Complejidad: {output.complexity}")

            return output

        except Exception as e:
            if self.enable_verbose:
                print(f"[CharacteristicEquationAgent] ❌ ERROR: {str(e)}")

            return CharacteristicEquationAgentOutput(
                recurrence_form="Error en análisis",
                characteristic_equation="No determinada",
                roots=[],
                general_solution="No calculada",
                final_solution="Error",
                complexity="O(?)",
                detailed_explanation=f"Error al resolver: {str(e)}",
            )


# **********************************************
# 4. Estrategia Principal
# **********************************************


class CharacteristicEquationStrategy(RecurrenceStrategy):
    """
    Estrategia híbrida para resolver recurrencias lineales con la ecuación característica.

    **Requisito:** La ecuación debe ser lineal con coeficientes constantes:
    T(n) = c₁T(n-1) + c₂T(n-2) + ... + cₖT(n-k) + g(n)

    **Flujo:**
    1. Verifica que sea lineal con coeficientes constantes
    2. Si es orden ≤ 2 homogénea → resuelve con reglas
    3. Si es complejo → usa agente IA
    4. Retorna diccionario con solución paso a paso
    """

    def __init__(self, enable_verbose: bool = False):
        super().__init__()
        self.name = "Ecuación Característica"
        self.description = (
            "Resuelve recurrencias lineales con coeficientes constantes "
            "formando y resolviendo la ecuación característica."
        )
        self.enable_verbose = enable_verbose
        self.agent: Optional[CharacteristicEquationAgent] = None

    def _get_agent(self) -> CharacteristicEquationAgent:
        """Lazy loading del agente."""
        if self.agent is None:
            if self.enable_verbose:
                print("[CharacteristicEquationStrategy] Inicializando agente...")
            self.agent = CharacteristicEquationAgent(
                model_type="Modelo_Codigo", enable_verbose=self.enable_verbose
            )
        return self.agent

    def solve(self, recurrenceEquation: str) -> Dict[str, Any]:
        """
        Resuelve la ecuación usando el método de la ecuación característica.

        Args:
            recurrenceEquation: Ecuación en formato "T(n) = c₁T(n-1) + ..."

        Returns:
            Diccionario con la solución completa
        """
        if self.enable_verbose:
            print(f"\n{'='*70}")
            print(f"[CharacteristicEquationStrategy] Resolviendo ecuación")
            print(f"{'='*70}")
            print(f"Ecuación: {recurrenceEquation}")

        # ==========================================
        # PASO 1: Analizar ecuación
        # ==========================================
        if self.enable_verbose:
            print(f"\n[Paso 1/3] Analizando aplicabilidad...")

        params = CharacteristicAnalyzer.parse_equation(recurrenceEquation)

        # Verificar aplicabilidad
        if not params["is_applicable"]:
            if self.enable_verbose:
                print(f"❌ La ecuación característica NO es aplicable")

            return {
                "complexity": "N/A",
                "steps": [
                    "La ecuación característica requiere:",
                    "- Recurrencia lineal: T(n) = c₁T(n-1) + c₂T(n-2) + ...",
                    "- Coeficientes constantes",
                    "Esta ecuación no cumple los requisitos.",
                ],
                "explanation": (
                    "El método de la ecuación característica solo aplica a recurrencias "
                    "lineales con coeficientes constantes. Esta ecuación no tiene esa forma."
                ),
                "applicable": False,
                "method": self.name,
            }

        # ==========================================
        # PASO 2: Resolver caso estándar (si aplica)
        # ==========================================
        if params["is_standard"] and params["standard_result"]:
            if self.enable_verbose:
                print(
                    f"[Paso 2/3] ✅ Caso estándar detectado, resolviendo con reglas..."
                )
                print(f"Complejidad: {params['standard_result']['complexity']}")

            return params["standard_result"]

        # ==========================================
        # PASO 3: Resolver con agente IA
        # ==========================================
        if self.enable_verbose:
            print(f"[Paso 2/3] Caso complejo, delegando al agente...")

        agent = self._get_agent()
        agent_output = agent.solve_complex(recurrenceEquation, params)
        if self.enable_verbose:
            print(f"[Paso 3/3] Formateando resultado...")

        result = {
            "complexity": agent_output.complexity,
            "steps": self._format_steps(agent_output),
            "explanation": agent_output.detailed_explanation,
            "applicable": True,
            "method": self.name,
            "recurrence_form": agent_output.recurrence_form,
            "characteristic_equation": agent_output.characteristic_equation,
            "roots": agent_output.roots,
            "general_solution": agent_output.general_solution,
            "particular_solution": agent_output.particular_solution,
            "final_solution": agent_output.final_solution,
        }

        if self.enable_verbose:
            print(f"\n{'='*70}")
            print(f"✅ SOLUCIÓN COMPLETADA")
            print(f"{'='*70}")
            print(f"Complejidad: {result['complexity']}")

        return result

    def _format_steps(
        self, agent_output: CharacteristicEquationAgentOutput
    ) -> List[str]:
        """Formatea la salida del agente en pasos legibles."""
        steps = []

        # Paso 1: Forma
        steps.append("**Paso 1 - Identificar forma de la recurrencia:**")
        steps.append(f"   {agent_output.recurrence_form}")
        if agent_output.coefficients:
            steps.append(f"   Coeficientes: {agent_output.coefficients}")
        steps.append("")

        # Paso 2: Ecuación característica
        steps.append("**Paso 2 - Formar ecuación característica:**")
        steps.append(f"   {agent_output.characteristic_equation}")
        steps.append("")

        # Paso 3: Raíces
        steps.append("**Paso 3 - Resolver para las raíces:**")
        if agent_output.roots:
            for i, root in enumerate(agent_output.roots, 1):
                steps.append(f"   r₍{i}₎ = {root}")
        steps.append("")

        # Paso 4: Solución general
        steps.append("**Paso 4 - Formar solución general:**")
        steps.append(f"   T(n) = {agent_output.general_solution}")
        steps.append("")

        # Paso 5: Solución particular (si existe)
        if agent_output.particular_solution:
            steps.append("**Paso 5 - Solución particular:**")
            steps.append(f"   T_p(n) = {agent_output.particular_solution}")
            steps.append("")

            steps.append("**Paso 6 - Solución completa:**")
            steps.append(f"   T(n) = {agent_output.final_solution}")
            steps.append("")

            steps.append("**Paso 7 - Complejidad final:**")
        else:
            steps.append("**Paso 5 - Complejidad final:**")

        steps.append(f"   {agent_output.complexity}")

        return steps
        #

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
import re

from ...external_services.Agentes.Agent import AgentBase
from .recurrence_method import StrategyType

# **********************************************
# 1. Tipos y Schemas
# **********************************************

class ClassificationOutput(BaseModel):
    """Resultado de la clasificación de la ecuación."""

    method: StrategyType = Field(
        ..., description="Método recomendado para resolver la ecuación"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confianza en la clasificación (0-1)"
    )
    reasoning: str = Field(
        default="", description="Explicación de por qué se eligió este método"
    )
    equation_normalized: str = Field(
        default="", description="Ecuación normalizada/parseada"
    )


# **********************************************
# 2. Clasificador por Reglas (Capa Rápida)
# **********************************************

class RuleBasedClassifier:
    """
    Clasificador heurístico de ecuaciones de recurrencia.
    Maneja ~90% de casos comunes sin usar LLM.
    """

    @staticmethod
    def normalize_equation(equation: str) -> str:
        """Normaliza la ecuación para análisis."""
        eq = equation.replace(" ", "").lower()
        eq = eq.replace("//", "/").replace("⌊", "").replace("⌋", "")
        eq = eq.replace("^", "**").replace("{", "").replace("}", "")
        return eq

    @staticmethod
    def extract_pattern(equation: str) -> dict:
        """Extrae características clave de la ecuación."""
        eq = RuleBasedClassifier.normalize_equation(equation)

        pattern = {
            # División (Divide y Conquista)
            "has_division": bool(re.search(r"t\(n/\d+\)", eq)),
            "division_factor": None,
            "num_division_calls": 0,
            # Resta (Recurrencias Lineales)
            "has_subtraction": bool(re.search(r"t\(n-\d+\)", eq)),
            "subtraction_values": [],
            "num_subtraction_calls": 0,
            # Características especiales
            "has_multiple_recursive_terms": False,
            "has_exponential": bool(re.search(r"(\d+\*\*|exp\(|2\*\*)", eq)),
            "has_logarithm": bool(re.search(r"log", eq)),
            "has_any_recursive_call": bool(re.search(r"t\([^)]+\)", eq)),
            "work_function": None,
            "total_recursive_calls": 0,
            "is_trivial": False,
        }

        # Analizar llamadas con división: T(n/b)
        div_matches = re.findall(r"t\(n/(\d+)\)", eq)
        if div_matches:
            pattern["division_factor"] = int(div_matches[0])
            pattern["num_division_calls"] = len(div_matches)
            pattern["total_recursive_calls"] += len(div_matches)

        # Analizar llamadas con resta: T(n-k)
        sub_matches = re.findall(r"t\(n-(\d+)\)", eq)
        if sub_matches:
            pattern["subtraction_values"] = [int(x) for x in sub_matches]
            pattern["num_subtraction_calls"] = len(sub_matches)
            pattern["total_recursive_calls"] += len(sub_matches)

        # Detectar múltiples términos recursivos
        all_recursive = re.findall(r"t\([^)]+\)", eq)
        pattern["has_multiple_recursive_terms"] = len(all_recursive) > 1
        pattern["has_any_recursive_call"] = len(all_recursive) > 0

        # Extraer función de trabajo
        work = re.sub(r"\d*t\([^)]+\)", "", eq)
        work = work.replace("t(n)=", "").replace("t(n)", "").strip()
        if work and work not in ["+", "-", "*", "/", "=", ""]:
            pattern["work_function"] = work

        # Detectar si es trivial (sin llamadas recursivas)
        if not pattern["has_any_recursive_call"]:
            pattern["is_trivial"] = True

        return pattern

    @staticmethod
    def classify_by_rules(equation: str) -> Optional[ClassificationOutput]:
        """
        Clasifica usando reglas heurísticas.

        Returns:
            ClassificationOutput si confianza >= 0.8, None si necesita agente
        """
        pattern = RuleBasedClassifier.extract_pattern(equation)
        eq_norm = RuleBasedClassifier.normalize_equation(equation)

        # ==================================================
        # REGLA 0: Sin Recursión (NONE)
        # Forma: T(n) = constante, T(n) = n, T(n) = n², etc.
        # Condiciones:
        # - NO tiene llamadas recursivas T(...)
        # - Es una función directa de n
        # ==================================================
        if pattern["is_trivial"] or not pattern["has_any_recursive_call"]:
            # Verificar si es una constante
            if re.match(r'^t\(n\)\s*=\s*\d+$', eq_norm):
                return ClassificationOutput(
                    method=StrategyType.NONE,
                    confidence=1.0,
                    reasoning=(
                        "Ecuación trivial sin recursión: T(n) = constante. "
                        "No requiere análisis de recurrencia. "
                        "La complejidad es directamente O(1)."
                    ),
                    equation_normalized=eq_norm,
                )
            
            # Verificar si es una función polinomial simple
            if re.search(r't\(n\)\s*=\s*n(\*\*\d+)?$', eq_norm):
                degree_match = re.search(r'n\*\*(\d+)', eq_norm)
                degree = int(degree_match.group(1)) if degree_match else 1
                
                return ClassificationOutput(
                    method=StrategyType.NONE,
                    confidence=1.0,
                    reasoning=(
                        f"Ecuación trivial sin recursión: T(n) = n^{degree}. "
                        "No requiere análisis de recurrencia. "
                        f"La complejidad es directamente O(n^{degree})."
                    ),
                    equation_normalized=eq_norm,
                )
            
            # Otros casos sin recursión
            if not pattern["has_any_recursive_call"]:
                return ClassificationOutput(
                    method=StrategyType.NONE,
                    confidence=0.95,
                    reasoning=(
                        "Ecuación sin llamadas recursivas detectadas. "
                        "No se requiere análisis de recurrencia. "
                        "La complejidad se puede determinar directamente de la expresión."
                    ),
                    equation_normalized=eq_norm,
                )

        # ==================================================
        # REGLA 1: Teorema Maestro
        # Forma: T(n) = aT(n/b) + f(n)
        # ==================================================
        if (
            pattern["has_division"]
            and not pattern["has_subtraction"]
            and pattern["division_factor"]
            and pattern["division_factor"] > 1
            and not pattern["has_exponential"]
        ):
            if pattern["num_division_calls"] == 1 or all(
                re.search(rf't\(n/{pattern["division_factor"]}\)', eq_norm)
                for _ in range(pattern["num_division_calls"])
            ):
                return ClassificationOutput(
                    method=StrategyType.MASTER_THEOREM,
                    confidence=0.95,
                    reasoning=(
                        f"Ecuación en forma T(n) = aT(n/{pattern['division_factor']}) + f(n). "
                        f"Divide el problema en {pattern['num_division_calls']} subproblema(s) "
                        f"de tamaño n/{pattern['division_factor']}. "
                        f"Trabajo adicional: {pattern['work_function'] or 'constante'}. "
                        "El Teorema Maestro es el método óptimo."
                    ),
                    equation_normalized=eq_norm,
                )

        # ==================================================
        # REGLA 2: Ecuación Característica - MEJORADA
        # Detecta: T(n-k), sumatorias con T(i)
        # ==================================================
        
        # Detectar patrones T(n-k) directamente
        linear_pattern = re.search(r't\s*\(\s*n\s*-\s*\d+\s*\)', eq_norm)
        
        # Detectar sumatorias con recurrencias lineales
        has_summation = any(symbol in equation for symbol in ['Σ', '∑', 'sum', 'σ'])
        has_ti_pattern = 't(i)' in eq_norm and ('t(i-1)' in eq_norm or 't(i-k)' in eq_norm)
        
        if linear_pattern or (has_summation and has_ti_pattern):
            reasoning_parts = []
            
            if has_summation and has_ti_pattern:
                reasoning_parts.append("Sumatoria con recurrencia lineal T(i) = T(i-1) + c detectada")
            elif pattern["has_multiple_recursive_terms"]:
                reasoning_parts.append(
                    f"Recurrencia lineal de orden superior. "
                    f"Términos: {', '.join([f'T(n-{v})' for v in pattern['subtraction_values']])}"
                )
            else:
                k = pattern["subtraction_values"][0] if pattern["subtraction_values"] else 1
                reasoning_parts.append(f"Recurrencia lineal simple T(n) = cT(n-{k}) + f(n)")
            
            if pattern['work_function']:
                reasoning_parts.append(f"Trabajo adicional: {pattern['work_function']}")
            
            reasoning_parts.append("La ecuación característica es ideal para resolver este tipo de recurrencia.")
            
            return ClassificationOutput(
                method=StrategyType.EQUATION_CHARACTERISTICS,
                confidence=0.90,
                reasoning=". ".join(reasoning_parts) + ".",
                equation_normalized=eq_norm,
            )

        # ==================================================
        # REGLA 3: Método del Árbol - Casos Complejos
        # ==================================================
        if pattern["has_exponential"]:
            return ClassificationOutput(
                method=StrategyType.TREE_METHOD,
                confidence=0.85,
                reasoning=(
                    "La ecuación contiene términos exponenciales. "
                    "El método del árbol de recursión permite visualizar "
                    "y sumar los costos nivel por nivel."
                ),
                equation_normalized=eq_norm,
            )

        if pattern["has_division"] and pattern["has_multiple_recursive_terms"]:
            return ClassificationOutput(
                method=StrategyType.TREE_METHOD,
                confidence=0.82,
                reasoning=(
                    "Recurrencia con múltiples subproblemas de tamaños diferentes. "
                    "El método del árbol es más apropiado que el Teorema Maestro "
                    "para analizar este tipo de división no uniforme."
                ),
                equation_normalized=eq_norm,
            )

        if pattern["has_division"] and pattern["has_subtraction"]:
            return ClassificationOutput(
                method=StrategyType.TREE_METHOD,
                confidence=0.80,
                reasoning=(
                    "Combinación inusual de división y resta en las llamadas recursivas. "
                    "El método del árbol proporciona un análisis más claro."
                ),
                equation_normalized=eq_norm,
            )

        return None


# **********************************************
# 3. Agente de Clasificación (Capa Inteligente)
# **********************************************

class ClassificationAgent(AgentBase[ClassificationOutput]):
    """
    Agente IA para clasificar ecuaciones complejas o ambiguas.
    Solo se invoca cuando las reglas heurísticas fallan.
    """

    def __init__(
        self, model_type: str = "Modelo_Clasificacion", enable_verbose: bool = False
    ):
        self.enable_verbose = enable_verbose
        super().__init__(model_type)

    def _configure(self) -> None:
        """Configura el agente según la clase base."""
        self.response_format = ClassificationOutput
        self.tools = []         # <-- IMPORTANTÍSIMO
        self.tool_choice = "none"  # <-- Evita tool_calls del modelo
        self.context_schema = None

        self.SYSTEM_PROMPT = """Eres un experto en análisis de algoritmos especializado en clasificar ecuaciones de recurrencia.

**TU TAREA:** Clasificar la ecuación en UNO de estos 4 métodos de resolución:

---
**0. NONE (Sin Recursión)**
- **Forma:** T(n) = constante, T(n) = n, T(n) = n², T(n) = f(n) sin términos T(...)
- **Características:** NO tiene llamadas recursivas
- **Ejemplos:**
  * T(n) = 1 → O(1)
  * T(n) = n → O(n)
  * T(n) = n² → O(n²)
  * T(n) = n log n → O(n log n)
- **Cuándo usar:** Cuando la ecuación es trivial y no requiere análisis de recurrencia

---
**1. MASTER_THEOREM (Teorema Maestro)**
- **Forma:** T(n) = aT(n/b) + f(n)
- **Condiciones:** a ≥ 1, b > 1, división uniforme
- **Ejemplos:**
  * T(n) = 2T(n/2) + n → Merge Sort
  * T(n) = T(n/2) + 1 → Búsqueda binaria

---
**2. EQUATION_CHARACTERISTICS (Ecuación Característica)**
- **Forma:** T(n) = c₁T(n-k₁) + c₂T(n-k₂) + ... + g(n)
- **Características:** Coeficientes constantes, resta en argumentos
- **Ejemplos:**
  * T(n) = T(n-1) + T(n-2) → Fibonacci
  * T(n) = 2T(n-1) + 1 → Torres de Hanoi

---
**3. TREE_METHOD (Método del Árbol)**
- **Casos:** Recurrencias complejas que no encajan en los anteriores
- **Incluye:**
  * Múltiples ramas de tamaño diferente
  * Exponenciales, logaritmos complejos
  * Recurrencias no estándar

---
**INSTRUCCIONES:**
1. **PRIMERO** verifica si hay llamadas recursivas T(...)
   - Si NO hay: usa NONE
   - Si hay: continúa con el análisis
2. Identifica parámetros clave (a, b, tipo de división/resta)
3. Elige el método MÁS APROPIADO
4. Asigna confidence (0.6-1.0)
5. Explica brevemente tu decisión

**EJEMPLOS DE NONE:**
- "T(n) = 1" → NONE (constante)
- "T(n) = n" → NONE (lineal directo)
- "T(n) = 5" → NONE (constante)
- "T(n) = n²" → NONE (cuadrático directo)

**RESPONDE con el objeto ClassificationOutput.**"""

    def classify(self, equation: str) -> ClassificationOutput:
        """Clasifica una ecuación usando el agente IA."""
        try:
            if self.enable_verbose:
                print(f"[ClassificationAgent] 🤖 Analizando: {equation}")

            content = f"""Clasifica esta ecuación de recurrencia:

**Ecuación:** {equation}

Determina el método de resolución más apropiado. Si no hay llamadas recursivas T(...), usa NONE.

Responde con el objeto ClassificationOutput."""

            thread_id = f"classify_{abs(hash(equation))}"
            result = self.invoke_simple(content=content, thread_id=thread_id)
            output = self.extract_response(result)

            if output is None:
                raise ValueError("El agente no retornó una clasificación válida")

            if self.enable_verbose:
                print(f"[ClassificationAgent] ✅ Método: {output.method.value} (conf: {output.confidence:.2f})")

            return output

        except Exception as e:
            if self.enable_verbose:
                print(f"[ClassificationAgent] ❌ ERROR: {str(e)}")

            return ClassificationOutput(
                method=StrategyType.TREE_METHOD,
                confidence=0.50,
                reasoning=f"Clasificación por defecto (error: {str(e)})",
                equation_normalized=equation,
            )


# **********************************************
# 4. Clase Principal - Clasificador Híbrido
# **********************************************

class ClassificationEquation:
    """
    Clasificador híbrido de ecuaciones de recurrencia.
    
    Incluye detección de casos triviales (NONE) sin recursión.
    """

    def __init__(self, use_agent: bool = True, enable_verbose: bool = False):
        self.use_agent = use_agent
        self.enable_verbose = enable_verbose
        self.agent = None

        if use_agent:
            self.agent = ClassificationAgent(
                model_type="Modelo_Clasificacion", enable_verbose=enable_verbose
            )

    def classify(self, equation: str) -> ClassificationOutput:
        """
        Clasifica la ecuación usando estrategia híbrida.

        Args:
            equation: Ecuación de recurrencia (ej: "T(n) = 2T(n/2) + n")

        Returns:
            ClassificationOutput con método, confianza y razonamiento
        """
        if self.enable_verbose:
            print(f"\n{'='*70}")
            print(f"[ClassificationEquation] 📊 Clasificando ecuación")
            print(f"{'='*70}")
            print(f"Ecuación: {equation}")

        # PASO 1: Intentar con reglas rápidas
        if self.enable_verbose:
            print(f"\n[Paso 1/3] Aplicando reglas heurísticas...")

        rule_result = RuleBasedClassifier.classify_by_rules(equation)

        if rule_result and rule_result.confidence >= 0.80:
            if self.enable_verbose:
                print(f"✅ Clasificado por reglas (confianza: {rule_result.confidence:.2f})")
                print(f"   Método: {rule_result.method.value}")
            return rule_result

        # PASO 2: Usar agente IA si disponible
        if self.use_agent and self.agent:
            if self.enable_verbose:
                print(f"\n[Paso 2/3] Reglas insuficientes, consultando agente IA...")

            agent_result = self.agent.classify(equation)

            if self.enable_verbose:
                print(f"✅ Clasificado por agente (confianza: {agent_result.confidence:.2f})")

            return agent_result

        # PASO 3: Fallback - Método del árbol
        if self.enable_verbose:
            print(f"\n[Paso 3/3] Sin agente disponible, usando fallback...")

        fallback = ClassificationOutput(
            method=StrategyType.TREE_METHOD,
            confidence=0.60,
            reasoning=(
                "No se pudo clasificar con certeza alta. El método del árbol "
                "es aplicable a cualquier ecuación de recurrencia."
            ),
            equation_normalized=RuleBasedClassifier.normalize_equation(equation),
        )

        if self.enable_verbose:
            print(f"⚠️ Clasificación por defecto: {fallback.method.value}")

        return fallback

    def classify_batch(self, equations: List[str]) -> List[ClassificationOutput]:
        """Clasifica múltiples ecuaciones en lote."""
        results = []
        total = len(equations)

        if self.enable_verbose:
            print(f"\n{'='*70}")
            print(f"CLASIFICACIÓN EN LOTE: {total} ecuaciones")
            print(f"{'='*70}")

        for i, eq in enumerate(equations, 1):
            if self.enable_verbose:
                print(f"\n--- [{i}/{total}] ---")

            result = self.classify(eq)
            results.append(result)

        return results


# **********************************************
# 5. Función de Conveniencia
# **********************************************

def classify_recurrence(
    equation, use_agent: bool = True, verbose: bool = False, type = "C"
) -> ClassificationOutput:
    """
    Función de conveniencia para clasificar una ecuación.

    Args:
        equation: Ecuación de recurrencia
        use_agent: Usar agente IA para casos complejos
        verbose: Mostrar logs detallados

    Returns:
        ClassificationOutput

    Ejemplos:
        >>> classify_recurrence("T(n) = 2T(n/2) + n")
        ClassificationOutput(method=StrategyType.MASTER_THEOREM, ...)
        
        >>> classify_recurrence("T(n) = 1")
        ClassificationOutput(method=StrategyType.NONE, ...)
        
        >>> classify_recurrence("T(n) = n")
        ClassificationOutput(method=StrategyType.NONE, ...)
    """
    classifier = ClassificationEquation(use_agent=use_agent, enable_verbose=verbose)
    if type == "C":
        return classifier.classify(equation)
    if type == "B":
        return classifier.classify_batch(equation)
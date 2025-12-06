"""
Agente completo de análisis de algoritmos (recursivos e iterativos).
Implementa AgentBase y retorna estructura Solution.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from .Agent import AgentBase
from app.models.solution import Solution
import json
import re


# ================= SCHEMAS PYDANTIC =================


class LineAnalysis(BaseModel):
    """Análisis de costo por línea."""

    line: int = Field(description="Número de línea")
    code: str = Field(description="Código de la línea")
    cost: str = Field(description="Costo en formato: constante * función (ej: c1 * n)")
    explanation: str = Field(description="Explicación del costo")


class CaseAnalysis(BaseModel):
    """Análisis de un caso específico (mejor/peor/promedio)."""

    complexity: str = Field(description="Complejidad del caso (ej: O(n))")
    condition: str = Field(description="Condición que define este caso")
    example: str = Field(description="Ejemplo concreto del caso")
    explanation: str = Field(description="Explicación detallada del caso")


class CompleteAnalysisResponse(BaseModel):
    """Respuesta estructurada del agente de análisis completo."""

    algorithm_purpose: str = Field(description="Para qué sirve el algoritmo")
    algorithm_name: str = Field(description="Nombre del algoritmo si es reconocido")
    algorithm_category: str = Field(
        description="Categoría: Programación Dinámica, Divide y Conquista, Búsqueda, Ordenamiento, Greedy, Backtracking, etc."
    )
    algorithm_type: str = Field(description="Tipo: 'recursive' o 'iterative'")

    line_by_line_analysis: List[LineAnalysis] = Field(
        description="Análisis de costo por cada línea del pseudocódigo"
    )

    equation: str = Field(
        description="Ecuación de recurrencia (recursivo) o sumatoria (iterativo)"
    )

    solution_method: str = Field(
        description="Método usado para resolver: Teorema Maestro, Árbol de Recursión, Sustitución, Análisis de Sumatorias, etc."
    )

    solution_steps: List[str] = Field(
        description="Pasos detallados de la resolución de la ecuación"
    )

    final_complexity: str = Field(
        description="Complejidad final simplificada (ej: O(n log n))"
    )

    has_multiple_cases: bool = Field(
        description="True si el algoritmo tiene mejor/peor/promedio casos diferentes"
    )

    best_case: Optional[CaseAnalysis] = Field(
        default=None,
        description="Análisis del mejor caso (solo si has_multiple_cases=True)"
    )

    worst_case: Optional[CaseAnalysis] = Field(
        default=None,
        description="Análisis del peor caso (solo si has_multiple_cases=True)"
    )

    average_case: Optional[CaseAnalysis] = Field(
        default=None,
        description="Análisis del caso promedio (solo si has_multiple_cases=True)"
    )

    asymptotic_best: str = Field(description="Cota inferior Ω (mejor caso)")
    asymptotic_worst: str = Field(description="Cota superior O (peor caso)")
    asymptotic_average: str = Field(description="Cota ajustada Θ (caso promedio)")

    notation_explanation: str = Field(
        description="Explicación de las notaciones asintóticas"
    )

    case_determination_criteria: Optional[str] = Field(
        default=None,
        description="Criterio que determina los diferentes casos (solo si has_multiple_cases=True)"
    )


# ================= AGENTE PRINCIPAL =================


class CompleteAnalysisAgent(AgentBase[CompleteAnalysisResponse]):
    """
    Agente que realiza análisis completo de algoritmos recursivos e iterativos.

    Funcionalidades:
    1. Explica para qué sirve el algoritmo
    2. Clasifica el tipo (programación dinámica, greedy, búsqueda, etc.)
    3. Saca costo por línea (constante * función)
    4. Genera ecuación de recurrencia o sumatoria
    5. Resuelve la ecuación paso a paso
    6. Expresa en notaciones asintóticas (O, Ω, Θ)
    """

    def __init__(self):
        """
        Inicializa el agente con Gemini Largo (modelo potente para razonamiento).
        """
        super().__init__(
            model_type="Gemini_Largo",  # Gemini 2.5 Pro - modelo de razonamiento
            provider="gemini",
            fallback=False,
        )

    def _configure(self) -> None:
        """Configura el prompt del sistema, herramientas y formato de respuesta."""

        self.SYSTEM_PROMPT = """Eres un experto en análisis de complejidad algorítmica.

Tu tarea es analizar algoritmos (recursivos o iterativos) y proporcionar un análisis matemático completo y riguroso.

IMPORTANTE - REGLAS ESTRICTAS:

1. **IDENTIFICACIÓN DEL TIPO**:
   - Detecta si es recursivo (tiene llamadas a sí mismo) o iterativo (usa bucles)
   - Responde con "recursive" o "iterative" en algorithm_type

2. **ANÁLISIS LÍNEA POR LÍNEA**:
   - Formato del costo: "constante * función"
   - Ejemplos válidos:
     * Asignación: "c1 * 1"
     * Comparación: "c2 * 1"
     * Bucle for i=1 to n: "c3 * n"
     * Llamada recursiva: "T(n-1)" o "T(n/2)"
     * Bucle anidado: "c4 * n²"

3. **ECUACIÓN**:
   - **Recursivo**: Ecuación de recurrencia
     * Ejemplo: "T(n) = 2T(n/2) + cn"
     * Incluye caso base: "T(1) = c"
   - **Iterativo**: Sumatoria
     * Ejemplo: "T(n) = Σ(i=1 to n) c*i = c*n(n+1)/2"

4. **MÉTODOS DE RESOLUCIÓN**:
   - Recursivos: Teorema Maestro, Árbol de Recursión, Método de Sustitución
   - Iterativos: Análisis de Sumatorias, Conteo de Operaciones

5. **PASOS DETALLADOS**:
   - Muestra TODOS los pasos matemáticos
   - Justifica cada simplificación
   - Llega a la forma cerrada (sin recurrencias ni sumatorias)

6. **NOTACIONES ASINTÓTICAS**:
   - Ω (Omega): Cota inferior - mejor caso
   - O (Big-O): Cota superior - peor caso  
   - Θ (Theta): Cota ajustada - caso promedio (cuando Ω = O)

7. **CASOS MÚLTIPLES**:
   - Detecta si el algoritmo tiene diferentes complejidades según la entrada
   - Ejemplos con múltiples casos:
     * Búsqueda lineal: O(1) mejor, O(n) peor
     * QuickSort: O(n log n) mejor, O(n²) peor
     * Insertion Sort: O(n) mejor, O(n²) peor
   - Ejemplos sin múltiples casos:
     * Merge Sort: siempre O(n log n)
     * Búsqueda binaria: siempre O(log n)
   - Si tiene múltiples casos, set has_multiple_cases=True y proporciona:
     * best_case: análisis del mejor caso
     * worst_case: análisis del peor caso
     * average_case: análisis del caso promedio
     * case_determination_criteria: qué determina cada caso

RESPONDE SIEMPRE EN JSON VÁLIDO CON LA ESTRUCTURA ESPECIFICADA."""

        # Sin herramientas adicionales por ahora
        self.tools = []

        # Schema de contexto (opcional)
        self.context_schema = None

        # Formato de respuesta esperado
        self.response_format = CompleteAnalysisResponse

    def analyze(self, pseudocode: str) -> Solution:
        """
        Analiza un algoritmo completo y retorna objeto Solution.

        Args:
            pseudocode: Pseudocódigo del algoritmo a analizar

        Returns:
            Objeto Solution con análisis completo
        """

        # Validar entrada
        if not pseudocode or pseudocode.strip() == "":
            raise ValueError("El pseudocódigo no puede estar vacío")

        # Construir prompt detallado
        prompt = self._build_analysis_prompt(pseudocode)

        # Invocar agente
        result = self.invoke_simple(content=prompt, thread_id="complete_analysis")

        # Extraer respuesta estructurada
        analysis = self.extract_response(result)

        if not analysis:
            raise ValueError("No se pudo extraer respuesta estructurada del agente")

        # Validar análisis
        self._validate_analysis(analysis)

        # Convertir a Solution
        solution = self._convert_to_solution(analysis, pseudocode)

        return solution

    def _build_analysis_prompt(self, pseudocode: str) -> str:
        """Construye el prompt de análisis."""

        return f"""Analiza el siguiente pseudocódigo de forma completa y rigurosa:

```
{pseudocode}
```

Proporciona un análisis matemático detallado siguiendo EXACTAMENTE esta estructura:

1. **Propósito**: Explica para qué sirve este algoritmo (2-3 líneas)

2. **Nombre**: Si reconoces el algoritmo, indica su nombre (ej: "Merge Sort", "Fibonacci", "Binary Search")

3. **Categoría**: Clasifica en UNA de estas:
   - Programación Dinámica
   - Divide y Conquista  
   - Algoritmo Greedy (Voraz)
   - Búsqueda
   - Ordenamiento
   - Backtracking
   - Recursión Simple
   - Iteración Simple
   - Otro (especifica)

4. **Tipo**: Indica si es "recursive" o "iterative"

5. **Análisis línea por línea**:
   - Para CADA línea del pseudocódigo
   - Formato: "constante * función"
   - Ejemplos: "c1 * 1", "c2 * n", "T(n-1)", "c3 * n²"

6. **Ecuación**:
   - Si es recursivo: ecuación de recurrencia con caso base
   - Si es iterativo: sumatoria o función de complejidad

7. **Método de resolución**:
   - Indica qué método usaste
   - Ejemplos: "Teorema Maestro", "Árbol de Recursión", "Análisis de Sumatorias"

8. **Pasos de resolución**:
   - Lista TODOS los pasos matemáticos
   - Muestra expansiones, simplificaciones, límites
   - Llega a la forma cerrada final

9. **Complejidad final**: Resultado simplificado (ej: "O(n log n)")

10. **Notaciones asintóticas**:
    - Ω (mejor caso)
    - O (peor caso)
    - Θ (caso promedio)
    - Explicación de cada una

11. **Casos múltiples** (SI APLICA):
    - Detecta si el algoritmo tiene diferentes complejidades según la entrada
    - Si has_multiple_cases = True, proporciona:
      * best_case: {complexity, condition, example, explanation}
      * worst_case: {complexity, condition, example, explanation}
      * average_case: {complexity, condition, example, explanation}
      * case_determination_criteria: qué determina cada caso
    - Ejemplos:
      * Búsqueda lineal: mejor O(1) si está al inicio, peor O(n) si al final
      * Merge Sort: siempre O(n log n), NO tiene casos múltiples

RESPONDE EN JSON VÁLIDO siguiendo el schema CompleteAnalysisResponse."""

    def _convert_to_solution(
        self, analysis: CompleteAnalysisResponse, pseudocode: str
    ) -> Solution:
        """
        Convierte la respuesta del agente a objeto Solution.

        Args:
            analysis: Respuesta estructurada del agente
            pseudocode: Pseudocódigo original

        Returns:
            Objeto Solution completo
        """

        # Convertir line_by_line_analysis a formato esperado por Solution
        complexity_lines = []
        for line_analysis in analysis.line_by_line_analysis:
            complexity_lines.append(
                {
                    "line": line_analysis.line,
                    "code": line_analysis.code,
                    "complexity": line_analysis.cost,
                    "explanation": line_analysis.explanation,
                }
            )

        # Construir explain_complexity (explicación textual del análisis)
        explain_complexity = self._build_complexity_explanation(analysis)

        # Construir notación asintótica
        asymptotic_notation = {
            "best": analysis.asymptotic_best,
            "worst": analysis.asymptotic_worst,
            "average": analysis.asymptotic_average,
            "explanation": analysis.notation_explanation,
            "has_multiple_cases": analysis.has_multiple_cases,
        }

        # Agregar análisis de casos si aplica
        if analysis.has_multiple_cases:
            if analysis.best_case:
                asymptotic_notation["best_case_analysis"] = {
                    "complexity": analysis.best_case.complexity,
                    "condition": analysis.best_case.condition,
                    "example": analysis.best_case.example,
                    "explanation": analysis.best_case.explanation,
                }
            if analysis.worst_case:
                asymptotic_notation["worst_case_analysis"] = {
                    "complexity": analysis.worst_case.complexity,
                    "condition": analysis.worst_case.condition,
                    "example": analysis.worst_case.example,
                    "explanation": analysis.worst_case.explanation,
                }
            if analysis.average_case:
                asymptotic_notation["average_case_analysis"] = {
                    "complexity": analysis.average_case.complexity,
                    "condition": analysis.average_case.condition,
                    "example": analysis.average_case.example,
                    "explanation": analysis.average_case.explanation,
                }
            if analysis.case_determination_criteria:
                asymptotic_notation["case_criteria"] = analysis.case_determination_criteria

        # Crear objeto Solution
        solution = Solution(
            type=analysis.algorithm_type,
            code_explain=analysis.algorithm_purpose,
            complexity_line_to_line=complexity_lines,
            explain_complexity=explain_complexity,
            asymptotic_notation=asymptotic_notation,
            algorithm_name=analysis.algorithm_name,
            algorithm_category=analysis.algorithm_category,
            equation=analysis.equation,
            method_solution=analysis.solution_method,
            solution_equation=analysis.final_complexity,
            explain_solution_steps=analysis.solution_steps,
            diagrams=None,  # Podría generarse en futuras versiones
            extra={"pseudocode": pseudocode, "analysis_complete": True},
        )

        return solution

    def _validate_analysis(self, analysis: CompleteAnalysisResponse) -> None:
        """Valida que el análisis esté completo y sea consistente."""

        # Validación de campos básicos
        if not analysis.algorithm_purpose or analysis.algorithm_purpose.strip() == "":
            raise ValueError("Falta el propósito del algoritmo")

        if not analysis.algorithm_name or analysis.algorithm_name.strip() == "":
            raise ValueError("Falta el nombre del algoritmo")

        if not analysis.line_by_line_analysis or len(analysis.line_by_line_analysis) == 0:
            raise ValueError("Falta el análisis línea por línea")

        if not analysis.equation or analysis.equation.strip() == "":
            raise ValueError("Falta la ecuación de complejidad")

        if not analysis.solution_steps or len(analysis.solution_steps) == 0:
            raise ValueError("Faltan los pasos de resolución")

        # Validación de casos múltiples
        if analysis.has_multiple_cases:
            if not analysis.best_case:
                raise ValueError("Si tiene múltiples casos, falta el mejor caso")
            if not analysis.worst_case:
                raise ValueError("Si tiene múltiples casos, falta el peor caso")
            if not analysis.average_case:
                raise ValueError("Si tiene múltiples casos, falta el caso promedio")

    def _build_complexity_explanation(self, analysis: CompleteAnalysisResponse) -> str:
        """Construye explicación textual de la complejidad."""

        parts = []

        parts.append(f"**Algoritmo**: {analysis.algorithm_name}")
        parts.append(f"**Categoría**: {analysis.algorithm_category}")
        parts.append(
            f"**Tipo**: {'Recursivo' if analysis.algorithm_type == 'recursive' else 'Iterativo'}"
        )
        parts.append("")

        parts.append(f"**Ecuación**: {analysis.equation}")
        parts.append(f"**Método de resolución**: {analysis.solution_method}")
        parts.append(f"**Complejidad final**: {analysis.final_complexity}")
        parts.append("")

        parts.append("**Notaciones asintóticas**:")
        parts.append(f"- Mejor caso (Ω): {analysis.asymptotic_best}")
        parts.append(f"- Peor caso (O): {analysis.asymptotic_worst}")
        parts.append(f"- Caso promedio (Θ): {analysis.asymptotic_average}")

        # Agregar análisis de casos múltiples si aplica
        if analysis.has_multiple_cases:
            parts.append("")
            parts.append("**Análisis de casos múltiples**:")
            
            if analysis.best_case:
                parts.append(f"\n**Mejor Caso** - {analysis.best_case.complexity}")
                parts.append(f"- Condición: {analysis.best_case.condition}")
                parts.append(f"- Ejemplo: {analysis.best_case.example}")
                parts.append(f"- Explicación: {analysis.best_case.explanation}")
            
            if analysis.worst_case:
                parts.append(f"\n**Peor Caso** - {analysis.worst_case.complexity}")
                parts.append(f"- Condición: {analysis.worst_case.condition}")
                parts.append(f"- Ejemplo: {analysis.worst_case.example}")
                parts.append(f"- Explicación: {analysis.worst_case.explanation}")
            
            if analysis.average_case:
                parts.append(f"\n**Caso Promedio** - {analysis.average_case.complexity}")
                parts.append(f"- Condición: {analysis.average_case.condition}")
                parts.append(f"- Ejemplo: {analysis.average_case.example}")
                parts.append(f"- Explicación: {analysis.average_case.explanation}")

        return "\n".join(parts)


# ================= FUNCIÓN DE PRUEBA =================


def test_complete_analysis_agent():
    """Prueba el agente con ejemplos recursivos e iterativos."""

    agent = CompleteAnalysisAgent()

    # Ejemplo 1: Algoritmo recursivo (Fibonacci)
    print("=" * 80)
    print("PRUEBA 1: ALGORITMO RECURSIVO - FIBONACCI")
    print("=" * 80)

    pseudocode_recursive = """
fibonacci(n)
begin
    if (n <= 1) then
        return n
    else
        return fibonacci(n-1) + fibonacci(n-2)
    end
end
"""

    try:
        solution1 = agent.analyze(pseudocode_recursive)
        print(solution1)
        print("\n✅ Análisis recursivo completado exitosamente\n")
    except Exception as e:
        print(f"❌ Error en análisis recursivo: {e}\n")

    # Ejemplo 2: Algoritmo iterativo (Bubble Sort)
    print("=" * 80)
    print("PRUEBA 2: ALGORITMO ITERATIVO - BUBBLE SORT")
    print("=" * 80)

    pseudocode_iterative = """
bubbleSort(arr, n)
begin
    for i = 0 to n-1 do
        for j = 0 to n-i-1 do
            if arr[j] > arr[j+1] then
                swap(arr[j], arr[j+1])
            end
        end
    end
end
"""

    try:
        solution2 = agent.analyze(pseudocode_iterative)
        print(solution2)
        print("\n✅ Análisis iterativo completado exitosamente\n")
    except Exception as e:
        print(f"❌ Error en análisis iterativo: {e}\n")


if __name__ == "__main__":
    test_complete_analysis_agent()
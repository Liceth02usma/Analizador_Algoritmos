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
    
    asymptotic_best: str = Field(
        description="Cota inferior Ω (mejor caso)"
    )
    asymptotic_worst: str = Field(
        description="Cota superior O (peor caso)"
    )
    asymptotic_average: str = Field(
        description="Cota ajustada Θ (caso promedio)"
    )
    
    notation_explanation: str = Field(
        description="Explicación de las notaciones asintóticas"
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
            fallback=False
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
        
        # Construir prompt detallado
        prompt = self._build_analysis_prompt(pseudocode)
        
        # Invocar agente
        result = self.invoke_simple(
            content=prompt,
            thread_id="complete_analysis"
        )
        
        # Extraer respuesta estructurada
        analysis = self.extract_response(result)
        
        if not analysis:
            raise ValueError("No se pudo extraer respuesta estructurada del agente")
        
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

RESPONDE EN JSON VÁLIDO siguiendo el schema CompleteAnalysisResponse."""

    def _convert_to_solution(
        self, 
        analysis: CompleteAnalysisResponse, 
        pseudocode: str
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
            complexity_lines.append({
                "line": line_analysis.line,
                "code": line_analysis.code,
                "complexity": line_analysis.cost,
                "explanation": line_analysis.explanation
            })
        
        # Construir explain_complexity (explicación textual del análisis)
        explain_complexity = self._build_complexity_explanation(analysis)
        
        # Construir notación asintótica
        asymptotic_notation = {
            "best": analysis.asymptotic_best,
            "worst": analysis.asymptotic_worst,
            "average": analysis.asymptotic_average,
            "explanation": analysis.notation_explanation
        }
        
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
            extra={
                "pseudocode": pseudocode,
                "analysis_complete": True
            }
        )
        
        return solution

    def _build_complexity_explanation(self, analysis: CompleteAnalysisResponse) -> str:
        """Construye explicación textual de la complejidad."""
        
        parts = []
        
        parts.append(f"**Algoritmo**: {analysis.algorithm_name}")
        parts.append(f"**Categoría**: {analysis.algorithm_category}")
        parts.append(f"**Tipo**: {'Recursivo' if analysis.algorithm_type == 'recursive' else 'Iterativo'}")
        parts.append("")
        
        parts.append(f"**Ecuación**: {analysis.equation}")
        parts.append(f"**Método de resolución**: {analysis.solution_method}")
        parts.append(f"**Complejidad final**: {analysis.final_complexity}")
        parts.append("")
        
        parts.append("**Notaciones asintóticas**:")
        parts.append(f"- Mejor caso (Ω): {analysis.asymptotic_best}")
        parts.append(f"- Peor caso (O): {analysis.asymptotic_worst}")
        parts.append(f"- Caso promedio (Θ): {analysis.asymptotic_average}")
        
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

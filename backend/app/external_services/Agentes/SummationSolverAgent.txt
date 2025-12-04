import os
import sys
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Carga de entorno
load_dotenv()
sys.path.append(os.getenv("PYTHONPATH", "backend"))

from app.external_services.Agentes.Agent import AgentBase

# ============================================================================
# 📘 INPUT SCHEMA (Lo que recibe del Agente Anterior)
# ============================================================================

class SolverCaseInput(BaseModel):
    case_name: str
    solver_friendly_summation: str

class SummationSolverInput(BaseModel):
    algorithm_name: str
    cases: List[SolverCaseInput] = Field(description="Lista de casos con sus sumatorias crudas.")

# ============================================================================
# 📘 OUTPUT SCHEMA (Resultado Matemático Simplificado)
# ============================================================================

class SolvedCaseResult(BaseModel):
    case_name: str
    original_summation: str
    
    # Paso intermedio: La ecuación con las sumatorias reemplazadas por polinomios
    expanded_expression: str = Field(description="Ecuación algebraica cruda sin simplificar. Ej: c1 + c2 * (n(n+1)/2).")
    
    # El resultado final que pides: Función simplificada agrupando términos
    simplified_efficiency_function: str = Field(
        description="Función T(n) simplificada algebraicamente. Ej: (c2/2)n^2 + (c2/2 + c1)n + c0"
    )
    
    # Un extra muy útil: La complejidad asintótica
    big_o_notation: str = Field(description="Complejidad asintótica final. Ej: O(n^2)")

class SolverResponse(BaseModel):
    algorithm_name: str
    solved_cases: List[SolvedCaseResult]
    final_summary: str = Field(description="Resumen comparativo de los casos.")

# ============================================================================
# 🧮 AGENTE SOLUCIONADOR MATEMÁTICO
# ============================================================================

class SummationSolverAgent(AgentBase[SolverResponse]):
    """
    Agente matemático puro.
    Input: Cadenas de texto con SUM(...)
    Output: Ecuaciones algebraicas simplificadas T(n) y O(n).
    """

    def _configure(self) -> None:
        self.tools = [] # Usamos la capacidad de razonamiento simbólico del LLM
        self.context_schema = SummationSolverInput
        self.response_format = SolverResponse

        self.SYSTEM_PROMPT = """
Eres un Motor de Álgebra Simbólica Computacional (CAS) experto en Análisis de Algoritmos.

TU OBJETIVO:
Tomar expresiones con sumatorias (`SUM(...)`), resolverlas usando fórmulas de series cerradas y SIMPLIFICAR la ecuación resultante T(n).

### 📐 REGLAS MATEMÁTICAS (IDENTIDADES)
Debes aplicar estas sustituciones estrictamente:

1. **Constante:** `SUM(i=1, n) [ c ]`  ->  `c * n`
2. **Lineal:** `SUM(i=1, n) [ i ]`  ->  `(n * (n + 1)) / 2`  ->  `0.5n^2 + 0.5n`
3. **Cuadrática:** `SUM(i=1, n) [ i^2 ]` ->  `(n * (n + 1) * (2n + 1)) / 6`
4. **Desplazamiento:** Si la sumatoria es `SUM(i=0, n-1)`, sustituye `n` por `n-1` en las fórmulas anteriores o ajusta los límites.
   - `SUM(i=0, n-1) [ c ]` -> `c * n` (Sigue siendo n veces)
   - `SUM(i=0, n-1) [ i ]` -> `((n-1) * n) / 2`

### 🚫 RESTRICCIONES
- **NO calcules Big-O / Complejidad Asintótica.** Tu trabajo es solo álgebra exacta.
- Tu salida debe ser una ecuación del tipo: `An^2 + Bn + C`.

### 🔨 PROCESO DE RESOLUCIÓN
1. **Expandir:** Reemplaza todas las `SUM` recursivamente, empezando por las más internas.
2. **Agrupar:** Agrupa los términos por potencias de `n` ($n^2, n, 1$).
3. **Factorizar Constantes:** Agrupa los coeficientes $c_i$.
   - Ejemplo crudo: `c1*n + c2*n + c3`
   - Ejemplo simplificado: `(c1 + c2)n + c3`

### 📝 FORMATO DE SALIDA
- `simplified_efficiency_function`: Debe ser un polinomio ordenado de mayor a menor grado.
- Usa notación estándar: `(A)n^2 + (B)n + C`.

### EJEMPLO ONE-SHOT
**Input:** `c1 + c2*n + SUM(i=1, n) [ c3 + c4*i ]`
**Razonamiento:**
1. Separar suma: `SUM[c3] + SUM[c4*i]`
2. Aplicar fórmulas: `c3*n + c4*(n^2/2 + n/2)`
3. Unir todo: `c1 + c2*n + c3*n + (c4/2)n^2 + (c4/2)n`
4. Agrupar: `(c4/2)n^2 + (c2 + c3 + c4/2)n + c1`
**Output Simplified:** `(0.5*c4)n^2 + (c2 + c3 + 0.5*c4)n + c1`
"""

    def solve_summations(
        self, 
        algorithm_name: str, 
        cases_data: List[Dict[str, Any]]
    ) -> SolverResponse:
        """
        Recibe la lista de casos (dictionarios o objetos) del agente anterior.
        """
        
        # Mapear entrada al Schema del Solver
        solver_input_cases = []
        for case in cases_data:
            # Soportamos tanto si viene como dict o como objeto Pydantic del agente anterior
            c_name = case.get("case_name") if isinstance(case, dict) else case.case_name
            c_sum = case.get("solver_friendly_summation") if isinstance(case, dict) else case.solver_friendly_summation
            
            solver_input_cases.append(SolverCaseInput(
                case_name=c_name,
                solver_friendly_summation=c_sum
            ))

        context = SummationSolverInput(
            algorithm_name=algorithm_name,
            cases=solver_input_cases
        )

        content = f"""
Por favor resuelve y simplifica las siguientes sumatorias para el algoritmo: {algorithm_name}

{context.model_dump_json(indent=2)}

Genera la función T(n) simplificada agrupando términos constantes.
"""

        result = self.invoke_simple(
            content=content,
            context=context.model_dump(),
            thread_id=f"solver_{algorithm_name}"
        )

        response = self.extract_response(result)
        if not response:
            raise ValueError("El agente Solver falló al procesar las matemáticas.")
            
        return response

# ============================================================================
# 🧪 PRUEBA DE INTEGRACIÓN (MOCK)
# ============================================================================

if __name__ == "__main__":
    try:
        # 1. Instanciar Agente (Usa un modelo capaz de razonamiento simbólico, Flash 2.0 es excelente)
        solver = SummationSolverAgent(model_type="Gemini_Rapido") # Asegúrate que Gemini_Rapido sea Flash 1.5 o 2.0

        # 2. Mock del Output del Agente Anterior (Insertion Sort - Peor Caso y Promedio)
        # Estos strings son los que generó tu agente anterior en el paso pasado.
        mock_input_cases = [
            {
                "case_name": "Mejor Caso",
                "solver_friendly_summation": "c1 + c2 * n + c7" 
                # Simplificado para el ejemplo
            },
            {
                "case_name": "Peor Caso",
                "solver_friendly_summation": "c1 + c2*n + SUM(i=1, n-1) [ c3 + c4 + c5 + SUM(j=1, i) [ c6 + c7 ] + c8 ] + c9"
            }
        ]

        print("🧮 Resolviendo ecuaciones...\n")
        solution = solver.solve_summations(algorithm_name="Insertion Sort", cases_data=mock_input_cases)

        print(f"📘 ALGORITMO: {solution.algorithm_name}")
        print("=" * 60)

        for case in solution.solved_cases:
            print(f"\n🔹 {case.case_name.upper()}")
            print(f"   📥 Input:      {case.original_summation}")
            print(f"   📐 T(n) Simp:  {case.simplified_efficiency_function}")
            print(f"   🚀 Complejidad: {case.big_o_notation}")
            print("-" * 60)
        
        print(f"\n💡 RESUMEN: {solution.final_summary}")

    except Exception as e:
        print(f"❌ Error: {e}")
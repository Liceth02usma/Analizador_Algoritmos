# app/external_services/Agentes/IterativeAnalyzerAgent.py

import os
import sys
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool

load_dotenv()
sys.path.append(os.getenv("PYTHONPATH", "backend"))

from app.external_services.Agentes.Agent import AgentBase

# ============================================================================
# 📘 SCHEMAS OPTIMIZADOS (Con lista 'cases')
# ============================================================================

class IterativeAnalysisInput(BaseModel):
    pseudocode: str = Field(description="Pseudocódigo numerado.")
    ast: Any = Field(description="AST simplificado.")
    algorithm_name: str = Field(description="Nombre.")

class LineCost(BaseModel):
    line: int = Field(description="Número de línea.")
    # Nota: Eliminamos 'content' para ahorrar tokens
    cost_constant: str = Field(description="Simbolo (c1, c2).")
    execution_count: str = Field(description="Algebraico (n, n+1).")
    total_cost_expression: str = Field(description="c1 * (n+1).")

class CaseDetail(BaseModel):
    case_name: str = Field(description="'General', 'Mejor', 'Peor', etc.")
    condition: str = Field(description="Condición que activa este caso.")
    line_analysis: List[LineCost] = Field(description="Tabla de costos.")
    solver_friendly_summation: str = Field(description="Formato funcional SUM(i=1, n)...")
    efficiency_function: str = Field(description="T(n) cruda.")

class IterativeAnalysisResponse(BaseModel):
    algorithm_name: str
    is_case_dependent: bool = Field(
        description="True si existen diferencias entre Mejor/Peor caso. False si siempre es igual."
    )
    # 🌟 AQUÍ ESTÁ EL CAMBIO IMPORTANTE QUE FALTABA:
    cases: List[CaseDetail] = Field(
        description="Lista de casos. Si is_case_dependent=False, retorna solo un caso 'General'."
    )
    general_explanation: str = Field(description="Breve resumen.")

# ============================================================================
# 🏎️ AGENTE VELOZ
# ============================================================================

class IterativeAnalyzerAgent(AgentBase[IterativeAnalysisResponse]):
    
    def _configure(self) -> None:
        self.tools = []
        self.context_schema = IterativeAnalysisInput
        self.response_format = IterativeAnalysisResponse

        # Prompt optimizado para generar la lista 'cases'
        self.SYSTEM_PROMPT = """
Eres un Experto en Eficiencia Algorítmica (Método de Conteo de Pasos).

### ⚡ ESTRATEGIA DE DETECCIÓN
1. **Determinista:** Si el flujo NO depende de los datos (ej: Factorial), genera 1 caso "General".
2. **Dependiente:** Si el flujo depende de los datos (ej:Ordenamientos, Búsqueda), **ACCIÓN:** Genera OBLIGATORIAMENTE  "Mejor", "Promedio", "Peor".

### ⚖️ REGLAS DE CONTEO (HEADER vs BODY)
- **Header (for/while):** Ejecuciones = (Iteraciones del Cuerpo) + 1.
- **Body:** Ejecuciones = Iteraciones exactas.

### ⚠️ REGLA DE ORO: SUMATORIA TOTAL
La `solver_friendly_summation` debe ser la suma de **TODAS** las líneas del código.
- **ERROR COMÚN:** Olvidar sumar las líneas fuera de los bucles (inicializaciones `i=0`, `return x`).
- **CORRECTO:** `c1 + c2 + SUM(i=1, n) [ ... ] + c_return`.
- Debes incluir explícitamente las constantes `c` de las líneas que se ejecutan 1 vez.

### 📝 SALIDA JSON
- `line_analysis`: Detalle línea por línea.
- `cases`: Lista de casos (Nunca vacía).

MANTÉN LA RESPUESTA CONCISA.
"""

    def _add_line_numbers(self, code: str) -> str:
        lines = [l for l in code.split('\n') if l.strip()] # Ignorar vacías
        return "\n".join([f"{i+1}. {line}" for i, line in enumerate(lines)])

    def analyze_algorithm(
        self,
        pseudocode: str,
        ast: Dict[str, Any],
        algorithm_name: str = "Algoritmo"
    ) -> IterativeAnalysisResponse:
        
        numbered_code = self._add_line_numbers(pseudocode)

        context = IterativeAnalysisInput(
            pseudocode=numbered_code,
            ast=ast, 
            algorithm_name=algorithm_name
        )

        content = f"""
Código Numerado:
{numbered_code}

1. ¿Es caso-dependiente?
2. Calcula T(n) y Sumatorias.
3. Si Best == Worst, devuelve solo 1 caso "General" dentro de la lista `cases`.
"""
        
        result = self.invoke_simple(
            content=content, 
            context=context.model_dump(),
            thread_id=f"fast_analysis_{algorithm_name}"
        )

        response = self.extract_response(result)
        
        if not response: 
            # Debug extra por si falla el parseo
            print(f"RAW RESULT: {result}")
            raise ValueError("Error en agente: No se obtuvo respuesta estructurada.")
            
        return response
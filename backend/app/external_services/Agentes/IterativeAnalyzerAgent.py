import os
import sys
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from app.external_services.Agentes.Agent import AgentBase

# Importamos la nueva utilidad determinista
from app.models.iterative.complexity_utils import calculate_elementary_operations

load_dotenv()
sys.path.append(os.getenv("PYTHONPATH", "backend"))

# ============================================================================
# 📘 SCHEMAS ACTUALIZADOS (Strict Typing)
# ============================================================================

class IterativeAnalysisInput(BaseModel):
    pseudocode: str = Field(description="Pseudocódigo numerado.")
    line_costs_map: str = Field(description="Mapa textual de costos pre-calculados para guiar al agente.")
    ast: Any = Field(description="AST simplificado.")
    algorithm_name: str = Field(description="Nombre.")

class LineCost(BaseModel):
    line: int = Field(description="Número de línea.")
    
    # CAMBIO IMPORTANTE: Ahora es un entero exacto
    cost_constant: int = Field(description="Número de operaciones elementales calculado (C).")
    
    execution_count: str = Field(description="Expresión algebraica de repeticiones (E). Ej: 'n', 'n+1'.")
    
    # El agente debe formar la expresión C * E
    total_cost_expression: str = Field(description="Expresión total. Ej: '3 * (n+1)'.")

class CaseDetail(BaseModel):
    case_name: str = Field(description="'General', 'Mejor', 'Peor', 'Promedio'.")
    condition: str = Field(description="Condición del caso.")
    line_analysis: List[LineCost] = Field(description="Tabla de análisis.")
    solver_friendly_summation: str = Field(description="Sumatoria total. Ej: '3*(n+1) + SUM(...)'")
    efficiency_function: str = Field(description="T(n) cruda.")

class IterativeAnalysisResponse(BaseModel):
    algorithm_name: str
    is_case_dependent: bool = Field(description="True si hay diferencia entre casos.")
    cases: List[CaseDetail]
    general_explanation: str

# ============================================================================
# 🤖 AGENTE ITERATIVO (Lógica Híbrida: Python + LLM)
# ============================================================================

class IterativeAnalyzerAgent(AgentBase[IterativeAnalysisResponse]):
    
    def _configure(self) -> None:
        self.tools = []
        self.context_schema = IterativeAnalysisInput
        self.response_format = IterativeAnalysisResponse

        # Prompt Reforzado con las Reglas de Costo
        self.SYSTEM_PROMPT = """
Eres un Experto en Eficiencia Algorítmica (Método de Conteo de Pasos).

### 🎯 OBJETIVO
Construir la función de complejidad T(n) usando costos pre-calculados y lógica de bucles.

### 📥 INPUT QUE RECIBIRÁS
1. **Pseudocódigo Numerado**
2. **Mapa de Costos:** Una lista que dice "Línea X: Costo Y".
   - ⚠️ **REGLA DE ORO:** DEBES USAR EXACTAMENTE EL COSTO `Y` QUE TE DOY PARA CADA LÍNEA. No inventes ni recalcules el costo unitario.

### ⚙️ TU TRABAJO (Paso a Paso)
Para cada línea de código:
1. **Identificar Costo (C):** Copia el valor entero del "Mapa de Costos".
2. **Determinar Ejecuciones (E):** Analiza algebraicamente cuántas veces se ejecuta.
   - **Header de FOR/WHILE:** `Iteraciones del cuerpo + 1`.
   - **Cuerpo:** `Iteraciones exactas`.
   - **Fuera de bucles:** `1` (o `0` si está en un `else` no visitado).
3. **Calcular Total:** `C * E`. (Ejemplo: Si Costo=3 y Ejecuciones=n+1 -> `3 * (n+1)`).

### ⚡ ESTRATEGIA DE CASOS
- **Determinista:** (Factorial, Fibonacci Iterativo) -> Genera 1 caso "General".
- **Dependiente:** (Bubble Sort, Búsqueda Lineal) -> Genera "Mejor", "Promedio", "Peor".

### 📝 FORMATO DE SALIDA
- `cases`: Lista de casos. Nunca vacía.
- `solver_friendly_summation`: La suma de TODOS los costos totales. Incluye las líneas constantes fuera de los bucles.

MANTÉN LA RESPUESTA CONCISA.
"""

    def _prepare_data(self, code: str):
        """
        Pre-procesa el código:
        1. Lo numera.
        2. Calcula el costo determinista de cada línea usando la función Python.
        """
        lines = code.split('\n')
        numbered_lines = []
        costs_context = []
        
        real_idx = 1
        for line in lines:
            # Ignoramos líneas vacías para la numeración lógica visual, 
            # pero mantenemos consistencia con el código original.
            if not line.strip(): 
                continue
                
            # Calculamos costo exacto con la utilidad
            cost = calculate_elementary_operations(line)
            
            numbered_lines.append(f"{real_idx}. {line}")
            
            if cost > 0:
                costs_context.append(f"Línea {real_idx}: Costo {cost}")
            else:
                costs_context.append(f"Línea {real_idx}: Costo 0 (Estructural)")
                
            real_idx += 1
            
        return "\n".join(numbered_lines), "\n".join(costs_context)

    def analyze_algorithm(
        self,
        pseudocode: str,
        ast: Dict[str, Any],
        algorithm_name: str = "Algoritmo"
    ) -> IterativeAnalysisResponse:
        
        # 1. Ejecutar el cálculo determinista
        numbered_code, costs_map = self._prepare_data(pseudocode)

        context = IterativeAnalysisInput(
            pseudocode=numbered_code,
            line_costs_map=costs_map, # Inyección de costos reales
            ast=ast, 
            algorithm_name=algorithm_name
        )

        content = f"""
Analiza este algoritmo paso a paso.

--- CÓDIGO NUMERADO ---
{numbered_code}

--- TABLA DE COSTOS ELEMENTALES (OBLIGATORIO USAR ESTOS VALORES) ---
{costs_map}

Instrucciones:
1. Determina algebraicamente el número de ejecuciones (E) para cada línea.
2. Multiplica E por el Costo (C) dado en la tabla.
3. Genera la sumatoria total.
"""
        
        result = self.invoke_simple(
            content=content, 
            context=context.model_dump(),
            thread_id=f"analysis_{algorithm_name}"
        )

        response = self.extract_response(result)
        
        if not response: 
            raise ValueError("Error en agente: No se obtuvo respuesta estructurada.")
            
        return response
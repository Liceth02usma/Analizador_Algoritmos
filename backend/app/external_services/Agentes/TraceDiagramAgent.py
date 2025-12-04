import os
import sys
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
sys.path.append(os.getenv("PYTHONPATH", "backend"))

from app.external_services.Agentes.Agent import AgentBase

# ============================================================================
# 📘 SCHEMAS
# ============================================================================

class TraceRequest(BaseModel):
    pseudocode: str = Field(description="Pseudocódigo del algoritmo.")
    algorithm_name: str = Field(description="Nombre del algoritmo.")
    # Recibimos los casos detectados por el agente anterior para saber qué graficar
    cases_summary: str = Field(description="Resumen de los casos (Mejor/Peor) y sus condiciones.")

class DiagramDetail(BaseModel):
    case_name: str = Field(description="Ej: 'Mejor Caso', 'Peor Caso'.")
    description: str = Field(description="Breve descripción del flujo (ej: 'El bucle termina inmediatamente').")
    mermaid_code: str = Field(description="Código fuente Mermaid.js (graph TD) del diagrama de flujo.")

class TraceResponse(BaseModel):
    algorithm_name: str
    diagrams: List[DiagramDetail] = Field(description="Lista de diagramas generados.")

# ============================================================================
# 🎨 AGENTE DE DIAGRAMACIÓN
# ============================================================================

class TraceDiagramAgent(AgentBase[TraceResponse]):
    """
    Agente visualizador. Convierte la lógica de ejecución en diagramas de flujo Mermaid.js.
    """

    def _configure(self) -> None:
        self.tools = []
        self.context_schema = TraceRequest
        self.response_format = TraceResponse

        self.SYSTEM_PROMPT = """
Eres un Experto en Visualización de Algoritmos y sintaxis Mermaid.js.
Tu tarea es generar **Diagramas de Flujo (Flowcharts)** que representen el seguimiento de la ejecución de un algoritmo.

### 🎯 OBJETIVO
Generar código `mermaid` (graph TD) para visualizar el flujo de control en diferentes escenarios (Mejor, Peor, Promedio).

### 🎨 REGLAS DE MERMAID (Estricto)
1. Usa `graph TD` al inicio.
2. Nodos:
   - Inicio/Fin: `id((Inicio))` / `id((Fin))` (Círculos o estadios)
   - Procesos/Asignaciones: `id[Texto]` (Rectángulos)
   - Decisiones (If/While): `id{Condición?}` (Rombos)
3. Conexiones:
   - `A --> B`
   - `A -- Sí --> B`
   - `A -- No --> C`
4. **NO uses espacios ni caracteres especiales en los IDs de los nodos.** (Ej: usa `node1`, `decision2`, no `nodo 1`).

### 🧠 LÓGICA DE SEGUIMIENTO (TRACE)
Debes adaptar el diagrama según el caso:
- **Mejor Caso:** Si la condición del bucle o if hace que el algoritmo termine rápido, dibuja ESE camino específico.
- **Peor Caso:** Muestra el ciclo completo. Usa notas en Mermaid (`Note right of id: Se repite N veces`) para indicar iteraciones masivas.
- **Estilo Pascal-like:** Recuerda que en tu gramática `for i=1 to n` implica una condición implícita `i <= n`.

### EJEMPLO ONE-SHOT (Búsqueda Lineal - Mejor Caso)
Input: "Buscar x en A. Mejor caso: x está en A[0]"
Output Mermaid:
graph TD
    Start((Inicio)) --> Init[i = 0]
    Init --> Check{i < n?}
    Check -- Sí --> Found{A[i] == x?}
    Found -- Sí (Mejor Caso) --> Ret[Return i]
    Ret --> End((Fin))
    Check -- No --> End
    Found -- No --> Inc[i = i + 1]
    Inc --> Check

### SALIDA JSON
Devuelve una lista de diagramas. Si el algoritmo es simple, un solo diagrama "General" basta.
"""

    def generate_diagrams(
        self, 
        pseudocode: str, 
        algorithm_name: str,
        cases_summary: str
    ) -> TraceResponse:
        
        context = TraceRequest(
            pseudocode=pseudocode,
            algorithm_name=algorithm_name,
            cases_summary=cases_summary
        )

        content = f"""
Genera los diagramas de flujo para: {algorithm_name}.

--- CÓDIGO ---
{pseudocode}

--- ESCENARIOS A GRAFICAR ---
{cases_summary}

Crea el código Mermaid para visualizar el flujo en el Mejor y Peor caso (y Promedio si aplica).
Usa notas para explicar repeticiones.
"""

        result = self.invoke_simple(
            content=content,
            context=context.model_dump(),
            thread_id=f"trace_{algorithm_name}"
        )

        response = self.extract_response(result)
        if not response:
            raise ValueError("Error generando diagramas.")
            
        return response
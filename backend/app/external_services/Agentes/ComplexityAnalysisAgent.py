import os
import sys
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from app.external_services.Agentes.Agent import AgentBase

load_dotenv()
sys.path.append(os.getenv("PYTHONPATH", "backend"))


class ComplexityCaseInput(BaseModel):
    case_name: str
    efficiency_function: str  # El polinomio T(n)


class ComplexityInput(BaseModel):
    algorithm_name: str
    cases: List[ComplexityCaseInput]


class AsymptoticResult(BaseModel):
    case_name: str

    # Aquí cumplimos el requisito de
    notation_type: str = Field(
        description="Tipo de cota: 'O' (Techo/Peor), 'Ω' (Piso/Mejor), 'Θ' (Exacta)."
    )
    complexity_class: str = Field(
        description="Clase de complejidad (ej: n, n^2, log n)."
    )
    formatted_notation: str = Field(description="Ej: 'O(n^2)', 'Ω(1)'.")
    justification: str = Field(
        description="Explicación basada en el término dominante."
    )


class ComplexityResponse(BaseModel):
    algorithm_name: str
    analysis: List[AsymptoticResult]
    final_conclusion: str


class ComplexityAnalysisAgent(AgentBase[ComplexityResponse]):
    """
    Agente Teórico. Asigna la notación asintótica correcta según el caso.
    """

    def _configure(self) -> None:
        self.tools = []
        self.context_schema = ComplexityInput
        self.response_format = ComplexityResponse

        self.SYSTEM_PROMPT = """
Eres un Teórico de la Computación. Tu trabajo es clasificar la complejidad asintótica de polinomios T(n).

### 🎯 REGLAS DE ASIGNACIÓN (Estricto según Proyecto)
Debes asignar la notación correcta basándote en el nombre del caso:

1. **Peor Caso (Worst)** -> Tu salida DEBE usar **O (Big-O)**. Representa la cota superior.
2. **Mejor Caso (Best)** -> Tu salida DEBE usar **Ω (Omega)**. Representa la cota inferior.
3. **Caso Promedio (Average)** -> Tu salida DEBE usar **Θ (Theta)**. Representa el orden exacto.
4. **Caso General** (Algoritmos deterministas) -> Usa **Θ (Theta)**.

### ⚡ PROCESO
1. Identifica el **término dominante** del polinomio (mayor grado).
   - Ej: `(0.5)n^2 + 3n` -> Dominante `n^2`.
2. Ignora constantes y coeficientes menores.
3. Formatea la salida usando la notación asignada.

### EJEMPLO
Input: Case="Peor", T(n)="(c1)n^2 + n"
Output: notation="O", class="n^2", formatted="O(n^2)"
"""

    def determine_complexity(
        self, algorithm_name: str, cases_data: List[dict]
    ) -> ComplexityResponse:
        context = ComplexityInput(
            algorithm_name=algorithm_name,
            cases=[ComplexityCaseInput(**c) for c in cases_data],
        )

        content = f"Clasifica la complejidad asintótica para: {algorithm_name}\n{context.model_dump_json(indent=2)}"
        result = self.invoke_simple(
            content=content,
            context=context.model_dump(),
            thread_id=f"complex_{algorithm_name}",
        )
        return self.extract_response(result)

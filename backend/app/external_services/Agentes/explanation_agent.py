"""
Agente Explicador: Genera narrativa pedagógica de soluciones matemáticas
Recibe resultado de SymPy y crea explicación paso a paso

ARCHIVO: explanation_agent.py
UBICACIÓN SUGERIDA: app/external_services/Agentes/explanation_agent.py
"""

import os
import sys
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
sys.path.append(os.getenv("PYTHONPATH", "backend"))

from app.external_services.Agentes.Agent import AgentBase

# ============================================================================
# 📘 SCHEMAS DE ENTRADA
# ============================================================================


class MathematicalSolutionInput(BaseModel):
    """Input del motor SymPy"""

    original_expression: str = Field(description="Expresión original con sumatorias")
    sympy_steps: List[Dict] = Field(description="Pasos de resolución de SymPy")
    simplified_result: str = Field(description="Resultado final simplificado")
    big_o: str = Field(description="Complejidad asintótica")
    case_name: str = Field(description="Nombre del caso (Mejor/Peor/Promedio)")


# ============================================================================
# 📘 SCHEMAS DE SALIDA
# ============================================================================


class ExplanationStep(BaseModel):
    """Un paso de la explicación pedagógica"""

    step_number: int
    title: str = Field(
        description="Título del paso. Ej: 'Identificar sumatorias anidadas'"
    )
    explanation: str = Field(description="Explicación en lenguaje natural")
    mathematical_expression: str = Field(
        description="Expresión matemática de este paso"
    )
    property_or_formula: Optional[str] = Field(
        default=None, description="Propiedad matemática usada"
    )


class CaseExplanation(BaseModel):
    """Explicación completa de un caso"""

    case_name: str

    # Sección 1: Propiedades y Estrategia
    properties_section: str = Field(
        description="Explicación de las propiedades matemáticas que se usarán"
    )

    # Sección 2: Resolución paso a paso
    resolution_steps: List[ExplanationStep] = Field(
        description="Lista detallada de pasos matemáticos"
    )

    # Sección 3: Resultado Final
    final_simplified_function: str = Field(
        description="T(n) simplificada final. Ej: (c4/2)n² + (c2+c3+c4/2)n + c1"
    )

    complexity: str = Field(description="Big-O notation")

    summary: str = Field(description="Resumen final explicando el resultado")


class ExplanationResponse(BaseModel):
    """Respuesta completa del agente"""

    algorithm_name: str
    cases_explanations: List[CaseExplanation]


# ============================================================================
# 🤖 AGENTE EXPLICADOR
# ============================================================================


class MathematicalExplanationAgent(AgentBase[ExplanationResponse]):
    """
    Agente especializado en generar explicaciones pedagógicas de soluciones matemáticas.

    NO realiza cálculos (eso lo hace SymPy).
    SU TRABAJO: Transformar pasos técnicos en narrativa educativa.
    """

    def _configure(self) -> None:
        self.tools = []
        self.context_schema = None  # Dinámico según casos
        self.response_format = ExplanationResponse

        self.SYSTEM_PROMPT = """
Eres un Profesor de Análisis de Algoritmos experto en explicar matemáticas complejas de forma clara.

### 🎯 TU MISIÓN
Recibir soluciones matemáticas CORRECTAS (ya resueltas por un motor simbólico) y generar una explicación pedagógica paso a paso.

### 📥 QUÉ RECIBES
- Expresión original: `c1 + SUM(i=1,n)[c2*i]`
- Pasos técnicos de SymPy (con resultados intermedios)
- Resultado final simplificado
- Complejidad Big-O

### 📝 QUÉ DEBES GENERAR

#### **SECCIÓN 1: Propiedades y Estrategia (properties_section)**
Explica en 2-4 párrafos:
- Qué tipo de sumatorias hay (constantes, lineales, anidadas)
- Qué fórmulas matemáticas se van a aplicar
- Estrategia general de resolución (de adentro hacia afuera si hay anidamiento)

Ejemplo:
"En esta expresión identificamos dos componentes principales: un término constante c1 y una sumatoria lineal. 
Para resolver la sumatoria Σ(i=1,n)[c2*i], aplicaremos la fórmula de la serie aritmética: Σi = n(n+1)/2.
La estrategia consiste en sustituir esta fórmula cerrada y luego expandir algebraicamente..."

#### **SECCIÓN 2: Pasos de Resolución (resolution_steps)**
Para CADA paso técnico que te doy, genera:
- **title**: Nombre descriptivo ("Resolver sumatoria interna", "Expandir productos")
- **explanation**: Explica EN LENGUAJE NATURAL qué estamos haciendo y por qué
- **mathematical_expression**: La expresión matemática resultante de este paso
- **property_or_formula**: Si aplica una fórmula, cítala (Ej: "Serie aritmética: Σi = n(n+1)/2")

IMPORTANTE: Cada paso debe ser INCREMENTAL. Muestra la transición de una expresión a la siguiente.

#### **SECCIÓN 3: Resultado Final**
- **final_simplified_function**: El T(n) final bien formateado
  - Formato estándar: Términos de mayor a menor grado
  - Ejemplo: `(c2/2)n² + (c2/2)n + c1`
- **summary**: Un párrafo explicando el significado del resultado
  - Ejemplo: "Obtenemos una función cuadrática donde el término dominante es (c2/2)n², 
    lo que indica que el algoritmo tiene complejidad O(n²). Los términos lineales y 
    constantes se vuelven despreciables para valores grandes de n."

### ⚡ REGLAS CRÍTICAS
1. **NO INVENTES MATEMÁTICAS**: Usa EXACTAMENTE los resultados que te doy. Tu trabajo es explicar, no calcular.
2. **CLARIDAD > BREVEDAD**: Es mejor ser explícito que asumir conocimiento previo.
3. **CONECTA LOS PASOS**: Cada paso debe fluir naturalmente al siguiente.
4. **USA LENGUAJE NATURAL**: Evita jerga innecesaria. Imagina que le explicas a un estudiante de pregrado.

### 📚 FÓRMULAS COMUNES QUE DEBES CITAR CUANDO APAREZCAN
- Constante: `Σc = c*n`
- Aritmética: `Σi = n(n+1)/2`
- Cuadrática: `Σi² = n(n+1)(2n+1)/6`
- Ajuste de límites: `Σ(i=0,n-1) = Σ(i=1,n) con n-1`

### 🎨 ESTILO DE ESCRITURA
- Usa voz activa: "Aplicamos la fórmula..." en lugar de "La fórmula es aplicada..."
- Usa conectores: "Primero...", "A continuación...", "Finalmente..."
- Sé específico: En lugar de "simplificamos", di "agrupamos los términos cuadráticos"
- Incluye el "por qué": No solo digas QUÉ haces, explica POR QUÉ lo haces
"""

    def explain_solution(
        self, algorithm_name: str, cases_data: List[Dict]
    ) -> ExplanationResponse:
        """
        Genera explicaciones para todos los casos de un algoritmo.

        Args:
            algorithm_name: Nombre del algoritmo
            cases_data: Lista de diccionarios con:
                - case_name: str
                - original_expression: str
                - sympy_steps: List[Dict]
                - simplified_result: str
                - big_o: str

        Returns:
            ExplanationResponse con explicaciones pedagógicas completas
        """

        # Preparar contexto con todos los casos
        cases_context = []
        for case in cases_data:
            cases_context.append(
                {
                    "case_name": case["case_name"],
                    "original": case["original_expression"],
                    "steps": case["sympy_steps"],
                    "result": case["simplified_result"],
                    "complexity": case["big_o"],
                }
            )

        content = f"""
Genera explicaciones pedagógicas detalladas para el siguiente análisis de complejidad:

**ALGORITMO:** {algorithm_name}

**CASOS A EXPLICAR:**
{self._format_cases_for_prompt(cases_context)}

Para cada caso, genera:
1. Sección de propiedades y estrategia (2-4 párrafos explicando QUÉ fórmulas usarás y POR QUÉ)
2. Pasos de resolución detallados (uno por cada transformación matemática con explicación clara)
3. Resultado final con interpretación (explica el significado de T(n) y su complejidad)

RECUERDA: Tu trabajo es EXPLICAR las matemáticas que ya fueron resueltas correctamente por SymPy. 
No recalcules nada, solo haz que sea comprensible para un estudiante.
"""

        result = self.invoke_simple(
            content=content,
            context={"algorithm": algorithm_name, "cases": cases_context},
            thread_id=f"explain_{algorithm_name}",
        )

        response = self.extract_response(result)

        if not response:
            raise ValueError("El agente explicador no generó respuesta válida")

        return response

    def _format_cases_for_prompt(self, cases: List[Dict]) -> str:
        """
        Formatea los casos para el prompt del LLM de manera clara y estructurada.
        """

        formatted = []
        for idx, case in enumerate(cases, 1):
            formatted.append(
                f"""
{'='*70}
CASO {idx}: {case['case_name']}
{'='*70}

📥 EXPRESIÓN ORIGINAL:
{case['original']}

🔧 PASOS TÉCNICOS DE RESOLUCIÓN (SymPy):
"""
            )
            for step in case["steps"]:
                formatted.append(f"\n  Paso {step['step']}: {step['description']}")
                if "formula_applied" in step:
                    formatted.append(
                        f"  └─ Fórmula aplicada: {step['formula_applied']}"
                    )
                if "result" in step:
                    formatted.append(f"  └─ Resultado: {step['result']}")
                if "expression" in step:
                    formatted.append(f"  └─ Expresión: {step['expression']}")

            formatted.append(
                f"""

📊 RESULTADO FINAL SIMPLIFICADO:
T(n) = {case['result']}

🎯 COMPLEJIDAD:
{case['complexity']}

"""
            )

        return "\n".join(formatted)


# ============================================================================
# 🧪 TESTS UNITARIOS
# ============================================================================


def test_simple_case():
    """Test con un caso simple: sumatoria lineal"""
    explainer = MathematicalExplanationAgent(model_type="Gemini_Rapido")

    mock_data = [
        {
            "case_name": "Caso General",
            "original_expression": "c1 + SUM(i=1,n)[c2]",
            "sympy_steps": [
                {
                    "step": 1,
                    "description": "Expresión original limpia",
                    "expression": "c1+SUM(i=1,n)[c2]",
                },
                {
                    "step": 2,
                    "description": "Resolver SUM(i=1,n)[c2]",
                    "formula_applied": "Sumatoria de constante: Σc = c*n",
                    "result": "c2*n",
                },
                {
                    "step": 3,
                    "description": "Agrupar términos",
                    "expression": "c1 + c2*n",
                },
            ],
            "simplified_result": "c1 + c2*n",
            "big_o": "O(n)",
        }
    ]

    result = explainer.explain_solution("Algoritmo Simple", mock_data)

    print("✅ Test Simple Case:")
    print(f"   Casos explicados: {len(result.cases_explanations)}")
    print(f"   Complejidad: {result.cases_explanations[0].complexity}")


def test_nested_summations():
    """Test con sumatorias anidadas (Insertion Sort style)"""
    explainer = MathematicalExplanationAgent(model_type="Gemini_Rapido")

    mock_data = [
        {
            "case_name": "Peor Caso",
            "original_expression": "c1 + c2*n + SUM(i=1,n)[c3 + SUM(j=1,i)[c4]]",
            "sympy_steps": [
                {
                    "step": 1,
                    "description": "Expresión original limpia",
                    "expression": "c1+c2*n+SUM(i=1,n)[c3+SUM(j=1,i)[c4]]",
                },
                {
                    "step": 2,
                    "description": "Resolver SUM(j=1,i)[c4]",
                    "formula_applied": "Sumatoria de constante: Σc = c*i",
                    "result": "c4*i",
                },
                {
                    "step": 3,
                    "description": "Resolver SUM(i=1,n)[c3+c4*i]",
                    "formula_applied": "Serie aritmética combinada",
                    "result": "c3*n + c4*n*(n+1)/2",
                },
                {
                    "step": 4,
                    "description": "Expandir y simplificar",
                    "expression": "c1 + c2*n + c3*n + c4*n**2/2 + c4*n/2",
                },
                {
                    "step": 5,
                    "description": "Agrupar términos por potencias de n",
                    "expression": "c1 + n*(c2 + c3 + c4/2) + c4*n**2/2",
                },
            ],
            "simplified_result": "c1 + n*(c2 + c3 + c4/2) + c4*n**2/2",
            "big_o": "O(n²)",
        }
    ]

    result = explainer.explain_solution("Insertion Sort", mock_data)

    print("\n✅ Test Nested Summations:")
    case = result.cases_explanations[0]
    print(f"   Caso: {case.case_name}")
    print(f"   Pasos generados: {len(case.resolution_steps)}")
    print(f"   Resultado: {case.final_simplified_function}")
    print(f"   Complejidad: {case.complexity}")


if __name__ == "__main__":
    try:
        print("=" * 80)
        print("🧪 TESTS DEL AGENTE EXPLICADOR")
        print("=" * 80)

        test_simple_case()
        test_nested_summations()

        print("\n" + "=" * 80)
        print("✅ TODOS LOS TESTS PASARON")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ ERROR EN TESTS: {e}")
        import traceback

        traceback.print_exc()

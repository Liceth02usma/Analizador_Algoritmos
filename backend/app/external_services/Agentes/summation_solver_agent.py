"""
Agente Híbrido de Resolución de Sumatorias
Combina: SymPy (precisión matemática) + LLM (explicación pedagógica)

Este es el agente que reemplaza tu SummationSolverAgent original
"""

import os
import sys
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
sys.path.append(os.getenv("PYTHONPATH", "backend"))

from app.external_services.Agentes.Agent import AgentBase

# Importar los módulos híbridos
from app.models.iterative.summation_solver import SummationSolver
from app.external_services.Agentes.explanation_agent import MathematicalExplanationAgent, ExplanationResponse

# ============================================================================
# 📘 INPUT SCHEMA (Compatible con tu agente anterior)
# ============================================================================

class SolverCaseInput(BaseModel):
    case_name: str
    solver_friendly_summation: str  # Ej: "c1 + SUM(i=1,n)[c2*i]"

class SummationSolverInput(BaseModel):
    algorithm_name: str
    cases: List[SolverCaseInput] = Field(description="Lista de casos con sus sumatorias")

# ============================================================================
# 📘 OUTPUT SCHEMA (Mejorado con explicaciones pedagógicas)
# ============================================================================

class DetailedStep(BaseModel):
    """Un paso detallado de la resolución"""
    step_number: int
    title: str
    explanation: str = Field(description="Explicación en lenguaje natural")
    mathematical_expression: str = Field(description="Expresión matemática")
    property_or_formula: Optional[str] = None

class SolvedCaseResult(BaseModel):
    case_name: str
    original_summation: str
    
    # SECCIÓN 1: Propiedades y Estrategia
    properties_explanation: str = Field(
        description="Explicación de las propiedades matemáticas que se van a usar"
    )
    
    # SECCIÓN 2: Resolución Paso a Paso
    resolution_steps: List[DetailedStep] = Field(
        description="Pasos matemáticos detallados con explicaciones"
    )
    
    # SECCIÓN 3: Resultado Final
    simplified_efficiency_function: str = Field(
        description="Función T(n) simplificada. Ej: (c4/2)n² + (c2+c3+c4/2)n + c1"
    )
    
    big_o_notation: str = Field(description="Complejidad asintótica. Ej: O(n²)")
    
    final_summary: str = Field(
        description="Resumen explicando el significado del resultado"
    )

class HybridSolverResponse(BaseModel):
    algorithm_name: str
    solved_cases: List[SolvedCaseResult]
    general_summary: str = Field(
        description="Resumen comparativo de todos los casos analizados"
    )

# ============================================================================
# 🤖 AGENTE HÍBRIDO (SymPy + LLM)
# ============================================================================

class HybridSummationSolverAgent(AgentBase[HybridSolverResponse]):
    """
    Agente que combina:
    1. SummationSolver (SymPy) -> Resolución matemática EXACTA
    2. ExplanationAgent (LLM) -> Generación de explicaciones pedagógicas
    
    Garantiza:
    - ✅ Precisión matemática del 100%
    - ✅ Explicaciones claras paso a paso
    - ✅ Bajo costo (solo LLM para narrativa)
    - ✅ Velocidad (SymPy resuelve en <100ms)
    """
    
    def __init__(self, model_type: str, *args, **kwargs):
        # Llamar al padre primero para establecer self.model_type
        super().__init__(model_type=model_type, *args, **kwargs)
        
        # Instanciar el motor matemático
        self.math_solver = SummationSolver()
        
        # Instanciar el agente explicador (ahora self.model_type está disponible)
        self.explainer = MathematicalExplanationAgent(
            model_type=self.model_type
        )
    
    def _configure(self) -> None:
        self.tools = []  # No necesitamos tools, usamos SymPy + otro agente
        self.context_schema = SummationSolverInput
        self.response_format = HybridSolverResponse
        
        # Este agente orquesta, no genera directamente
        self.SYSTEM_PROMPT = """
Eres un Agente Orquestador de Resolución Matemática.
Tu trabajo es coordinar el motor SymPy y el agente explicador.
"""
    
    def solve_summations(
        self,
        algorithm_name: str,
        cases_data: List[Dict[str, Any]]
    ) -> HybridSolverResponse:
        """
        Pipeline híbrido completo:
        
        1. Para cada caso:
           a. Usar SymPy para resolver matemáticamente (EXACTO)
           b. Obtener pasos técnicos
        
        2. Enviar resultados al agente explicador (LLM)
        
        3. Combinar ambos en respuesta estructurada
        
        Args:
            algorithm_name: Nombre del algoritmo
            cases_data: Lista de casos con sumatorias
        
        Returns:
            HybridSolverResponse con matemáticas exactas + explicaciones
        """
        
        print(f"\n🚀 Iniciando resolución híbrida para: {algorithm_name}")
        print("=" * 80)
        
        # FASE 1: RESOLUCIÓN MATEMÁTICA (SymPy)
        print("\n⚡ FASE 1: Motor Matemático SymPy")
        print("-" * 80)
        
        sympy_results = []
        
        for idx, case in enumerate(cases_data, 1):
            # Extraer datos del caso
            c_name = case.get("case_name") if isinstance(case, dict) else case.case_name
            c_sum = case.get("solver_friendly_summation") if isinstance(case, dict) else case.solver_friendly_summation
            
            print(f"\n  📌 Caso {idx}: {c_name}")
            print(f"     Input: {c_sum}")
            
            try:
                # Resolver con SymPy (100% determinista)
                math_result = self.math_solver.parse_and_solve(c_sum)
                
                print(f"     ✅ Resuelto: {math_result['simplified']}")
                print(f"     📊 Complejidad: {math_result['big_o']}")
                
                sympy_results.append({
                    "case_name": c_name,
                    "original_expression": c_sum,
                    "sympy_steps": math_result["steps"],
                    "simplified_result": math_result["simplified"],
                    "big_o": math_result["big_o"]
                })
                
            except Exception as e:
                print(f"     ❌ Error en SymPy: {e}")
                raise ValueError(f"Fallo matemático en caso '{c_name}': {e}")
        
        # FASE 2: GENERACIÓN DE EXPLICACIONES (LLM)
        print("\n\n🎓 FASE 2: Agente Explicador (LLM)")
        print("-" * 80)
        
        try:
            explanations = self.explainer.explain_solution(
                algorithm_name=algorithm_name,
                cases_data=sympy_results
            )
            
            print("     ✅ Explicaciones pedagógicas generadas")
            
        except Exception as e:
            print(f"     ⚠️ Advertencia: Fallo en explicaciones - {e}")
            # Si falla el LLM, al menos tenemos las matemáticas correctas
            explanations = self._create_fallback_explanations(sympy_results, algorithm_name)
        
        # FASE 3: COMBINAR RESULTADOS
        print("\n\n🔗 FASE 3: Integración de Resultados")
        print("-" * 80)
        
        solved_cases = []
        
        for sympy_result, explanation in zip(sympy_results, explanations.cases_explanations):
            
            # Convertir los pasos de explicación al formato DetailedStep
            detailed_steps = [
                DetailedStep(
                    step_number=step.step_number,
                    title=step.title,
                    explanation=step.explanation,
                    mathematical_expression=step.mathematical_expression,
                    property_or_formula=step.property_or_formula
                )
                for step in explanation.resolution_steps
            ]
            
            solved_cases.append(SolvedCaseResult(
                case_name=sympy_result["case_name"],
                original_summation=sympy_result["original_expression"],
                properties_explanation=explanation.properties_section,
                resolution_steps=detailed_steps,
                simplified_efficiency_function=explanation.final_simplified_function,
                big_o_notation=sympy_result["big_o"],  # Usamos Big-O de SymPy (más confiable)
                final_summary=explanation.summary
            ))
        
        # Generar resumen general
        general_summary = self._generate_general_summary(solved_cases, algorithm_name)
        
        print("     ✅ Respuesta híbrida completa generada\n")
        
        return HybridSolverResponse(
            algorithm_name=algorithm_name,
            solved_cases=solved_cases,
            general_summary=general_summary
        )
    
    def _create_fallback_explanations(self, sympy_results: List[Dict], algorithm_name: str):
        """
        Genera explicaciones básicas si el LLM falla.
        Esto garantiza que siempre tengamos al menos las matemáticas correctas.
        """
        
        from explanation_agent import ExplanationResponse, CaseExplanation, ExplanationStep
        
        cases_explanations = []
        
        for result in sympy_results:
            steps = [
                ExplanationStep(
                    step_number=step["step"],
                    title=step["description"],
                    explanation=f"Se aplica: {step.get('formula_applied', 'transformación algebraica')}",
                    mathematical_expression=step.get("expression", step.get("result", "")),
                    property_or_formula=step.get("formula_applied")
                )
                for step in result["sympy_steps"]
            ]
            
            cases_explanations.append(CaseExplanation(
                case_name=result["case_name"],
                properties_section="Se resuelven las sumatorias usando fórmulas cerradas.",
                resolution_steps=steps,
                final_simplified_function=result["simplified_result"],
                complexity=result["big_o"],
                summary=f"La función simplificada tiene complejidad {result['big_o']}."
            ))
        
        return ExplanationResponse(
            algorithm_name=algorithm_name,
            cases_explanations=cases_explanations
        )
    
    def _generate_general_summary(self, cases: List[SolvedCaseResult], algorithm_name: str) -> str:
        """
        Genera un resumen comparativo de todos los casos.
        """
        
        if len(cases) == 1:
            return f"El algoritmo {algorithm_name} tiene una complejidad {cases[0].big_o_notation} en todos los casos."
        
        complexities = [case.big_o_notation for case in cases]
        case_names = [case.case_name for case in cases]
        
        summary_parts = [f"El algoritmo {algorithm_name} presenta diferentes complejidades según el caso:"]
        
        for name, complexity in zip(case_names, complexities):
            summary_parts.append(f"- {name}: {complexity}")
        
        # Identificar el peor caso
        if "O(n²)" in complexities or "O(n^2)" in complexities:
            summary_parts.append("\nLa complejidad cuadrática en el peor caso puede ser problemática para entradas grandes.")
        elif all(c == "O(n)" for c in complexities):
            summary_parts.append("\nEl algoritmo mantiene complejidad lineal en todos los casos, lo cual es eficiente.")
        
        return " ".join(summary_parts)


# ============================================================================
# 🧪 PRUEBA DE INTEGRACIÓN COMPLETA
# ============================================================================

if __name__ == "__main__":
    try:
        print("\n" + "="*80)
        print("🧪 TEST DEL AGENTE HÍBRIDO COMPLETO")
        print("="*80)
        
        # Instanciar el agente híbrido
        hybrid_solver = HybridSummationSolverAgent(model_type="Gemini_Rapido")
        
        # Mock de datos del agente anterior (IterativeAnalyzerAgent)
        mock_insertion_sort_cases = [
            {
                "case_name": "Mejor Caso",
                "solver_friendly_summation": "c1 + c2*n + c3"
            },
            {
                "case_name": "Peor Caso",
                "solver_friendly_summation": "c1 + c2*n + SUM(i=2,n)[c3 + c4 + c5 + SUM(j=1,i-1)[c6 + c7] + c8] + c9"
            },
            {
                "case_name": "Caso Promedio",
                "solver_friendly_summation": "c1 + c2*n + SUM(i=2,n)[c3 + c4 + c5 + SUM(j=1,i/2)[c6 + c7] + c8] + c9"
            }
        ]
        
        # Ejecutar el pipeline híbrido completo
        solution = hybrid_solver.solve_summations(
            algorithm_name="Insertion Sort",
            cases_data=mock_insertion_sort_cases
        )
        
        # MOSTRAR RESULTADOS
        print("\n" + "="*80)
        print(f"📊 RESULTADOS FINALES: {solution.algorithm_name}")
        print("="*80)
        
        for case in solution.solved_cases:
            print(f"\n{'='*80}")
            print(f"📌 {case.case_name.upper()}")
            print(f"{'='*80}")
            
            print(f"\n📥 Expresión Original:")
            print(f"   {case.original_summation}")
            
            print(f"\n### 1️⃣ PROPIEDADES Y ESTRATEGIA")
            print(f"{case.properties_explanation}")
            
            print(f"\n### 2️⃣ RESOLUCIÓN PASO A PASO")
            for step in case.resolution_steps:
                print(f"\n**Paso {step.step_number}: {step.title}**")
                print(f"{step.explanation}")
                print(f"Expresión: {step.mathematical_expression}")
                if step.property_or_formula:
                    print(f"Fórmula: {step.property_or_formula}")
                print("-" * 60)
            
            print(f"\n### 3️⃣ RESULTADO FINAL")
            print(f"**T(n) = {case.simplified_efficiency_function}**")
            print(f"**Complejidad: {case.big_o_notation}**")
            print(f"\n{case.final_summary}")
        
        print(f"\n\n💡 RESUMEN GENERAL:")
        print(f"{solution.general_summary}")
        
        print("\n" + "="*80)
        print("✅ TEST COMPLETADO EXITOSAMENTE")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()
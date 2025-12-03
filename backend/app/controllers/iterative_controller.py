from typing import Dict, Any, List
# Importación de los 4 Agentes Especialistas
from app.external_services.Agentes.IterativeAnalyzerAgent import IterativeAnalyzerAgent
from app.external_services.Agentes.SummationSolverAgent import SummationSolverAgent
from app.external_services.Agentes.ComplexityAnalysisAgent import ComplexityAnalysisAgent
from app.external_services.Agentes.TraceDiagramAgent import TraceDiagramAgent

def analyze_iterative(pseudocode: str, ast: Dict[str, Any], algorithm_name: str = "Algoritmo Iterativo") -> Dict[str, Any]:
    """
    Orquesta el pipeline de análisis iterativo:
    1. Analyzer: Estructura y Conteo (n+1).
    2. Solver: Álgebra exacta (Polinomios).
    3. Complexity: Teoría Asintótica (O, Omega, Theta).
    4. Diagram: Visualización Mermaid.js.
    5. Merge: Fusión y Clonación de casos deterministas.
    """
    
    # Perfil rápido (Flash Lite / Flash 1.5) para velocidad
    MODEL_PROFILE = "Gemini_Ultra" 

    try:
        # ====================================================================
        # PASO 1: ANÁLISIS ESTRUCTURAL (Line by Line)
        # ====================================================================
        print(f"=== 🤖 1. Analizando Estructura ({algorithm_name})... ===")
        analyzer_agent = IterativeAnalyzerAgent(model_type=MODEL_PROFILE)
        structural_response = analyzer_agent.analyze_algorithm(
            pseudocode=pseudocode, ast=ast, algorithm_name=algorithm_name
        )
        
        # Validación de seguridad: Si falla el prompt y devuelve vacío
        if not structural_response.cases:
            return {"error": "El agente no detectó casos de análisis. Intente de nuevo."}

        # ====================================================================
        # PASO 2: RESOLUCIÓN ALGEBRAICA (Solver)
        # ====================================================================
        print(f"=== 🧮 2. Resolviendo Polinomios T(n)... ===")
        # Filtramos datos para ahorrar tokens (solo enviamos nombres y sumatorias)
        cases_for_solver = [
            {"case_name": c.case_name, "solver_friendly_summation": c.solver_friendly_summation}
            for c in structural_response.cases
        ]

        solver_agent = SummationSolverAgent(model_type=MODEL_PROFILE)
        math_response = solver_agent.solve_summations(
            algorithm_name=algorithm_name, cases_data=cases_for_solver
        )

        # ====================================================================
        # PASO 3: CLASIFICACIÓN ASINTÓTICA (O, Omega, Theta)
        # ====================================================================
        print(f"=== ⚖️ 3. Determinando Notación Asintótica... ===")
        # Preparamos los polinomios resueltos para que el experto teórico los clasifique
        cases_for_complexity = [
            {"case_name": c.case_name, "efficiency_function": c.simplified_efficiency_function}
            for c in math_response.solved_cases
        ]

        complexity_agent = ComplexityAnalysisAgent(model_type=MODEL_PROFILE)
        asymptotic_response = complexity_agent.determine_complexity(
            algorithm_name=algorithm_name, cases_data=cases_for_complexity
        )

        # ====================================================================
        # PASO 4: GENERACIÓN DE DIAGRAMAS
        # ====================================================================
        print(f"=== 🎨 4. Generando Diagramas de Flujo... ===")
        diagram_agent = TraceDiagramAgent(model_type=MODEL_PROFILE)
        
        # Resumen breve para el diagramador
        summary_text = "\n".join([f"- {c.case_name}: {c.condition}" for c in structural_response.cases])
        
        diagram_response = diagram_agent.generate_diagrams(
            pseudocode=pseudocode, algorithm_name=algorithm_name, cases_summary=summary_text
        )

        # ====================================================================
        # PASO 5: FUSIÓN INTELIGENTE (MERGE & CLONE) 🧠
        # ====================================================================
        print(f"=== 🔄 5. Fusionando Resultados... ===")
        merged_cases = []

        # Función auxiliar para construir el objeto final unificado
        def build_merged_case(struct_case, override_name=None):
            current_name = override_name if override_name else struct_case.case_name
            
            # Buscamos coincidencias en las respuestas de los otros agentes
            # Usamos lógica laxa (contains) para los nombres por si acaso
            solved_match = next((s for s in math_response.solved_cases if s.case_name == struct_case.case_name), None)
            asymp_match = next((a for a in asymptotic_response.analysis if a.case_name == struct_case.case_name), None)
            
            # Para diagramas, buscamos coincidencia aproximada
            diagram_match = next((d for d in diagram_response.diagrams if d.case_name.lower() in struct_case.case_name.lower() or struct_case.case_name.lower() in d.case_name.lower()), None)
            if not diagram_match and diagram_response.diagrams:
                diagram_match = diagram_response.diagrams[0] # Fallback al primero si no hay match

            # Ajuste de Notación para casos clonados (Requisito del Documento)
            # Si estamos clonando un caso General a Mejor/Peor, ajustamos la notación visualmente
            notation_str = asymp_match.formatted_notation if asymp_match else "N/A"
            notation_type = asymp_match.notation_type if asymp_match else "?"

            if override_name == "Mejor":
                notation_type = "Ω" # Omega
                notation_str = notation_str.replace("Θ", "Ω").replace("O", "Ω")
            elif override_name == "Peor":
                notation_type = "O" # Big-O
                notation_str = notation_str.replace("Θ", "O").replace("Ω", "O")
            elif override_name == "Promedio":
                notation_type = "Θ" # Theta
                notation_str = notation_str.replace("O", "Θ").replace("Ω", "Θ")

            return {
                "case_name": current_name,
                "condition": struct_case.condition,
                
                # Detalle Estructural
                "line_analysis": [line.model_dump() for line in struct_case.line_analysis],
                
                # Matemáticas Intermedias
                "raw_summation_str": struct_case.solver_friendly_summation,
                "math_steps": solved_match.expanded_expression if solved_match else "",
                
                # Resultado Final T(n)
                "simplified_complexity": solved_match.simplified_efficiency_function if solved_match else "N/A",
                
                # Teoría Asintótica (Cumpliendo Requisitos de Notación)
                "complexity_class": asymp_match.complexity_class if asymp_match else "Unknown",
                "notation_type": notation_type,
                "big_o": notation_str, # Campo legado para frontend, contiene la string completa "O(n^2)"
                
                # Visualización
                "trace_diagram": diagram_match.mermaid_code if diagram_match else ""
            }

        # LÓGICA DE EXPANSIÓN (Optimización de Costos)
        # Si detectamos que es un algoritmo determinista (1 caso "General"), lo triplicamos.
        is_single_general_case = len(structural_response.cases) == 1 and \
                                 "general" in structural_response.cases[0].case_name.lower()

        if is_single_general_case:
            print("⚡ Algoritmo Determinista detectado. Replicando caso General en Mejor/Promedio/Peor...")
            general_case = structural_response.cases[0]
            
            merged_cases.append(build_merged_case(general_case, override_name="Mejor"))
            merged_cases.append(build_merged_case(general_case, override_name="Promedio"))
            merged_cases.append(build_merged_case(general_case, override_name="Peor"))
        
        else:
            # Flujo normal: Mapeo 1 a 1 para algoritmos dependientes de datos (Insertion Sort, etc.)
            for struct_case in structural_response.cases:
                merged_cases.append(build_merged_case(struct_case))

        # Construcción final de la respuesta
        final_output = {
            "algorithm_name": algorithm_name,
            "complexity_type": "Iterativo",
            "is_case_dependent": not is_single_general_case,
            "general_explanation": structural_response.general_explanation,
            "math_summary": asymptotic_response.final_conclusion if asymptotic_response else "",
            "cases": merged_cases,
            "project_metadata": {
                "diagrams_generated": len(diagram_response.diagrams),
                "agent_model": MODEL_PROFILE,
                "optimization": "Cases replicated" if is_single_general_case else "Full analysis"
            }
        }

        return final_output

    except Exception as e:
        print(f"⚠️ Error Crítico en Controlador Iterativo: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
from typing import Dict, Any, List
import time

from app.models.solution import Solution


from app.external_services.Agentes.IterativeAnalyzerAgent import IterativeAnalyzerAgent

# from app.external_services.Agentes.SummationSolverAgent import SummationSolverAgent
from app.external_services.Agentes.ComplexityAnalysisAgent import (
    ComplexityAnalysisAgent,
)
from app.external_services.Agentes.TraceDiagramAgent import TraceDiagramAgent
from app.external_services.Agentes.summation_solver_agent import (
    HybridSummationSolverAgent,
)


def analyze_iterative(
    pseudocode: str, ast: Dict[str, Any], algorithm_name: str = "Algoritmo Iterativo"
) -> Dict[str, Any]:
    """
    Orquesta el pipeline de análisis iterativo y retorna un modelo Solution.
    """

    MODEL_PROFILE = "Gemini_Rapido"
    MODEL_PROFILE2 = "Gemini_Ultra"

    start_time = time.time()

    total_tokens = {"input": 0, "output": 0, "total": 0}
    agent_token_usage = {}

    try:

        print(f"=== 🤖 1. Analizando Estructura ({algorithm_name})... ===")
        analyzer_agent = IterativeAnalyzerAgent(model_type=MODEL_PROFILE2)
        structural_response = analyzer_agent.analyze_algorithm(
            pseudocode=pseudocode, ast=ast, algorithm_name=algorithm_name
        )

        agent_token_usage["IterativeAnalyzerAgent"] = {
            "input": analyzer_agent._last_input_tokens,
            "output": analyzer_agent._last_output_tokens,
            "total": analyzer_agent._last_total_tokens,
        }
        total_tokens["input"] += analyzer_agent._last_input_tokens
        total_tokens["output"] += analyzer_agent._last_output_tokens
        total_tokens["total"] += analyzer_agent._last_total_tokens

        if not structural_response.cases:
            return {
                "error": "El agente no detectó casos de análisis. Intente de nuevo."
            }

        print(f"=== 🧮 2. Resolviendo Polinomios T(n)... ===")
        cases_for_solver = [
            {
                "case_name": c.case_name,
                "solver_friendly_summation": c.solver_friendly_summation,
            }
            for c in structural_response.cases
        ]

        solver_agent = HybridSummationSolverAgent(model_type=MODEL_PROFILE)
        math_response = solver_agent.solve_summations(
            algorithm_name=algorithm_name, cases_data=cases_for_solver
        )

        agent_token_usage["HybridSummationSolverAgent"] = {
            "input": solver_agent._last_input_tokens,
            "output": solver_agent._last_output_tokens,
            "total": solver_agent._last_total_tokens,
        }
        total_tokens["input"] += solver_agent._last_input_tokens
        total_tokens["output"] += solver_agent._last_output_tokens
        total_tokens["total"] += solver_agent._last_total_tokens

        print(
            f"✅ Matemáticas completadas para {len(math_response.solved_cases)} casos."
        )
        print(math_response)

        print(f"=== ⚖️ 3. Determinando Notación Asintótica... ===")
        cases_for_complexity = [
            {
                "case_name": c.case_name,
                "efficiency_function": c.simplified_efficiency_function,
            }
            for c in math_response.solved_cases
        ]

        complexity_agent = ComplexityAnalysisAgent(model_type=MODEL_PROFILE)
        asymptotic_response = complexity_agent.determine_complexity(
            algorithm_name=algorithm_name, cases_data=cases_for_complexity
        )

        agent_token_usage["ComplexityAnalysisAgent"] = {
            "input": complexity_agent._last_input_tokens,
            "output": complexity_agent._last_output_tokens,
            "total": complexity_agent._last_total_tokens,
        }
        total_tokens["input"] += complexity_agent._last_input_tokens
        total_tokens["output"] += complexity_agent._last_output_tokens
        total_tokens["total"] += complexity_agent._last_total_tokens

        print(f"=== 🎨 4. Generando Diagramas de Flujo... ===")
        diagram_agent = TraceDiagramAgent(model_type=MODEL_PROFILE)
        summary_text = "\n".join(
            [f"- {c.case_name}: {c.condition}" for c in structural_response.cases]
        )

        diagram_response = diagram_agent.generate_diagrams(
            pseudocode=pseudocode,
            algorithm_name=algorithm_name,
            cases_summary=summary_text,
        )

        agent_token_usage["TraceDiagramAgent"] = {
            "input": diagram_agent._last_input_tokens,
            "output": diagram_agent._last_output_tokens,
            "total": diagram_agent._last_total_tokens,
        }
        total_tokens["input"] += diagram_agent._last_input_tokens
        total_tokens["output"] += diagram_agent._last_output_tokens
        total_tokens["total"] += diagram_agent._last_total_tokens

        print(f"=== 🔄 5. Fusionando Resultados... ===")
        merged_cases = []

        def build_merged_case(struct_case, override_name=None):
            current_name = override_name if override_name else struct_case.case_name

            solved_match = next(
                (
                    s
                    for s in math_response.solved_cases
                    if s.case_name == struct_case.case_name
                ),
                None,
            )
            asymp_match = next(
                (
                    a
                    for a in asymptotic_response.analysis
                    if a.case_name == struct_case.case_name
                ),
                None,
            )

            diagram_match = next(
                (
                    d
                    for d in diagram_response.diagrams
                    if d.case_name.lower() in struct_case.case_name.lower()
                    or struct_case.case_name.lower() in d.case_name.lower()
                ),
                None,
            )
            if not diagram_match and diagram_response.diagrams:
                diagram_match = diagram_response.diagrams[0]

            notation_str = asymp_match.formatted_notation if asymp_match else "N/A"
            notation_type = asymp_match.notation_type if asymp_match else "?"

            if override_name == "Mejor":
                notation_type = "Ω"
                notation_str = notation_str.replace("Θ", "Ω").replace("O", "Ω")
            elif override_name == "Peor":
                notation_type = "O"
                notation_str = notation_str.replace("Θ", "O").replace("Ω", "O")
            elif override_name == "Promedio":
                notation_type = "Θ"
                notation_str = notation_str.replace("O", "Θ").replace("Ω", "Θ")

            return {
                "case_name": current_name,
                "condition": struct_case.condition,
                "line_analysis": [
                    line.model_dump() for line in struct_case.line_analysis
                ],
                "raw_summation_str": struct_case.solver_friendly_summation,
                "math_steps": (
                    solved_match.simplified_efficiency_function if solved_match else ""
                ),
                "simplified_complexity": (
                    solved_match.simplified_efficiency_function
                    if solved_match
                    else "N/A"
                ),
                "complexity_class": (
                    asymp_match.complexity_class if asymp_match else "Unknown"
                ),
                "notation_type": notation_type,
                "big_o": notation_str,
                "trace_diagram": diagram_match.mermaid_code if diagram_match else "",
            }

        is_single_general_case = (
            len(structural_response.cases) == 1
            and "general" in structural_response.cases[0].case_name.lower()
        )

        if is_single_general_case:
            print("⚡ Algoritmo Determinista detectado. Replicando casos...")
            gen_case = structural_response.cases[0]
            merged_cases.append(build_merged_case(gen_case, "Mejor"))
            merged_cases.append(build_merged_case(gen_case, "Promedio"))
            merged_cases.append(build_merged_case(gen_case, "Peor"))
        else:
            for struct_case in structural_response.cases:
                merged_cases.append(build_merged_case(struct_case))

        asymptotic_dict = {}
        equations_list = []
        solutions_list = []
        explain_steps_list = []

        for idx, case in enumerate(merged_cases):
            c_name = case["case_name"]
            name_lower = c_name.lower()

            if "mejor" in name_lower or "best" in name_lower:
                asymptotic_dict["best"] = case["big_o"]
            elif "peor" in name_lower or "worst" in name_lower:
                asymptotic_dict["worst"] = case["big_o"]
            elif "promedio" in name_lower or "average" in name_lower:
                asymptotic_dict["average"] = case["big_o"]

            equations_list.append(f"{c_name}: {case['raw_summation_str']}")
            solutions_list.append(f"{c_name}: T(n) = {case['simplified_complexity']}")

            solved_case = (
                math_response.solved_cases[idx]
                if idx < len(math_response.solved_cases)
                else None
            )

            if solved_case:
                explain_steps_list.append(
                    f"**{c_name}**: {solved_case.final_summary if hasattr(solved_case, 'final_summary') else case['math_steps']}"
                )
            else:
                explain_steps_list.append(f"**{c_name}**: {case['math_steps']}")

        asymptotic_dict["explanation"] = (
            asymptotic_response.final_conclusion if asymptotic_response else ""
        )

        for idx, merged_case in enumerate(merged_cases):
            if idx < len(math_response.solved_cases):
                solved_case = math_response.solved_cases[idx]

                merged_case["properties_explanation"] = (
                    solved_case.properties_explanation
                    if hasattr(solved_case, "properties_explanation")
                    else ""
                )

                merged_case["resolution_steps"] = (
                    [
                        {
                            "step_number": step.step_number,
                            "title": step.title,
                            "explanation": step.explanation,
                            "mathematical_expression": step.mathematical_expression,
                            "property_or_formula": step.property_or_formula,
                        }
                        for step in solved_case.resolution_steps
                    ]
                    if hasattr(solved_case, "resolution_steps")
                    else []
                )

                merged_case["final_summary"] = (
                    solved_case.final_summary
                    if hasattr(solved_case, "final_summary")
                    else ""
                )

        execution_time = time.time() - start_time

        print(f"\n⏱️ Tiempo total de ejecución: {execution_time:.2f}s")
        print(f"📊 Tokens totales consumidos: {total_tokens['total']:,}")

        complexity_line_to_line_str = ""

        pseudocode_lines = pseudocode.split("\n")

        for merged_case in merged_cases:
            case_name = merged_case["case_name"]
            line_analysis = merged_case.get("line_analysis", [])

            line_cost_map = {}
            for line_item in line_analysis:
                line_num = line_item.get("line")
                total_cost = line_item.get("total_cost_expression", "")
                if line_num is not None:
                    line_cost_map[line_num] = total_cost

            complexity_line_to_line_str += f"=== {case_name.upper()} ===\n"

            for idx, code_line in enumerate(pseudocode_lines, start=1):
                complexity_line_to_line_str += f"{code_line}"

                if idx in line_cost_map:
                    total_cost = line_cost_map[idx]
                    complexity_line_to_line_str += f" // Costo: {total_cost}"

                complexity_line_to_line_str += "\n"

            complexity_line_to_line_str += "\n"

        def calculate_opd_total(merged_cases):
            """
            Suma el cost_constant de todas las líneas en todos los casos.
            Retorna el número total de operaciones básicas detectadas.
            """
            total_opd = 0
            for case in merged_cases:
                line_analysis = case.get("line_analysis", [])
                for line_item in line_analysis:
                    cost_constant = line_item.get("cost_constant", 0)

                    total_opd += cost_constant
            return total_opd

        opd_count = calculate_opd_total(merged_cases)
        print(f"\n📊 OPD Total (Operaciones básicas detectadas): {opd_count}")

        solution = Solution(
            type="iterativo",
            algorithm_name=algorithm_name,
            algorithm_category="Iterativo / Bucle",
            code_explain=structural_response.general_explanation,
            explain_complexity=math_response.general_summary,
            complexity_line_to_line=complexity_line_to_line_str,
            equation=equations_list,
            method_solution="Método de Conteo de Pasos + Sumatorias",
            solution_equation=solutions_list,
            explain_solution_steps=explain_steps_list,
            asymptotic_notation=asymptotic_dict,
            opd_count=opd_count,
            diagrams={
                "main_flowchart": (
                    merged_cases[-1]["trace_diagram"] if merged_cases else ""
                )
            },
            extra={
                "is_case_dependent": not is_single_general_case,
                "cases": merged_cases,
                "hybrid_solver_summary": math_response.general_summary,
                "project_metadata": {
                    "diagrams_generated": len(diagram_response.diagrams),
                    "agent_model": MODEL_PROFILE,
                    "optimization": (
                        "Cases replicated"
                        if is_single_general_case
                        else "Full analysis"
                    ),
                    "execution_time": execution_time,
                    "token_usage": agent_token_usage,
                    "total_tokens": total_tokens,
                },
            },
        )

        return solution

    except Exception as e:
        print(f"⚠️ Error Crítico en Controlador Iterativo: {e}")
        import traceback

        traceback.print_exc()
        return {"error": str(e)}

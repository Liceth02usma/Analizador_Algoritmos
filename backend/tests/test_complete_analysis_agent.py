"""
Tests unitarios para CompleteAnalysisAgent usando mocks.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.external_services.Agentes.CompleteAnalysisAgent import (
    CompleteAnalysisAgent,
    CompleteAnalysisResponse,
    LineAnalysis,
    CaseAnalysis,
)
from app.models.solution import Solution


class TestCompleteAnalysisAgent:
    """Suite de tests para CompleteAnalysisAgent."""

    @pytest.fixture
    def agent(self):
        """Fixture que crea una instancia del agente."""
        return CompleteAnalysisAgent()

    @pytest.fixture
    def mock_linear_search_response(self):
        """Mock de respuesta para búsqueda lineal (múltiples casos)."""
        return CompleteAnalysisResponse(
            algorithm_purpose="Busca un elemento en un array secuencialmente",
            algorithm_name="Búsqueda Lineal",
            algorithm_category="Búsqueda",
            algorithm_type="iterative",
            line_by_line_analysis=[
                LineAnalysis(
                    line=1,
                    code="for i = 0 to n-1 do",
                    cost="c1 * n",
                    explanation="El bucle se ejecuta n veces en el peor caso"
                ),
                LineAnalysis(
                    line=2,
                    code="if arr[i] == x then",
                    cost="c2 * 1",
                    explanation="Comparación constante por iteración"
                ),
                LineAnalysis(
                    line=3,
                    code="return i",
                    cost="c3 * 1",
                    explanation="Retorno constante si se encuentra"
                ),
            ],
            equation="T(n) = c1*n + c2*1 en promedio",
            solution_method="Análisis de Sumatorias",
            solution_steps=[
                "Paso 1: Identificar bucle principal que itera n veces",
                "Paso 2: En mejor caso, encuentra en primera posición: T(n) = O(1)",
                "Paso 3: En peor caso, recorre todo el array: T(n) = O(n)",
                "Paso 4: En promedio, encuentra a la mitad: T(n) = O(n)",
            ],
            final_complexity="O(n)",
            has_multiple_cases=True,
            best_case=CaseAnalysis(
                complexity="O(1)",
                condition="El elemento está en la primera posición",
                example="arr=[5,2,3], x=5 → encuentra en i=0",
                explanation="Solo se ejecuta una iteración del bucle"
            ),
            worst_case=CaseAnalysis(
                complexity="O(n)",
                condition="El elemento está al final o no existe",
                example="arr=[1,2,3,4,5], x=5 → encuentra en i=4",
                explanation="Debe recorrer todo el array"
            ),
            average_case=CaseAnalysis(
                complexity="O(n)",
                condition="El elemento está en posición aleatoria",
                example="arr=[1,2,3,4,5], x=3 → encuentra en i=2",
                explanation="En promedio recorre n/2 elementos, que es O(n)"
            ),
            asymptotic_best="Ω(1)",
            asymptotic_worst="O(n)",
            asymptotic_average="Θ(n)",
            notation_explanation="Ω para mejor caso, O para peor, Θ cuando coinciden",
            case_determination_criteria="La posición del elemento determina el caso"
        )

    @pytest.fixture
    def mock_merge_sort_response(self):
        """Mock de respuesta para merge sort (caso general único)."""
        return CompleteAnalysisResponse(
            algorithm_purpose="Ordena un array usando estrategia divide y conquista",
            algorithm_name="Merge Sort",
            algorithm_category="Divide y Conquista",
            algorithm_type="recursive",
            line_by_line_analysis=[
                LineAnalysis(
                    line=1,
                    code="if left < right then",
                    cost="c1 * 1",
                    explanation="Comparación constante"
                ),
                LineAnalysis(
                    line=2,
                    code="mid = (left + right) / 2",
                    cost="c2 * 1",
                    explanation="Cálculo constante"
                ),
                LineAnalysis(
                    line=3,
                    code="mergeSort(arr, left, mid)",
                    cost="T(n/2)",
                    explanation="Llamada recursiva con mitad izquierda"
                ),
                LineAnalysis(
                    line=4,
                    code="mergeSort(arr, mid+1, right)",
                    cost="T(n/2)",
                    explanation="Llamada recursiva con mitad derecha"
                ),
                LineAnalysis(
                    line=5,
                    code="merge(arr, left, mid, right)",
                    cost="c3 * n",
                    explanation="Mezcla lineal de ambas mitades"
                ),
            ],
            equation="T(n) = 2T(n/2) + n, T(1) = 1",
            solution_method="Teorema Maestro (a=2, b=2, f(n)=n)",
            solution_steps=[
                "Paso 1: Identificar parámetros: a=2, b=2, f(n)=n",
                "Paso 2: Calcular n^(log_b(a)) = n^(log_2(2)) = n",
                "Paso 3: Comparar f(n)=n con n^1: son iguales (Caso 2)",
                "Paso 4: Aplicar Caso 2 del Teorema Maestro: T(n) = Θ(n log n)",
            ],
            final_complexity="O(n log n)",
            has_multiple_cases=False,
            best_case=None,
            worst_case=None,
            average_case=None,
            asymptotic_best="Ω(n log n)",
            asymptotic_worst="O(n log n)",
            asymptotic_average="Θ(n log n)",
            notation_explanation="Merge Sort siempre es O(n log n) independiente de la entrada",
            case_determination_criteria="Siempre divide en mitades exactas, caso único"
        )

    def test_agent_initialization(self, agent):
        """Test: El agente se inicializa correctamente."""
        assert agent is not None
        assert agent.model_type == "Gemini_Largo"
        assert agent.response_format == CompleteAnalysisResponse

    def test_analyze_linear_search_with_mock(self, agent, mock_linear_search_response):
        """Test: Análisis de búsqueda lineal con mock (múltiples casos)."""
        
        pseudocode = """
linearSearch(arr, n, x)
begin
    for i = 0 to n-1 do
        if arr[i] == x then
            return i
        end
    end
    return -1
end
"""
        
        # Mock del método invoke_simple y extract_response
        with patch.object(agent, 'invoke_simple') as mock_invoke, \
             patch.object(agent, 'extract_response') as mock_extract:
            
            mock_invoke.return_value = {"mocked": "response"}
            mock_extract.return_value = mock_linear_search_response
            
            # Ejecutar análisis
            solution = agent.analyze(pseudocode)
            
            # Verificaciones
            assert isinstance(solution, Solution)
            assert solution.type == "iterative"
            assert solution.algorithm_name == "Búsqueda Lineal"
            assert solution.algorithm_category == "Búsqueda"
            assert solution.solution_equation == "O(n)"
            assert solution.method_solution == "Análisis de Sumatorias"
            
            # Verificar análisis de múltiples casos
            assert solution.extra["has_multiple_cases"] is True
            assert solution.asymptotic_notation["has_multiple_cases"] is True
            assert solution.asymptotic_notation["best"] == "Ω(1)"
            assert solution.asymptotic_notation["worst"] == "O(n)"
            assert solution.asymptotic_notation["average"] == "Θ(n)"
            
            # Verificar que se llamaron los métodos
            mock_invoke.assert_called_once()
            mock_extract.assert_called_once()

    def test_analyze_merge_sort_with_mock(self, agent, mock_merge_sort_response):
        """Test: Análisis de merge sort con mock (caso general único)."""
        
        pseudocode = """
mergeSort(arr, left, right)
begin
    if left < right then
        mid = (left + right) / 2
        mergeSort(arr, left, mid)
        mergeSort(arr, mid+1, right)
        merge(arr, left, mid, right)
    end
end
"""
        
        with patch.object(agent, 'invoke_simple') as mock_invoke, \
             patch.object(agent, 'extract_response') as mock_extract:
            
            mock_invoke.return_value = {"mocked": "response"}
            mock_extract.return_value = mock_merge_sort_response
            
            # Ejecutar análisis
            solution = agent.analyze(pseudocode)
            
            # Verificaciones
            assert isinstance(solution, Solution)
            assert solution.type == "recursive"
            assert solution.algorithm_name == "Merge Sort"
            assert solution.algorithm_category == "Divide y Conquista"
            assert solution.solution_equation == "O(n log n)"
            assert solution.method_solution == "Teorema Maestro (a=2, b=2, f(n)=n)"
            
            # Verificar caso general único
            assert solution.extra["has_multiple_cases"] is False
            assert solution.asymptotic_notation["has_multiple_cases"] is False
            assert solution.asymptotic_notation["best"] == "Ω(n log n)"
            assert solution.asymptotic_notation["worst"] == "O(n log n)"
            assert solution.asymptotic_notation["average"] == "Θ(n log n)"

    def test_analyze_empty_pseudocode_raises_error(self, agent):
        """Test: Analizar pseudocódigo vacío lanza ValueError."""
        
        with pytest.raises(ValueError, match="El pseudocódigo no puede estar vacío"):
            agent.analyze("")
        
        with pytest.raises(ValueError, match="El pseudocódigo no puede estar vacío"):
            agent.analyze("   ")

    def test_validate_analysis_missing_purpose(self, agent):
        """Test: Validación falla si falta el propósito."""
        
        incomplete_response = CompleteAnalysisResponse(
            algorithm_purpose="",  # Vacío
            algorithm_name="Test",
            algorithm_category="Test",
            algorithm_type="iterative",
            line_by_line_analysis=[],
            equation="T(n) = n",
            solution_method="Test",
            solution_steps=["Step 1"],
            final_complexity="O(n)",
            has_multiple_cases=False,
            asymptotic_best="Ω(n)",
            asymptotic_worst="O(n)",
            asymptotic_average="Θ(n)",
            notation_explanation="Test",
            case_determination_criteria="Test"
        )
        
        with pytest.raises(ValueError, match="Falta el propósito del algoritmo"):
            agent._validate_analysis(incomplete_response)

    def test_validate_analysis_missing_line_analysis(self, agent):
        """Test: Validación falla si falta análisis línea por línea."""
        
        incomplete_response = CompleteAnalysisResponse(
            algorithm_purpose="Test purpose",
            algorithm_name="Test",
            algorithm_category="Test",
            algorithm_type="iterative",
            line_by_line_analysis=[],  # Vacío
            equation="T(n) = n",
            solution_method="Test",
            solution_steps=["Step 1"],
            final_complexity="O(n)",
            has_multiple_cases=False,
            asymptotic_best="Ω(n)",
            asymptotic_worst="O(n)",
            asymptotic_average="Θ(n)",
            notation_explanation="Test",
            case_determination_criteria="Test"
        )
        
        with pytest.raises(ValueError, match="Falta el análisis línea por línea"):
            agent._validate_analysis(incomplete_response)

    def test_validate_analysis_multiple_cases_missing_worst(self, agent):
        """Test: Validación falla si indica múltiples casos pero falta peor caso."""
        
        incomplete_response = CompleteAnalysisResponse(
            algorithm_purpose="Test",
            algorithm_name="Test",
            algorithm_category="Test",
            algorithm_type="iterative",
            line_by_line_analysis=[
                LineAnalysis(line=1, code="test", cost="c1*1", explanation="test")
            ],
            equation="T(n) = n",
            solution_method="Test",
            solution_steps=["Step 1"],
            final_complexity="O(n)",
            has_multiple_cases=True,  # Indica múltiples casos
            best_case=CaseAnalysis(
                complexity="O(1)",
                condition="Test",
                example="Test",
                explanation="Test"
            ),
            worst_case=None,  # Pero falta el peor caso
            average_case=None,
            asymptotic_best="Ω(1)",
            asymptotic_worst="O(n)",
            asymptotic_average="Θ(n)",
            notation_explanation="Test",
            case_determination_criteria="Test"
        )
        
        with pytest.raises(ValueError, match="falta el peor caso"):
            agent._validate_analysis(incomplete_response)

    def test_build_complexity_explanation(self, agent, mock_linear_search_response):
        """Test: Construcción de explicación de complejidad."""
        
        explanation = agent._build_complexity_explanation(mock_linear_search_response)
        
        # Verificar que contiene secciones clave
        assert "ANÁLISIS DE COMPLEJIDAD ALGORÍTMICA" in explanation
        assert "Búsqueda Lineal" in explanation
        assert "ANÁLISIS DE CASOS" in explanation
        assert "MÚLTIPLES CASOS" in explanation
        assert "MEJOR CASO" in explanation
        assert "PEOR CASO" in explanation
        assert "CASO PROMEDIO" in explanation
        assert "NOTACIONES ASINTÓTICAS" in explanation
        assert "Ω(1)" in explanation
        assert "O(n)" in explanation
        assert "Θ(n)" in explanation

    def test_convert_to_solution_structure(self, agent, mock_merge_sort_response):
        """Test: Conversión correcta de respuesta a Solution."""
        
        pseudocode = "test code"
        solution = agent._convert_to_solution(mock_merge_sort_response, pseudocode)
        
        # Verificar estructura básica
        assert solution.type == "recursive"
        assert solution.code_explain == "Ordena un array usando estrategia divide y conquista"
        assert solution.algorithm_name == "Merge Sort"
        assert solution.algorithm_category == "Divide y Conquista"
        assert solution.equation == "T(n) = 2T(n/2) + n, T(1) = 1"
        assert solution.method_solution == "Teorema Maestro (a=2, b=2, f(n)=n)"
        assert solution.solution_equation == "O(n log n)"
        
        # Verificar complejidad línea por línea
        assert len(solution.complexity_line_to_line) == 5
        assert solution.complexity_line_to_line[0]["line"] == 1
        assert solution.complexity_line_to_line[0]["complexity"] == "c1 * 1"
        
        # Verificar pasos de solución
        assert len(solution.explain_solution_steps) == 4
        assert "Teorema Maestro" in solution.explain_solution_steps[3]
        
        # Verificar extra
        assert solution.extra["pseudocode"] == pseudocode
        assert solution.extra["analysis_complete"] is True
        assert solution.extra["has_multiple_cases"] is False

    def test_convert_to_solution_with_multiple_cases(self, agent, mock_linear_search_response):
        """Test: Conversión correcta cuando hay múltiples casos."""
        
        pseudocode = "test code"
        solution = agent._convert_to_solution(mock_linear_search_response, pseudocode)
        
        # Verificar análisis de casos en asymptotic_notation
        assert solution.asymptotic_notation["has_multiple_cases"] is True
        assert "best_case_analysis" in solution.asymptotic_notation
        assert "worst_case_analysis" in solution.asymptotic_notation
        assert "average_case_analysis" in solution.asymptotic_notation
        
        # Verificar detalles del mejor caso
        best_case = solution.asymptotic_notation["best_case_analysis"]
        assert best_case["complexity"] == "O(1)"
        assert "primera posición" in best_case["condition"]
        assert "i=0" in best_case["example"]
        
        # Verificar detalles del peor caso
        worst_case = solution.asymptotic_notation["worst_case_analysis"]
        assert worst_case["complexity"] == "O(n)"
        assert "final" in worst_case["condition"] or "no existe" in worst_case["condition"]

    def test_analyze_with_extraction_failure(self, agent):
        """Test: Manejo de error cuando extract_response falla."""
        
        pseudocode = "test code"
        
        with patch.object(agent, 'invoke_simple') as mock_invoke, \
             patch.object(agent, 'extract_response') as mock_extract:
            
            mock_invoke.return_value = {"mocked": "response"}
            mock_extract.return_value = None  # Simula falla en extracción
            
            with pytest.raises(ValueError, match="No se pudo extraer respuesta estructurada"):
                agent.analyze(pseudocode)

    def test_analyze_with_validation_failure(self, agent):
        """Test: Manejo de error cuando la validación falla."""
        
        pseudocode = "test code"
        
        incomplete_response = CompleteAnalysisResponse(
            algorithm_purpose="",  # Provocará falla en validación
            algorithm_name="Test",
            algorithm_category="Test",
            algorithm_type="iterative",
            line_by_line_analysis=[],
            equation="T(n) = n",
            solution_method="Test",
            solution_steps=[],
            final_complexity="",
            has_multiple_cases=False,
            asymptotic_best="",
            asymptotic_worst="",
            asymptotic_average="",
            notation_explanation="",
            case_determination_criteria=""
        )
        
        with patch.object(agent, 'invoke_simple') as mock_invoke, \
             patch.object(agent, 'extract_response') as mock_extract:
            
            mock_invoke.return_value = {"mocked": "response"}
            mock_extract.return_value = incomplete_response
            
            with pytest.raises(ValueError):
                agent.analyze(pseudocode)

    def test_build_analysis_prompt_contains_key_sections(self, agent):
        """Test: El prompt de análisis contiene todas las secciones clave."""
        
        pseudocode = "test code"
        prompt = agent._build_analysis_prompt(pseudocode)
        
        # Verificar que contiene instrucciones clave
        assert "Propósito del Algoritmo" in prompt
        assert "Nombre del Algoritmo" in prompt
        assert "Categoría" in prompt
        assert "Análisis Línea por Línea" in prompt
        assert "Ecuación de Complejidad" in prompt
        assert "Método de Resolución" in prompt
        assert "Pasos de Resolución Detallados" in prompt
        assert "Complejidad Final" in prompt
        assert "Análisis de Casos" in prompt
        assert "Notaciones Asintóticas" in prompt
        assert "Criterios de Determinación de Casos" in prompt
        assert pseudocode in prompt

    def test_solution_to_backend_format(self, agent, mock_linear_search_response):
        """Test: Conversión de Solution a formato backend."""
        
        pseudocode = "test code"
        solution = agent._convert_to_solution(mock_linear_search_response, pseudocode)
        
        # Convertir a formato backend
        backend_dict = solution.to_backend()
        
        # Verificar estructura
        assert "type" in backend_dict
        assert "code_explain" in backend_dict
        assert "complexity_line_to_line" in backend_dict
        assert "asymptotic_notation" in backend_dict
        assert "algorithm_name" in backend_dict

    def test_solution_to_frontend_format(self, agent, mock_merge_sort_response):
        """Test: Conversión de Solution a formato frontend."""
        
        pseudocode = "test code"
        solution = agent._convert_to_solution(mock_merge_sort_response, pseudocode)
        
        # Convertir a formato frontend
        frontend_dict = solution.to_frontend()
        
        # Verificar estructura
        assert "algorithmName" in frontend_dict
        assert "category" in frontend_dict
        assert "complexity" in frontend_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

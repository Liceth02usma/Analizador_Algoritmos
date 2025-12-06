"""
Tests unitarios para CompleteAnalysisAgent usando mocks (estilo classification).
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from app.external_services.Agentes.CompleteAnalysisAgent import (
    CompleteAnalysisAgent,
    CompleteAnalysisResponse,
    LineAnalysis,
    CaseAnalysis,
)
from app.models.solution import Solution


class TestCompleteAnalysisAgentMock(unittest.TestCase):
    """Suite de tests para CompleteAnalysisAgent usando mocks."""

    def setUp(self):
        """Configuración previa a cada test."""
        print(f"\n--- Ejecutando test: {self._testMethodName} ---")
        self.agent = CompleteAnalysisAgent()
        
        # Flag para decidir si usar el agente real o mocks
        # True = usa LLM real (gasta tokens), False = usa mocks
        self.use_real_agent = False

    def get_mock_linear_search_response(self):
        """Mock de respuesta para búsqueda lineal (múltiples casos)."""
        return CompleteAnalysisResponse(
            algorithm_purpose="Busca un elemento en un arreglo secuencialmente",
            algorithm_name="Búsqueda Lineal",
            algorithm_category="Búsqueda",
            algorithm_type="iterative",
            line_by_line_analysis=[
                LineAnalysis(line=1, code="for i = 0 to n-1", cost="c1 * n", explanation="Loop ejecuta n veces"),
                LineAnalysis(line=2, code="if arr[i] == x", cost="c2 * n", explanation="Comparación en cada iteración"),
                LineAnalysis(line=3, code="return i", cost="c3 * 1", explanation="Retorno temprano (mejor caso)"),
                LineAnalysis(line=4, code="return -1", cost="c4 * 1", explanation="No encontrado"),
            ],
            equation="T(n) = c1*n + c2*n + c3",
            solution_method="Conteo directo de operaciones",
            solution_steps=[
                "1. Loop principal: n iteraciones",
                "2. Comparación: n veces",
                "3. En mejor caso retorna inmediatamente",
                "4. T(n) = c1*n + c2*n = O(n)"
            ],
            final_complexity="O(n)",
            has_multiple_cases=True,
            best_case=CaseAnalysis(
                complexity="O(1)",
                condition="Elemento está en la primera posición",
                example="arr=[5,2,8], x=5, i=0",
                explanation="Solo una comparación"
            ),
            worst_case=CaseAnalysis(
                complexity="O(n)",
                condition="Elemento al final o no existe",
                example="arr=[5,2,8], x=9 o x=8",
                explanation="Recorre todo el arreglo"
            ),
            average_case=CaseAnalysis(
                complexity="O(n)",
                condition="Elemento en posición aleatoria",
                example="Promedio de todas las posiciones",
                explanation="Promedio: n/2 comparaciones → O(n)"
            ),
            asymptotic_best="Ω(1)",
            asymptotic_worst="O(n)",
            asymptotic_average="Θ(n)",
            notation_explanation="Best Ω(1), Worst O(n), Average Θ(n)",
            case_determination_criteria="Posición del elemento en el arreglo"
        )

    def get_mock_merge_sort_response(self):
        """Mock de respuesta para merge sort (caso general único)."""
        return CompleteAnalysisResponse(
            algorithm_purpose="Ordena un array usando estrategia divide y conquista",
            algorithm_name="Merge Sort",
            algorithm_category="Divide y Conquista",
            algorithm_type="recursive",
            line_by_line_analysis=[
                LineAnalysis(line=1, code="if left < right", cost="c1 * 1", explanation="Comparación base"),
                LineAnalysis(line=2, code="mid = (left + right) / 2", cost="c2 * 1", explanation="Cálculo punto medio"),
                LineAnalysis(line=3, code="mergeSort(arr, left, mid)", cost="T(n/2)", explanation="Llamada recursiva izquierda"),
                LineAnalysis(line=4, code="mergeSort(arr, mid+1, right)", cost="T(n/2)", explanation="Llamada recursiva derecha"),
                LineAnalysis(line=5, code="merge(arr, left, mid, right)", cost="c3 * n", explanation="Combinar subarreglos"),
            ],
            equation="T(n) = 2T(n/2) + n, T(1) = 1",
            solution_method="Teorema Maestro (a=2, b=2, f(n)=n)",
            solution_steps=[
                "1. Identificar: a=2, b=2, f(n)=n",
                "2. log_b(a) = log_2(2) = 1",
                "3. f(n) = n = Θ(n^1)",
                "4. Caso 2 del Teorema: T(n) = Θ(n^1 * log n) = Θ(n log n)"
            ],
            final_complexity="O(n log n)",
            has_multiple_cases=False,
            best_case=None,
            worst_case=None,
            average_case=None,
            asymptotic_best="Ω(n log n)",
            asymptotic_worst="O(n log n)",
            asymptotic_average="Θ(n log n)",
            notation_explanation="Siempre O(n log n) - no depende del orden de entrada",
            case_determination_criteria="No aplica - complejidad constante"
        )

    # ==========================================
    # 1. TESTS DE INICIALIZACIÓN
    # ==========================================

    def test_agent_initialization(self):
        """Test: El agente se inicializa correctamente."""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.model_type, "Gemini_Largo")
        self.assertEqual(self.agent.response_format, CompleteAnalysisResponse)
        print("✅ Agente inicializado correctamente")

    # ==========================================
    # 2. TESTS CON MOCKS - BÚSQUEDA LINEAL
    # ==========================================

    def test_analyze_linear_search_with_mock(self):
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
        
        if self.use_real_agent:
            # Usa el agente real (gasta tokens)
            result = self.agent.analyze(pseudocode)
        else:
            # Mock del método invoke_simple y extract_response
            mock_response = self.get_mock_linear_search_response()
            
            with patch.object(self.agent, 'invoke_simple') as mock_invoke, \
                 patch.object(self.agent, 'extract_response') as mock_extract:
                
                mock_invoke.return_value = {"mock": "response"}
                mock_extract.return_value = mock_response
                
                result = self.agent.analyze(pseudocode)
        
        # Verificaciones
        self.assertIsInstance(result, Solution)
        self.assertEqual(result.type, "iterative")
        self.assertEqual(result.algorithm_name, "Búsqueda Lineal")
        self.assertEqual(result.solution_equation, "O(n)")
        
        # Verificar que tiene múltiples casos
        self.assertTrue(result.asymptotic_notation.get("has_multiple_cases", False))
        self.assertIn("best_case_analysis", result.asymptotic_notation)
        self.assertIn("worst_case_analysis", result.asymptotic_notation)
        
        print(f"✅ Búsqueda Lineal analizada: {result.solution_equation}")

    # ==========================================
    # 3. TESTS CON MOCKS - MERGE SORT
    # ==========================================

    def test_analyze_merge_sort_with_mock(self):
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
        
        if self.use_real_agent:
            result = self.agent.analyze(pseudocode)
        else:
            mock_response = self.get_mock_merge_sort_response()
            
            with patch.object(self.agent, 'invoke_simple') as mock_invoke, \
                 patch.object(self.agent, 'extract_response') as mock_extract:
                
                mock_invoke.return_value = {"mock": "response"}
                mock_extract.return_value = mock_response
                
                result = self.agent.analyze(pseudocode)
        
        # Verificaciones
        self.assertIsInstance(result, Solution)
        self.assertEqual(result.type, "recursive")
        self.assertEqual(result.algorithm_name, "Merge Sort")
        self.assertIn("n log n", result.solution_equation.lower())
        
        # Verificar que NO tiene múltiples casos
        self.assertFalse(result.asymptotic_notation.get("has_multiple_cases", True))
        
        print(f"✅ Merge Sort analizado: {result.solution_equation}")

    # ==========================================
    # 4. TESTS DE VALIDACIÓN
    # ==========================================

    def test_analyze_empty_pseudocode_raises_error(self):
        """Test: Analizar pseudocódigo vacío lanza ValueError."""
        
        with self.assertRaises(ValueError) as context:
            self.agent.analyze("")
        
        self.assertIn("pseudocódigo", str(context.exception).lower())
        print("✅ Validación de pseudocódigo vacío correcta")

    def test_validate_analysis_missing_purpose(self):
        """Test: Validación falla si falta el propósito."""
        
        incomplete_response = self.get_mock_merge_sort_response()
        incomplete_response.algorithm_purpose = ""  # Vacío
        
        with self.assertRaises(ValueError) as context:
            self.agent._validate_analysis(incomplete_response)
        
        self.assertIn("propósito", str(context.exception).lower())
        print("✅ Validación de propósito faltante correcta")

    def test_validate_analysis_missing_line_analysis(self):
        """Test: Validación falla si falta análisis línea por línea."""
        
        incomplete_response = self.get_mock_merge_sort_response()
        incomplete_response.line_by_line_analysis = []  # Vacío
        
        with self.assertRaises(ValueError) as context:
            self.agent._validate_analysis(incomplete_response)
        
        self.assertIn("línea", str(context.exception).lower())
        print("✅ Validación de análisis línea por línea faltante correcta")

    def test_validate_analysis_multiple_cases_missing_worst(self):
        """Test: Validación falla si indica múltiples casos pero falta peor caso."""
        
        incomplete_response = self.get_mock_linear_search_response()
        incomplete_response.worst_case = None  # Falta peor caso
        
        with self.assertRaises(ValueError) as context:
            self.agent._validate_analysis(incomplete_response)
        
        self.assertIn("peor caso", str(context.exception).lower())
        print("✅ Validación de peor caso faltante correcta")

    # ==========================================
    # 5. TESTS DE CONVERSIÓN
    # ==========================================

    def test_convert_to_solution_structure(self):
        """Test: Conversión correcta de respuesta a Solution."""
        
        mock_response = self.get_mock_merge_sort_response()
        pseudocode = "test code"
        solution = self.agent._convert_to_solution(mock_response, pseudocode)
        
        # Verificar estructura básica
        self.assertEqual(solution.type, "recursive")
        self.assertIn("divide", solution.code_explain.lower())
        self.assertEqual(solution.algorithm_name, "Merge Sort")
        self.assertEqual(solution.algorithm_category, "Divide y Conquista")
        self.assertIn("Maestro", solution.method_solution)
        self.assertIn("n log n", solution.solution_equation.lower())
        
        # Verificar complejidad línea por línea
        self.assertEqual(len(solution.complexity_line_to_line), 5)
        
        # Verificar extra
        self.assertEqual(solution.extra["pseudocode"], pseudocode)
        self.assertTrue(solution.extra["analysis_complete"])
        
        print("✅ Conversión a Solution correcta")

    def test_convert_to_solution_with_multiple_cases(self):
        """Test: Conversión correcta cuando hay múltiples casos."""
        
        mock_response = self.get_mock_linear_search_response()
        pseudocode = "test code"
        solution = self.agent._convert_to_solution(mock_response, pseudocode)
        
        # Verificar análisis de casos
        self.assertTrue(solution.asymptotic_notation["has_multiple_cases"])
        self.assertIn("best_case_analysis", solution.asymptotic_notation)
        self.assertIn("worst_case_analysis", solution.asymptotic_notation)
        
        print("✅ Conversión con múltiples casos correcta")

    # ==========================================
    # 6. TESTS DE CONSTRUCCIÓN
    # ==========================================

    def test_build_complexity_explanation(self):
        """Test: Construcción de explicación de complejidad."""
        
        mock_response = self.get_mock_linear_search_response()
        explanation = self.agent._build_complexity_explanation(mock_response)
        
        # Verificar secciones clave
        self.assertIn("ANÁLISIS", explanation.upper())
        self.assertIn("Búsqueda Lineal", explanation)
        self.assertIn("MEJOR CASO", explanation.upper())
        self.assertIn("O(n)", explanation)
        
        print("✅ Construcción de explicación correcta")

    def test_build_analysis_prompt_contains_sections(self):
        """Test: El prompt contiene secciones clave."""
        
        pseudocode = "test code"
        prompt = self.agent._build_analysis_prompt(pseudocode)
        
        self.assertIn("Propósito", prompt)
        self.assertIn("Complejidad", prompt)
        self.assertIn(pseudocode, prompt)
        
        print("✅ Prompt contiene secciones clave")


if __name__ == "__main__":
    unittest.main(verbosity=2)

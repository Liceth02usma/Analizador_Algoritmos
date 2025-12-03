"""
Test Suite para ComplexityAnalysisService

Prueba el servicio determinista de análisis de complejidad asintótica
con una variedad de ecuaciones de complejidad común.
"""

import unittest
from app.external_services.Agentes.ComplexityAnalysisAgent import (
    ComplexityAnalysisService,
    ComplexityResponse,
    AsymptoticResult,
)


class TestComplexityAnalysisService(unittest.TestCase):
    """Suite de pruebas para el servicio de análisis de complejidad."""

    def setUp(self):
        """Inicializa el servicio antes de cada prueba."""
        self.service = ComplexityAnalysisService()

    # =========================================================================
    # PRUEBAS DE COMPLEJIDAD CONSTANTE - O(1)
    # =========================================================================

    def test_constant_complexity_simple(self):
        """Prueba complejidad constante simple: T(n) = 5"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "5"}]

        result = self.service.determine_complexity("Acceso Array", cases_data)

        self.assertIsInstance(result, ComplexityResponse)
        self.assertEqual(len(result.analysis), 1)
        self.assertEqual(result.analysis[0].complexity_class, "1")
        self.assertEqual(result.analysis[0].notation_type, "O")
        self.assertEqual(result.analysis[0].formatted_notation, "O(1)")

    def test_constant_complexity_with_tn(self):
        """Prueba constante con notación T(n): T(n) = 1"""
        cases_data = [{"case_name": "General", "efficiency_function": "T(n) = 1"}]

        result = self.service.determine_complexity("Operación Básica", cases_data)

        self.assertEqual(result.analysis[0].complexity_class, "1")
        self.assertEqual(result.analysis[0].formatted_notation, "Θ(1)")

    def test_constant_with_arbitrary_constants(self):
        """Prueba constante con constantes arbitrarias: T(n) = c1 + c2"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "c1 + c2 + 10"}]

        result = self.service.determine_complexity("Suma Constantes", cases_data)

        self.assertEqual(result.analysis[0].complexity_class, "1")

    # =========================================================================
    # PRUEBAS DE COMPLEJIDAD LINEAL - O(n)
    # =========================================================================

    def test_linear_complexity_simple(self):
        """Prueba complejidad lineal simple: T(n) = n"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "n"}]

        result = self.service.determine_complexity("Búsqueda Lineal", cases_data)

        self.assertEqual(result.analysis[0].complexity_class, "n")
        self.assertEqual(result.analysis[0].formatted_notation, "O(n)")

    def test_linear_complexity_with_coefficient(self):
        """Prueba lineal con coeficiente: T(n) = 5n + 3"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "5*n + 3"}]

        result = self.service.determine_complexity("Recorrido Array", cases_data)

        self.assertEqual(result.analysis[0].complexity_class, "n")

    def test_linear_complexity_with_constants(self):
        """Prueba lineal con constantes: T(n) = c1*n + c2"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "c1*n + c2"}]

        result = self.service.determine_complexity("Loop Simple", cases_data)

        self.assertEqual(result.analysis[0].complexity_class, "n")

    def test_linear_half_n(self):
        """Prueba lineal con n/2: T(n) = n/2"""
        cases_data = [{"case_name": "Promedio", "efficiency_function": "n/2"}]

        result = self.service.determine_complexity("Caso Promedio", cases_data)

        # n/2 sigue siendo O(n)
        self.assertEqual(result.analysis[0].complexity_class, "n")

    # =========================================================================
    # PRUEBAS DE COMPLEJIDAD CUADRÁTICA - O(n²)
    # =========================================================================

    def test_quadratic_complexity_simple(self):
        """Prueba complejidad cuadrática simple: T(n) = n²"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "n**2"}]

        result = self.service.determine_complexity("Bubble Sort", cases_data)

        self.assertEqual(result.analysis[0].complexity_class, "n^2")
        self.assertEqual(result.analysis[0].formatted_notation, "O(n^2)")

    def test_quadratic_with_caret_notation(self):
        """Prueba cuadrática con notación ^: T(n) = n^2"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "n^2"}]

        result = self.service.determine_complexity("Selection Sort", cases_data)

        self.assertEqual(result.analysis[0].complexity_class, "n^2")

    def test_quadratic_with_linear_term(self):
        """Prueba cuadrática con término lineal: T(n) = n² + n"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "n**2 + n"}]

        result = self.service.determine_complexity("Insertion Sort", cases_data)

        # El término dominante es n²
        self.assertEqual(result.analysis[0].complexity_class, "n^2")

    def test_quadratic_complex_expression(self):
        """Prueba cuadrática compleja: T(n) = 3n² + 5n + 2"""
        cases_data = [
            {"case_name": "Peor Caso", "efficiency_function": "3*n**2 + 5*n + 2"}
        ]

        result = self.service.determine_complexity("Algoritmo Cuadrático", cases_data)

        self.assertEqual(result.analysis[0].complexity_class, "n^2")

    # =========================================================================
    # PRUEBAS DE COMPLEJIDAD CÚBICA - O(n³)
    # =========================================================================

    def test_cubic_complexity(self):
        """Prueba complejidad cúbica: T(n) = n³"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "n**3"}]

        result = self.service.determine_complexity("Triple Loop", cases_data)

        self.assertEqual(result.analysis[0].complexity_class, "n^3")
        self.assertEqual(result.analysis[0].formatted_notation, "O(n^3)")

    def test_cubic_with_lower_terms(self):
        """Prueba cúbica con términos menores: T(n) = n³ + n² + n"""
        cases_data = [
            {"case_name": "Peor Caso", "efficiency_function": "n**3 + n**2 + n"}
        ]

        result = self.service.determine_complexity("Matriz 3D", cases_data)

        self.assertEqual(result.analysis[0].complexity_class, "n^3")

    # =========================================================================
    # PRUEBAS DE COMPLEJIDAD LOGARÍTMICA - O(log n)
    # =========================================================================

    def test_logarithmic_complexity(self):
        """Prueba complejidad logarítmica: T(n) = log(n)"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "log(n)"}]

        result = self.service.determine_complexity("Búsqueda Binaria", cases_data)

        self.assertIn("log", result.analysis[0].complexity_class.lower())
        self.assertEqual(result.analysis[0].formatted_notation, "O(log(n))")

    def test_logarithmic_with_coefficient(self):
        """Prueba logarítmica con coeficiente: T(n) = 5*log(n)"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "5*log(n)"}]

        result = self.service.determine_complexity("Divide y Conquista", cases_data)

        self.assertIn("log", result.analysis[0].complexity_class.lower())

    # =========================================================================
    # PRUEBAS DE COMPLEJIDAD LINEAL-LOGARÍTMICA - O(n log n)
    # =========================================================================

    def test_nlogn_complexity(self):
        """Prueba complejidad n*log(n): T(n) = n*log(n)"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "n*log(n)"}]

        result = self.service.determine_complexity("Merge Sort", cases_data)

        complexity = result.analysis[0].complexity_class.lower()
        self.assertIn("n", complexity)
        self.assertIn("log", complexity)
        self.assertEqual(result.analysis[0].formatted_notation, "O(nlog(n))")

    def test_nlogn_with_constants(self):
        """Prueba n*log(n) con constantes: T(n) = c1*n*log(n) + c2"""
        cases_data = [
            {"case_name": "Peor Caso", "efficiency_function": "c1*n*log(n) + c2"}
        ]

        result = self.service.determine_complexity("Quick Sort Promedio", cases_data)

        complexity = result.analysis[0].complexity_class.lower()
        self.assertIn("n", complexity)
        self.assertIn("log", complexity)

    # =========================================================================
    # PRUEBAS DE COMPLEJIDAD EXPONENCIAL - O(2^n)
    # =========================================================================

    def test_exponential_base2(self):
        """Prueba complejidad exponencial base 2: T(n) = 2^n"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "2**n"}]

        result = self.service.determine_complexity("Fibonacci Recursivo", cases_data)

        complexity = result.analysis[0].complexity_class
        # SymPy puede devolver "2**n" o simplemente exponencial
        self.assertTrue(
            "2**n" in complexity or "exp" in complexity.lower() or "2" in complexity
        )

    def test_exponential_with_linear(self):
        """Prueba exponencial con término lineal: T(n) = 2^n + n"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "2**n + n"}]

        result = self.service.determine_complexity("Subconjuntos", cases_data)

        # El término dominante debe ser exponencial
        complexity = result.analysis[0].complexity_class
        self.assertTrue("2^n" in complexity or "exp" in complexity.lower())

    # =========================================================================
    # PRUEBAS CON MÚLTIPLES CASOS (MEJOR, PEOR, PROMEDIO)
    # =========================================================================

    def test_multiple_cases_search(self):
        """Prueba búsqueda lineal con tres casos"""
        cases_data = [
            {"case_name": "Mejor Caso", "efficiency_function": "1"},
            {"case_name": "Peor Caso", "efficiency_function": "n"},
            {"case_name": "Caso Promedio", "efficiency_function": "n/2"},
        ]

        result = self.service.determine_complexity("Búsqueda Lineal", cases_data)

        self.assertEqual(len(result.analysis), 3)

        # Mejor caso
        self.assertEqual(result.analysis[0].notation_type, "Ω")
        self.assertEqual(result.analysis[0].complexity_class, "1")
        self.assertEqual(result.analysis[0].formatted_notation, "Ω(1)")

        # Peor caso
        self.assertEqual(result.analysis[1].notation_type, "O")
        self.assertEqual(result.analysis[1].complexity_class, "n")
        self.assertEqual(result.analysis[1].formatted_notation, "O(n)")

        # Caso promedio
        self.assertEqual(result.analysis[2].notation_type, "Θ")
        self.assertEqual(result.analysis[2].complexity_class, "n")
        self.assertEqual(result.analysis[2].formatted_notation, "Θ(n)")

    def test_multiple_cases_sorting(self):
        """Prueba ordenamiento con tres casos"""
        cases_data = [
            {"case_name": "Mejor Caso", "efficiency_function": "n"},
            {"case_name": "Peor Caso", "efficiency_function": "n**2"},
            {"case_name": "Caso Promedio", "efficiency_function": "n*log(n)"},
        ]

        result = self.service.determine_complexity("Quick Sort", cases_data)

        self.assertEqual(len(result.analysis), 3)
        self.assertEqual(result.analysis[0].notation_type, "Ω")
        self.assertEqual(result.analysis[1].notation_type, "O")
        self.assertEqual(result.analysis[2].notation_type, "Θ")

    # =========================================================================
    # PRUEBAS DE CASOS ESPECIALES Y EDGE CASES
    # =========================================================================

    def test_empty_efficiency_function(self):
        """Prueba con función de eficiencia vacía"""
        cases_data = [{"case_name": "Caso", "efficiency_function": ""}]

        result = self.service.determine_complexity("Vacío", cases_data)

        # Debe devolver O(1) por defecto
        self.assertEqual(result.analysis[0].complexity_class, "1")

    def test_na_efficiency_function(self):
        """Prueba con función N/A"""
        cases_data = [{"case_name": "Caso", "efficiency_function": "N/A"}]

        result = self.service.determine_complexity("N/A", cases_data)

        # Debe devolver O(1) por defecto
        self.assertEqual(result.analysis[0].complexity_class, "1")

    def test_already_with_o_notation(self):
        """Prueba con entrada que ya tiene notación O()"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "O(n)"}]

        result = self.service.determine_complexity("Pre-anotado", cases_data)

        # Debe extraer correctamente y devolver O(n)
        self.assertEqual(result.analysis[0].complexity_class, "n")

    def test_complex_polynomial(self):
        """Prueba polinomio complejo: T(n) = 5n^4 + 3n^3 + 2n^2 + n + 10"""
        cases_data = [
            {
                "case_name": "Peor Caso",
                "efficiency_function": "5*n**4 + 3*n**3 + 2*n**2 + n + 10",
            }
        ]

        result = self.service.determine_complexity("Polinomio Grado 4", cases_data)

        # El término dominante debe ser n^4
        self.assertEqual(result.analysis[0].complexity_class, "n^4")

    def test_notation_symbols_correctness(self):
        """Verifica que los símbolos de notación sean correctos según el caso"""
        test_cases = [
            ("Mejor Caso", "Ω"),
            ("best case", "Ω"),
            ("Peor Caso", "O"),
            ("worst case", "O"),
            ("Caso Promedio", "Θ"),
            ("average case", "Θ"),
            ("General", "Θ"),
        ]

        for case_name, expected_symbol in test_cases:
            cases_data = [{"case_name": case_name, "efficiency_function": "n"}]
            result = self.service.determine_complexity("Test", cases_data)
            self.assertEqual(
                result.analysis[0].notation_type,
                expected_symbol,
                f"Failed for case: {case_name}",
            )

    # =========================================================================
    # PRUEBAS DE JUSTIFICACIÓN Y METADATA
    # =========================================================================

    def test_justification_exists(self):
        """Verifica que cada resultado tenga justificación"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "n**2"}]

        result = self.service.determine_complexity("Test", cases_data)

        self.assertIsNotNone(result.analysis[0].justification)
        self.assertGreater(len(result.analysis[0].justification), 0)
        self.assertIn("dominado", result.analysis[0].justification.lower())

    def test_final_conclusion_exists(self):
        """Verifica que exista conclusión final"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "n*log(n)"}]

        result = self.service.determine_complexity("Merge Sort", cases_data)

        self.assertIsNotNone(result.final_conclusion)
        self.assertIn("Merge Sort", result.final_conclusion)
        self.assertIn("complejidad", result.final_conclusion.lower())

    def test_algorithm_name_preservation(self):
        """Verifica que el nombre del algoritmo se preserve"""
        algorithm_name = "Algoritmo de Prueba Especial"
        cases_data = [{"case_name": "Caso", "efficiency_function": "n"}]

        result = self.service.determine_complexity(algorithm_name, cases_data)

        self.assertEqual(result.algorithm_name, algorithm_name)

    # =========================================================================
    # PRUEBAS DE PERFORMANCE Y STRESS
    # =========================================================================

    def test_many_cases_at_once(self):
        """Prueba con muchos casos a la vez"""
        cases_data = [
            {"case_name": f"Caso {i}", "efficiency_function": f"{i}*n + {i}"}
            for i in range(1, 11)
        ]

        result = self.service.determine_complexity("Multi-caso", cases_data)

        self.assertEqual(len(result.analysis), 10)
        # Todos deben ser lineales
        for analysis in result.analysis:
            self.assertEqual(analysis.complexity_class, "n")

    def test_recursive_equation_format(self):
        """Prueba con formato de ecuación recursiva resuelta"""
        cases_data = [
            {"case_name": "Peor Caso", "efficiency_function": "T(n) = n + 1"}
        ]

        result = self.service.determine_complexity("Recursivo Resuelto", cases_data)

        self.assertEqual(result.analysis[0].complexity_class, "n")

    def test_fraction_expressions(self):
        """Prueba expresiones con fracciones: T(n) = (n+2)/2"""
        cases_data = [{"case_name": "Promedio", "efficiency_function": "(n+2)/2"}]

        result = self.service.determine_complexity("Con Fracción", cases_data)

        # (n+2)/2 sigue siendo O(n)
        self.assertEqual(result.analysis[0].complexity_class, "n")


class TestComplexityAnalysisServiceEdgeCases(unittest.TestCase):
    """Pruebas adicionales para casos extremos y errores"""

    def setUp(self):
        """Inicializa el servicio antes de cada prueba."""
        self.service = ComplexityAnalysisService()

    def test_malformed_expression_fallback(self):
        """Prueba que el fallback funcione con expresiones malformadas"""
        cases_data = [
            {"case_name": "Caso", "efficiency_function": "algo_raro_que_no_parsea"}
        ]

        result = self.service.determine_complexity("Malformado", cases_data)

        # Debe devolver algo válido (probablemente O(1) por el fallback)
        self.assertIsNotNone(result.analysis[0].complexity_class)
        self.assertIsNotNone(result.analysis[0].formatted_notation)

    def test_very_large_exponent(self):
        """Prueba con exponente muy grande: T(n) = n^100"""
        cases_data = [{"case_name": "Peor Caso", "efficiency_function": "n**100"}]

        result = self.service.determine_complexity("Exponente Grande", cases_data)

        self.assertEqual(result.analysis[0].complexity_class, "n^100")

    def test_mixed_log_notations(self):
        """Prueba con diferentes notaciones de logaritmo"""
        test_functions = ["log(n)", "ln(n)", "log2(n)"]

        for func in test_functions:
            cases_data = [{"case_name": "Caso", "efficiency_function": func}]
            result = self.service.determine_complexity("Log Test", cases_data)
            self.assertIn("log", result.analysis[0].complexity_class.lower())


if __name__ == "__main__":
    # Ejecutar todas las pruebas
    unittest.main(verbosity=2)

import unittest
from unittest.mock import MagicMock, patch
import sys
import os


from app.models.recursive.none_strategy import (
    NoneStrategy,
    NoneStrategyAgentOutput,
    DirectExpressionAnalyzer,
)


class TestNoneStrategy(unittest.TestCase):

    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.strategy = NoneStrategy(enable_verbose=True)

    def mock_agent_response(self, expr, expr_type, dominant, complexity, explanation):
        """Helper para crear una respuesta simulada del agente."""
        return NoneStrategyAgentOutput(
            expression=expr,
            expression_type=expr_type,
            dominant_term=dominant,
            complexity=complexity,
            detailed_explanation=explanation,
            simplification_steps=[
                "Expresión analizada",
                f"Término dominante: {dominant}",
                f"Complejidad: {complexity}",
            ],
        )

    # ==========================================
    # 1. PRUEBAS DE LÓGICA INTERNA (ANALYZER / TRIVIAL)
    # Estos casos se resuelven con reglas Python, sin IA.
    # ==========================================

    def test_analyzer_constant_expression(self):
        """
        Prueba T(n) = 5 -> O(1)
        Caso constante detectado por reglas internas.
        """
        equation = "T(n) = 5"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Constant Expression] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Tipo de expresión: {result.get('expression_type')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertTrue(result["applicable"])
        self.assertEqual(result["complexity"], "O(1)")
        self.assertEqual(result["expression_type"], "Constante")

    def test_analyzer_constant_complex(self):
        """
        Prueba T(n) = 100 -> O(1)
        Constante más grande.
        """
        equation = "T(n) = 100"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Constant Complex] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Complejidad: {result['complexity']}")

        self.assertTrue(result["applicable"])
        self.assertEqual(result["complexity"], "O(1)")

    def test_analyzer_linear_simple(self):
        """
        Prueba T(n) = n -> O(n)
        Expresión lineal simple.
        """
        equation = "T(n) = n"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Linear Simple] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Tipo de expresión: {result.get('expression_type')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertTrue(result["applicable"])
        self.assertEqual(result["complexity"], "O(n)")
        self.assertEqual(result["expression_type"], "Lineal")

    def test_analyzer_quadratic_simple(self):
        """
        Prueba T(n) = n**2 -> O(n²)
        Expresión cuadrática simple.
        """
        equation = "T(n) = n**2"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Quadratic Simple] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Tipo de expresión: {result.get('expression_type')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertTrue(result["applicable"])
        self.assertEqual(result["complexity"], "O(n²)")
        self.assertEqual(result["expression_type"], "Cuadrática")

    def test_analyzer_cubic_simple(self):
        """
        Prueba T(n) = n**3 -> O(n³)
        Expresión cúbica simple.
        """
        equation = "T(n) = n**3"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Cubic Simple] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Tipo de expresión: {result.get('expression_type')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertTrue(result["applicable"])
        self.assertEqual(result["complexity"], "O(n³)")
        self.assertEqual(result["expression_type"], "Cúbica")

    def test_analyzer_parsing_polynomial(self):
        """
        Prueba el parsing de: T(n) = n**2 + 3n + 5
        Verifica que detecta grado 2.
        """
        equation = "T(n) = n**2 + 3n + 5"
        params = DirectExpressionAnalyzer.parse_expression(equation)

        print(f"\n{'='*80}")
        print(f"[Test Parsing Polynomial] {equation}")
        print(f"{'='*80}")
        print(f"\n📊 PARÁMETROS EXTRAÍDOS:")
        print(f"  Tiene recursión: {params['has_recursion']}")
        print(f"  Es polinomial: {params['is_polynomial']}")
        print(f"  Grado: {params['degree']}")

        self.assertFalse(params["has_recursion"])
        self.assertTrue(params["is_polynomial"])
        self.assertEqual(params["degree"], 2)

    def test_analyzer_parsing_linear(self):
        """
        Prueba el parsing de: T(n) = 3n + 10
        Verifica que detecta grado 1.
        """
        equation = "T(n) = 3n + 10"
        params = DirectExpressionAnalyzer.parse_expression(equation)

        print(f"\n{'='*80}")
        print(f"[Test Parsing Linear] {equation}")
        print(f"{'='*80}")
        print(f"\n📊 PARÁMETROS EXTRAÍDOS:")
        print(f"  Tiene recursión: {params['has_recursion']}")
        print(f"  Es polinomial: {params['is_polynomial']}")
        print(f"  Grado: {params['degree']}")

        self.assertFalse(params["has_recursion"])
        self.assertTrue(params["is_polynomial"])
        self.assertEqual(params["degree"], 1)

    # ==========================================
    # 2. PRUEBAS CON MOCK AGENT (CASOS COMPLEJOS)
    # Expresiones con logaritmos, exponenciales, etc.
    # ==========================================

    @patch("app.models.recursive.none_strategy.NoneStrategyAgent")
    def test_agent_nlogn(self, MockAgent):
        """
        Prueba T(n) = n * log(n)
        Complejidad O(n log n).
        """
        # Configurar Mock
        mock_instance = MockAgent.return_value
        mock_instance.analyze_direct.return_value = self.mock_agent_response(
            expr="n * log(n)",
            expr_type="Logarítmico-Lineal",
            dominant="n log n",
            complexity="O(n log n)",
            explanation="La expresión n * log(n) tiene complejidad O(n log n), típica de algoritmos como Merge Sort.",
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = n * log(n)"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Agent n log n] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Tipo de expresión: {result.get('expression_type')}")
        print(f"✅ Término dominante: {result.get('dominant_term', 'n/a')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(n log n)")
        self.assertEqual(result["expression_type"], "Logarítmico-Lineal")

    @patch("app.models.recursive.none_strategy.NoneStrategyAgent")
    def test_agent_exponential(self, MockAgent):
        """
        Prueba T(n) = 2**n
        Complejidad O(2^n).
        """
        mock_instance = MockAgent.return_value
        mock_instance.analyze_direct.return_value = self.mock_agent_response(
            expr="2**n",
            expr_type="Exponencial",
            dominant="2^n",
            complexity="O(2^n)",
            explanation="La expresión 2^n tiene crecimiento exponencial, complejidad O(2^n).",
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = 2**n"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Agent Exponential] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Tipo de expresión: {result.get('expression_type')}")
        print(f"✅ Término dominante: {result.get('dominant_term', 'n/a')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(2^n)")
        self.assertEqual(result["expression_type"], "Exponencial")

    @patch("app.models.recursive.none_strategy.NoneStrategyAgent")
    def test_agent_polynomial_complex(self, MockAgent):
        """
        Prueba T(n) = 3n**2 + 5n + 10
        El término dominante es n², complejidad O(n²).
        """
        mock_instance = MockAgent.return_value
        mock_instance.analyze_direct.return_value = self.mock_agent_response(
            expr="3n**2 + 5n + 10",
            expr_type="Cuadrática",
            dominant="n²",
            complexity="O(n²)",
            explanation="El término dominante es 3n², las constantes y términos menores se eliminan en Big-O.",
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = 3n**2 + 5n + 10"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Agent Polynomial Complex] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Tipo de expresión: {result.get('expression_type')}")
        print(f"✅ Término dominante: {result.get('dominant_term', 'n/a')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(n²)")

    @patch("app.models.recursive.none_strategy.NoneStrategyAgent")
    def test_agent_logarithmic(self, MockAgent):
        """
        Prueba T(n) = log(n)
        Complejidad O(log n).
        """
        mock_instance = MockAgent.return_value
        mock_instance.analyze_direct.return_value = self.mock_agent_response(
            expr="log(n)",
            expr_type="Logarítmica",
            dominant="log n",
            complexity="O(log n)",
            explanation="La expresión log(n) tiene complejidad logarítmica O(log n).",
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = log(n)"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Agent Logarithmic] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Tipo de expresión: {result.get('expression_type')}")
        print(f"✅ Término dominante: {result.get('dominant_term', 'n/a')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(log n)")

    @patch("app.models.recursive.none_strategy.NoneStrategyAgent")
    def test_agent_mixed_dominant(self, MockAgent):
        """
        Prueba T(n) = 2**n + n**3
        El término exponencial domina, complejidad O(2^n).
        """
        mock_instance = MockAgent.return_value
        mock_instance.analyze_direct.return_value = self.mock_agent_response(
            expr="2**n + n**3",
            expr_type="Exponencial",
            dominant="2^n",
            complexity="O(2^n)",
            explanation="El término exponencial 2^n domina completamente sobre el polinomial n³.",
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = 2**n + n**3"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Agent Mixed Dominant Terms] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Tipo de expresión: {result.get('expression_type')}")
        print(f"✅ Término dominante: {result.get('dominant_term', 'n/a')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(2^n)")

    # ==========================================
    # 3. PRUEBAS DE VALIDACIÓN Y CASOS ESPECIALES
    # ==========================================

    def test_invalid_recursive_equation(self):
        """
        Prueba ecuación que contiene recursión T(n-1).
        Esta estrategia NO debe aplicar.
        """
        equation = "T(n) = T(n-1) + 1"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Invalid Recursive Equation] {equation}")
        print(f"{'='*80}")
        print(f"\n❌ Aplicable: {result['applicable']}")
        print(f"\n💡 EXPLICACIÓN:")
        print(result.get('explanation', 'No disponible'))

        self.assertFalse(result["applicable"])
        self.assertIn("recursiv", result["explanation"].lower())

    def test_invalid_divide_conquer(self):
        """
        Prueba ecuación divide y conquista T(n/2).
        Esta estrategia NO debe aplicar.
        """
        equation = "T(n) = 2T(n/2) + n"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Invalid Divide & Conquer] {equation}")
        print(f"{'='*80}")
        print(f"\n❌ Aplicable: {result['applicable']}")
        print(f"\n💡 EXPLICACIÓN:")
        print(result.get('explanation', 'No disponible'))

        self.assertFalse(result["applicable"])
        self.assertIn("recursiv", result["explanation"].lower())

    def test_polynomial_higher_degree(self):
        """
        Prueba T(n) = n**5 -> O(n^5)
        Polinomio de grado 5.
        """
        equation = "T(n) = n**5"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Polynomial Higher Degree] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Complejidad: {result['complexity']}")

        self.assertTrue(result["applicable"])
        self.assertEqual(result["complexity"], "O(n^5)")

    def test_complexity_type_detection(self):
        """
        Verifica que DirectExpressionAnalyzer detecta tipos correctamente.
        """
        # Constante
        params1 = DirectExpressionAnalyzer.parse_expression("T(n) = 10")
        type1 = DirectExpressionAnalyzer.determine_complexity_type(params1)
        self.assertEqual(type1, "Constante")

        # Lineal
        params2 = DirectExpressionAnalyzer.parse_expression("T(n) = 5n")
        type2 = DirectExpressionAnalyzer.determine_complexity_type(params2)
        self.assertEqual(type2, "Lineal")

        # Cuadrática
        params3 = DirectExpressionAnalyzer.parse_expression("T(n) = n**2")
        type3 = DirectExpressionAnalyzer.determine_complexity_type(params3)
        self.assertEqual(type3, "Cuadrática")

        # Cúbica
        params4 = DirectExpressionAnalyzer.parse_expression("T(n) = n**3")
        type4 = DirectExpressionAnalyzer.determine_complexity_type(params4)
        self.assertEqual(type4, "Cúbica")

        print(f"\n{'='*80}")
        print(f"[Test Complexity Type Detection]")
        print(f"{'='*80}")
        print(f"\n📋 TIPOS DETECTADOS:")
        print(f"  T(n) = 10 -> {type1}")
        print(f"  T(n) = 5n -> {type2}")
        print(f"  T(n) = n**2 -> {type3}")
        print(f"  T(n) = n**3 -> {type4}")


if __name__ == "__main__":
    unittest.main()

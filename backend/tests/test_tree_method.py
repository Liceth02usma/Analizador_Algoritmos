import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ajusta el path para importar tus módulos backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.recursive.tree_method import (
    TreeMethodStrategy,
    TreeMethodAgentOutput,
    EquationAnalyzer,
)


class TestTreeMethodStrategy(unittest.TestCase):

    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.strategy = TreeMethodStrategy(enable_verbose=True)

    def mock_agent_response(self, depth, expansion, work, total, simple, complexity):
        """Helper para crear una respuesta simulada del agente."""
        return TreeMethodAgentOutput(
            tree_depth=depth,
            levels_expansion=expansion,
            work_per_level=work,
            total_sum=total,
            sum_simplification=simple,
            complexity=complexity,
            detailed_explanation="Mocked explanation",
        )

    # ==========================================
    # 1. PRUEBAS DE LÓGICA INTERNA (ANALYZER / TRIVIAL)
    # Estos casos se resuelven con reglas Python, sin IA.
    # ==========================================

    def test_analyzer_trivial_linear_constant(self):
        """
        Prueba T(n) = T(n-1) + 1 -> O(n)
        Caso trivial detectado por reglas internas.
        """
        equation = "T(n) = T(n-1) + 1"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Trivial Linear Constant] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get("steps", []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(
            result.get(
                "detailed_explanation", result.get("explanation", "No disponible")
            )
        )
        print(f"\n✅ Método: {result.get('method')}")
        print(f"✅ Profundidad del árbol: {result.get('tree_depth')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertTrue(result["applicable"])
        self.assertEqual(result["complexity"], "O(n)")
        # Verificar que el método contenga "trivial" (case insensitive)
        self.assertIn("trivial", result["method"].lower())
        self.assertIn("trivial", result["method"])
        self.assertEqual(result["tree_depth"], "n")

    def test_analyzer_parsing_divide_conquer(self):
        """
        Prueba solo el parsing de: T(n) = 2T(n/2) + n
        Verifica que extrae a=2, b=2, f(n)=n
        """
        equation = "T(n) = 2T(n/2) + n"
        params = EquationAnalyzer.parse_equation(equation)

        print(f"\n{'='*80}")
        print(f"[Test Parsing Divide & Conquer] {equation}")
        print(f"{'='*80}")
        print(f"\n📊 PARÁMETROS EXTRAÍDOS:")
        print(f"  Tipo: {params['type']}")
        print(f"  a = {params['a']}")
        print(f"  b = {params['b']}")
        print(f"  f(n) = {params['f_n']}")

        self.assertEqual(params["type"], "divide_conquer")
        self.assertEqual(params["a"], 2)
        self.assertEqual(params["b"], 2)
        self.assertEqual(params["f_n"], "n")

    # ==========================================
    # 2. PRUEBAS CON MOCK AGENT (CASOS COMPLEJOS)
    # Divide y Vencerás, Lineales complejas, Sumatorias.
    # ==========================================

    @patch("app.models.recursive.tree_method.TreeMethodAgent")
    def test_agent_merge_sort(self, MockAgent):
        """
        Prueba T(n) = 2T(n/2) + n (Merge Sort)
        El agente debe sumar n en cada nivel log(n).
        """
        # Configurar Mock
        mock_instance = MockAgent.return_value
        mock_instance.solve_complex.return_value = self.mock_agent_response(
            depth="log₂(n)",
            expansion=["1*T(n)", "2*T(n/2)", "4*T(n/4)"],
            work=["n", "n", "n"],
            total="n * log₂(n)",
            simple="n log n",
            complexity="O(n log n)",
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = 2T(n/2) + n"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Agent Merge Sort] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get("steps", []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(
            result.get(
                "detailed_explanation", result.get("explanation", "No disponible")
            )
        )
        print(f"\n✅ Profundidad del árbol: {result.get('tree_depth')}")
        print(f"✅ Suma total: {result.get('total_sum', 'n/a')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(n log n)")
        self.assertEqual(result["tree_depth"], "log₂(n)")

    @patch("app.models.recursive.tree_method.TreeMethodAgent")
    def test_agent_linear_quadratic(self, MockAgent):
        """
        Prueba T(n) = T(n-1) + n (Selection Sort recursivo)
        Esto no es trivial para el analyzer porque f(n)=n.
        Suma: n + (n-1) + ... + 1 = n(n+1)/2 -> O(n^2)
        """
        mock_instance = MockAgent.return_value
        mock_instance.solve_complex.return_value = self.mock_agent_response(
            depth="n",
            expansion=["T(n)", "T(n-1)", "T(n-2)"],
            work=["n", "n-1", "n-2"],
            total="n(n+1)/2",
            simple="n²/2",
            complexity="O(n²)",
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = T(n-1) + n"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Agent Linear Quadratic] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get("steps", []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(
            result.get(
                "detailed_explanation", result.get("explanation", "No disponible")
            )
        )
        print(f"\n✅ Profundidad del árbol: {result.get('tree_depth')}")
        print(f"✅ Suma total: {result.get('total_sum', 'n/a')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(n²)")

    @patch("app.models.recursive.tree_method.TreeMethodAgent")
    def test_agent_summation_quicksort_avg(self, MockAgent):
        """
        Prueba T_avg(n) = (1/n) * sum[i=0 to n-1] T(i) + n
        Caso complejo que requiere el agente.
        """
        mock_instance = MockAgent.return_value
        mock_instance.solve_complex.return_value = self.mock_agent_response(
            depth="n",
            expansion=["Expansión de sumatoria..."],
            work=["Análisis probabilístico..."],
            total="Sumatoria armónica...",
            simple="n log n",
            complexity="O(n log n)",
        )
        self.strategy.agent = mock_instance

        # Nota: La ecuación exacta puede variar, probamos el parsing de sumatoria
        equation = "T_avg(n) = (1/n) * sum[i=0 to n-1] T(i) + n"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Agent Summation QuickSort] {equation[:50]}...")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get("steps", []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(
            result.get(
                "detailed_explanation", result.get("explanation", "No disponible")
            )
        )
        print(f"\n✅ Profundidad del árbol: {result.get('tree_depth')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(n log n)")
        # Verificar que el parser detectó que era tipo sumatoria antes de enviar al agente
        # (Esto se valida indirectamente si el agente recibió el contexto correcto,
        # pero aquí confiamos en el resultado del mock).

    @patch("app.models.recursive.tree_method.TreeMethodAgent")
    def test_agent_irregular_tree(self, MockAgent):
        """
        Prueba T(n) = T(n/3) + T(2n/3) + n
        Árbol irregular donde el Teorema Maestro falla.
        """
        mock_instance = MockAgent.return_value
        mock_instance.solve_complex.return_value = self.mock_agent_response(
            depth="log_{3/2}(n)",  # La rama más profunda
            expansion=["T(n)", "T(n/3) + T(2n/3)", "..."],
            work=["n", "n", "n"],  # El trabajo suma n en cada nivel completo
            total="n * log(n)",  # Método de Akra-Bazzi simplificado
            simple="n log n",
            complexity="O(n log n)",
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = T(n/3) + T(2n/3) + n"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Agent Irregular Tree] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get("steps", []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(
            result.get(
                "detailed_explanation", result.get("explanation", "No disponible")
            )
        )
        print(f"\n✅ Profundidad del árbol: {result.get('tree_depth')}")
        print(f"✅ Suma total: {result.get('total_sum', 'n/a')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(n log n)")

    # ==========================================
    # 3. PRUEBAS DE PARSING DE SUMATORIAS
    # ==========================================

    def test_parser_summation_structure(self):
        """Prueba que EquationAnalyzer entienda la estructura de sumatoria compleja."""
        equation = "T_avg(n) = (1/(n+1)) * sum[i=0 to n] T(i), donde T(i)=T(i-1)+1"
        params = EquationAnalyzer.parse_equation(equation)

        print(f"\n{'='*80}")
        print(f"[Test Parsing Summation] {equation[:50]}...")
        print(f"{'='*80}")
        print(f"\n📊 PARÁMETROS EXTRAÍDOS:")
        print(f"  Tipo: {params['type']}")
        print(f"  Tiene sumatoria: {params['has_summation']}")
        sum_params = params["summation_params"]
        print(f"  Factor multiplicativo: {sum_params['multiplicative_factor']}")
        print(f"  Límite inferior: {sum_params['lower_bound']}")
        print(f"  Límite superior: {sum_params['upper_bound']}")
        print(f"  Recurrencia interna: {sum_params['inner_recurrence'][:30]}...")

        self.assertEqual(params["type"], "summation")
        self.assertTrue(params["has_summation"])

        self.assertEqual(sum_params["multiplicative_factor"], "n+1")  # o (n+1)
        self.assertEqual(sum_params["lower_bound"], "0")
        self.assertEqual(sum_params["upper_bound"], "n")
        self.assertIn("t(i-1)", sum_params["inner_recurrence"].lower())


if __name__ == "__main__":
    unittest.main()

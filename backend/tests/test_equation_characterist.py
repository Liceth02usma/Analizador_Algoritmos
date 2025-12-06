import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ajusta el path para importar tus módulos backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.recursive.equation_characteristic import (
    CharacteristicEquationStrategy,
    CharacteristicEquationAgentOutput,
    CharacteristicAnalyzer,
)


class TestCharacteristicEquationStrategy(unittest.TestCase):

    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.strategy = CharacteristicEquationStrategy(enable_verbose=True)

    def mock_agent_response(self, form, char_eq, roots, gen_sol, final_sol, complexity):
        """Helper para crear una respuesta simulada del agente."""
        return CharacteristicEquationAgentOutput(
            recurrence_form=form,
            coefficients=[],
            characteristic_equation=char_eq,
            roots=roots,
            general_solution=gen_sol,
            particular_solution="N/A",
            final_solution=final_sol,
            complexity=complexity,
            detailed_explanation="Mocked explanation",
        )

    # ==========================================
    # 1. PRUEBAS DE LÓGICA INTERNA (ANALYZER)
    # Estos casos NO llaman al agente, se resuelven con tu código Python.
    # ==========================================

    def test_analyzer_order_1_homogeneous(self):
        """Prueba T(n) = 2T(n-1) -> O(2^n)"""
        equation = "T(n) = 2T(n-1)"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Order 1] {equation} -> {result['complexity']}")
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
        print(
            f"\n✅ Ecuación característica: {result.get('characteristic_equation', 'N/A')}"
        )
        print(f"✅ Raíces: {result.get('roots', 'N/A')}")
        print(f"✅ Solución general: {result.get('general_solution', 'N/A')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertTrue(result["applicable"])
        self.assertEqual(result["complexity"], "O(2^n)")
        self.assertIn("r - 2 = 0", result["characteristic_equation"])
        self.assertIn("2", result["roots"])

    def test_analyzer_order_2_distinct_roots(self):
        """Prueba T(n) = 5T(n-1) - 6T(n-2) -> Raíces 2 y 3"""
        # r^2 - 5r + 6 = 0 -> (r-2)(r-3)=0 -> r=2, r=3
        equation = "T(n) = 5T(n-1) - 6T(n-2)"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Order 2 Distinct] {equation} -> Raíces: {result['roots']}")
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
        print(
            f"\n✅ Ecuación característica: {result.get('characteristic_equation', 'N/A')}"
        )
        print(f"✅ Raíces: {result.get('roots', 'N/A')}")
        print(f"✅ Solución general: {result.get('general_solution', 'N/A')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(3.000^n)")
        # Verificamos que detecte ambas raíces
        roots = result["roots"]
        self.assertTrue(any("2.000" in r for r in roots))
        self.assertTrue(any("3.000" in r for r in roots))

    def test_analyzer_order_2_repeated_roots(self):
        """Prueba T(n) = 4T(n-1) - 4T(n-2) -> Raíz repetida 2"""
        # r^2 - 4r + 4 = 0 -> (r-2)^2=0 -> r=2
        equation = "T(n) = 4T(n-1) - 4T(n-2)"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Order 2 Repeated] {equation} -> Raíces: {result['roots']}")
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
        print(
            f"\n✅ Ecuación característica: {result.get('characteristic_equation', 'N/A')}"
        )
        print(f"✅ Raíces: {result.get('roots', 'N/A')}")
        print(f"✅ Solución general: {result.get('general_solution', 'N/A')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(2.000^n)")
        self.assertIn("C₂·n", result["general_solution"])  # Debe tener el término n*r^n

    def test_analyzer_fibonacci(self):
        """Prueba T(n) = T(n-1) + T(n-2) -> Fibonacci"""
        equation = "T(n) = T(n-1) + T(n-2)"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Fibonacci] {equation} -> {result['complexity']}")
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
        print(
            f"\n✅ Ecuación característica: {result.get('characteristic_equation', 'N/A')}"
        )
        print(f"✅ Raíces: {result.get('roots', 'N/A')}")
        print(f"✅ Solución general: {result.get('general_solution', 'N/A')}")
        print(f"✅ Complejidad: {result['complexity']}")

        # Debe detectar phi
        self.assertEqual(result["complexity"], "O(φ^n)")
        self.assertIn("1.618", result["explanation"])

    # ==========================================
    # 2. PRUEBAS DE SUMATORIAS (ANALYZER ESPECIAL)
    # ==========================================

    def test_summation_linear(self):
        """Prueba T_avg(n) = (1/(n+1)) * sum(T(i)) con T(i)=T(i-1)+1"""
        equation = (
            "T_avg(n) = (1/(n+1)) * sum[i=0 to n] T(i), donde T(i)=T(i-1)+1, T(0)=1"
        )
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Summation] {equation[:50]}...")
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
        print(f"\n✅ Método: {result.get('method', 'N/A')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertTrue(result["applicable"])
        self.assertEqual(result["complexity"], "O(n)")
        self.assertEqual(result["method"], "Ecuación Característica (Sumatoria)")

    # ==========================================
    # 3. PRUEBAS CON MOCK AGENT (CASOS COMPLEJOS)
    # No homogéneas o de orden superior delegan al Agente IA.
    # ==========================================

    @patch("app.models.recursive.equation_characteristic.CharacteristicEquationAgent")
    def test_agent_non_homogeneous(self, MockAgent):
        """Prueba T(n) = T(n-1) + 1 (No homogénea)"""
        # Configurar Mock
        mock_instance = MockAgent.return_value
        mock_instance.solve_complex.return_value = self.mock_agent_response(
            form="No homogénea, orden 1",
            char_eq="r - 1 = 0",
            roots=["1"],
            gen_sol="C*1^n",
            final_sol="T(n) = n + C",
            complexity="O(n)",
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = T(n-1) + 1"
        # El analyzer detectará 'non_homogeneous'='1' y pasará al agente
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Agent Non-Homogeneous] {equation} -> {result['complexity']}")
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
        print(f"\n✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(n)")
        # Verificar que NO intentó usar la lógica estándar
        self.assertNotIn("is_standard", result)

    @patch("app.models.recursive.equation_characteristic.CharacteristicEquationAgent")
    def test_agent_order_3(self, MockAgent):
        """Prueba T(n) = T(n-1) + T(n-2) + T(n-3) (Orden 3)"""
        mock_instance = MockAgent.return_value
        mock_instance.solve_complex.return_value = self.mock_agent_response(
            form="Homogénea, orden 3",
            char_eq="r^3 - r^2 - r - 1 = 0",
            roots=["1.839", "-0.4+0.6i", "-0.4-0.6i"],  # Constante de Tribonacci
            gen_sol="...",
            final_sol="...",
            complexity="O(1.839^n)",
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = T(n-1) + T(n-2) + T(n-3)"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Agent Order 3] {equation} -> {result['complexity']}")
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
        print(
            f"\n✅ Ecuación característica: {result.get('characteristic_equation', 'N/A')}"
        )
        print(f"✅ Raíces: {result.get('roots', 'N/A')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["complexity"], "O(1.839^n)")

    # ==========================================
    # 4. PRUEBAS DE VALIDACIÓN
    # ==========================================

    def test_invalid_format(self):
        """Prueba ecuación que no es lineal (División)"""
        equation = "T(n) = T(n/2) + 1"  # Esto es Master Theorem, no Characteristic
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Invalid] {equation}")
        print(f"{'='*80}")
        print(f"✅ Aplicable: {result.get('applicable', False)}")

        if result.get("steps"):
            print(f"\n📋 PASOS:")
            for step in result["steps"]:
                print(step)

        print(f"\n💡 EXPLICACIÓN:")
        print(
            result.get(
                "detailed_explanation", result.get("explanation", "No disponible")
            )
        )

        # El parser debería retornar is_applicable=False
        if "applicable" in result:
            self.assertFalse(result["applicable"])
        else:
            # Si tu código retorna error en estructura diferente
            self.assertIn("no cumple los requisitos", str(result))


if __name__ == "__main__":
    unittest.main()

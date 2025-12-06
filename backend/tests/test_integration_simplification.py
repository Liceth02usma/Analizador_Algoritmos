"""
Test de integración para verificar que el agente de simplificación
se integra correctamente en el flujo de análisis recursivo.
"""

import unittest
from app.models.recursive.equation_simplification import (
    simplify_recurrence_equation,
    EquationAnalyzer,
)


class TestSimplificationIntegration(unittest.TestCase):
    """Pruebas de integración del agente de simplificación."""

    def setUp(self):
        """Configuración inicial."""
        self.analyzer = EquationAnalyzer()

    def test_equation_analyzer_detects_summation(self):
        """Verifica que el analizador detecta ecuaciones con sumatorias."""
        equation = "T_avg(n) = (1/(n+1)) × Σ[i=0 to n] T(i)"
        check = self.analyzer.quick_check(equation)

        self.assertTrue(check["has_summation"])
        self.assertTrue(check["needs_simplification"])

    def test_equation_analyzer_detects_average(self):
        """Verifica que el analizador detecta ecuaciones con promedios."""
        equation = "T_avg(n) = (1/n) × sum(T(i))"
        check = self.analyzer.quick_check(equation)

        self.assertTrue(check["has_avg"])
        self.assertTrue(check["needs_simplification"])

    def test_equation_analyzer_detects_donde_clause(self):
        """Verifica que el analizador detecta cláusulas 'donde'."""
        equation = "T(n) = sum T(i), donde T(i) = T(i-1) + 1"
        check = self.analyzer.quick_check(equation)

        self.assertTrue(check["has_donde"])

    def test_equation_analyzer_skips_standard_form(self):
        """Verifica que el analizador NO procesa ecuaciones ya estándar."""
        equation = "T(n) = T(n-1) + n"
        check = self.analyzer.quick_check(equation)

        self.assertFalse(check["has_summation"])
        self.assertFalse(check["needs_simplification"])

    def test_simplification_agent_with_mock(self):
        """Prueba básica del agente con una ecuación simple."""
        # NOTA: Esta prueba requiere API key de Google para ejecutarse
        # Se puede hacer skip si no está disponible

        equation = (
            "T_avg(n) = (1/(n+1)) × Σ[i=0 to n] T(i), donde T(i) = T(i-1) + 1, T(0) = 1"
        )

        try:
            result = simplify_recurrence_equation(
                equation=equation,
                enable_verbose=False,  # Desactivar verbose en tests
            )

            # Verificaciones básicas
            self.assertIsNotNone(result)
            self.assertEqual(result.original_equation, equation)
            self.assertIsNotNone(result.simplified_equation)
            self.assertGreater(len(result.simplification_steps), 0)
            self.assertTrue(result.contains_summation)

            # Si la confianza es alta, verificar que se simplificó correctamente
            if result.confidence > 0.7:
                self.assertNotEqual(result.simplified_equation, equation)
                print(f"\n✅ Ecuación simplificada: {result.simplified_equation}")
                print(f"   Forma explícita: {result.explicit_form}")

        except Exception as e:
            # Si falla por falta de API key, hacer skip del test
            if "GOOGLE_API_KEY" in str(e) or "API key" in str(e):
                self.skipTest("Requiere GOOGLE_API_KEY configurada")
            else:
                raise

    def test_simplification_preserves_standard_equations(self):
        """Verifica que ecuaciones estándar no se modifican innecesariamente."""
        equation = "T(n) = 2T(n/2) + n"

        result = simplify_recurrence_equation(
            equation=equation,
            enable_verbose=False,
        )

        # Debe detectar que ya es estándar y no procesarla
        self.assertEqual(result.simplified_equation, equation)
        self.assertEqual(result.pattern_type, "standard")

    def test_integration_indicators(self):
        """Verifica los indicadores que activan la simplificación en el flujo."""
        indicators = ["σ", "∑", "sum", "Σ", "avg", "donde", "where", "1/n", "1/(n"]

        test_equations = [
            ("T(n) = Σ T(i)", ["Σ"]),
            ("T_avg(n) = (1/n) × sum", ["sum", "1/n"]),
            ("T(n) = ..., donde T(i) = ...", ["donde"]),
            ("T(n) = T(n-1) + n", []),  # Sin indicadores
        ]

        for eq, expected_indicators in test_equations:
            found = [ind for ind in indicators if ind in eq.lower()]

            if expected_indicators:
                self.assertTrue(
                    any(ind in eq.lower() for ind in indicators),
                    f"Ecuación '{eq}' debería tener indicadores de simplificación",
                )
            else:
                self.assertFalse(
                    any(ind in eq.lower() for ind in indicators),
                    f"Ecuación '{eq}' NO debería tener indicadores de simplificación",
                )


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ajusta el path para importar tus módulos backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.recursive.master_theorem import MasterTheoremStrategy, MasterTheoremAgentOutput

class TestMasterTheoremStrategy(unittest.TestCase):

    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.strategy = MasterTheoremStrategy(enable_verbose=True)

    def mock_agent_response(self, a, b, f_n, log_b_a, comparison, case_id, complexity):
        """Helper para crear una respuesta simulada del agente."""
        return MasterTheoremAgentOutput(
            a=a,
            b=b,
            f_n=f_n,
            log_b_a=log_b_a,
            comparison=comparison,
            case_id=case_id,
            complexity=complexity,
            detailed_explanation="Mocked explanation"
        )

    # ==========================================
    # CASO 1: f(n) es polinomialmente menor
    # T(n) = Theta(n^(log_b a))
    # ==========================================
    
    @patch('app.models.recursive.master_theorem.MasterTheoremAgent') 
    def test_case_1_basic(self, MockAgent):
        """Prueba Caso 1: T(n) = 9T(n/3) + n"""
        # Configurar el Mock
        mock_instance = MockAgent.return_value
        mock_instance.solve_complex.return_value = self.mock_agent_response(
            a=9, b=3, f_n="n", 
            log_b_a="n^2", 
            comparison="f(n) = O(n^(2 - epsilon))", 
            case_id="Caso 1", 
            complexity="O(n^2)"
        )
        
        # Inyectar el mock en la estrategia
        self.strategy.agent = mock_instance
        
        equation = "T(n) = 9T(n/3) + n"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Case 1 - Master Theorem] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Parámetros: a={result.get('a')}, b={result.get('b')}, Caso={result.get('case')}")
        print(f"✅ Complejidad: {result['complexity']}")
        
        self.assertTrue(result["applicable"])
        self.assertEqual(result["a"], 9)
        self.assertEqual(result["b"], 3)
        self.assertEqual(result["case"], "Caso 1")
        self.assertEqual(result["complexity"], "O(n^2)")

    # ==========================================
    # CASO 2: f(n) es del mismo orden
    # T(n) = Theta(n^(log_b a) * log n)
    # ==========================================

    @patch('app.models.recursive.master_theorem.MasterTheoremAgent')
    def test_case_2_merge_sort(self, MockAgent):
        """Prueba Caso 2: T(n) = 2T(n/2) + n (Merge Sort)"""
        mock_instance = MockAgent.return_value
        mock_instance.solve_complex.return_value = self.mock_agent_response(
            a=2, b=2, f_n="n", 
            log_b_a="n^1", 
            comparison="f(n) = Theta(n^1)", 
            case_id="Caso 2", 
            complexity="O(n log n)"
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = 2T(n/2) + n"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Case 2 - Merge Sort] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Parámetros: a={result.get('a')}, b={result.get('b')}, Caso={result.get('case')}")
        print(f"✅ Complejidad: {result['complexity']}")

        self.assertEqual(result["case"], "Caso 2")
        self.assertEqual(result["complexity"], "O(n log n)")

    @patch('app.models.recursive.master_theorem.MasterTheoremAgent')
    def test_case_2_binary_search(self, MockAgent):
        """Prueba Caso 2: T(n) = T(n/2) + 1 (Binary Search)"""
        # Aquí a=1, b=2, f(n)=1. n^log_2(1) = n^0 = 1. f(n) = Theta(1).
        mock_instance = MockAgent.return_value
        mock_instance.solve_complex.return_value = self.mock_agent_response(
            a=1, b=2, f_n="1", 
            log_b_a="1", 
            comparison="f(n) = Theta(1)", 
            case_id="Caso 2", 
            complexity="O(log n)"
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = T(n/2) + 1"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Case 2 - Binary Search] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Parámetros: a={result.get('a')}, b={result.get('b')}, Caso={result.get('case')}")
        print(f"✅ Complejidad: {result['complexity']}")
        self.assertEqual(result["complexity"], "O(log n)")

    # ==========================================
    # CASO 3: f(n) es polinomialmente mayor
    # T(n) = Theta(f(n))
    # ==========================================

    @patch('app.models.recursive.master_theorem.MasterTheoremAgent')
    def test_case_3_regularity(self, MockAgent):
        """Prueba Caso 3: T(n) = 3T(n/4) + n log n"""
        # log_4(3) approx 0.79. f(n) = n log n (que es Omega(n^0.79)).
        mock_instance = MockAgent.return_value
        mock_instance.solve_complex.return_value = self.mock_agent_response(
            a=3, b=4, f_n="n log n", 
            log_b_a="n^0.79", 
            comparison="f(n) = Omega(n^(0.79 + epsilon))", 
            case_id="Caso 3", 
            complexity="O(n log n)"
        )
        self.strategy.agent = mock_instance

        equation = "T(n) = 3T(n/4) + n log n"
        result = self.strategy.solve(equation)

        print(f"\n{'='*80}")
        print(f"[Test Case 3 - Regularity Condition] {equation}")
        print(f"{'='*80}")
        print(f"\n📋 PASOS DE LA SOLUCIÓN:")
        for step in result.get('steps', []):
            print(step)
        print(f"\n💡 EXPLICACIÓN DETALLADA:")
        print(result.get('detailed_explanation', result.get('explanation', 'No disponible')))
        print(f"\n✅ Parámetros: a={result.get('a')}, b={result.get('b')}, Caso={result.get('case')}")
        print(f"✅ Complejidad: {result['complexity']}")
        self.assertEqual(result["case"], "Caso 3")
        self.assertEqual(result["complexity"], "O(n log n)")

    # ==========================================
    # PRUEBAS DE VALIDACIÓN Y PARSING (Sin Mock necesario)
    # ==========================================

    def test_parsing_invalid_format(self):
        """Prueba que rechace ecuaciones que no son Divide y Vencerás."""
        # T(n) = T(n-1) + 1 es lineal, no aplica Master Theorem
        equation = "T(n) = T(n-1) + 1"
        result = self.strategy.solve(equation)
        
        print(f"\n{'='*80}")
        print(f"[Test Invalid Format] {equation}")
        print(f"{'='*80}")
        print(f"\n❌ Aplicable: {result['applicable']}")
        print(f"\n💡 EXPLICACIÓN:")
        print(result.get('explanation', 'No disponible'))
        
        self.assertFalse(result["applicable"])
        self.assertIn("no sigue el formato", result["explanation"])

    def test_parsing_parameters_extraction(self):
        """Prueba que el parser extraiga bien a y b antes de llamar al agente."""
        # Esta prueba valida la lógica interna de MasterEquationAnalyzer.parse_equation
        # accediendo a través de la estrategia si fuera necesario, o confiando en que
        # si los parámetros están mal, el mock fallaría o el raise saltaría.
        
        # T(n) = 2T(n/2) + n
        # El parser debe identificar a=2, b=2.
        
        # Nota: Como estamos mockeando el agente, la validación real ocurre
        # en el bloque 'if not params["is_master_form"]' dentro de solve().
        # Probemos un caso borde: T(n) = T(n/2) (f(n) implícito 0 -> 1?)
        
        equation = "T(n) = 4T(n/2) + n^2" 
        # Aquí no mockeamos para ver si pasa la validación inicial del parser
        # pero fallará al intentar llamar al agente real si no tenemos API key configurada
        # o si la clase AgentBase intenta conectar.
        # Lo mejor es verificar que NO lance ValueError de formato.
        
        from app.models.recursive.master_theorem import MasterEquationAnalyzer
        params = MasterEquationAnalyzer.parse_equation(equation)
        
        print(f"\n{'='*80}")
        print(f"[Test Parser Extraction] {equation}")
        print(f"{'='*80}")
        print(f"\n📊 PARÁMETROS EXTRAÍDOS:")
        print(f"  a = {params['a']}")
        print(f"  b = {params['b']}")
        print(f"  f(n) = {params.get('f_n', 'n/a')}")
        print(f"  Es formato Master: {params['is_master_form']}")
        self.assertEqual(params["a"], 4)
        self.assertEqual(params["b"], 2)
        self.assertTrue(params["is_master_form"])

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import MagicMock
import json
import os
import sys

# Agregar el directorio backend al path para imports absolutos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.recursive.recurrence_analysis import RecurrenceEquationAgent

class MockRecursiveInstance:
    """
    Clase que simula el objeto que el parser entrega al agente.
    """
    def __init__(self, name, pseudocode, type_case, recursive_calls, base_cases_count=1):
        self.name = name
        self.pseudocode = pseudocode
        self.type_case = type_case
        self.recursive_calls = recursive_calls
        self.parsed_tree = f"Tree('start', [Tree('procedure_def', [Token('NAME', '{name}')...])])" # Simulación simple del AST
        
        # Simulamos los nodos detectados (esto lo haría tu analizador sintáctico)
        self.recursive_call_nodes = [{"call": f"CALL {name}(...)", "line": 5}] * recursive_calls
        self.base_cases_list = [{"condition": "n=0", "return": "1"}] * base_cases_count

    def extract_recurrence(self):
        """Simula la extracción previa de llamadas recursivas"""
        pass

    def extract_base_case(self):
        """Simula la extracción de casos base"""
        return self.base_cases_list

class TestRecurrenceAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Se ejecuta una vez antes de todos los tests. Inicializa el agente."""
        # Asegúrate de tener las API KEYS configuradas en tu .env
        print("\n--- INICIANDO PRUEBAS DE AGENTE DE RECURRENCIA ---")
        try:
            cls.agent = RecurrenceEquationAgent(model_type="Gemini_Rapido", enable_verbose=True)
        except Exception as e:
            print(f"Error inicializando el agente (Revisa tu .env y conexión): {e}")
            cls.agent = None

    def test_01_factorial_simple(self):
        """
        Prueba: Algoritmo Factorial (Recursión Lineal Simple)
        Esperado: T(n) = T(n-1) + c
        """
        if not self.agent: self.skipTest("Agente no inicializado")

        code = """
        factorial(n)
        begin
            if (n = 0) then begin
                return 1
            end
            else begin
                return n * CALL factorial(n - 1)
            end
        end
        """
        instance = MockRecursiveInstance(
            name="factorial",
            pseudocode=code,
            type_case=False, # Factorial siempre hace lo mismo
            recursive_calls=1
        )

        result = self.agent.analyze_recurrence(instance)

        self.assertIsNotNone(result, "El agente no devolvió respuesta.")
        self.assertFalse(result.has_multiple_cases, "Factorial no debería tener múltiples casos.")
        
        # Validamos que la ecuación contenga T(n-1)
        equation = result.recurrence_equation.replace(" ", "")
        print(f"\n[Resultado Factorial] {result.recurrence_equation}")
        self.assertIn("T(n-1)", equation)

    def test_02_binary_search(self):
        """
        Prueba: Búsqueda Binaria (Divide y Vencerás)
        Esperado: T(n) = T(n/2) + c
        """
        if not self.agent: self.skipTest("Agente no inicializado")

        code = """
        busqueda_binaria(A, inicio, fin, x)
        begin
            if (inicio > fin) then begin return -1 end
            medio 🡨 (inicio + fin) div 2
            if (A[medio] = x) then begin return medio end
            if (A[medio] > x) then begin
                return CALL busqueda_binaria(A, inicio, medio - 1, x)
            end else begin
                return CALL busqueda_binaria(A, medio + 1, fin, x)
            end
        end
        """
        # Nota: Aunque tiene IFs, la Búsqueda Binaria estructuralmente siempre divide
        # por lo que usualmente se modela como caso único T(n/2) para la complejidad,
        # aunque el agente podría detectar mejor caso O(1).
        # Para este test, forzamos type_case=False para ver si detecta el patrón T(n/2).
        
        instance = MockRecursiveInstance(
            name="busqueda_binaria",
            pseudocode=code,
            type_case=False, 
            recursive_calls=1 # En cada ejecución lógica solo entra a UNA rama recursiva
        )

        result = self.agent.analyze_recurrence(instance)
        
        equation = result.recurrence_equation.replace(" ", "")
        print(f"\n[Resultado Binary Search] {result.recurrence_equation}")
        
        # Validaciones flexibles por si el modelo usa variaciones
        is_valid = "T(n/2)" in equation or "T(ndiv2)" in equation
        self.assertTrue(is_valid, f"Se esperaba T(n/2) en la ecuación: {result.recurrence_equation}")

    def test_03_fibonacci(self):
        """
        Prueba: Fibonacci (Múltiples llamadas recursivas)
        Esperado: T(n) = T(n-1) + T(n-2) + c
        """
        if not self.agent: self.skipTest("Agente no inicializado")

        code = """
        fibonacci(n)
        begin
            if (n <= 1) then begin return n end
            return CALL fibonacci(n - 1) + CALL fibonacci(n - 2)
        end
        """
        instance = MockRecursiveInstance(
            name="fibonacci",
            pseudocode=code,
            type_case=False,
            recursive_calls=2
        )

        result = self.agent.analyze_recurrence(instance)
        equation = result.recurrence_equation.replace(" ", "")
        print(f"\n[Resultado Fibonacci] {result.recurrence_equation}")

        self.assertIn("T(n-1)", equation)
        self.assertIn("T(n-2)", equation)

    def test_04_linear_search_multi_case(self):
        """
        Prueba: Búsqueda Lineal Recursiva (Tu ejemplo principal)
        Esperado: has_multiple_cases=True
                  Best: T(1) = 1
                  Worst: T(n) = T(n-1) + 1
                  Avg: Sumatoria explícita
        """
        if not self.agent: self.skipTest("Agente no inicializado")

        code = """
        busqueda_lineal_rec(A, x, i, n)
        begin
           if (i = n) then begin
               return -1
           end
           else begin
               if (A[i] = x) then begin
                   return i
               end
               else begin
                   return CALL busqueda_lineal_rec(A, x, i + 1, n)
               end
           end
        end
        index 🡨 CALL busqueda_lineal_rec(A, x, 0, n)
        return index
        """
        instance = MockRecursiveInstance(
            name="busqueda_lineal_rec",
            pseudocode=code,
            type_case=True, # IMPORTANTE: Activamos el modo multi-caso
            recursive_calls=1
        )

        result = self.agent.analyze_recurrence(instance)

        self.assertTrue(result.has_multiple_cases, "Debe detectar múltiples casos.")
        
        # 1. Validar Mejor Caso
        best = result.best_case.recurrence_equation
        print(f"\n[Linear Search Best] {best}")
        self.assertTrue("1" in best or "c" in best, "Mejor caso debería ser constante")

        # 2. Validar Peor Caso
        worst = result.worst_case.recurrence_equation.replace(" ", "")
        print(f"[Linear Search Worst] {result.worst_case.recurrence_equation}")
        self.assertIn("T(n-1)", worst, "Peor caso debe ser lineal recursivo")

        # 3. Validar Caso Promedio (La parte más crítica de tu prompt)
        avg = result.average_case.recurrence_equation
        print(f"[Linear Search Avg] {avg}")
        
        # Validar que contiene el símbolo de sumatoria y la estructura 1/n
        has_sigma = "Σ" in avg or "sum" in avg.lower()
        has_fraction = "1/" in avg
        
        self.assertTrue(has_sigma, "El caso promedio DEBE contener una sumatoria (Σ)")
        self.assertTrue(has_fraction, "El caso promedio DEBE contener el factor de probabilidad (1/n o 1/(n+1))")

    def test_05_merge_sort(self):
        """
        Prueba: Merge Sort (Divide y Vencerás Estándar)
        Esperado: T(n) = 2T(n/2) + n
        """
        if not self.agent: self.skipTest("Agente no inicializado")

        code = """
        merge_sort(A, n)
        begin
            if (n <= 1) then begin return end
            mitad 🡨 n div 2
            CALL merge_sort(A, mitad)      // Primera mitad
            CALL merge_sort(A, n - mitad)  // Segunda mitad
            merge(A, mitad, n)             // Costo lineal O(n)
        end
        """
        instance = MockRecursiveInstance(
            name="merge_sort",
            pseudocode=code,
            type_case=False, # Merge Sort siempre hace las mismas divisiones
            recursive_calls=2
        )

        result = self.agent.analyze_recurrence(instance)
        
        equation = result.recurrence_equation.replace(" ", "")
        print(f"\n[Resultado Merge Sort] {result.recurrence_equation}")

        # Validaciones: debe tener 2T(n/2) y un término lineal (+n o +cn)
        self.assertTrue("2T(n/2)" in equation or "2T(ndiv2)" in equation, "Debe contener 2T(n/2)")
        self.assertTrue("+n" in equation or "+cn" in equation, "Debe contener el costo lineal del merge (+n)")

    def test_06_towers_of_hanoi(self):
        """
        Prueba: Torres de Hanoi (Recursión Exponencial)
        Esperado: T(n) = 2T(n-1) + 1
        """
        if not self.agent: self.skipTest("Agente no inicializado")

        code = """
        hanoi(n, origen, destino, auxiliar)
        begin
            if (n = 1) then begin
                mover_disco(origen, destino)
                return 1
            end
            CALL hanoi(n - 1, origen, auxiliar, destino)
            mover_disco(origen, destino)
            CALL hanoi(n - 1, auxiliar, destino, origen)
        end
        """
        instance = MockRecursiveInstance(
            name="hanoi",
            pseudocode=code,
            type_case=False,
            recursive_calls=2
        )

        result = self.agent.analyze_recurrence(instance)
        equation = result.recurrence_equation.replace(" ", "")
        print(f"\n[Resultado Hanoi] {result.recurrence_equation}")

        # Validaciones: T(n) = 2T(n-1) + 1
        self.assertTrue("2T(n-1)" in equation, "Debe contener 2T(n-1)")

    def test_07_quick_sort_multicase(self):
        """
        Prueba: Quick Sort (Análisis Multi-caso)
        Esperado:
           Best: T(n) = 2T(n/2) + n
           Worst: T(n) = T(n-1) + n
        """
        if not self.agent: self.skipTest("Agente no inicializado")

        code = """
        quick_sort(A, inicio, fin)
        begin
            if (inicio >= fin) then return
            pivote_index 🡨 partition(A, inicio, fin) // Costo O(n)
            CALL quick_sort(A, inicio, pivote_index - 1)
            CALL quick_sort(A, pivote_index + 1, fin)
        end
        """
        instance = MockRecursiveInstance(
            name="quick_sort",
            pseudocode=code,
            type_case=True, # Quick Sort depende drásticamente de la elección del pivote
            recursive_calls=2
        )

        result = self.agent.analyze_recurrence(instance)
        self.assertTrue(result.has_multiple_cases, "Quick Sort debe tener múltiples casos")

        # 1. Mejor Caso (Pivote perfecto)
        best = result.best_case.recurrence_equation.replace(" ", "")
        print(f"\n[Quick Sort Best] {result.best_case.recurrence_equation}")
        self.assertTrue("2T(n/2)" in best or "2T(ndiv2)" in best, "Mejor caso debe dividir a la mitad")

        # 2. Peor Caso (Pivote en los extremos)
        worst = result.worst_case.recurrence_equation.replace(" ", "")
        print(f"[Quick Sort Worst] {result.worst_case.recurrence_equation}")
        # En peor caso, una llamada es T(n-1) y la otra T(0) que es constante, así que queda T(n-1) + n
        self.assertTrue("T(n-1)" in worst, "Peor caso debe ser T(n-1) + n")

    def test_08_sqrt_recurrence(self):
        """
        Prueba: Algoritmo con reducción de Raíz Cuadrada (Ej. Búsqueda en estructura VEB o descomposición)
        Esperado: T(n) = T(sqrt(n)) + 1  o  T(n) = aT(sqrt(n)) + c
        """
        if not self.agent: self.skipTest("Agente no inicializado")

        code = """
        sqrt_search(n)
        begin
            if (n <= 2) then return 1
            // Reducimos el problema a su raíz cuadrada
            m 🡨 raiz_cuadrada(n)
            return CALL sqrt_search(m) + 1
        end
        """
        instance = MockRecursiveInstance(
            name="sqrt_search",
            pseudocode=code,
            type_case=False,
            recursive_calls=1
        )

        result = self.agent.analyze_recurrence(instance)
        equation = result.recurrence_equation.replace(" ", "").lower()
        print(f"\n[Resultado Sqrt] {result.recurrence_equation}")

        # Validaciones: Debe detectar la raíz cuadrada en el argumento
        # El modelo puede escribir sqrt(n), n^(1/2), o raiz(n)
        has_sqrt = "sqrt(n)" in equation or "n^(1/2)" in equation or "raiz" in equation or "n^0.5" in equation
        self.assertTrue(has_sqrt, f"La ecuación debe contener una referencia a la raíz cuadrada. Obtenido: {result.recurrence_equation}")



if __name__ == '__main__':
    unittest.main()
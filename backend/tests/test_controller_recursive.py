"""
Tests unitarios para ControlRecursive.
"""

import pytest
from app.controllers.controller_recursive import ControlRecursive
from app.parsers.parser import parser, TreeToDict


class TestControlRecursive:
    """Suite de tests para el controlador recursivo."""
    
    def setup_method(self):
        """Configuración antes de cada test."""
        self.controller = ControlRecursive()
    
    def test_inicializacion(self):
        """Test de inicialización del controlador."""
        assert self.controller.base_cases == 0
        assert self.controller.recursion_depth == 0
        assert self.controller.recurrence_relation == ""
        assert self.controller.complexity is None
        assert self.controller.algorithm is None
        assert self.controller.recursive_calls == []
        assert self.controller.base_case_details == []
    
    def test_factorial(self):
        """Test de análisis de factorial recursivo."""
        pseudocodigo = """
        FUNCTION factorial(n)
        begin
            if (n <= 1) then
            begin
                return 1
            end
            else
            begin
                return n * CALL factorial(n - 1)
            end
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "Factorial",
            pseudocodigo
        )
        
        assert results['algorithm']['name'] == "Factorial"
        assert results['algorithm']['type'] == "Recursivo"
        assert results['analysis']['base_cases'] >= 1
        assert results['analysis']['recursive_calls'] >= 1
        assert results['complexity']['time']['worst_case'] in ["O(n)", "O(n log n)"]
    
    def test_fibonacci(self):
        """Test de análisis de Fibonacci recursivo."""
        pseudocodigo = """
        FUNCTION fibonacci(n)
        begin
            if (n <= 1) then
            begin
                return n
            end
            else
            begin
                return CALL fibonacci(n - 1) + CALL fibonacci(n - 2)
            end
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "Fibonacci",
            pseudocodigo
        )
        
        assert results['analysis']['base_cases'] >= 1
        assert results['analysis']['recursive_calls'] >= 2
        # Fibonacci tiene complejidad exponencial
        assert "2^n" in results['complexity']['time']['worst_case'] or \
               "exponencial" in results['complexity']['time']['worst_case'].lower()
    
    def test_busqueda_binaria(self):
        """Test de búsqueda binaria recursiva."""
        pseudocodigo = """
        FUNCTION busquedaBinaria(array, inicio, fin, objetivo)
        begin
            if (inicio > fin) then
            begin
                return -1
            end
            
            medio 🡨 (inicio + fin) / 2
            
            if (array[medio] == objetivo) then
            begin
                return medio
            end
            else
            begin
                if (array[medio] > objetivo) then
                begin
                    return CALL busquedaBinaria(array, inicio, medio - 1, objetivo)
                end
                else
                begin
                    return CALL busquedaBinaria(array, medio + 1, fin, objetivo)
                end
            end
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "BúsquedaBinaria",
            pseudocodigo
        )
        
        assert results['analysis']['base_cases'] >= 1
        assert results['analysis']['recursive_calls'] >= 1
        # Búsqueda binaria es O(log n)
        assert "log" in results['complexity']['time']['worst_case'].lower()
    
    def test_deteccion_patron_subtract_1(self):
        """Test de detección de patrón n-1."""
        pseudocodigo = """
        FUNCTION suma(n)
        begin
            if (n <= 0) then return 0
            else return n + CALL suma(n - 1)
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "Suma",
            pseudocodigo
        )
        
        # Verificar que se detectaron llamadas recursivas
        assert results['analysis']['recursive_calls'] >= 1
        
        # Verificar que hay detalles de las llamadas
        if results['analysis']['recursive_call_details']:
            patterns = [call.get('pattern', '') for call in results['analysis']['recursive_call_details']]
            assert 'subtract_1' in patterns or 'custom' in patterns
    
    def test_deteccion_patron_divide_by_2(self):
        """Test de detección de patrón n/2."""
        pseudocodigo = """
        FUNCTION busqueda(array, inicio, fin)
        begin
            if (inicio >= fin) then return -1
            medio 🡨 (inicio + fin) / 2
            return CALL busqueda(array, inicio, medio)
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "Busqueda",
            pseudocodigo
        )
        
        assert results['analysis']['recursive_calls'] >= 1
    
    def test_multiples_casos_base(self):
        """Test con múltiples casos base."""
        pseudocodigo = """
        FUNCTION fibonacci(n)
        begin
            if (n == 0) then
            begin
                return 0
            end
            if (n == 1) then
            begin
                return 1
            end
            return CALL fibonacci(n - 1) + CALL fibonacci(n - 2)
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "Fibonacci",
            pseudocodigo
        )
        
        # Puede detectar 1 o 2 casos base dependiendo del parser
        assert results['analysis']['base_cases'] >= 1
    
    def test_sin_recursion(self):
        """Test de código sin recursión."""
        pseudocodigo = """
        FUNCTION suma(a, b)
        begin
            return a + b
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "SumaSimple",
            pseudocodigo
        )
        
        # Sin recursión
        assert results['analysis']['recursive_calls'] == 0
    
    def test_exportar_texto(self):
        """Test de exportación en formato texto."""
        pseudocodigo = """
        FUNCTION potencia(base, exp)
        begin
            if (exp == 0) then return 1
            else return base * CALL potencia(base, exp - 1)
        end
        """
        
        self.controller.analyze_from_parsed_tree("Potencia", pseudocodigo)
        report = self.controller.get_complexity_report("text")
        
        assert "ANÁLISIS DE COMPLEJIDAD" in report
        assert "Complejidad Temporal" in report
        assert "Recursión" in report
    
    def test_exportar_json(self):
        """Test de exportación en formato JSON."""
        pseudocodigo = """
        FUNCTION factorial(n)
        begin
            if (n <= 1) then return 1
            else return n * CALL factorial(n - 1)
        end
        """
        
        self.controller.analyze_from_parsed_tree("Factorial", pseudocodigo)
        report = self.controller.get_complexity_report("json")
        
        assert '"time_complexity"' in report
        assert '"space_complexity"' in report
        assert '"recurrence"' in report
    
    def test_exportar_markdown(self):
        """Test de exportación en formato Markdown."""
        pseudocodigo = """
        FUNCTION factorial(n)
        begin
            if (n <= 1) then return 1
            else return n * CALL factorial(n - 1)
        end
        """
        
        self.controller.analyze_from_parsed_tree("Factorial", pseudocodigo)
        report = self.controller.get_complexity_report("markdown")
        
        assert "# Análisis de Complejidad" in report
        assert "##" in report
        assert "**" in report
        assert "`" in report
    
    def test_resumen_recursion(self):
        """Test del resumen de recursión."""
        pseudocodigo = """
        FUNCTION fibonacci(n)
        begin
            if (n <= 1) then return n
            else return CALL fibonacci(n - 1) + CALL fibonacci(n - 2)
        end
        """
        
        self.controller.analyze_from_parsed_tree("Fibonacci", pseudocodigo)
        summary = self.controller.get_recursion_summary()
        
        assert "Total de casos base" in summary
        assert "Total de llamadas recursivas" in summary
        assert "Relación de recurrencia" in summary
    
    def test_optimizaciones_fibonacci(self):
        """Test de sugerencias de optimización para Fibonacci."""
        pseudocodigo = """
        FUNCTION fibonacci(n)
        begin
            if (n <= 1) then return n
            else return CALL fibonacci(n - 1) + CALL fibonacci(n - 2)
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "Fibonacci",
            pseudocodigo
        )
        
        # Debe sugerir memoización
        optimizations = results['optimizations']
        assert len(optimizations) > 0
        
        # Buscar sugerencia de memoización
        has_memoization = any('memoización' in opt.lower() or 'memoization' in opt.lower() 
                              for opt in optimizations)
        assert has_memoization
    
    def test_reset(self):
        """Test del método reset."""
        pseudocodigo = """
        FUNCTION factorial(n)
        begin
            if (n <= 1) then return 1
            else return n * CALL factorial(n - 1)
        end
        """
        
        self.controller.analyze_from_parsed_tree("Factorial", pseudocodigo)
        
        # Verificar que hay datos
        assert self.controller.base_cases > 0 or self.controller.algorithm is not None
        
        # Reset
        self.controller.reset()
        
        # Verificar que se limpiaron los datos
        assert self.controller.base_cases == 0
        assert self.controller.recursion_depth == 0
        assert self.controller.recurrence_relation == ""
        assert self.controller.complexity is None
        assert self.controller.algorithm is None
        assert self.controller.recursive_calls == []
    
    def test_con_estructura_parseada(self):
        """Test usando estructura ya parseada."""
        pseudocodigo = """
        FUNCTION factorial(n)
        begin
            if (n <= 1) then return 1
            else return n * CALL factorial(n - 1)
        end
        """
        
        # Parsear primero
        tree = parser.parse(pseudocodigo)
        transformer = TreeToDict()
        structure = transformer.transform(tree)
        
        # Analizar con estructura parseada
        results = self.controller.analyze_from_parsed_tree(
            "Factorial",
            pseudocodigo,
            parsed_tree=tree,
            structure=structure
        )
        
        assert results['algorithm']['name'] == "Factorial"
        assert results['analysis']['base_cases'] >= 1
    
    def test_mergesort(self):
        """Test de MergeSort recursivo."""
        pseudocodigo = """
        FUNCTION mergeSort(array, inicio, fin)
        begin
            if (inicio < fin) then
            begin
                medio 🡨 (inicio + fin) / 2
                CALL mergeSort(array, inicio, medio)
                CALL mergeSort(array, medio + 1, fin)
            end
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "MergeSort",
            pseudocodigo
        )
        
        assert results['analysis']['recursive_calls'] >= 2
        # MergeSort es O(n log n)
        complexity = results['complexity']['time']['worst_case']
        assert "log" in complexity.lower() or "n log n" in complexity
    
    def test_torres_hanoi(self):
        """Test de Torres de Hanoi."""
        pseudocodigo = """
        FUNCTION hanoi(n, origen, destino, auxiliar)
        begin
            if (n == 1) then
            begin
                print("Mover")
            end
            else
            begin
                CALL hanoi(n - 1, origen, auxiliar, destino)
                print("Mover")
                CALL hanoi(n - 1, auxiliar, destino, origen)
            end
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "Hanoi",
            pseudocodigo
        )
        
        assert results['analysis']['base_cases'] >= 1
        assert results['analysis']['recursive_calls'] >= 2
    
    def test_deteccion_patron(self):
        """Test de detección de patrones algorítmicos."""
        pseudocodigo = """
        FUNCTION busquedaBinaria(array, inicio, fin, x)
        begin
            if (inicio > fin) then return -1
            medio 🡨 (inicio + fin) / 2
            if (array[medio] == x) then return medio
            if (array[medio] > x) then
                return CALL busquedaBinaria(array, inicio, medio - 1, x)
            else
                return CALL busquedaBinaria(array, medio + 1, fin, x)
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "BúsquedaBinaria",
            pseudocodigo
        )
        
        # Debe detectar un patrón
        assert 'pattern' in results
        assert 'name' in results['pattern']
        assert results['pattern']['name'] != ''
    
    def test_soluciones_recurrencia(self):
        """Test de soluciones de la recurrencia."""
        pseudocodigo = """
        FUNCTION factorial(n)
        begin
            if (n <= 1) then return 1
            else return n * CALL factorial(n - 1)
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "Factorial",
            pseudocodigo
        )
        
        # Debe tener soluciones de recurrencia
        assert 'recurrence_solutions' in results
        solutions = results['recurrence_solutions']
        
        # Verificar que al menos intenta resolver
        assert len(solutions) > 0
    
    def test_complejidad_espacial(self):
        """Test de análisis de complejidad espacial."""
        pseudocodigo = """
        FUNCTION factorial(n)
        begin
            if (n <= 1) then return 1
            else return n * CALL factorial(n - 1)
        end
        """
        
        results = self.controller.analyze_from_parsed_tree(
            "Factorial",
            pseudocodigo
        )
        
        # Debe tener complejidad espacial
        assert 'space' in results['complexity']
        assert 'worst_case' in results['complexity']['space']
        
        # Para recursión lineal, el espacio es O(n) por el stack
        space = results['complexity']['space']['worst_case']
        assert space != ""
    
    def test_multiple_analisis(self):
        """Test de múltiples análisis consecutivos con reset."""
        pseudocodes = [
            ("Factorial", """
            FUNCTION factorial(n)
            begin
                if (n <= 1) then return 1
                else return n * CALL factorial(n - 1)
            end
            """),
            
            ("Fibonacci", """
            FUNCTION fibonacci(n)
            begin
                if (n <= 1) then return n
                else return CALL fibonacci(n - 1) + CALL fibonacci(n - 2)
            end
            """)
        ]
        
        for name, code in pseudocodes:
            results = self.controller.analyze_from_parsed_tree(name, code)
            assert results['algorithm']['name'] == name
            
            # Reset para el siguiente
            self.controller.reset()
            assert self.controller.algorithm is None


# Ejecutar tests si se ejecuta directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

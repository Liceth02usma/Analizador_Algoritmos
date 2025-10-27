"""
Tests unitarios para ControlIterative.
"""

import pytest
from app.controllers.controller_iterative import ControlIterative
from app.parsers.parser import parser, TreeToDict


class TestControlIterative:

    def test_no_loops(self):
        pseudocode = """
        x 🡨 5
        y 🡨 10
        z 🡨 x + y
        """
        controller = ControlIterative()
        results = controller.analyze_from_parsed_tree("SinCiclos", pseudocode)
        assert results["analysis"]["loops_detected"] == 0
        assert results["analysis"]["nested_levels"] == 0
        assert results["analysis"]["loop_details"] == []

    def test_single_for_loop(self):
        pseudocode = """
        for i 🡨 0 to n do
        begin
            suma 🡨 suma + i
        end
        """
        controller = ControlIterative()
        results = controller.analyze_from_parsed_tree("SumaSimple", pseudocode)
        assert results["analysis"]["loops_detected"] == 1
        assert results["analysis"]["nested_levels"] == 1
        assert len(results["analysis"]["loop_details"]) == 1
        loop = results["analysis"]["loop_details"][0]
        assert loop["type"] == "for"
        assert loop["nesting_level"] == 1
        assert loop["operations_count"] >= 1

    def test_two_sequential_for_loops(self):
        pseudocode = """
        for i 🡨 0 to n do
        begin
            suma 🡨 suma + i
        end

        for j 🡨 0 to n do
        begin
            suma 🡨 suma + j
        end
        """
        controller = ControlIterative()
        results = controller.analyze_from_parsed_tree("DosFor", pseudocode)
        assert results["analysis"]["loops_detected"] == 2
        assert results["analysis"]["nested_levels"] == 1
        assert len(results["analysis"]["loop_details"]) == 2
        types = {ld["type"] for ld in results["analysis"]["loop_details"]}
        assert "for" in types

    def test_nested_for_loops(self):
        pseudocode = """
        for i 🡨 0 to n do
        begin
            for j 🡨 0 to n do
            begin
                matriz 🡨 0
            end
        end
        """
        controller = ControlIterative()
        results = controller.analyze_from_parsed_tree("NestedFor", pseudocode)
        assert results["analysis"]["loops_detected"] == 2
        assert results["analysis"]["nested_levels"] == 2
        assert len(results["analysis"]["loop_details"]) == 2
        # verificar que hay un loop con nesting_level 2
        assert any(ld["nesting_level"] == 2 for ld in results["analysis"]["loop_details"])

    def test_three_level_nested_loops(self):
        pseudocode = """
        for i 🡨 0 to n do
        begin
            for j 🡨 0 to n do
            begin
                for k 🡨 0 to n do
                begin
                    x 🡨 x + 1
                end
            end
        end
        """
        controller = ControlIterative()
        results = controller.analyze_from_parsed_tree("TresNiveles", pseudocode)
        assert results["analysis"]["loops_detected"] == 3
        assert results["analysis"]["nested_levels"] == 3
        assert results["complexity"]["time"]["worst_case"] in ["O(n³)", "O(n^3)"]

    def test_while_and_repeat_loops(self):
        pseudocode = """
        while (i < n) do
        begin
            suma 🡨 suma + array[i]
            i 🡨 i + 1
        end

        repeat
            suma 🡨 suma + array[i]
            i 🡨 i + 1
        until (i >= n)
        """
        controller = ControlIterative()
        results = controller.analyze_from_parsed_tree("WhileRepeat", pseudocode)
        assert results["analysis"]["loops_detected"] == 2
        assert results["analysis"]["nested_levels"] == 1
        types = {ld["type"] for ld in results["analysis"]["loop_details"]}
        assert "while" in types and "repeat" in types

    # """Suite de tests para el controlador iterativo."""
    
    # def setup_method(self):
    #     """Configuración antes de cada test."""
    #     self.controller = ControlIterative()
    
    # def test_inicializacion(self):
    #     """Test de inicialización del controlador."""
    #     assert self.controller.loops_detected == 0
    #     assert self.controller.nested_levels == 0
    #     assert self.controller.complexity is None
    #     assert self.controller.algorithm is None
    #     assert self.controller.loop_details == []
    
    # def test_analisis_ciclo_simple(self):
    #     """Test de análisis con un solo ciclo for."""
    #     pseudocodigo = """
    #     for i 🡨 0 to n do
    #     begin
    #         suma 🡨 suma + i
    #     end
    #     """
        
    #     results = self.controller.analyze_from_parsed_tree(
    #         "SumaSimple",
    #         pseudocodigo
    #     )
        
    #     assert results['analysis']['loops_detected'] == 1
    #     assert results['analysis']['nested_levels'] == 1
    #     assert results['complexity']['time']['worst_case'] == "O(n)"
    #     assert results['algorithm']['name'] == "SumaSimple"
    #     assert results['algorithm']['type'] == "Iterativo"
    
    # def test_analisis_ciclos_anidados(self):
    #     """Test de análisis con ciclos anidados."""
    #     pseudocodigo = """
    #     for i 🡨 0 to n do
    #     begin
    #         for j 🡨 0 to n do
    #         begin
    #             matriz[i][j] 🡨 0
    #         end
    #     end
    #     """
        
    #     results = self.controller.analyze_from_parsed_tree(
    #         "InicializarMatriz",
    #         pseudocodigo
    #     )
        
    #     assert results['analysis']['loops_detected'] == 2
    #     assert results['analysis']['nested_levels'] == 2
    #     assert results['complexity']['time']['worst_case'] == "O(n²)"
    
    # def test_analisis_while(self):
    #     """Test de análisis con ciclo while."""
    #     pseudocodigo = """
    #     while (i < n) do
    #     begin
    #         suma 🡨 suma + array[i]
    #         i 🡨 i + 1
    #     end
    #     """
        
    #     results = self.controller.analyze_from_parsed_tree(
    #         "SumaWhile",
    #         pseudocodigo
    #     )
        
    #     assert results['analysis']['loops_detected'] == 1
    #     assert results['analysis']['nested_levels'] == 1
    #     assert len(results['analysis']['loop_details']) == 1
    #     assert results['analysis']['loop_details'][0]['type'] == 'while'
    
    # def test_analisis_repeat(self):
    #     """Test de análisis con ciclo repeat."""
    #     pseudocodigo = """
    #     repeat
    #         suma 🡨 suma + array[i]
    #         i 🡨 i + 1
    #     until (i >= n)
    #     """
        
    #     results = self.controller.analyze_from_parsed_tree(
    #         "SumaRepeat",
    #         pseudocodigo
    #     )
        
    #     assert results['analysis']['loops_detected'] == 1
    #     assert results['analysis']['loop_details'][0]['type'] == 'repeat'
    
    # def test_deteccion_patron_lineal(self):
    #     """Test de detección de patrón lineal."""
    #     pseudocodigo = """
    #     for i 🡨 0 to n do
    #     begin
    #         x 🡨 x + 1
    #     end
    #     """
        
    #     results = self.controller.analyze_from_parsed_tree(
    #         "LinealSimple",
    #         pseudocodigo
    #     )
        
    #     pattern = results['pattern']
    #     assert "Lineal" in pattern['name'] or "Simple" in pattern['name']
    #     assert pattern['complexity_hint'] in ["O(n)", "O(n log n)"]
    
    # def test_deteccion_patron_cuadratico(self):
    #     """Test de detección de patrón cuadrático."""
    #     pseudocodigo = """
    #     for i 🡨 0 to n do
    #     begin
    #         for j 🡨 0 to n do
    #         begin
    #             suma 🡨 suma + matriz[i][j]
    #         end
    #     end
    #     """
        
    #     results = self.controller.analyze_from_parsed_tree(
    #         "PatronCuadratico",
    #         pseudocodigo
    #     )
        
    #     pattern = results['pattern']
    #     assert "Cuadrático" in pattern['name'] or "Matriz" in pattern['name']
    #     assert pattern['complexity_hint'] == "O(n²)"
    
    # def test_ciclos_tres_niveles(self):
    #     """Test con tres niveles de anidamiento."""
    #     pseudocodigo = """
    #     for i 🡨 0 to n do
    #     begin
    #         for j 🡨 0 to n do
    #         begin
    #             for k 🡨 0 to n do
    #             begin
    #                 x 🡨 x + 1
    #             end
    #         end
    #     end
    #     """
        
    #     results = self.controller.analyze_from_parsed_tree(
    #         "TresNiveles",
    #         pseudocodigo
    #     )
        
    #     assert results['analysis']['loops_detected'] == 3
    #     assert results['analysis']['nested_levels'] == 3
    #     assert results['complexity']['time']['worst_case'] == "O(n³)"
    
    # def test_sin_ciclos(self):
    #     """Test de algoritmo sin ciclos."""
    #     pseudocodigo = """
    #     x 🡨 5
    #     y 🡨 10
    #     z 🡨 x + y
    #     """
        
    #     results = self.controller.analyze_from_parsed_tree(
    #         "SinCiclos",
    #         pseudocodigo
    #     )
        
    #     assert results['analysis']['loops_detected'] == 0
    #     assert results['analysis']['nested_levels'] == 0
    #     assert results['complexity']['time']['worst_case'] == "O(1)"
    
    # def test_exportar_complejidad_texto(self):
    #     """Test de exportación en formato texto."""
    #     pseudocodigo = """
    #     for i 🡨 0 to n do
    #     begin
    #         suma 🡨 suma + i
    #     end
    #     """
        
    #     self.controller.analyze_from_parsed_tree("Test", pseudocodigo)
    #     report = self.controller.get_complexity_report("text")
        
    #     assert "Análisis de Complejidad" in report
    #     assert "O(n)" in report
    
    # def test_exportar_complejidad_json(self):
    #     """Test de exportación en formato JSON."""
    #     pseudocodigo = """
    #     for i 🡨 0 to n do
    #     begin
    #         suma 🡨 suma + i
    #     end
    #     """
        
    #     self.controller.analyze_from_parsed_tree("Test", pseudocodigo)
    #     report = self.controller.get_complexity_report("json")
        
    #     assert '"worst_case"' in report
    #     assert '"best_case"' in report
    #     assert '"time_complexity"' in report
    
    # def test_exportar_complejidad_markdown(self):
    #     """Test de exportación en formato Markdown."""
    #     pseudocodigo = """
    #     for i 🡨 0 to n do
    #     begin
    #         suma 🡨 suma + i
    #     end
    #     """
        
    #     self.controller.analyze_from_parsed_tree("Test", pseudocodigo)
    #     report = self.controller.get_complexity_report("markdown")
        
    #     assert "# Análisis de Complejidad" in report
    #     assert "**" in report  # Markdown bold
    #     assert "`" in report   # Markdown code
    
    # def test_resumen_ciclos(self):
    #     """Test del resumen de ciclos."""
    #     pseudocodigo = """
    #     for i 🡨 0 to n do
    #     begin
    #         for j 🡨 0 to m do
    #         begin
    #             x 🡨 x + 1
    #         end
    #     end
    #     """
        
    #     self.controller.analyze_from_parsed_tree("Test", pseudocodigo)
    #     summary = self.controller.get_loop_summary()
        
    #     assert "Total de ciclos: 2" in summary
    #     assert "Nivel máximo de anidamiento: 2" in summary
    #     assert "Nivel 0" in summary or "Nivel 1" in summary
    
    # def test_reset_controlador(self):
    #     """Test del método reset."""
    #     pseudocodigo = """
    #     for i 🡨 0 to n do
    #     begin
    #         x 🡨 x + 1
    #     end
    #     """
        
    #     self.controller.analyze_from_parsed_tree("Test", pseudocodigo)
        
    #     # Verificar que hay datos
    #     assert self.controller.loops_detected > 0
    #     assert self.controller.algorithm is not None
        
    #     # Reset
    #     self.controller.reset()
        
    #     # Verificar que se limpiaron los datos
    #     assert self.controller.loops_detected == 0
    #     assert self.controller.nested_levels == 0
    #     assert self.controller.complexity is None
    #     assert self.controller.algorithm is None
    #     assert self.controller.loop_details == []
    
    # def test_con_estructura_parseada(self):
    #     """Test usando estructura ya parseada."""
    #     pseudocodigo = """
    #     for i 🡨 0 to n do
    #     begin
    #         suma 🡨 suma + i
    #     end
    #     """
        
    #     # Parsear primero
    #     tree = parser.parse(pseudocodigo)
    #     transformer = TreeToDict()
    #     structure = transformer.transform(tree)
        
    #     # Analizar con estructura parseada
    #     results = self.controller.analyze_from_parsed_tree(
    #         "TestParsed",
    #         pseudocodigo,
    #         parsed_tree=tree,
    #         structure=structure
    #     )
        
    #     assert results['analysis']['loops_detected'] == 1
    #     assert results['algorithm']['name'] == "TestParsed"
    
    # def test_detalles_ciclo_for(self):
    #     """Test de detalles específicos de ciclo for."""
    #     pseudocodigo = """
    #     for contador 🡨 1 to 100 do
    #     begin
    #         suma 🡨 suma + contador
    #     end
    #     """
        
    #     results = self.controller.analyze_from_parsed_tree(
    #         "TestFor",
    #         pseudocodigo
    #     )
        
    #     loop_detail = results['analysis']['loop_details'][0]
    #     assert loop_detail['type'] == 'for'
    #     assert loop_detail['variable'] == 'contador'
    #     assert 'from' in loop_detail
    #     assert 'to' in loop_detail
    
    # def test_optimizaciones_sugeridas(self):
    #     """Test de sugerencias de optimización."""
    #     pseudocodigo = """
    #     for i 🡨 0 to n do
    #     begin
    #         for j 🡨 0 to n do
    #         begin
    #             x 🡨 x + matriz[i][j]
    #         end
    #     end
    #     """
        
    #     results = self.controller.analyze_from_parsed_tree(
    #         "TestOptim",
    #         pseudocodigo
    #     )
        
    #     # Debe haber optimizaciones sugeridas
    #     assert 'optimizations' in results
    #     # Para algoritmos cuadráticos, debería haber sugerencias
    #     if results['analysis']['nested_levels'] >= 2:
    #         assert len(results['optimizations']) > 0


# Ejecutar tests si se ejecuta directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

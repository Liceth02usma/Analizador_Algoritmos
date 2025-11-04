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


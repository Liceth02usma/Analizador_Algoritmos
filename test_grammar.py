#!/usr/bin/env python3
"""
Test script for the pseudocode grammar
Demonstrates parsing of basic control structures
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import Lexer
from parser import parse_pseudocode, ParseError
from ast_nodes import ASTPrinter


def test_lexer():
    """Test the lexer with sample code"""
    print("=== Testing Lexer ===")
    
    code = """
    ENTERO x = 5;
    SI x > 0 ENTONCES
        print("Positivo");
    FIN_SI
    """
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    print("Tokens:")
    for token in tokens:
        if token.type.name not in ['NEWLINE', 'EOF']:
            print(f"  {token.type.name}: '{token.value}' at line {token.line}")
    print()


def test_parser_simple():
    """Test parser with simple code"""
    print("=== Testing Parser - Simple Assignment ===")
    
    code = """
    ENTERO x = 5;
    x = x + 1;
    """
    
    try:
        ast = parse_pseudocode(code)
        printer = ASTPrinter()
        printer.visit(ast)
        print("✓ Parsing successful")
    except ParseError as e:
        print(f"✗ Parse error: {e}")
    print()


def test_parser_if():
    """Test parser with IF statement"""
    print("=== Testing Parser - IF Statement ===")
    
    code = """
    ENTERO x = 5;
    SI x > 0 ENTONCES
        print("Positivo");
    SINO
        print("No positivo");
    FIN_SI
    """
    
    try:
        ast = parse_pseudocode(code)
        printer = ASTPrinter()
        printer.visit(ast)
        print("✓ Parsing successful")
    except ParseError as e:
        print(f"✗ Parse error: {e}")
    print()


def test_parser_while():
    """Test parser with WHILE loop"""
    print("=== Testing Parser - WHILE Loop ===")
    
    code = """
    ENTERO i = 0;
    MIENTRAS i < 10 HACER
        i = i + 1;
    FIN_MIENTRAS
    """
    
    try:
        ast = parse_pseudocode(code)
        printer = ASTPrinter()
        printer.visit(ast)
        print("✓ Parsing successful")
    except ParseError as e:
        print(f"✗ Parse error: {e}")
    print()


def test_parser_for():
    """Test parser with FOR loop"""
    print("=== Testing Parser - FOR Loop ===")
    
    code = """
    ENTERO suma = 0;
    PARA i = 1 HASTA 10 HACER
        suma = suma + i;
    FIN_PARA
    """
    
    try:
        ast = parse_pseudocode(code)
        printer = ASTPrinter()
        printer.visit(ast)
        print("✓ Parsing successful")
    except ParseError as e:
        print(f"✗ Parse error: {e}")
    print()


def test_parser_english():
    """Test parser with English keywords"""
    print("=== Testing Parser - English Keywords ===")
    
    code = """
    int x = 5;
    IF x > 0 THEN
        print("Positive");
    ELSE
        print("Not positive");
    END_IF
    
    FOR i = 1 TO 10 DO
        x = x + i;
    END_FOR
    """
    
    try:
        ast = parse_pseudocode(code)
        printer = ASTPrinter()
        printer.visit(ast)
        print("✓ Parsing successful")
    except ParseError as e:
        print(f"✗ Parse error: {e}")
    print()


def test_example_files():
    """Test parsing example pseudocode files"""
    print("=== Testing Example Files ===")
    
    examples_dir = os.path.join(os.path.dirname(__file__), 'examples')
    
    for filename in os.listdir(examples_dir):
        if filename.endswith('.pseudo'):
            print(f"Testing {filename}:")
            filepath = os.path.join(examples_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                ast = parse_pseudocode(code)
                print(f"  ✓ Successfully parsed {filename}")
                
                # Print a simplified AST structure
                printer = ASTPrinter()
                printer.visit(ast)
                
            except ParseError as e:
                print(f"  ✗ Parse error in {filename}: {e}")
            except Exception as e:
                print(f"  ✗ Error reading {filename}: {e}")
            print()


if __name__ == "__main__":
    print("Pseudocode Grammar Test Suite")
    print("=" * 40)
    
    test_lexer()
    test_parser_simple()
    test_parser_if()
    test_parser_while()
    test_parser_for()
    test_parser_english()
    test_example_files()
    
    print("Test suite completed!")
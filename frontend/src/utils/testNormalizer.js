/**
 * Test file to verify data normalization works correctly
 * Run this in browser console or Node environment with the normalizer
 */

import { 
  detectAnalysisType, 
  normalizeAnalysisData, 
  getDiagrams 
} from './dataNormalizer';

// Mock iterative data structure
const iterativeData = {
  "type": "iterativo",
  "code_explain": "Bubble Sort es un algoritmo...",
  "complexity_line_to_line": "...",
  "explain_complexity": "Para el algoritmo Bubble Sort...",
  "asymptotic_notation": {
    "best": "Ω(n)",
    "worst": "O(n^2)",
    "explanation": "El algoritmo Bubble Sort tiene una complejidad..."
  },
  "algorithm_name": "Bubble Sort",
  "algorithm_category": "Iterativo / Bucle",
  "equation": [
    "Mejor: c1 + c2 + 2*c3 + c4 + n*c5 + (n-1)*c6 + c11 + c12",
    "Peor: c1 + c2 + (n+1)*c3 + n*c4 + (n*(n+1)/2)*c5..."
  ],
  "method_solution": "Método de Conteo de Pasos + Sumatorias",
  "solution_equation": [
    "Mejor: T(n) = (c5 + c6)n + ...",
    "Peor: T(n) = (0.5*c5 + 0.5*c6...)n^2 + ..."
  ],
  "extra": {
    "is_case_dependent": true,
    "cases": [
      {
        "case_name": "Mejor",
        "condition": "El arreglo ya está ordenado.",
        "raw_summation_str": "c1 + c2 + 2*c3 + c4 + n*c5 + (n-1)*c6 + c11 + c12",
        "simplified_complexity": "(c5 + c6)n + (c1 + c2 + 2*c3 + c4 - c6 + c11 + c12)",
        "complexity_class": "n",
        "notation_type": "Ω",
        "big_o": "Ω(n)",
        "line_analysis": [
          { "line": "1", "cost_constant": "c1", "execution_count": "1", "total_cost_expression": "c1" },
          { "line": "2", "cost_constant": "c2", "execution_count": "n", "total_cost_expression": "c2*n" }
        ],
        "trace_diagram": "graph TD\n    Start((Inicio)) --> InitVars[swapped = T, i = 0]..."
      },
      {
        "case_name": "Peor",
        "condition": "El arreglo está ordenado en orden inverso.",
        "raw_summation_str": "c1 + c2 + (n+1)*c3 + n*c4 + (n*(n+1)/2)*c5...",
        "simplified_complexity": "(0.5*c5 + 0.5*c6 + 0.5*c7 + 0.5*c8 + 0.5*c9 + 0.5*c10)n^2 + ...",
        "complexity_class": "n^2",
        "notation_type": "O",
        "big_o": "O(n^2)",
        "line_analysis": [
          { "line": "1", "cost_constant": "c1", "execution_count": "1", "total_cost_expression": "c1" }
        ],
        "trace_diagram": "graph TD\n    Start((Inicio)) --> InitVars[swapped = T, i = 0]..."
      }
    ]
  }
};

// Mock recursive data structure
const recursiveData = {
  "type": "Recursivo",
  "code_explain": "Este algoritmo calcula el n-ésimo número de Fibonacci...",
  "complexity_line_to_line": "=== MEJOR CASO ===\nfibonacci(n)...",
  "explain_complexity": "Mejor caso: La complejidad de este algoritmo...",
  "asymptotic_notation": {
    "explanation": "El algoritmo tiene una complejidad temporal de O(exp(0.481...))...",
    "best": "Ω(exp(0.481...))",
    "worst": "O(exp(0.481...))",
    "average": "Θ(exp(0.481...))"
  },
  "algorithm_name": "Fibonacci",
  "algorithm_category": "Recursivo",
  "equation": [
    "T(n) = T(n-1) + T(n-2), T(0) = 1, T(1) = 1",
    "T(n) = T(n-1) + T(n-2), T(0) = 1, T(1) = 1",
    "T(n) = T(n-1) + T(n-2), T(0) = 1, T(1) = 1"
  ],
  "method_solution": [
    "equation_characteristics",
    "equation_characteristics",
    "equation_characteristics"
  ],
  "solution_equation": ["1.618^n", "1.618^n", "1.618^n"],
  "explain_solution_steps": [
    {
      "case_type": "best_case",
      "equation": "T(n) = T(n-1) + T(n-2), T(0) = 1, T(1) = 1",
      "method": "equation_characteristics",
      "complexity": "1.618^n",
      "steps": ["La herramienta SymPy reportó un error..."],
      "explanation": "La herramienta SymPy reportó un error en el cálculo simbólico...",
      "classification_confidence": 0.9,
      "classification_reasoning": "Recurrencia lineal de orden superior..."
    },
    {
      "case_type": "worst_case",
      "equation": "T(n) = T(n-1) + T(n-2), T(0) = 1, T(1) = 1",
      "method": "equation_characteristics",
      "complexity": "1.618^n",
      "steps": ["La herramienta SymPy reportó un error..."],
      "explanation": "La herramienta SymPy reportó un error en el cálculo simbólico...",
      "classification_confidence": 0.9,
      "classification_reasoning": "Recurrencia lineal de orden superior..."
    }
  ],
  "diagrams": {
    "tree_method_best_case": "graph TD\n    T0_L0_P0((\"T(n)\"))...",
    "tree_method_worst_case": "graph TD\n    T0_L0_P0((\"T(n)\"))..."
  }
};

// Test detection
console.log('=== Testing Detection ===');
console.log('Iterative type:', detectAnalysisType(iterativeData)); // Should be 'iterative'
console.log('Recursive type:', detectAnalysisType(recursiveData)); // Should be 'recursive'

// Test normalization
console.log('\n=== Testing Normalization ===');
const normalizedIterative = normalizeAnalysisData(iterativeData);
const normalizedRecursive = normalizeAnalysisData(recursiveData);

console.log('Normalized iterative has explain_solution_steps:', 
  Array.isArray(normalizedIterative.explain_solution_steps));
console.log('Normalized iterative steps count:', 
  normalizedIterative.explain_solution_steps?.length);
console.log('First step case_type:', 
  normalizedIterative.explain_solution_steps?.[0]?.case_type);

console.log('\nNormalized recursive has explain_solution_steps:', 
  Array.isArray(normalizedRecursive.explain_solution_steps));
console.log('Normalized recursive steps count:', 
  normalizedRecursive.explain_solution_steps?.length);

// Test diagram extraction
console.log('\n=== Testing Diagram Extraction ===');
const iterativeDiagrams = getDiagrams(iterativeData, normalizedIterative);
const recursiveDiagrams = getDiagrams(recursiveData, normalizedRecursive);

console.log('Iterative diagrams keys:', Object.keys(iterativeDiagrams));
console.log('Recursive diagrams keys:', Object.keys(recursiveDiagrams));

// Test that both formats produce compatible structures
console.log('\n=== Testing Compatibility ===');
const iterativeStep = normalizedIterative.explain_solution_steps[0];
const recursiveStep = normalizedRecursive.explain_solution_steps[0];

console.log('Both have case_type:', 
  !!iterativeStep.case_type, !!recursiveStep.case_type);
console.log('Both have equation:', 
  !!iterativeStep.equation, !!recursiveStep.equation);
console.log('Both have complexity:', 
  !!iterativeStep.complexity, !!recursiveStep.complexity);

// Iterative has unique fields
console.log('\nIterative unique fields:');
console.log('  - condition:', !!iterativeStep.condition);
console.log('  - big_o:', !!iterativeStep.big_o);
console.log('  - line_analysis:', !!iterativeStep.line_analysis);
console.log('  - trace_diagram:', !!iterativeStep.trace_diagram);

// Recursive has unique fields
console.log('\nRecursive unique fields:');
console.log('  - classification_reasoning:', !!recursiveStep.classification_reasoning);
console.log('  - steps array:', Array.isArray(recursiveStep.steps));

console.log('\n✅ All tests completed!');

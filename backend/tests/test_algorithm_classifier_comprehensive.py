"""
Suite de Pruebas Exhaustivas para AlgorithmClassifier
Niveles de dificultad: BÁSICO, INTERMEDIO, AVANZADO, EXTREMO
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.controllers.algorithm_type_controller import AlgorithmClassifier


# ============================================================================
# 🟢 NIVEL BÁSICO - Casos Simples y Claros
# ============================================================================

def test_basico_1_fibonacci_recursivo():
    """✅ RECURSIVO - Fibonacci clásico (recursión directa doble)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'fibonacci',
        'params': ['n'],
        'body': [
            {'type': 'if', 'cond': {'lhs': 'n', 'op': '<=', 'rhs': 1},
             'then': [{'type': 'return', 'value': 'n'}],
             'else': [
                 {'type': 'call', 'name': 'fibonacci', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}]},
                 {'type': 'call', 'name': 'fibonacci', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 2}]}
             ]}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo", f"❌ Esperado: recursivo, Obtenido: {result['algorithm_type']}"
    assert result["has_recursion"] == True
    assert "fibonacci" in result["recursive_functions"]
    print(f"✅ BÁSICO-1: Fibonacci → {result['algorithm_type'].upper()}")
    return True


def test_basico_2_factorial_recursivo():
    """✅ RECURSIVO - Factorial (recursión simple lineal)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'factorial',
        'params': ['n'],
        'body': [
            {'type': 'if', 'cond': {'lhs': 'n', 'op': '<=', 'rhs': 1},
             'then': [{'type': 'return', 'value': 1}],
             'else': [
                 {'type': 'return', 'value': {
                     'op': '*', 
                     'lhs': 'n', 
                     'rhs': {'type': 'call', 'name': 'factorial', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}]}
                 }}
             ]}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ BÁSICO-2: Factorial → {result['algorithm_type'].upper()}")
    return True


def test_basico_3_bubble_sort_iterativo():
    """✅ ITERATIVO - Bubble Sort (bucles anidados sin recursión)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'bubbleSort',
        'params': ['arr', 'n'],
        'body': [
            {'type': 'for_loop', 'var': 'i', 'start': 0, 'end': 'n',
             'body': [
                 {'type': 'for_loop', 'var': 'j', 'start': 0, 'end': {'op': '-', 'lhs': 'n', 'rhs': 'i'},
                  'body': [
                      {'type': 'if', 'cond': {'op': '>', 'lhs': 'arr[j]', 'rhs': 'arr[j+1]'},
                       'then': [{'type': 'call', 'name': 'swap', 'args': ['arr[j]', 'arr[j+1]']}]}
                  ]}
             ]}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "iterativo"
    assert result["has_recursion"] == False
    print(f"✅ BÁSICO-3: Bubble Sort → {result['algorithm_type'].upper()}")
    return True


def test_basico_4_linear_search_iterativo():
    """✅ ITERATIVO - Búsqueda lineal (un solo bucle)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'linearSearch',
        'params': ['arr', 'n', 'target'],
        'body': [
            {'type': 'for_loop', 'var': 'i', 'start': 0, 'end': 'n',
             'body': [
                 {'type': 'if', 'cond': {'op': '==', 'lhs': 'arr[i]', 'rhs': 'target'},
                  'then': [{'type': 'return', 'value': 'i'}]}
             ]},
            {'type': 'return', 'value': -1}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "iterativo"
    print(f"✅ BÁSICO-4: Linear Search → {result['algorithm_type'].upper()}")
    return True


def test_basico_5_secuencial_iterativo():
    """✅ ITERATIVO - Swap (sin bucles ni recursión, solo asignaciones)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'swap',
        'params': ['a', 'b'],
        'body': [
            {'type': 'assign', 'lvalue': 'temp', 'value': 'a'},
            {'type': 'assign', 'lvalue': 'a', 'value': 'b'},
            {'type': 'assign', 'lvalue': 'b', 'value': 'temp'}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "iterativo"
    print(f"✅ BÁSICO-5: Swap Secuencial → {result['algorithm_type'].upper()}")
    return True


# ============================================================================
# 🟡 NIVEL INTERMEDIO - Casos con Combinaciones
# ============================================================================

def test_intermedio_1_binary_search_recursivo():
    """✅ RECURSIVO - Binary Search recursivo (divide y conquista)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'binarySearch',
        'params': ['arr', 'target', 'left', 'right'],
        'body': [
            {'type': 'if', 'cond': {'op': '>', 'lhs': 'left', 'rhs': 'right'},
             'then': [{'type': 'return', 'value': -1}]},
            {'type': 'assign', 'lvalue': 'mid', 'value': {'op': '//', 'lhs': {'op': '+', 'lhs': 'left', 'rhs': 'right'}, 'rhs': 2}},
            {'type': 'if', 'cond': {'op': '==', 'lhs': 'arr[mid]', 'rhs': 'target'},
             'then': [{'type': 'return', 'value': 'mid'}],
             'else': [
                 {'type': 'if', 'cond': {'op': '>', 'lhs': 'arr[mid]', 'rhs': 'target'},
                  'then': [{'type': 'return', 'value': {'type': 'call', 'name': 'binarySearch', 'args': ['arr', 'target', 'left', {'op': '-', 'lhs': 'mid', 'rhs': 1}]}}],
                  'else': [{'type': 'return', 'value': {'type': 'call', 'name': 'binarySearch', 'args': ['arr', 'target', {'op': '+', 'lhs': 'mid', 'rhs': 1}, 'right']}}]}
             ]}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ INTERMEDIO-1: Binary Search Recursivo → {result['algorithm_type'].upper()}")
    return True


def test_intermedio_2_merge_sort_recursivo():
    """✅ RECURSIVO - Merge Sort (recursión + bucles internos)"""
    ast = [
        {
            'type': 'procedure_def',
            'name': 'mergeSort',
            'params': ['arr', 'left', 'right'],
            'body': [
                {'type': 'if', 'cond': {'op': '<', 'lhs': 'left', 'rhs': 'right'},
                 'then': [
                     {'type': 'assign', 'lvalue': 'mid', 'value': {'op': '//', 'lhs': {'op': '+', 'lhs': 'left', 'rhs': 'right'}, 'rhs': 2}},
                     {'type': 'call', 'name': 'mergeSort', 'args': ['arr', 'left', 'mid']},
                     {'type': 'call', 'name': 'mergeSort', 'args': ['arr', {'op': '+', 'lhs': 'mid', 'rhs': 1}, 'right']},
                     {'type': 'call', 'name': 'merge', 'args': ['arr', 'left', 'mid', 'right']}
                 ]}
            ]
        },
        {
            'type': 'procedure_def',
            'name': 'merge',
            'params': ['arr', 'left', 'mid', 'right'],
            'body': [
                {'type': 'while_loop', 'cond': {'op': 'and', 'lhs': {'op': '<', 'lhs': 'i', 'rhs': 'n1'}, 'rhs': {'op': '<', 'lhs': 'j', 'rhs': 'n2'}},
                 'body': [{'type': 'assign', 'lvalue': 'arr[k]', 'value': 'L[i]'}]}
            ]
        }
    ]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ INTERMEDIO-2: Merge Sort → {result['algorithm_type'].upper()} (recursión domina sobre bucles)")
    return True


def test_intermedio_3_quick_sort_recursivo():
    """✅ RECURSIVO - Quick Sort (recursión doble + bucle de partición)"""
    ast = [
        {
            'type': 'procedure_def',
            'name': 'quickSort',
            'params': ['arr', 'low', 'high'],
            'body': [
                {'type': 'if', 'cond': {'op': '<', 'lhs': 'low', 'rhs': 'high'},
                 'then': [
                     {'type': 'assign', 'lvalue': 'pivot', 'value': {'type': 'call', 'name': 'partition', 'args': ['arr', 'low', 'high']}},
                     {'type': 'call', 'name': 'quickSort', 'args': ['arr', 'low', {'op': '-', 'lhs': 'pivot', 'rhs': 1}]},
                     {'type': 'call', 'name': 'quickSort', 'args': ['arr', {'op': '+', 'lhs': 'pivot', 'rhs': 1}, 'high']}
                 ]}
            ]
        },
        {
            'type': 'procedure_def',
            'name': 'partition',
            'params': ['arr', 'low', 'high'],
            'body': [
                {'type': 'for_loop', 'var': 'j', 'start': 'low', 'end': {'op': '-', 'lhs': 'high', 'rhs': 1},
                 'body': [{'type': 'assign', 'lvalue': 'i', 'value': {'op': '+', 'lhs': 'i', 'rhs': 1}}]},
                {'type': 'return', 'value': 'i+1'}
            ]
        }
    ]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ INTERMEDIO-3: Quick Sort → {result['algorithm_type'].upper()}")
    return True


def test_intermedio_4_towers_hanoi_recursivo():
    """✅ RECURSIVO - Torres de Hanoi (recursión múltiple)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'hanoi',
        'params': ['n', 'origen', 'destino', 'auxiliar'],
        'body': [
            {'type': 'if', 'cond': {'op': '==', 'lhs': 'n', 'rhs': 1},
             'then': [{'type': 'print', 'value': 'mover disco'}],
             'else': [
                 {'type': 'call', 'name': 'hanoi', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}, 'origen', 'auxiliar', 'destino']},
                 {'type': 'print', 'value': 'mover disco'},
                 {'type': 'call', 'name': 'hanoi', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}, 'auxiliar', 'destino', 'origen']}
             ]}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ INTERMEDIO-4: Torres de Hanoi → {result['algorithm_type'].upper()}")
    return True


def test_intermedio_5_suma_arreglo_recursivo():
    """✅ RECURSIVO - Suma de arreglo (recursión tail-call)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'sumaArreglo',
        'params': ['arr', 'n'],
        'body': [
            {'type': 'if', 'cond': {'op': '==', 'lhs': 'n', 'rhs': 0},
             'then': [{'type': 'return', 'value': 0}],
             'else': [
                 {'type': 'return', 'value': {
                     'op': '+',
                     'lhs': 'arr[n-1]',
                     'rhs': {'type': 'call', 'name': 'sumaArreglo', 'args': ['arr', {'op': '-', 'lhs': 'n', 'rhs': 1}]}
                 }}
             ]}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ INTERMEDIO-5: Suma Arreglo Recursivo → {result['algorithm_type'].upper()}")
    return True


# ============================================================================
# 🟠 NIVEL AVANZADO - Recursión Indirecta y Casos Complejos
# ============================================================================

def test_avanzado_1_recursion_mutua():
    """✅ RECURSIVO - isEven/isOdd (recursión mutua/indirecta)"""
    ast = [
        {
            'type': 'procedure_def',
            'name': 'isEven',
            'params': ['n'],
            'body': [
                {'type': 'if', 'cond': {'op': '==', 'lhs': 'n', 'rhs': 0},
                 'then': [{'type': 'return', 'value': True}],
                 'else': [{'type': 'return', 'value': {'type': 'call', 'name': 'isOdd', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}]}}]}
            ]
        },
        {
            'type': 'procedure_def',
            'name': 'isOdd',
            'params': ['n'],
            'body': [
                {'type': 'if', 'cond': {'op': '==', 'lhs': 'n', 'rhs': 0},
                 'then': [{'type': 'return', 'value': False}],
                 'else': [{'type': 'return', 'value': {'type': 'call', 'name': 'isEven', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}]}}]}
            ]
        }
    ]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    assert len(result["recursive_functions"]) >= 1  # Al menos una función debe estar marcada
    print(f"✅ AVANZADO-1: Recursión Mutua (isEven/isOdd) → {result['algorithm_type'].upper()}")
    return True


def test_avanzado_2_ackermann_recursivo():
    """✅ RECURSIVO - Función de Ackermann (recursión anidada compleja)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'ackermann',
        'params': ['m', 'n'],
        'body': [
            {'type': 'if', 'cond': {'op': '==', 'lhs': 'm', 'rhs': 0},
             'then': [{'type': 'return', 'value': {'op': '+', 'lhs': 'n', 'rhs': 1}}],
             'else': [
                 {'type': 'if', 'cond': {'op': '==', 'lhs': 'n', 'rhs': 0},
                  'then': [{'type': 'return', 'value': {'type': 'call', 'name': 'ackermann', 'args': [{'op': '-', 'lhs': 'm', 'rhs': 1}, 1]}}],
                  'else': [
                      {'type': 'return', 'value': {
                          'type': 'call', 
                          'name': 'ackermann', 
                          'args': [
                              {'op': '-', 'lhs': 'm', 'rhs': 1},
                              {'type': 'call', 'name': 'ackermann', 'args': ['m', {'op': '-', 'lhs': 'n', 'rhs': 1}]}
                          ]
                      }}
                  ]}
             ]}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ AVANZADO-2: Ackermann → {result['algorithm_type'].upper()}")
    return True


def test_avanzado_3_recursion_triple_cadena():
    """✅ RECURSIVO - Recursión indirecta en cadena (A→B→C→A)"""
    ast = [
        {
            'type': 'procedure_def',
            'name': 'funcA',
            'params': ['n'],
            'body': [
                {'type': 'if', 'cond': {'op': '>', 'lhs': 'n', 'rhs': 0},
                 'then': [{'type': 'call', 'name': 'funcB', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}]}]}
            ]
        },
        {
            'type': 'procedure_def',
            'name': 'funcB',
            'params': ['n'],
            'body': [
                {'type': 'if', 'cond': {'op': '>', 'lhs': 'n', 'rhs': 0},
                 'then': [{'type': 'call', 'name': 'funcC', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}]}]}
            ]
        },
        {
            'type': 'procedure_def',
            'name': 'funcC',
            'params': ['n'],
            'body': [
                {'type': 'if', 'cond': {'op': '>', 'lhs': 'n', 'rhs': 0},
                 'then': [{'type': 'call', 'name': 'funcA', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}]}]}
            ]
        }
    ]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ AVANZADO-3: Recursión Triple Cadena (A→B→C→A) → {result['algorithm_type'].upper()}")
    return True


def test_avanzado_4_dfs_grafo_recursivo():
    """✅ RECURSIVO - DFS en grafo (recursión con bucle interno)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'dfs',
        'params': ['grafo', 'nodo', 'visitados'],
        'body': [
            {'type': 'assign', 'lvalue': 'visitados[nodo]', 'value': True},
            {'type': 'for_loop', 'var': 'vecino', 'start': 0, 'end': 'len(grafo[nodo])',
             'body': [
                 {'type': 'if', 'cond': {'op': 'not', 'value': 'visitados[vecino]'},
                  'then': [{'type': 'call', 'name': 'dfs', 'args': ['grafo', 'vecino', 'visitados']}]}
             ]}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ AVANZADO-4: DFS Grafo → {result['algorithm_type'].upper()} (recursión + bucle)")
    return True


def test_avanzado_5_permutaciones_recursivo():
    """✅ RECURSIVO - Generador de permutaciones (backtracking)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'permute',
        'params': ['arr', 'l', 'r'],
        'body': [
            {'type': 'if', 'cond': {'op': '==', 'lhs': 'l', 'rhs': 'r'},
             'then': [{'type': 'print', 'value': 'arr'}],
             'else': [
                 {'type': 'for_loop', 'var': 'i', 'start': 'l', 'end': 'r',
                  'body': [
                      {'type': 'call', 'name': 'swap', 'args': ['arr[l]', 'arr[i]']},
                      {'type': 'call', 'name': 'permute', 'args': ['arr', {'op': '+', 'lhs': 'l', 'rhs': 1}, 'r']},
                      {'type': 'call', 'name': 'swap', 'args': ['arr[l]', 'arr[i]']}
                  ]}
             ]}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ AVANZADO-5: Permutaciones (Backtracking) → {result['algorithm_type'].upper()}")
    return True


# ============================================================================
# 🔴 NIVEL EXTREMO - Casos Edge y Ambiguos
# ============================================================================

def test_extremo_1_funcion_vacia():
    """✅ ITERATIVO - Función vacía (sin código)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'empty',
        'params': [],
        'body': []
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "iterativo"  # Por defecto, sin recursión = iterativo
    print(f"✅ EXTREMO-1: Función Vacía → {result['algorithm_type'].upper()}")
    return True


def test_extremo_2_solo_return():
    """✅ ITERATIVO - Solo return (sin recursión)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'getConstant',
        'params': [],
        'body': [
            {'type': 'return', 'value': 42}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "iterativo"
    print(f"✅ EXTREMO-2: Solo Return → {result['algorithm_type'].upper()}")
    return True


def test_extremo_3_bucles_multiples_iterativo():
    """✅ ITERATIVO - Bucles múltiples secuenciales (sin recursión)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'multipleLoops',
        'params': ['n'],
        'body': [
            {'type': 'for_loop', 'var': 'i', 'start': 0, 'end': 'n',
             'body': [{'type': 'print', 'value': 'i'}]},
            {'type': 'while_loop', 'cond': {'op': '>', 'lhs': 'n', 'rhs': 0},
             'body': [{'type': 'assign', 'lvalue': 'n', 'value': {'op': '-', 'lhs': 'n', 'rhs': 1}}]},
            {'type': 'repeat_loop', 'body': [{'type': 'print', 'value': 'done'}],
             'until': {'op': 'true'}}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "iterativo"
    print(f"✅ EXTREMO-3: Bucles Múltiples Secuenciales → {result['algorithm_type'].upper()}")
    return True


def test_extremo_4_llamadas_externas_iterativo():
    """✅ ITERATIVO - Llamadas a funciones externas (no recursivas)"""
    ast = [
        {
            'type': 'procedure_def',
            'name': 'main',
            'params': ['arr'],
            'body': [
                {'type': 'call', 'name': 'print', 'args': ['arr']},
                {'type': 'call', 'name': 'sort', 'args': ['arr']},
                {'type': 'call', 'name': 'print', 'args': ['arr']},
                {'type': 'for_loop', 'var': 'i', 'start': 0, 'end': 'len(arr)',
                 'body': [{'type': 'call', 'name': 'process', 'args': ['arr[i]']}]}
            ]
        }
    ]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "iterativo"
    print(f"✅ EXTREMO-4: Llamadas Externas → {result['algorithm_type'].upper()} (no son auto-recursivas)")
    return True


def test_extremo_5_recursion_condicional_compleja():
    """✅ RECURSIVO - Recursión condicional anidada"""
    ast = [{
        'type': 'procedure_def',
        'name': 'complexRecursive',
        'params': ['n', 'flag'],
        'body': [
            {'type': 'if', 'cond': {'op': '==', 'lhs': 'n', 'rhs': 0},
             'then': [{'type': 'return', 'value': 0}]},
            {'type': 'if', 'cond': 'flag',
             'then': [
                 {'type': 'for_loop', 'var': 'i', 'start': 0, 'end': 'n',
                  'body': [
                      {'type': 'if', 'cond': {'op': '==', 'lhs': {'op': '%', 'lhs': 'i', 'rhs': 2}, 'rhs': 0},
                       'then': [{'type': 'call', 'name': 'complexRecursive', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}, False]}]}
                  ]}
             ],
             'else': [
                 {'type': 'while_loop', 'cond': {'op': '>', 'lhs': 'n', 'rhs': 10},
                  'body': [
                      {'type': 'call', 'name': 'complexRecursive', 'args': [{'op': '//', 'lhs': 'n', 'rhs': 2}, True]}
                  ]}
             ]},
            {'type': 'return', 'value': 'n'}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ EXTREMO-5: Recursión Condicional Compleja → {result['algorithm_type'].upper()}")
    return True


def test_extremo_6_floyd_warshall_iterativo():
    """✅ ITERATIVO - Floyd-Warshall (triple bucle anidado, sin recursión)"""
    ast = [{
        'type': 'procedure_def',
        'name': 'floydWarshall',
        'params': ['graph', 'V'],
        'body': [
            {'type': 'for_loop', 'var': 'k', 'start': 0, 'end': 'V',
             'body': [
                 {'type': 'for_loop', 'var': 'i', 'start': 0, 'end': 'V',
                  'body': [
                      {'type': 'for_loop', 'var': 'j', 'start': 0, 'end': 'V',
                       'body': [
                           {'type': 'if', 'cond': {'op': '>', 'lhs': 'graph[i][j]', 'rhs': 'graph[i][k] + graph[k][j]'},
                            'then': [{'type': 'assign', 'lvalue': 'graph[i][j]', 'value': 'graph[i][k] + graph[k][j]'}]}
                       ]}
                  ]}
             ]}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "iterativo"
    print(f"✅ EXTREMO-6: Floyd-Warshall → {result['algorithm_type'].upper()} (3 bucles, 0 recursión)")
    return True


# ============================================================================
# 🎯 RUNNER DE TESTS
# ============================================================================

def run_all_tests():
    """Ejecuta todas las pruebas organizadas por nivel"""
    
    print("=" * 80)
    print("🧪 SUITE EXHAUSTIVA DE PRUEBAS - ALGORITHM CLASSIFIER")
    print("=" * 80)
    print()
    
    tests = {
        "🟢 NIVEL BÁSICO": [
            test_basico_1_fibonacci_recursivo,
            test_basico_2_factorial_recursivo,
            test_basico_3_bubble_sort_iterativo,
            test_basico_4_linear_search_iterativo,
            test_basico_5_secuencial_iterativo,
        ],
        "🟡 NIVEL INTERMEDIO": [
            test_intermedio_1_binary_search_recursivo,
            test_intermedio_2_merge_sort_recursivo,
            test_intermedio_3_quick_sort_recursivo,
            test_intermedio_4_towers_hanoi_recursivo,
            test_intermedio_5_suma_arreglo_recursivo,
        ],
        "🟠 NIVEL AVANZADO": [
            test_avanzado_1_recursion_mutua,
            test_avanzado_2_ackermann_recursivo,
            test_avanzado_3_recursion_triple_cadena,
            test_avanzado_4_dfs_grafo_recursivo,
            test_avanzado_5_permutaciones_recursivo,
        ],
        "🔴 NIVEL EXTREMO": [
            test_extremo_1_funcion_vacia,
            test_extremo_2_solo_return,
            test_extremo_3_bucles_multiples_iterativo,
            test_extremo_4_llamadas_externas_iterativo,
            test_extremo_5_recursion_condicional_compleja,
            test_extremo_6_floyd_warshall_iterativo,
        ]
    }
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for level, test_list in tests.items():
        print(f"\n{level}")
        print("-" * 80)
        
        for test_func in test_list:
            total_tests += 1
            try:
                test_func()
                passed_tests += 1
            except AssertionError as e:
                failed_tests.append((test_func.__name__, str(e)))
                print(f"❌ {test_func.__name__}: {e}")
            except Exception as e:
                failed_tests.append((test_func.__name__, f"Error: {str(e)}"))
                print(f"💥 {test_func.__name__}: Error inesperado - {e}")
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 80)
    print(f"✅ Tests pasados: {passed_tests}/{total_tests}")
    print(f"❌ Tests fallidos: {len(failed_tests)}/{total_tests}")
    print(f"📈 Tasa de éxito: {100 * passed_tests / total_tests:.1f}%")
    
    if failed_tests:
        print("\n🔍 TESTS FALLIDOS:")
        for name, error in failed_tests:
            print(f"   ❌ {name}: {error}")
    else:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
    
    print("=" * 80)
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

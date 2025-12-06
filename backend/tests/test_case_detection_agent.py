"""
Suite de Pruebas para CaseDetectionAgent
Valida la detección de múltiples casos vs caso general en algoritmos recursivos
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv

    env_path = root_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from app.models.recursive.case_detection_agent import CaseDetectionAgent


# ============================================================================
# 🟢 CASOS BÁSICOS - Algoritmos Simples y Claros
# ============================================================================


def test_caso_basico_1_fibonacci():
    """
    ❌ CASO GENERAL - Fibonacci
    Siempre hace las mismas 2 llamadas recursivas, sin variación
    """
    pseudocode = """
fibonacci(n)
begin
    if (n <= 1) then
        return n
    else
        return fibonacci(n-1) + fibonacci(n-2)
    end
end
"""

    ast_structure = {
        "type": "procedure_def",
        "name": "fibonacci",
        "body": [
            {"type": "if", "condition": "n <= 1"},
            {"type": "call", "name": "fibonacci"},
            {"type": "call", "name": "fibonacci"},
        ],
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode, ast_structure=ast_structure, algorithm_name="Fibonacci"
    )

    expected = False  # Caso general
    status = "✅ CORRECTO" if result == expected else "❌ INCORRECTO"
    print(f"{status} | Fibonacci → Múltiples casos: {result} (esperado: {expected})")
    return result == expected


def test_caso_basico_2_factorial():
    """
    ❌ CASO GENERAL - Factorial
    Siempre ejecuta n llamadas recursivas linealmente
    """
    pseudocode = """
factorial(n)
begin
    if (n <= 1) then
        return 1
    else
        return n * factorial(n - 1)
    end
end
"""

    ast_structure = {
        "type": "procedure_def",
        "name": "factorial",
        "body": [
            {"type": "if", "condition": "n <= 1"},
            {"type": "call", "name": "factorial"},
        ],
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode, ast_structure=ast_structure, algorithm_name="Factorial"
    )

    expected = False
    status = "✅ CORRECTO" if result == expected else "❌ INCORRECTO"
    print(f"{status} | Factorial → Múltiples casos: {result} (esperado: {expected})")
    return result == expected


def test_caso_basico_3_torres_hanoi():
    """
    ❌ CASO GENERAL - Torres de Hanoi
    Siempre hace exactamente 2^n - 1 movimientos
    """
    pseudocode = """
hanoi(n, origen, destino, auxiliar)
begin
    if (n = 1) then
        mover disco de origen a destino
        return
    end
    
    hanoi(n - 1, origen, auxiliar, destino)
    mover disco de origen a destino
    hanoi(n - 1, auxiliar, destino, origen)
end
"""

    ast_structure = {
        "type": "procedure_def",
        "name": "hanoi",
        "body": [
            {"type": "if", "condition": "n = 1"},
            {"type": "call", "name": "hanoi"},
            {"type": "call", "name": "hanoi"},
        ],
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode,
        ast_structure=ast_structure,
        algorithm_name="Torres de Hanoi",
    )

    expected = False
    status = "✅ CORRECTO" if result == expected else "❌ INCORRECTO"
    print(
        f"{status} | Torres de Hanoi → Múltiples casos: {result} (esperado: {expected})"
    )
    return result == expected


# ============================================================================
# 🟡 CASOS INTERMEDIOS - Algoritmos con Condiciones Variables
# ============================================================================


def test_caso_intermedio_1_binary_search():
    """
    ✅ MÚLTIPLES CASOS - Binary Search
    Mejor caso: O(1) encuentra inmediatamente
    Peor caso: O(log n) no encuentra o está en extremo
    """
    pseudocode = """
binarySearch(arr, objetivo, inicio, fin)
begin
    if (inicio > fin) then
        return -1
    end
    
    medio ← (inicio + fin) / 2
    
    if (arr[medio] = objetivo) then
        return medio  // ← RETORNO TEMPRANO (mejor caso)
    else if (arr[medio] > objetivo) then
        return binarySearch(arr, objetivo, inicio, medio - 1)
    else
        return binarySearch(arr, objetivo, medio + 1, fin)
    end
end
"""

    ast_structure = {
        "type": "procedure_def",
        "name": "binarySearch",
        "body": [
            {"type": "if", "condition": "inicio > fin", "has_early_return": True},
            {
                "type": "if",
                "condition": "arr[medio] = objetivo",
                "has_early_return": True,
            },
            {"type": "call", "name": "binarySearch"},
        ],
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode,
        ast_structure=ast_structure,
        algorithm_name="Binary Search",
    )

    expected = True  # Tiene múltiples casos
    status = "✅ CORRECTO" if result == expected else "❌ INCORRECTO"
    print(
        f"{status} | Binary Search → Múltiples casos: {result} (esperado: {expected})"
    )
    return result == expected


def test_caso_intermedio_2_quicksort():
    """
    ✅ MÚLTIPLES CASOS - QuickSort
    Mejor caso: O(n log n) pivote balanceado
    Peor caso: O(n²) pivote siempre mínimo/máximo
    """
    pseudocode = """
quickSort(arr, bajo, alto)
begin
    if (bajo < alto) then
        pivote ← partition(arr, bajo, alto)  // ← PIVOTE VARIABLE
        quickSort(arr, bajo, pivote - 1)
        quickSort(arr, pivote + 1, alto)
    end
end

partition(arr, bajo, alto)
begin
    pivote ← arr[alto]
    i ← bajo - 1
    for j ← bajo to alto - 1 do
        if (arr[j] <= pivote) then
            i ← i + 1
            intercambiar arr[i] con arr[j]
        end
    end
    intercambiar arr[i + 1] con arr[alto]
    return i + 1
end
"""

    ast_structure = {
        "type": "procedure_def",
        "name": "quickSort",
        "body": [
            {
                "type": "assign",
                "lvalue": "pivote",
                "note": "Pivote variable según datos",
            },
            {"type": "call", "name": "quickSort"},
            {"type": "call", "name": "quickSort"},
        ],
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode, ast_structure=ast_structure, algorithm_name="QuickSort"
    )

    expected = True
    status = "✅ CORRECTO" if result == expected else "❌ INCORRECTO"
    print(f"{status} | QuickSort → Múltiples casos: {result} (esperado: {expected})")
    return result == expected


def test_caso_intermedio_3_mergesort():
    """
    ❌ CASO GENERAL - MergeSort
    Siempre divide en mitades exactas, O(n log n) constante
    """
    pseudocode = """
mergeSort(arr, inicio, fin)
begin
    if (inicio < fin) then
        medio ← (inicio + fin) / 2  // ← DIVISIÓN CONSTANTE
        mergeSort(arr, inicio, medio)
        mergeSort(arr, medio + 1, fin)
        merge(arr, inicio, medio, fin)
    end
end
"""

    ast_structure = {
        "type": "procedure_def",
        "name": "mergeSort",
        "body": [
            {
                "type": "assign",
                "lvalue": "medio",
                "note": "División siempre balanceada",
            },
            {"type": "call", "name": "mergeSort"},
            {"type": "call", "name": "mergeSort"},
        ],
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode, ast_structure=ast_structure, algorithm_name="MergeSort"
    )

    expected = False
    status = "✅ CORRECTO" if result == expected else "❌ INCORRECTO"
    print(f"{status} | MergeSort → Múltiples casos: {result} (esperado: {expected})")
    return result == expected


# ============================================================================
# 🟠 CASOS AVANZADOS - Algoritmos con Patrones Complejos
# ============================================================================


def test_caso_avanzado_1_linear_search_recursivo():
    """
    ✅ MÚLTIPLES CASOS - Búsqueda Lineal Recursiva
    Mejor caso: O(1) encuentra al inicio
    Peor caso: O(n) no encuentra o está al final
    """
    pseudocode = """
linearSearchRecursive(arr, n, target, index)
begin
    if (index >= n) then
        return -1
    end
    
    if (arr[index] = target) then
        return index  // ← RETORNO TEMPRANO
    end
    
    return linearSearchRecursive(arr, n, target, index + 1)
end
"""

    ast_structure = {
        "type": "procedure_def",
        "name": "linearSearchRecursive",
        "body": [
            {
                "type": "if",
                "condition": "arr[index] = target",
                "has_early_return": True,
            },
            {"type": "call", "name": "linearSearchRecursive"},
        ],
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode,
        ast_structure=ast_structure,
        algorithm_name="Linear Search Recursivo",
    )

    expected = True
    status = "✅ CORRECTO" if result == expected else "❌ INCORRECTO"
    print(
        f"{status} | Linear Search Recursivo → Múltiples casos: {result} (esperado: {expected})"
    )
    return result == expected


def test_caso_avanzado_2_suma_arreglo():
    """
    ❌ CASO GENERAL - Suma de Arreglo Recursiva
    Siempre procesa todos los elementos, O(n) fijo
    """
    pseudocode = """
sumaArreglo(arr, n)
begin
    if (n = 0) then
        return 0
    else
        return arr[n-1] + sumaArreglo(arr, n - 1)
    end
end
"""

    ast_structure = {
        "type": "procedure_def",
        "name": "sumaArreglo",
        "body": [
            {"type": "if", "condition": "n = 0"},
            {"type": "call", "name": "sumaArreglo"},
        ],
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode,
        ast_structure=ast_structure,
        algorithm_name="Suma Arreglo",
    )

    expected = False
    status = "✅ CORRECTO" if result == expected else "❌ INCORRECTO"
    print(f"{status} | Suma Arreglo → Múltiples casos: {result} (esperado: {expected})")
    return result == expected


def test_caso_avanzado_3_busqueda_exponencial():
    """
    ✅ MÚLTIPLES CASOS - Búsqueda Exponencial
    Mejor caso: O(1) encuentra en las primeras posiciones
    Peor caso: O(log n) debe duplicar el rango varias veces
    """
    pseudocode = """
exponentialSearch(arr, n, target)
begin
    if (arr[0] = target) then
        return 0  // ← MEJOR CASO O(1)
    end
    
    i ← 1
    while (i < n and arr[i] <= target) do
        i ← i * 2  // ← CRECIMIENTO EXPONENCIAL
    end
    
    return binarySearch(arr, target, i/2, min(i, n-1))
end
"""

    ast_structure = {
        "type": "procedure_def",
        "name": "exponentialSearch",
        "body": [
            {"type": "if", "condition": "arr[0] = target", "has_early_return": True},
            {"type": "while", "condition": "i < n"},
            {"type": "call", "name": "binarySearch"},
        ],
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode,
        ast_structure=ast_structure,
        algorithm_name="Búsqueda Exponencial",
    )

    expected = True
    status = "✅ CORRECTO" if result == expected else "❌ INCORRECTO"
    print(
        f"{status} | Búsqueda Exponencial → Múltiples casos: {result} (esperado: {expected})"
    )
    return result == expected


# ============================================================================
# 🔴 CASOS EXTREMOS - Edge Cases y Algoritmos Especiales
# ============================================================================


def test_caso_extremo_1_ackermann():
    """
    ❌ CASO GENERAL - Función de Ackermann
    Crece extremadamente rápido, pero de forma determinista
    """
    pseudocode = """
ackermann(m, n)
begin
    if (m = 0) then
        return n + 1
    else if (n = 0) then
        return ackermann(m - 1, 1)
    else
        return ackermann(m - 1, ackermann(m, n - 1))
    end
end
"""

    ast_structure = {
        "type": "procedure_def",
        "name": "ackermann",
        "body": [
            {"type": "if", "condition": "m = 0"},
            {"type": "if", "condition": "n = 0"},
            {"type": "call", "name": "ackermann"},
            {"type": "call", "name": "ackermann"},
        ],
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode, ast_structure=ast_structure, algorithm_name="Ackermann"
    )

    expected = False
    status = "✅ CORRECTO" if result == expected else "❌ INCORRECTO"
    print(f"{status} | Ackermann → Múltiples casos: {result} (esperado: {expected})")
    return result == expected


def test_caso_extremo_2_interpolation_search():
    """
    ✅ MÚLTIPLES CASOS - Interpolation Search
    Mejor caso: O(log log n) con distribución uniforme
    Peor caso: O(n) con distribución no uniforme
    """
    pseudocode = """
interpolationSearch(arr, n, target)
begin
    low ← 0
    high ← n - 1
    
    while (low <= high and target >= arr[low] and target <= arr[high]) do
        if (arr[low] = target) then
            return low  // ← RETORNO TEMPRANO
        end
        
        // ← POSICIÓN ESTIMADA (varía según distribución)
        pos ← low + ((target - arr[low]) * (high - low)) / (arr[high] - arr[low])
        
        if (arr[pos] = target) then
            return pos
        else if (arr[pos] < target) then
            low ← pos + 1
        else
            high ← pos - 1
        end
    end
    
    return -1
end
"""

    ast_structure = {
        "type": "procedure_def",
        "name": "interpolationSearch",
        "body": [
            {
                "type": "assign",
                "lvalue": "pos",
                "note": "Posición varía según distribución",
            },
            {"type": "if", "condition": "arr[pos] = target", "has_early_return": True},
        ],
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode,
        ast_structure=ast_structure,
        algorithm_name="Interpolation Search",
    )

    expected = True
    status = "✅ CORRECTO" if result == expected else "❌ INCORRECTO"
    print(
        f"{status} | Interpolation Search → Múltiples casos: {result} (esperado: {expected})"
    )
    return result == expected


def test_caso_extremo_3_permutaciones():
    """
    ❌ CASO GENERAL - Generador de Permutaciones
    Siempre genera n! permutaciones de forma determinista
    """
    pseudocode = """
permute(arr, l, r)
begin
    if (l = r) then
        print(arr)
        return
    end
    
    for i ← l to r do
        swap(arr[l], arr[i])
        permute(arr, l + 1, r)
        swap(arr[l], arr[i])  // backtrack
    end
end
"""

    ast_structure = {
        "type": "procedure_def",
        "name": "permute",
        "body": [
            {"type": "if", "condition": "l = r"},
            {"type": "for", "var": "i"},
            {"type": "call", "name": "permute"},
        ],
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode,
        ast_structure=ast_structure,
        algorithm_name="Permutaciones",
    )

    expected = False
    status = "✅ CORRECTO" if result == expected else "❌ INCORRECTO"
    print(
        f"{status} | Permutaciones → Múltiples casos: {result} (esperado: {expected})"
    )
    return result == expected


# ============================================================================
# 🎯 RUNNER DE TESTS
# ============================================================================


def run_all_tests():
    """Ejecuta todas las pruebas y genera reporte"""

    print("=" * 80)
    print("🧪 SUITE DE PRUEBAS - CASE DETECTION AGENT")
    print("=" * 80)
    print()

    tests = {
        "🟢 CASOS BÁSICOS": [
            ("Fibonacci (caso general)", test_caso_basico_1_fibonacci),
            ("Factorial (caso general)", test_caso_basico_2_factorial),
            ("Torres de Hanoi (caso general)", test_caso_basico_3_torres_hanoi),
        ],
        "🟡 CASOS INTERMEDIOS": [
            ("Binary Search (múltiples casos)", test_caso_intermedio_1_binary_search),
            ("QuickSort (múltiples casos)", test_caso_intermedio_2_quicksort),
            ("MergeSort (caso general)", test_caso_intermedio_3_mergesort),
        ],
        "🟠 CASOS AVANZADOS": [
            (
                "Linear Search Recursivo (múltiples casos)",
                test_caso_avanzado_1_linear_search_recursivo,
            ),
            ("Suma Arreglo (caso general)", test_caso_avanzado_2_suma_arreglo),
            (
                "Búsqueda Exponencial (múltiples casos)",
                test_caso_avanzado_3_busqueda_exponencial,
            ),
        ],
        "🔴 CASOS EXTREMOS": [
            ("Ackermann (caso general)", test_caso_extremo_1_ackermann),
            (
                "Interpolation Search (múltiples casos)",
                test_caso_extremo_2_interpolation_search,
            ),
            ("Permutaciones (caso general)", test_caso_extremo_3_permutaciones),
        ],
    }

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    for level, test_list in tests.items():
        print(f"\n{level}")
        print("-" * 80)

        for test_name, test_func in test_list:
            total_tests += 1
            try:
                success = test_func()
                if success:
                    passed_tests += 1
                else:
                    failed_tests.append(test_name)
            except Exception as e:
                failed_tests.append(test_name)
                print(f"💥 ERROR | {test_name}: {str(e)}")

        print()

    # Resumen final
    print("=" * 80)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 80)
    print(f"✅ Tests pasados: {passed_tests}/{total_tests}")
    print(f"❌ Tests fallidos: {len(failed_tests)}/{total_tests}")
    print(f"📈 Precisión: {100 * passed_tests / total_tests:.1f}%")

    if failed_tests:
        print("\n🔍 TESTS FALLIDOS:")
        for name in failed_tests:
            print(f"   ❌ {name}")
    else:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")

    print("=" * 80)

    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

"""
Script de prueba para CaseDetectionAgent.
Prueba la detección de múltiples casos vs caso general en algoritmos recursivos.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Cargar variables de entorno desde .env si existe
try:
    from dotenv import load_dotenv

    env_path = root_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Variables de entorno cargadas desde {env_path}")
    else:
        print(
            f"⚠️ Archivo .env no encontrado. Copia .env.example a .env y configura tus API keys."
        )
except ImportError:
    print("⚠️ python-dotenv no instalado. Ejecuta: pip install python-dotenv")

from app.models.recursive.case_detection_agent import CaseDetectionAgent


def test_quicksort():
    """QuickSort - Debería detectar MÚLTIPLES CASOS (mejor O(n log n), peor O(n²))"""

    pseudocode = """
quicksort(A, bajo, alto)
begin
    if bajo < alto then
    begin
        pivote 🡨 partition(A, bajo, alto)
        CALL quicksort(A, bajo, pivote - 1)
        CALL quicksort(A, pivote + 1, alto)
    end
end

partition(A, bajo, alto)
begin
    pivote 🡨 A[alto]
    i 🡨 bajo - 1
    for j 🡨 bajo to alto - 1 do
    begin
        if A[j] <= pivote then
        begin
            i 🡨 i + 1
            intercambiar A[i] con A[j]
        end
    end
    intercambiar A[i + 1] con A[alto]
    return i + 1
end
"""

    ast_structure = {
        "type": "function",
        "name": "quicksort",
        "body": {
            "if": {"condition": "bajo < alto"},
            "recursive_calls": [
                "quicksort(A, bajo, pivote-1)",
                "quicksort(A, pivote+1, alto)",
            ],
        },
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode, ast_structure=ast_structure, algorithm_name="QuickSort"
    )

    print(f"\n✓ QuickSort → Múltiples casos: {result}")
    print(f"   Esperado: True (tiene mejor y peor caso diferentes)")
    return result


def test_mergesort():
    """MergeSort - Debería detectar CASO GENERAL (siempre O(n log n))"""

    pseudocode = """
mergesort(A, inicio, fin)
begin
    if inicio < fin then
    begin
        medio 🡨 (inicio + fin) / 2
        CALL mergesort(A, inicio, medio)
        CALL mergesort(A, medio + 1, fin)
        merge(A, inicio, medio, fin)
    end
end

merge(A, inicio, medio, fin)
begin
    n1 🡨 medio - inicio + 1
    n2 🡨 fin - medio
    crear L[n1] y R[n2]
    
    for i 🡨 0 to n1 - 1 do
        L[i] 🡨 A[inicio + i]
    
    for j 🡨 0 to n2 - 1 do
        R[j] 🡨 A[medio + 1 + j]
    
    i 🡨 0
    j 🡨 0
    k 🡨 inicio
    
    while i < n1 and j < n2 do
    begin
        if L[i] <= R[j] then
        begin
            A[k] 🡨 L[i]
            i 🡨 i + 1
        end
        else
        begin
            A[k] 🡨 R[j]
            j 🡨 j + 1
        end
        k 🡨 k + 1
    end
end
"""

    ast_structure = {
        "type": "function",
        "name": "mergesort",
        "body": {
            "if": {"condition": "inicio < fin"},
            "recursive_calls": [
                "mergesort(A, inicio, medio)",
                "mergesort(A, medio+1, fin)",
            ],
            "always_divides_equally": True,
        },
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode, ast_structure=ast_structure, algorithm_name="MergeSort"
    )

    print(f"\n✓ MergeSort → Múltiples casos: {result}")
    print(f"   Esperado: False (siempre O(n log n), caso general)")
    return result


def test_binary_search():
    """Binary Search - Debería detectar MÚLTIPLES CASOS (mejor O(1), peor O(log n))"""

    pseudocode = """
binarySearch(A, objetivo, inicio, fin)
begin
    if inicio > fin then
        return -1
    
    medio 🡨 (inicio + fin) / 2
    
    if A[medio] = objetivo then
        return medio
    else if A[medio] > objetivo then
        return CALL binarySearch(A, objetivo, inicio, medio - 1)
    else
        return CALL binarySearch(A, objetivo, medio + 1, fin)
end
"""

    ast_structure = {
        "type": "function",
        "name": "binarySearch",
        "body": {
            "if": {"condition": "A[medio] = objetivo", "returns_early": True},
            "recursive_calls": [
                "binarySearch(A, objetivo, inicio, medio-1)",
                "binarySearch(A, objetivo, medio+1, fin)",
            ],
        },
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode,
        ast_structure=ast_structure,
        algorithm_name="Binary Search",
    )

    print(f"\n✓ Binary Search → Múltiples casos: {result}")
    print(f"   Esperado: True (mejor caso encuentra inmediato, peor caso no encuentra)")
    return result


def test_factorial():
    """Factorial - Debería detectar CASO GENERAL (siempre O(n))"""

    pseudocode = """
factorial(n)
begin
    if n <= 1 then
        return 1
    else
        return n * CALL factorial(n - 1)
end
"""

    ast_structure = {
        "type": "function",
        "name": "factorial",
        "body": {
            "if": {"condition": "n <= 1"},
            "recursive_calls": ["factorial(n - 1)"],
            "linear_recursion": True,
        },
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode, ast_structure=ast_structure, algorithm_name="Factorial"
    )

    print(f"\n✓ Factorial → Múltiples casos: {result}")
    print(f"   Esperado: False (siempre O(n), caso general)")
    return result


def test_towers_of_hanoi():
    """Torres de Hanoi - Debería detectar CASO GENERAL (siempre O(2^n))"""

    pseudocode = """
hanoi(n, origen, destino, auxiliar)
begin
    if n = 1 then
    begin
        mover disco de origen a destino
        return
    end
    
    CALL hanoi(n - 1, origen, auxiliar, destino)
    mover disco de origen a destino
    CALL hanoi(n - 1, auxiliar, destino, origen)
end
"""

    ast_structure = {
        "type": "function",
        "name": "hanoi",
        "body": {
            "if": {"condition": "n = 1"},
            "recursive_calls": [
                "hanoi(n-1, origen, auxiliar, destino)",
                "hanoi(n-1, auxiliar, destino, origen)",
            ],
            "exponential_recursion": True,
        },
    }

    agent = CaseDetectionAgent(model_type="Gemini_Rapido", provider="gemini")
    result = agent.detect_cases(
        pseudocode=pseudocode,
        ast_structure=ast_structure,
        algorithm_name="Torres de Hanoi",
    )

    print(f"\n✓ Torres de Hanoi → Múltiples casos: {result}")
    print(f"   Esperado: False (siempre O(2^n), caso general)")
    return result


def main():
    print("=" * 80)
    print("PRUEBAS DE CASE DETECTION AGENT")
    print("=" * 80)
    print("\nProbando detección de múltiples casos vs caso general...\n")

    results = {
        "QuickSort": test_quicksort(),
        "MergeSort": test_mergesort(),
        "Binary Search": test_binary_search(),
        "Factorial": test_factorial(),
        "Torres de Hanoi": test_towers_of_hanoi(),
    }

    print("\n" + "=" * 80)
    print("RESUMEN DE RESULTADOS")
    print("=" * 80)

    expected = {
        "QuickSort": True,
        "MergeSort": False,
        "Binary Search": True,
        "Factorial": False,
        "Torres de Hanoi": False,
    }

    correct = 0
    total = len(results)

    for algo, result in results.items():
        exp = expected[algo]
        status = "✅ CORRECTO" if result == exp else "❌ INCORRECTO"
        print(f"{algo:20} → {result:5} (esperado: {exp:5}) {status}")
        if result == exp:
            correct += 1

    print("=" * 80)
    print(f"Precisión: {correct}/{total} ({100 * correct / total:.1f}%)")
    print("=" * 80)


if __name__ == "__main__":
    main()

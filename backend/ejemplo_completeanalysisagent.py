"""
Script de prueba para el CompleteAnalysisAgent.
Prueba análisis de algoritmos recursivos e iterativos.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Cargar variables de entorno desde .env si existe
try:
    from dotenv import load_dotenv
    env_path = backend_path / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Variables de entorno cargadas desde {env_path}")
    else:
        print(f"⚠️ Archivo .env no encontrado. Copia .env.example a .env y configura tus API keys.")
except ImportError:
    print("⚠️ python-dotenv no instalado. Ejecuta: pip install python-dotenv")

from app.external_services.Agentes.CompleteAnalysisAgent import CompleteAnalysisAgent
import json


def print_separator(title=""):
    """Imprime un separador visual."""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)
    print()


def print_solution(solution, algorithm_name):
    """Imprime el objeto Solution de forma legible."""
    print_separator(f"ANÁLISIS COMPLETO: {algorithm_name}")
    
    print("🔹 INFORMACIÓN GENERAL")
    print(f"   Tipo: {solution.type}")
    print(f"   Nombre: {solution.algorithm_name}")
    print(f"   Categoría: {solution.algorithm_category}")
    print()
    
    print("📝 PROPÓSITO")
    print(f"   {solution.code_explain}")
    print()
    
    print("📊 ANÁLISIS LÍNEA POR LÍNEA")
    for line_data in solution.complexity_line_to_line:
        print(f"   Línea {line_data['line']}: {line_data['code']}")
        print(f"      └─ Costo: {line_data['complexity']}")
        print(f"      └─ {line_data['explanation']}")
        print()
    
    print("🧮 ECUACIÓN")
    print(f"   {solution.equation}")
    print()
    
    print("🔧 MÉTODO DE RESOLUCIÓN")
    print(f"   {solution.method_solution}")
    print()
    
    print("📐 PASOS DE RESOLUCIÓN")
    for i, step in enumerate(solution.explain_solution_steps, 1):
        print(f"   {i}. {step}")
    print()
    
    print("⚡ COMPLEJIDAD FINAL")
    print(f"   {solution.solution_equation}")
    print()
    
    print("📈 NOTACIONES ASINTÓTICAS")
    print(f"   Ω (mejor caso):    {solution.asymptotic_notation['best']}")
    print(f"   O (peor caso):     {solution.asymptotic_notation['worst']}")
    print(f"   Θ (caso promedio): {solution.asymptotic_notation['average']}")
    print()
    print(f"   Explicación: {solution.asymptotic_notation['explanation']}")
    print()
    
    print("📄 EXPLICACIÓN COMPLETA DE LA COMPLEJIDAD")
    print(solution.explain_complexity)
    print()


def test_recursive_algorithm():
    """Prueba con un algoritmo recursivo: Fibonacci."""
    print_separator("PRUEBA 1: ALGORITMO RECURSIVO - FIBONACCI")
    
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
    
    print("📥 PSEUDOCÓDIGO:")
    print(pseudocode)
    print()
    print("⏳ Analizando con CompleteAnalysisAgent...")
    print()
    
    agent = CompleteAnalysisAgent()
    
    try:
        solution = agent.analyze(pseudocode)
        print_solution(solution, "Fibonacci Recursivo")
        
        # Guardar en JSON
        output_file = "output/fibonacci_analysis.json"
        solution.save_to_json(output_file)
        print(f"✅ Análisis guardado en: {output_file}")
        
        return solution
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_iterative_algorithm():
    """Prueba con un algoritmo iterativo: Bubble Sort."""
    print_separator("PRUEBA 2: ALGORITMO ITERATIVO - BUBBLE SORT")
    
    pseudocode = """
bubbleSort(arr, n)
begin
    for i = 0 to n-1 do
        for j = 0 to n-i-1 do
            if arr[j] > arr[j+1] then
                swap(arr[j], arr[j+1])
            end
        end
    end
end
"""
    
    print("📥 PSEUDOCÓDIGO:")
    print(pseudocode)
    print()
    print("⏳ Analizando con CompleteAnalysisAgent...")
    print()
    
    agent = CompleteAnalysisAgent()
    
    try:
        solution = agent.analyze(pseudocode)
        print_solution(solution, "Bubble Sort")
        
        # Guardar en JSON
        output_file = "output/bubblesort_analysis.json"
        solution.save_to_json(output_file)
        print(f"✅ Análisis guardado en: {output_file}")
        
        return solution
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_divide_and_conquer():
    """Prueba con un algoritmo Divide y Conquista: Merge Sort."""
    print_separator("PRUEBA 3: DIVIDE Y CONQUISTA - MERGE SORT")
    
    pseudocode = """
mergeSort(arr, inicio, fin)
begin
    if (inicio < fin) then
        medio ← (inicio + fin) / 2
        mergeSort(arr, inicio, medio)
        mergeSort(arr, medio + 1, fin)
        merge(arr, inicio, medio, fin)
    end
end
"""
    
    print("📥 PSEUDOCÓDIGO:")
    print(pseudocode)
    print()
    print("⏳ Analizando con CompleteAnalysisAgent...")
    print()
    
    agent = CompleteAnalysisAgent()
    
    try:
        solution = agent.analyze(pseudocode)
        print_solution(solution, "Merge Sort")
        
        # Guardar en JSON
        output_file = "output/mergesort_analysis.json"
        solution.save_to_json(output_file)
        print(f"✅ Análisis guardado en: {output_file}")
        
        return solution
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_binary_search():
    """Prueba con búsqueda binaria recursiva."""
    print_separator("PRUEBA 4: BÚSQUEDA - BINARY SEARCH")
    
    pseudocode = """
binarySearch(arr, objetivo, inicio, fin)
begin
    if (inicio > fin) then
        return -1
    end
    
    medio ← (inicio + fin) / 2
    
    if (arr[medio] = objetivo) then
        return medio
    else
        if (arr[medio] > objetivo) then
            return binarySearch(arr, objetivo, inicio, medio - 1)
        else
            return binarySearch(arr, objetivo, medio + 1, fin)
        end
    end
end
"""
    
    print("📥 PSEUDOCÓDIGO:")
    print(pseudocode)
    print()
    print("⏳ Analizando con CompleteAnalysisAgent...")
    print()
    
    agent = CompleteAnalysisAgent()
    
    try:
        solution = agent.analyze(pseudocode)
        print_solution(solution, "Binary Search")
        
        # Guardar en JSON
        output_file = "output/binarysearch_analysis.json"
        solution.save_to_json(output_file)
        print(f"✅ Análisis guardado en: {output_file}")
        
        return solution
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Función principal."""
    print_separator("COMPLETEANALYSISAGENT - SUITE DE PRUEBAS")
    
    print("Este script prueba el CompleteAnalysisAgent con diferentes tipos de algoritmos:")
    print("  1. Recursivo simple (Fibonacci)")
    print("  2. Iterativo con bucles anidados (Bubble Sort)")
    print("  3. Divide y Conquista (Merge Sort)")
    print("  4. Búsqueda (Binary Search)")
    print()
    
    input("Presiona Enter para comenzar las pruebas...")
    
    # Ejecutar todas las pruebas
    results = []
    
    results.append(("Fibonacci", test_recursive_algorithm()))
    results.append(("Bubble Sort", test_iterative_algorithm()))
    results.append(("Merge Sort", test_divide_and_conquer()))
    results.append(("Binary Search", test_binary_search()))
    
    # Resumen final
    print_separator("RESUMEN DE PRUEBAS")
    
    for name, solution in results:
        if solution:
            print(f"✅ {name:20} - {solution.algorithm_category:25} - {solution.solution_equation}")
        else:
            print(f"❌ {name:20} - Error en el análisis")
    
    print()
    print("=" * 80)
    
    # Estadísticas
    successful = sum(1 for _, s in results if s is not None)
    total = len(results)
    print(f"\n🎯 Pruebas exitosas: {successful}/{total}")
    
    if successful == total:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
    
    print()


if __name__ == "__main__":
    main()

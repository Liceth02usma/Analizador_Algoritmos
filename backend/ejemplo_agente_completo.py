"""
Script de prueba para el agente completo de análisis recursivo.
Este agente NO usa parser ni módulos existentes, solo LLM.
"""

from app.external_services.Agentes.CompleteRecursiveAnalysisAgent import CompleteRecursiveAnalysisAgent
from app.external_services.Agentes.LLM_Factory import LLM_Factory
import json


def main():
    print("=" * 80)
    print("  AGENTE COMPLETO DE ANÁLISIS DE COMPLEJIDAD RECURSIVA")
    print("  (Sin parser, sin módulos externos, solo LLM)")
    print("=" * 80)
    print()
    
    # Ejemplo 1: Fibonacci recursivo
    fibonacci_code = """
fibonacci(n)
begin
    if (n <= 1) then
        return n
    else
        return fibonacci(n-1) + fibonacci(n-2)
    end
end
"""
    
    # Ejemplo 2: Merge Sort
    merge_sort_code = """
mergeSort(array, inicio, fin)
begin
    if (inicio < fin) then
        medio 🡨 (inicio + fin) / 2
        CALL mergeSort(array, inicio, medio)
        CALL mergeSort(array, medio + 1, fin)
        CALL merge(array, inicio, medio, fin)
    end
end
"""
    
    # Ejemplo 3: Binary Search
    binary_search_code = """
binarySearch(array, objetivo, inicio, fin)
begin
    if (inicio > fin) then
        return -1
    end
    
    medio 🡨 (inicio + fin) / 2
    
    if (array[medio] = objetivo) then
        return medio
    else
        if (array[medio] > objetivo) then
            return CALL binarySearch(array, objetivo, inicio, medio - 1)
        else
            return CALL binarySearch(array, objetivo, medio + 1, fin)
        end
    end
end
"""
    
    # Seleccionar ejemplo
    ejemplos = {
        "1": ("Fibonacci Recursivo", fibonacci_code),
        "2": ("Merge Sort", merge_sort_code),
        "3": ("Binary Search", binary_search_code)
    }
    
    print("Ejemplos disponibles:")
    for key, (nombre, _) in ejemplos.items():
        print(f"  {key}. {nombre}")
    print()
    
    seleccion = input("Selecciona un ejemplo (1-3) o presiona Enter para Fibonacci: ").strip()
    if not seleccion:
        seleccion = "1"
    
    nombre_algoritmo, pseudocode = ejemplos.get(seleccion, ejemplos["1"])
    
    print()
    print(f"Analizando: {nombre_algoritmo}")
    print("=" * 80)
    print(pseudocode)
    print("=" * 80)
    print()
    print("⏳ Realizando análisis completo (esto puede tomar 30-60 segundos)...")
    print()
    
    # Crear agente
    llm_factory = LLM_Factory()
    agent = CompleteRecursiveAnalysisAgent(llm_factory)
    
    try:
        # Analizar
        result = agent.analyze(pseudocode)
        
        # Imprimir reporte completo
        print(result["complete_analysis"])
        
        # Guardar resultado en JSON
        output_file = f"output/analisis_completo_{nombre_algoritmo.replace(' ', '_').lower()}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print()
        print(f"✅ Análisis guardado en: {output_file}")
        
        # Resumen ejecutivo
        print()
        print("=" * 80)
        print("  RESUMEN EJECUTIVO")
        print("=" * 80)
        print(f"Algoritmo: {nombre_algoritmo}")
        print(f"Clasificación: {result.get('algorithm_classification', {}).get('classification', 'N/A')}")
        print(f"Ecuación: {result.get('recurrence_equation', {}).get('recurrence_equation', 'N/A')}")
        print(f"Método: {result.get('solution_method', 'N/A')}")
        print(f"Complejidad: {result.get('final_complexity', 'N/A')}")
        print()
        asymptotic = result.get('asymptotic_notation', {})
        print(f"Big-O (peor caso): {asymptotic.get('big_O', 'N/A')}")
        print(f"Big-Ω (mejor caso): {asymptotic.get('big_Omega', 'N/A')}")
        print(f"Big-Θ (caso ajustado): {asymptotic.get('big_Theta', 'N/A')}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

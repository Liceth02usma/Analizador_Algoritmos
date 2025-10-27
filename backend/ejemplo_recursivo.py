"""
Ejemplo de análisis del algoritmo de Fibonacci recursivo.
"""

from app.controllers.controller_recursive import ControlRecursive

def main():
    print("=" * 80)
    print("  ANÁLISIS DE FIBONACCI RECURSIVO")
    print("=" * 80)
    print()
    
    # Crear controlador
    controller = ControlRecursive()
    
    # Pseudocódigo de Fibonacci (sintaxis del proyecto)
    pseudocodigo = """
    fibonacci(n)
    begin
        if (n <= 1) then
        begin
            return n
        end
        else
        begin
            n1 🡨 n - 1
            n2 🡨 n - 2
            fib1 🡨 CALL fibonacci(n1)
            fib2 🡨 CALL fibonacci(n2)
            resultado 🡨 fib1 + fib2
            return resultado
        end
    end
    """
    
    print("📝 Pseudocódigo:")
    print(pseudocodigo)
    print()
    
    # Realizar análisis
    print("🔍 Analizando...")
    results = controller.analyze_from_parsed_tree(
        "Fibonacci",
        pseudocodigo
    )
    
    # Mostrar resultados
    print("\n" + "=" * 80)
    print("  RESULTADOS DEL ANÁLISIS")
    print("=" * 80)
    
    # Información del algoritmo
    print("\n📊 Algoritmo:")
    print(f"  Nombre: {results['algorithm']['name']}")
    print(f"  Tipo: {results['algorithm']['type']}")
    
    # Análisis de estructura recursiva
    print("\n🔬 Análisis de Recursión:")
    print(f"  Casos base: {results['analysis']['base_cases']}")
    print(f"  Llamadas recursivas: {results['analysis']['recursive_calls']}")
    print(f"  Relación de recurrencia: {results['analysis']['recurrence_relation']}")
    print(f"  Profundidad estimada: {results['analysis']['recursion_depth']}")
    
    # Detalles de llamadas recursivas
    if results['analysis']['recursive_call_details']:
        print("\n  Detalles de llamadas recursivas:")
        for i, call in enumerate(results['analysis']['recursive_call_details'], 1):
            print(f"    {i}. Función: {call.get('function', 'N/A')}")
            print(f"       Patrón: {call.get('pattern', 'N/A')}")
    
    # Complejidad
    print("\n⏱️ Complejidad Temporal:")
    print(f"  Peor caso: {results['complexity']['time']['worst_case']}")
    print(f"  Mejor caso: {results['complexity']['time']['best_case']}")
    print(f"  Caso promedio: {results['complexity']['time']['average_case']}")
    
    print("\n💾 Complejidad Espacial:")
    print(f"  Peor caso: {results['complexity']['space']['worst_case']}")
    
    # Notaciones
    print("\n📐 Notaciones Asintóticas:")
    print(f"  Big O (O): {results['complexity']['notation']['big_o']}")
    print(f"  Big Omega (Ω): {results['complexity']['notation']['big_omega']}")
    print(f"  Big Theta (Θ): {results['complexity']['notation']['big_theta']}")
    
    # Soluciones de recurrencia
    print("\n🧮 Soluciones de la Recurrencia:")
    for method, solution in results['recurrence_solutions'].items():
        print(f"  {method}: {solution}")
    
    # Patrón detectado
    print("\n🎯 Patrón Detectado:")
    print(f"  Nombre: {results['pattern']['name']}")
    print(f"  Descripción: {results['pattern']['description']}")
    print(f"  Pista de complejidad: {results['pattern']['complexity_hint']}")
    if 'characteristics' in results['pattern']:
        print(f"  Características: {', '.join(results['pattern']['characteristics'])}")
    
    # Optimizaciones sugeridas
    print("\n💡 Optimizaciones Sugeridas:")
    for i, opt in enumerate(results['optimizations'], 1):
        print(f"  {i}. {opt}")
    
    # Razonamiento
    if results['complexity']['reasoning']:
        print("\n📝 Razonamiento:")
        print(results['complexity']['reasoning'])
    
    # Resumen
    print("\n" + "=" * 80)
    print("  RESUMEN")
    print("=" * 80)
    print(results['summary'])
    
    # Exportar reportes
    print("\n" + "=" * 80)
    print("  EXPORTACIÓN DE REPORTES")
    print("=" * 80)
    
    # Reporte en texto
    print("\n📄 Reporte en Texto:")
    print(controller.get_complexity_report("text"))
    
    # Reporte en Markdown
    print("\n📝 Reporte en Markdown:")
    print(controller.get_complexity_report("markdown"))
    
    # Resumen de recursión
    print("\n🔄 Resumen de Recursión:")
    print(controller.get_recursion_summary())
    
    print("\n✅ Análisis completado exitosamente!")

if __name__ == "__main__":
    main()
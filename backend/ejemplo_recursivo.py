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
    busquedaBinaria(array, izquierda, derecha, objetivo)
    begin
        if (izquierda > derecha) then
        begin
            return -1
        end
        medio 🡨 (izquierda + derecha) / 2
        if (array[medio] = objetivo) then
        begin
            return medio
        end
        else
        begin
            if (array[medio] < objetivo) then
            begin
                CALL busquedaBinaria(array, medio + 1, derecha, objetivo)
            end
            else
            begin
                CALL busquedaBinaria(array, izquierda, medio - 1, objetivo)
            end
        end
    end
    """
    print("📝 Pseudocódigo:")
    print(pseudocodigo)
    print()
    
    # Realizar análisis
    print("🔍 Analizando...")
    results = controller.analyze_from_parsed_tree(
        "busquedaBinaria",
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
    
    
    
    
    # Razonamiento
    if results['complexity']['reasoning']:
        print("\n📝 Razonamiento:")
        print(results['complexity']['reasoning'])
    

    
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
from app.controllers.controller_iterative import ControlIterative

# Algoritmo de búsqueda secuencial
pseudocodigo_busqueda = """
        for i 🡨 0 to n do
        begin
            for j 🡨 0 to n do
            begin
                matriz 🡨 0
            end
        end
"""

print("=" * 60)
print("ANÁLISIS DE BÚSQUEDA SECUENCIAL")
print("=" * 60)

controller = ControlIterative()

results = controller.analyze_from_parsed_tree(
    "BúsquedaSecuencial", pseudocodigo_busqueda
)

print("\n📊 Resultados del análisis:\n")
print(f"Algoritmo: {results['algorithm']['name']}")
print(f"Tipo: {results['algorithm']['type']}")

print(f"\n🔍 Análisis de ciclos:")
print(f"  - Ciclos detectados: {results['analysis']['loops_detected']}")
print(f"  - Niveles de anidamiento: {results['analysis']['nested_levels']}")

# Detalles por ciclo (si los hay)
loop_details = results["analysis"].get("loop_details", [])
if loop_details:
    print("\n🔎 Detalle de cada ciclo:")
    for i, loop in enumerate(loop_details, 1):
        print(
            f"  -> Ciclo #{i}: type={loop.get('type')}, level={loop.get('nesting_level')}"
        )
        if loop.get("type") == "for":
            print(
                f"     variable={loop.get('variable')}, from={loop.get('from')}, to={loop.get('to')}, pattern={loop.get('range_pattern')}"
            )
        else:
            print(f"     condition={loop.get('condition')}")
        print(f"     operaciones en el cuerpo: {loop.get('operations_count')}")
        print(f"     anidado: {loop.get('is_nested')}, padre: {loop.get('parent')}")

print(f"\n⏱️ Complejidad:")
print(f"  - Peor caso: {results['complexity']['time']['worst_case']}")
print(f"  - Mejor caso: {results['complexity']['time']['best_case']}")
print(f"  - Espacio: {results['complexity']['space']}")

# Mostrar razonamiento completo de la estimación
print("\n🧾 Razonamiento de la complejidad:")
reasoning = results["complexity"].get("reasoning", "")
if reasoning:
    print(reasoning)
else:
    # Fallback: pedir al controlador que exporte el reporte completo
    try:
        print(controller.get_complexity_report("markdown"))
    except Exception:
        pass

print(f"\n🎯 Patrón detectado:")
print(f"  - Nombre: {results['pattern']['name']}")
print(f"  - Descripción: {results['pattern']['description']}")
print(f"  - Complejidad esperada: {results['pattern']['complexity_hint']}")

if results["pattern"] and results["pattern"].get("examples"):
    examples = results["pattern"].get("examples", [])
    if examples:
        print("\n  Ejemplos:")
        for e in examples:
            print(f"    - {e}")

if results.get("optimizations"):
    print(f"\n💡 Sugerencias de optimización:")
    for opt in results["optimizations"]:
        print(f"  {opt}")

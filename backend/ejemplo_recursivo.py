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
quicksort(arr, low, high)
begin
    if (low < high) then
    begin
        pi 🡨 CALL partition(arr, low, high)
        CALL quicksort(arr, low, pi - 1)
        CALL quicksort(arr, pi + 1, high)
    end
end 
    """
    print("📝 Pseudocódigo:")
    print(pseudocodigo)
    print()

    results = controller.analyze_from_parsed_tree("quicksort", pseudocodigo)

    # Mostrar resultados
    print("\n" + "=" * 80)
    print("  RESULTADOS DEL ANÁLISIS")
    print("=" * 80)

    print(results.to_backend())
    filepath = results.save_to_json("estructura_frontend_general.json")


if __name__ == "__main__":
    main()

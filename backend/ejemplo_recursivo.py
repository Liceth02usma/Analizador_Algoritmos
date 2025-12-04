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
quicksort(A, low, high)
begin
    if (low < high) then
    begin
        p 🡨 CALL partition(A, low, high)
        CALL quicksort(A, low, p - 1)
        CALL quicksort(A, p + 1, high)
    end
    return A
end

partition(A, low, high)
begin
    pivot 🡨 A[high]
    i 🡨 low - 1

    for j 🡨 low to high - 1 do
    begin
        if (A[j] <= pivot) then
        begin
            i 🡨 i + 1
            temp 🡨 A[i]
            A[i] 🡨 A[j]
            A[j] 🡨 temp
        end
    end

    temp 🡨 A[i+1]
    A[i+1] 🡨 A[high]
    A[high] 🡨 temp

    return i + 1
end


    """
    print("📝 Pseudocódigo:")
    print(pseudocodigo)
    print()

    results = controller.analyze_from_parsed_tree("No se", pseudocodigo)

    # Mostrar resultados
    print("\n" + "=" * 80)
    print("  RESULTADOS DEL ANÁLISIS")
    print("=" * 80)

    print(results.to_backend())
    filepath = results.save_to_json("estructura_frontend_general.json")


if __name__ == "__main__":
    main()

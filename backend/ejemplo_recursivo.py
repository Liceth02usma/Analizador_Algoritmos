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
    busqueda_lineal_rec(A, x, i, n)
    begin
        if (i = n) then
            begin
                return -1
            end
        else
            begin
                if (A[i] = x) then
                    begin
                        return i
                    end
                else
                    begin
                        return CALL busqueda_lineal_rec(A, x, i + 1, n)
                    end
            end
    end

    index 🡨 CALL busqueda_lineal_rec(A, x, 0, n)
    return index

    """
    print("📝 Pseudocódigo:")
    print(pseudocodigo)
    print()

    results = controller.analyze_from_parsed_tree("No se", pseudocodigo)

    # Mostrar resultados
    print("\n" + "=" * 80)
    print("  RESULTADOS DEL ANÁLISIS")
    print("=" * 80)

    print(results)
    print(results.to_backend())


if __name__ == "__main__":
    main()

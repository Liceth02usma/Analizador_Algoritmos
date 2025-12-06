# app/data/seed_algorithms.py

# Diccionario: Clave (nombre común) -> Código Estricto
KNOWN_ALGORITHMS = [
    {
        "id": "bubble_sort_opt",
        "name": "Bubble Sort (Optimizado)",
        "keywords": "bubble sort, ordenamiento burbuja, burbuja",
        "pseudocode": """bubble_sort(A, n)
begin
    swapped 🡨 T
    i 🡨 0
    while (swapped = T) do
    begin
        swapped 🡨 F
        for j 🡨 0 to n - 2 - i do
        begin
            if (A[j] > A[j+1]) then
            begin
                temp 🡨 A[j]
                A[j] 🡨 A[j+1]
                A[j+1] 🡨 temp
                swapped 🡨 T
            end
        end
        i 🡨 i + 1
    end
    return A
end""",
    },
    {
        "id": "binary_search",
        "name": "Búsqueda Binaria",
        "keywords": "binary search, busqueda binaria, buscar mitad",
        "pseudocode": """binary_search(A, x, n)
begin
    low 🡨 0
    high 🡨 n - 1
    while (low <= high) do
    begin
        mid 🡨 (low + high) div 2
        if (A[mid] = x) then
        begin
            return mid
        end
        if (A[mid] < x) then
        begin
            low 🡨 mid + 1
        end
        else
        begin
            high 🡨 mid - 1
        end
    end
    return -1
end""",
    },
    {
        "id": "factorial_iter",
        "name": "Factorial Iterativo",
        "keywords": "factorial, calculo factorial, productoria",
        "pseudocode": """factorial(n)
begin
    f 🡨 1
    for i 🡨 1 to n do
    begin
        f 🡨 f * i
    end
    return f
end""",
    },
]

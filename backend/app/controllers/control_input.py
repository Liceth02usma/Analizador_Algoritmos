from app.parsers.parser import parser, TreeToDict
from app.models.solution import Solution
from lark import UnexpectedInput


class ControlInput:
    @staticmethod
    def parse_pseudocode(pseudocode: str):
        try:
            tree = parser.parse(pseudocode)
            transformer = TreeToDict()
            result = transformer.transform(tree)
            return result
        except UnexpectedInput as e:
            return {"error": f"Error al parsear el pseudocódigo: {str(e)}"}

    @staticmethod
    def get_mock_analysis_single_case() -> Solution:
        """
        Retorna un análisis completo de ejemplo con datos estáticos
        para emular un análisis recursivo con UN SOLO CASO (type_case=False).

        Este mock refleja EXACTAMENTE la estructura que genera recursive.py
        cuando type_case=False (caso único).
        """
        return Solution(
            type="Recursivo",
            # ===================================================================
            # ANÁLISIS DE COMPLEJIDAD LÍNEA POR LÍNEA (CASO ÚNICO)
            # ===================================================================
            code_explain="Algoritmo de búsqueda binaria recursiva que divide el espacio de búsqueda a la mitad en cada iteración.",
            complexity_line_to_line="""FUNCION busqueda_binaria(arr, objetivo, inicio, fin)
    // Línea 1 - O(1): Comparación simple
    SI inicio > fin ENTONCES
        // Línea 2 - O(1): Retorno directo
        RETORNAR -1
    FIN SI
    
    // Línea 3 - O(1): Operación aritmética
    medio = (inicio + fin) / 2
    
    // Línea 4 - O(1): Acceso a array y comparación
    SI arr[medio] = objetivo ENTONCES
        // Línea 5 - O(1): Retorno directo
        RETORNAR medio
    FIN SI
    
    // Línea 6 - O(1): Comparación
    SI arr[medio] > objetivo ENTONCES
        // Línea 7 - T(n/2): Llamada recursiva con mitad izquierda
        RETORNAR busqueda_binaria(arr, objetivo, inicio, medio - 1)
    SINO
        // Línea 8 - T(n/2): Llamada recursiva con mitad derecha
        RETORNAR busqueda_binaria(arr, objetivo, medio + 1, fin)
    FIN SI
FIN FUNCION""",
            explain_complexity="El algoritmo tiene complejidad logarítmica O(log n). En cada llamada recursiva, el espacio de búsqueda se reduce a la mitad, lo que resulta en log₂(n) llamadas recursivas máximas. Cada operación dentro de la función (comparaciones, cálculos aritméticos) es O(1).",
            # ===================================================================
            # ECUACIÓN DE RECURRENCIA (CASO ÚNICO)
            # ===================================================================
            equation="T(n) = T(n/2) + O(1)",
            # ===================================================================
            # MÉTODO DE RESOLUCIÓN (CASO ÚNICO)
            # ===================================================================
            method_solution=["master_theorem"],
            # ===================================================================
            # COMPLEJIDAD FINAL (CASO ÚNICO)
            # ===================================================================
            solution_equation=["O(log n)"],
            # ===================================================================
            # PASOS DE RESOLUCIÓN DETALLADOS (CASO ÚNICO)
            # ===================================================================
            explain_solution_steps=[
                {
                    "case_type": "single",
                    "equation": "T(n) = T(n/2) + O(1)",
                    "method": "master_theorem",
                    "complexity": "O(log n)",
                    "classification_confidence": 0.95,
                    "classification_reasoning": "La ecuación tiene la forma T(n) = aT(n/b) + f(n) con a=1, b=2, f(n)=O(1). Se aplica el Teorema Maestro directamente.",
                    "explanation": "Aplicando el Teorema Maestro para T(n) = T(n/2) + O(1):\n\n"
                    "1. Identificación de parámetros:\n"
                    "   - a = 1 (número de subproblemas)\n"
                    "   - b = 2 (factor de reducción del tamaño)\n"
                    "   - f(n) = O(1) (trabajo fuera de las llamadas recursivas)\n\n"
                    "2. Cálculo de n^(log_b(a)):\n"
                    "   - log₂(1) = 0\n"
                    "   - n^0 = 1 = O(1)\n\n"
                    "3. Comparación con f(n):\n"
                    "   - f(n) = O(1) = Θ(n^0)\n"
                    "   - Por lo tanto, f(n) = Θ(n^(log_b(a)))\n\n"
                    "4. Aplicación del Caso 2 del Teorema Maestro:\n"
                    "   - Cuando f(n) = Θ(n^(log_b(a))), la complejidad es Θ(n^(log_b(a)) * log n)\n"
                    "   - T(n) = Θ(n^0 * log n) = Θ(log n)\n\n"
                    "5. Resultado final: O(log n)",
                    "steps": [
                        "Identificar parámetros del Teorema Maestro: a=1, b=2, f(n)=O(1)",
                        "Calcular n^(log_b(a)) = n^(log₂(1)) = n^0 = 1",
                        "Comparar f(n) con n^(log_b(a)): O(1) = Θ(1)",
                        "Aplicar Caso 2: T(n) = Θ(log n)",
                        "Conclusión: La complejidad es O(log n)",
                    ],
                    "details": {
                        "theorem_case": 2,
                        "a": 1,
                        "b": 2,
                        "f_n": "O(1)",
                        "critical_exponent": 0,
                        "comparison": "f(n) = Θ(n^log_b(a))",
                    },
                }
            ],
            # ===================================================================
            # DIAGRAMAS Y ÁRBOLES (CASO ÚNICO)
            # ===================================================================
            diagrams={
                "recursion_trees": {
                    "has_multiple_cases": False,
                    "trees": [
                        {
                            "case_type": "single",
                            "recurrence_equation": "T(n) = T(n/2) + O(1)",
                            "tree_structure": [
                                {
                                    "level": 0,
                                    "position": 0,
                                    "label": "T(n)",
                                    "children_count": 1,
                                },
                                {
                                    "level": 1,
                                    "position": 0,
                                    "label": "T(n/2)",
                                    "children_count": 1,
                                },
                                {
                                    "level": 2,
                                    "position": 0,
                                    "label": "T(n/4)",
                                    "children_count": 1,
                                },
                                {
                                    "level": 3,
                                    "position": 0,
                                    "label": "T(n/8)",
                                    "children_count": 1,
                                },
                                {
                                    "level": 4,
                                    "position": 0,
                                    "label": "T(1)",
                                    "children_count": 0,
                                },
                            ],
                            "tree_depth": 4,
                            "description": "Árbol lineal para búsqueda binaria. Cada nodo tiene un solo hijo, formando una cadena de profundidad log₂(n).",
                        }
                    ],
                    "summary": "Árbol de recursión lineal con un solo camino desde la raíz hasta las hojas, característico de divide y conquista con una sola rama activa.",
                }
            },
            # ===================================================================
            # INFORMACIÓN EXTRA (CASO ÚNICO)
            # ===================================================================
            extra={
                "has_multiple_cases": False,
                "analysis_details": [
                    {
                        "case_type": "single",
                        "equation": "T(n) = T(n/2) + O(1)",
                        "method": "master_theorem",
                        "complexity": "O(log n)",
                        "classification_confidence": 0.95,
                    }
                ],
                "time_complexities": {"single": "O(log n)"},
                "space_complexity": "O(log n) por la profundidad de la pila de recursión",
            },
        )

    @staticmethod
    def get_mock_analysis() -> Solution:
        """
        Retorna un análisis completo de ejemplo con datos estáticos
        para emular un análisis recursivo completo con múltiples casos.

        Este mock refleja EXACTAMENTE la estructura que genera recursive.py
        cuando type_case=True (múltiples casos).
        """
        return Solution(
            type="Recursivo",
            code_explain="En el mejor caso, el elemento buscado se encuentra en la primera posición del arreglo, por lo que no se realizan llamadas recursivas adicionales.",
            complexity_line_to_line="""=== MEJOR CASO ===
busqueda_lineal_rec(A, x, i, n)
begin
    if (i = n) then    // O(1) - Comparación
        begin
            return -1    // O(1) - Retorno
        end
    else
        begin
            if (A[i] = x) then    // O(1) - Comparación (elemento encontrado en la primera posición)
                begin
                    return i    // O(1) - Retorno inmediato
                end
            else
                begin
                    return CALL busqueda_lineal_rec(A, x, i + 1, n)    // No ejecutado
                end
        end
end

index 🡨 CALL busqueda_lineal_rec(A, x, 0, n)    // O(1) - Llamada inicial
return index    // O(1) - Retorno

=== PEOR CASO ===
busqueda_lineal_rec(A, x, i, n)
begin
    if (i = n) then    // O(1) - Comparación (ejecutado en la última llamada)
        begin
            return -1    // O(1) - Retorno
        end
    else
        begin
            if (A[i] = x) then    // O(1) - Comparación (siempre falso)
                begin
                    return i    // No ejecutado
                end
            else
                begin
                    return CALL busqueda_lineal_rec(A, x, i + 1, n)    // T(n-1) - Llamada recursiva (n veces)
                end
        end
end

index 🡨 CALL busqueda_lineal_rec(A, x, 0, n)    // O(1) - Llamada inicial
return index    // O(1) - Retorno

=== CASO PROMEDIO ===
busqueda_lineal_rec(A, x, i, n)
begin
    if (i = n) then    // O(1) - Comparación
        begin
            return -1    // O(1) - Retorno
        end
    else
        begin
            if (A[i] = x) then    // O(1) - Comparación (éxito en posición promedio n/2)
                begin
                    return i    // O(1) - Retorno
                end
            else
                begin
                    return CALL busqueda_lineal_rec(A, x, i + 1, n)    // T(n/2) - Llamada recursiva (~n/2 veces)
                end
        end
end

index 🡨 CALL busqueda_lineal_rec(A, x, 0, n)    // O(1) - Llamada inicial
return index    // O(1) - Retorno""",
            explain_complexity=(
                "Mejor caso: Solo se ejecutan las operaciones iniciales y una comparación para encontrar el elemento. La complejidad total es constante.\n\n"
                "Peor caso: Cada llamada recursiva realiza trabajo constante O(1), y hay n llamadas en total. Por lo tanto, la complejidad total es O(n).\n\n"
                "Caso promedio: Cada llamada recursiva realiza trabajo constante O(1), y en promedio se realizan n/2 llamadas. Por lo tanto, la complejidad total sigue siendo O(n)."
            ),
            asymptotic_notation={
                "best": "Ω(1)",
                "worst": "O(n²)",
                "average": "Θ(n log n)",
                "explanation": "...",
            },
            algorithm_name="Busqueda lineal",
            algorithm_category="Busqueda y Ordenamiento",
            equation=[
                "T(n) = 1, T(1) = 1",
                "T(n) = T(n-1) + 1, T(1) = 1",
                "T_avg(n) = (1/n) × Σ[i=1 to n] T(i), donde T(i) = T(i-1) + 1, T(1) = 1",
            ],
            method_solution=[
                "none",
                "equation_characteristics",
                "equation_characteristics",
            ],
            solution_equation=["O(1)", "O(n)", "O(n)"],
            explain_solution_steps=[
                {
                    "case_type": "best_case",
                    "equation": "T(n) = 1",
                    "method": "none",
                    "complexity": "O(1)",
                    "steps": [
                        "**Paso 1 - Identificar expresión:**",
                        "   T(n) = 1",
                        "",
                        "**Paso 2 - Término dominante:**",
                        "   Constante (no depende de n)",
                        "",
                        "**Paso 3 - Simplificación:**",
                        "   Cualquier constante → O(1)",
                        "",
                        "**Paso 4 - Complejidad final:**",
                        "   O(1) - Tiempo constante",
                    ],
                    "explanation": "La expresión T(n) = 1 es una constante que no depende de n. Por lo tanto, la complejidad es O(1) - tiempo constante.",
                    "details": {
                        "complexity": "O(1)",
                        "steps": [
                            "**Paso 1 - Identificar expresión:**",
                            "   T(n) = 1",
                            "",
                            "**Paso 2 - Término dominante:**",
                            "   Constante (no depende de n)",
                            "",
                            "**Paso 3 - Simplificación:**",
                            "   Cualquier constante → O(1)",
                            "",
                            "**Paso 4 - Complejidad final:**",
                            "   O(1) - Tiempo constante",
                        ],
                        "explanation": "La expresión T(n) = 1 es una constante que no depende de n. Por lo tanto, la complejidad es O(1) - tiempo constante.",
                        "applicable": True,
                        "method": "Análisis Directo (Sin Recursión)",
                        "expression_type": "Constante",
                        "dominant_term": "constante",
                    },
                    "classification_confidence": 1.0,
                    "classification_reasoning": "La ecuación T(n) = 1 no contiene llamadas recursivas, por lo que se clasifica como NONE.",
                },
                {
                    "case_type": "worst_case",
                    "equation": "t(n)=t(n-1)+1,t(1)=1",
                    "method": "equation_characteristics",
                    "complexity": "O(n)",
                    "steps": [
                        "**Paso 1 - Identificar forma de la recurrencia:**",
                        "   No homogénea, orden 1",
                        "   Coeficientes: ['1']",
                        "",
                        "**Paso 2 - Formar ecuación característica:**",
                        "   r - 1 = 0",
                        "",
                        "**Paso 3 - Resolver para las raíces:**",
                        "   r₍1₎ = 1",
                        "",
                        "**Paso 4 - Formar solución general:**",
                        "   T(n) = T_h(n) = C·1^n = C",
                        "",
                        "**Paso 5 - Solución particular:**",
                        "   T_p(n) = T_p(n) = n",
                        "",
                        "**Paso 6 - Solución completa:**",
                        "   T(n) = T(n) = C + n",
                        "",
                        "**Paso 7 - Complejidad final:**",
                        "   O(n)",
                    ],
                    "explanation": "**Paso 1: Identificar la forma**\nLa ecuación dada es t(n) = t(n-1) + 1 con condición inicial t(1) = 1. Es una recurrencia lineal no homogénea de orden 1, ya que incluye un término constante g(n) = 1.\n\n**Paso 2: Formar la ecuación característica**\nPara la parte homogénea t(n) = t(n-1), sustituimos t(n) = r^n:\n    r^n = r^(n-1)\nDividiendo por r^(n-1):\n    r - 1 = 0\nLa ecuación característica es r - 1 = 0.\n\n**Paso 3: Resolver para las raíces**\nLa raíz de la ecuación característica es:\n    r = 1\n\n**Paso 4: Formar la solución general**\nLa solución general de la parte homogénea es:\n    T_h(n) = C·r^n = C·1^n = C\n\n**Paso 5: Encontrar solución particular**\nDado que g(n) = 1 (una constante), probamos una solución particular de la forma T_p(n) = A. Sustituyendo en la ecuación original:\n    T_p(n) = T_p(n-1) + 1\n    A = A + 1\nEsto no es posible, por lo que probamos T_p(n) = An. Sustituyendo:\n    An = A(n-1) + 1\n    An = An - A + 1\n    A = 1\nPor lo tanto, T_p(n) = n.\n\n**Paso 6: Solución completa**\nLa solución completa es la suma de la solución homogénea y la particular:\n    T(n) = T_h(n) + T_p(n)\n    T(n) = C + n\nUsando la condición inicial t(1) = 1:\n    1 = C + 1\n    C = 0\nPor lo tanto, la solución final es:\n    T(n) = n\n\n**Paso 7: Complejidad asintótica**\nLa solución está dominada por el término lineal n, por lo que la complejidad es:\n    O(n).",
                    "details": {
                        "complexity": "O(n)",
                        "steps": [
                            "**Paso 1 - Identificar forma de la recurrencia:**",
                            "   No homogénea, orden 1",
                            "   Coeficientes: ['1']",
                            "",
                            "**Paso 2 - Formar ecuación característica:**",
                            "   r - 1 = 0",
                            "",
                            "**Paso 3 - Resolver para las raíces:**",
                            "   r₍1₎ = 1",
                            "",
                            "**Paso 4 - Formar solución general:**",
                            "   T(n) = T_h(n) = C·1^n = C",
                            "",
                            "**Paso 5 - Solución particular:**",
                            "   T_p(n) = T_p(n) = n",
                            "",
                            "**Paso 6 - Solución completa:**",
                            "   T(n) = T(n) = C + n",
                            "",
                            "**Paso 7 - Complejidad final:**",
                            "   O(n)",
                        ],
                        "explanation": "**Paso 1: Identificar la forma**\nLa ecuación dada es t(n) = t(n-1) + 1 con condición inicial t(1) = 1. Es una recurrencia lineal no homogénea de orden 1, ya que incluye un término constante g(n) = 1.\n\n**Paso 2: Formar la ecuación característica**\nPara la parte homogénea t(n) = t(n-1), sustituimos t(n) = r^n:\n    r^n = r^(n-1)\nDividiendo por r^(n-1):\n    r - 1 = 0\nLa ecuación característica es r - 1 = 0.\n\n**Paso 3: Resolver para las raíces**\nLa raíz de la ecuación característica es:\n    r = 1\n\n**Paso 4: Formar la solución general**\nLa solución general de la parte homogénea es:\n    T_h(n) = C·r^n = C·1^n = C\n\n**Paso 5: Encontrar solución particular**\nDado que g(n) = 1 (una constante), probamos una solución particular de la forma T_p(n) = A. Sustituyendo en la ecuación original:\n    T_p(n) = T_p(n-1) + 1\n    A = A + 1\nEsto no es posible, por lo que probamos T_p(n) = An. Sustituyendo:\n    An = A(n-1) + 1\n    An = An - A + 1\n    A = 1\nPor lo tanto, T_p(n) = n.\n\n**Paso 6: Solución completa**\nLa solución completa es la suma de la solución homogénea y la particular:\n    T(n) = T_h(n) + T_p(n)\n    T(n) = C + n\nUsando la condición inicial t(1) = 1:\n    1 = C + 1\n    C = 0\nPor lo tanto, la solución final es:\n    T(n) = n\n\n**Paso 7: Complejidad asintótica**\nLa solución está dominada por el término lineal n, por lo que la complejidad es:\n    O(n).",
                        "applicable": True,
                        "method": "Ecuación Característica",
                        "recurrence_form": "No homogénea, orden 1",
                        "characteristic_equation": "r - 1 = 0",
                        "roots": ["1"],
                        "general_solution": "T_h(n) = C·1^n = C",
                        "particular_solution": "T_p(n) = n",
                        "final_solution": "T(n) = C + n",
                    },
                    "classification_confidence": 0.9,
                    "classification_reasoning": "Recurrencia lineal de orden superior. Términos: T(n-1). Trabajo adicional: =+1,=1. La ecuación característica es ideal para resolver este tipo de recurrencia..",
                },
                {
                    "case_type": "average_case",
                    "equation": "t_avg(n)=(1/n)×σ[i=1ton]t(i),dondet(i)=t(i-1)+1,t(1)=1",
                    "method": "equation_characteristics",
                    "complexity": "O(n)",
                    "steps": [
                        "**Paso 1 - Identificar estructura de sumatoria:**",
                        "   Ecuación: t_avg(n)=(1/n)×σ[i=1ton]t(i),dondet(i)=t(i-1)+1,t(1)=1",
                        "   Factor multiplicativo: 1/n",
                        "   Límites de sumatoria: i = 1 hasta n",
                        "   Recurrencia interna: T(i) = t(i-1)+1",
                        "   Caso base: T(1) = 1",
                        "",
                        "**Paso 2 - Expandir recurrencia interna T(i):**",
                        "   T(i) = T(i-1) + 1",
                        "   Expandiendo desde T(1) = 1:",
                        "      T(1) = 1",
                        "      T(2) = T(1) + 1 = 2",
                        "      T(3) = T(2) + 1 = 3",
                        "      ...",
                        "      T(i) = 1 + 1·(i - 1)",
                        "",
                        "**Paso 3 - Calcular Σ[i=a to b] T(i):**",
                    ],
                    "explanation": "Sumatoria con recurrencia lineal simple. La suma de una progresión aritmética resulta en complejidad O(n).",
                    "details": {
                        "complexity": "O(n)",
                        "steps": [
                            "**Paso 1 - Identificar estructura de sumatoria:**",
                            "   Ecuación: t_avg(n)=(1/n)×σ[i=1ton]t(i),dondet(i)=t(i-1)+1,t(1)=1",
                            "   Factor multiplicativo: 1/n",
                            "   Límites de sumatoria: i = 1 hasta n",
                            "   Recurrencia interna: T(i) = t(i-1)+1",
                            "   Caso base: T(1) = 1",
                            "",
                            "**Paso 2 - Expandir recurrencia interna T(i):**",
                            "   T(i) = T(i-1) + 1",
                            "   Expandiendo desde T(1) = 1:",
                            "      T(1) = 1",
                            "      T(2) = T(1) + 1 = 2",
                            "      T(3) = T(2) + 1 = 3",
                            "      ...",
                            "      T(i) = 1 + 1·(i - 1)",
                            "",
                            "**Paso 3 - Calcular Σ[i=a to b] T(i):**",
                        ],
                        "explanation": "Sumatoria con recurrencia lineal simple. La suma de una progresión aritmética resulta en complejidad O(n).",
                        "applicable": True,
                        "method": "Ecuación Característica (Sumatoria)",
                    },
                    "classification_confidence": 0.9,
                    "classification_reasoning": "Sumatoria con recurrencia lineal T(i) = T(i-1) + c detectada. Trabajo adicional: t_avg(n)=(1/n)×σ[i=1ton],donde=+1,=1. La ecuación característica es ideal para resolver este tipo de recurrencia..",
                },
            ],
            diagrams={
                "recursion_trees": {
                    "has_multiple_cases": True,
                    "trees": [
                        {
                            "case_type": "best",
                            "recurrence_equation": "T(n) = 1",
                            "tree_structure": [
                                {
                                    "level": 0,
                                    "position": 0,
                                    "label": "Level 0, Node 0",
                                    "children_count": 1,
                                },
                                {
                                    "level": 1,
                                    "position": 0,
                                    "label": "Level 1, Node 0",
                                    "children_count": 1,
                                },
                                {
                                    "level": 2,
                                    "position": 0,
                                    "label": "Level 2, Node 0",
                                    "children_count": 1,
                                },
                                {
                                    "level": 3,
                                    "position": 0,
                                    "label": "Level 3, Node 0",
                                    "children_count": 0,
                                },
                            ],
                            "tree_depth": 4,
                            "description": "Árbol desconocido con un único nodo raíz.",
                        },
                        {
                            "case_type": "worst",
                            "recurrence_equation": "T(n) = T(n-1) + 1",
                            "tree_structure": [
                                {
                                    "level": 0,
                                    "position": 0,
                                    "label": "T(n)",
                                    "children_count": 1,
                                },
                                {
                                    "level": 1,
                                    "position": 0,
                                    "label": "T(n-1)",
                                    "children_count": 1,
                                },
                                {
                                    "level": 2,
                                    "position": 0,
                                    "label": "T(n-2)",
                                    "children_count": 1,
                                },
                                {
                                    "level": 3,
                                    "position": 0,
                                    "label": "T(n-3)",
                                    "children_count": 0,
                                },
                            ],
                            "tree_depth": 4,
                            "description": "Árbol lineal (cadena) con 1 hijo por nodo.",
                        },
                        {
                            "case_type": "average",
                            "recurrence_equation": "T_avg(n) = (1/n) × Σ[i=1 to n] T(i), donde T(i) = T(i-1) + 1",
                            "tree_structure": [
                                {
                                    "level": 0,
                                    "position": 0,
                                    "label": "Level 0, Node 0",
                                    "children_count": 1,
                                },
                                {
                                    "level": 1,
                                    "position": 0,
                                    "label": "Level 1, Node 0",
                                    "children_count": 1,
                                },
                                {
                                    "level": 2,
                                    "position": 0,
                                    "label": "Level 2, Node 0",
                                    "children_count": 1,
                                },
                                {
                                    "level": 3,
                                    "position": 0,
                                    "label": "Level 3, Node 0",
                                    "children_count": 0,
                                },
                            ],
                            "tree_depth": 4,
                            "description": "Árbol desconocido con un único nodo raíz.",
                        },
                    ],
                    "summary": "Se generaron bosquejos de árboles para los casos mejor, peor y promedio.",
                }
            },
            extra={
                "has_multiple_cases": True,
                "analysis_details": [
                    {
                        "case_type": "best_case",
                        "equation": "T(n) = 1",
                        "method": "none",
                        "complexity": "O(1)",
                        "steps": [
                            "**Paso 1 - Identificar expresión:**",
                            "   T(n) = 1",
                            "",
                            "**Paso 2 - Término dominante:**",
                            "   Constante (no depende de n)",
                            "",
                            "**Paso 3 - Simplificación:**",
                            "   Cualquier constante → O(1)",
                            "",
                            "**Paso 4 - Complejidad final:**",
                            "   O(1) - Tiempo constante",
                        ],
                        "explanation": "La expresión T(n) = 1 es una constante que no depende de n. Por lo tanto, la complejidad es O(1) - tiempo constante.",
                        "details": {
                            "complexity": "O(1)",
                            "steps": [
                                "**Paso 1 - Identificar expresión:**",
                                "   T(n) = 1",
                                "",
                                "**Paso 2 - Término dominante:**",
                                "   Constante (no depende de n)",
                                "",
                                "**Paso 3 - Simplificación:**",
                                "   Cualquier constante → O(1)",
                                "",
                                "**Paso 4 - Complejidad final:**",
                                "   O(1) - Tiempo constante",
                            ],
                            "explanation": "La expresión T(n) = 1 es una constante que no depende de n. Por lo tanto, la complejidad es O(1) - tiempo constante.",
                            "applicable": True,
                            "method": "Análisis Directo (Sin Recursión)",
                            "expression_type": "Constante",
                            "dominant_term": "constante",
                        },
                        "classification_confidence": 1.0,
                        "classification_reasoning": "La ecuación T(n) = 1 no contiene llamadas recursivas, por lo que se clasifica como NONE.",
                    },
                    {
                        "case_type": "worst_case",
                        "equation": "t(n)=t(n-1)+1,t(1)=1",
                        "method": "equation_characteristics",
                        "complexity": "O(n)",
                        "steps": [
                            "**Paso 1 - Identificar forma de la recurrencia:**",
                            "   No homogénea, orden 1",
                            "   Coeficientes: ['1']",
                            "",
                            "**Paso 2 - Formar ecuación característica:**",
                            "   r - 1 = 0",
                            "",
                            "**Paso 3 - Resolver para las raíces:**",
                            "   r₍1₎ = 1",
                            "",
                            "**Paso 4 - Formar solución general:**",
                            "   T(n) = T_h(n) = C·1^n = C",
                            "",
                            "**Paso 5 - Solución particular:**",
                            "   T_p(n) = T_p(n) = n",
                            "",
                            "**Paso 6 - Solución completa:**",
                            "   T(n) = T(n) = C + n",
                            "",
                            "**Paso 7 - Complejidad final:**",
                            "   O(n)",
                        ],
                        "explanation": "**Paso 1: Identificar la forma**\nLa ecuación dada es t(n) = t(n-1) + 1 con condición inicial t(1) = 1. Es una recurrencia lineal no homogénea de orden 1, ya que incluye un término constante g(n) = 1.\n\n**Paso 2: Formar la ecuación característica**\nPara la parte homogénea t(n) = t(n-1), sustituimos t(n) = r^n:\n    r^n = r^(n-1)\nDividiendo por r^(n-1):\n    r - 1 = 0\nLa ecuación característica es r - 1 = 0.\n\n**Paso 3: Resolver para las raíces**\nLa raíz de la ecuación característica es:\n    r = 1\n\n**Paso 4: Formar la solución general**\nLa solución general de la parte homogénea es:\n    T_h(n) = C·r^n = C·1^n = C\n\n**Paso 5: Encontrar solución particular**\nDado que g(n) = 1 (una constante), probamos una solución particular de la forma T_p(n) = A. Sustituyendo en la ecuación original:\n    T_p(n) = T_p(n-1) + 1\n    A = A + 1\nEsto no es posible, por lo que probamos T_p(n) = An. Sustituyendo:\n    An = A(n-1) + 1\n    An = An - A + 1\n    A = 1\nPor lo tanto, T_p(n) = n.\n\n**Paso 6: Solución completa**\nLa solución completa es la suma de la solución homogénea y la particular:\n    T(n) = T_h(n) + T_p(n)\n    T(n) = C + n\nUsando la condición inicial t(1) = 1:\n    1 = C + 1\n    C = 0\nPor lo tanto, la solución final es:\n    T(n) = n\n\n**Paso 7: Complejidad asintótica**\nLa solución está dominada por el término lineal n, por lo que la complejidad es:\n    O(n).",
                        "details": {
                            "complexity": "O(n)",
                            "steps": [
                                "**Paso 1 - Identificar forma de la recurrencia:**",
                                "   No homogénea, orden 1",
                                "   Coeficientes: ['1']",
                                "",
                                "**Paso 2 - Formar ecuación característica:**",
                                "   r - 1 = 0",
                                "",
                                "**Paso 3 - Resolver para las raíces:**",
                                "   r₍1₎ = 1",
                                "",
                                "**Paso 4 - Formar solución general:**",
                                "   T(n) = T_h(n) = C·1^n = C",
                                "",
                                "**Paso 5 - Solución particular:**",
                                "   T_p(n) = T_p(n) = n",
                                "",
                                "**Paso 6 - Solución completa:**",
                                "   T(n) = T(n) = C + n",
                                "",
                                "**Paso 7 - Complejidad final:**",
                                "   O(n)",
                            ],
                            "explanation": "**Paso 1: Identificar la forma**\nLa ecuación dada es t(n) = t(n-1) + 1 con condición inicial t(1) = 1. Es una recurrencia lineal no homogénea de orden 1, ya que incluye un término constante g(n) = 1.\n\n**Paso 2: Formar la ecuación característica**\nPara la parte homogénea t(n) = t(n-1), sustituimos t(n) = r^n:\n    r^n = r^(n-1)\nDividiendo por r^(n-1):\n    r - 1 = 0\nLa ecuación característica es r - 1 = 0.\n\n**Paso 3: Resolver para las raíces**\nLa raíz de la ecuación característica es:\n    r = 1\n\n**Paso 4: Formar la solución general**\nLa solución general de la parte homogénea es:\n    T_h(n) = C·r^n = C·1^n = C\n\n**Paso 5: Encontrar solución particular**\nDado que g(n) = 1 (una constante), probamos una solución particular de la forma T_p(n) = A. Sustituyendo en la ecuación original:\n    T_p(n) = T_p(n-1) + 1\n    A = A + 1\nEsto no es posible, por lo que probamos T_p(n) = An. Sustituyendo:\n    An = A(n-1) + 1\n    An = An - A + 1\n    A = 1\nPor lo tanto, T_p(n) = n.\n\n**Paso 6: Solución completa**\nLa solución completa es la suma de la solución homogénea y la particular:\n    T(n) = T_h(n) + T_p(n)\n    T(n) = C + n\nUsando la condición inicial t(1) = 1:\n    1 = C + 1\n    C = 0\nPor lo tanto, la solución final es:\n    T(n) = n\n\n**Paso 7: Complejidad asintótica**\nLa solución está dominada por el término lineal n, por lo que la complejidad es:\n    O(n).",
                            "applicable": True,
                            "method": "Ecuación Característica",
                            "recurrence_form": "No homogénea, orden 1",
                            "characteristic_equation": "r - 1 = 0",
                            "roots": ["1"],
                            "general_solution": "T_h(n) = C·1^n = C",
                            "particular_solution": "T_p(n) = n",
                            "final_solution": "T(n) = C + n",
                        },
                        "classification_confidence": 0.9,
                        "classification_reasoning": "Recurrencia lineal de orden superior. Términos: T(n-1). Trabajo adicional: =+1,=1. La ecuación característica es ideal para resolver este tipo de recurrencia..",
                    },
                    {
                        "case_type": "average_case",
                        "equation": "t_avg(n)=(1/n)×σ[i=1ton]t(i),dondet(i)=t(i-1)+1,t(1)=1",
                        "method": "equation_characteristics",
                        "complexity": "O(n)",
                        "steps": [
                            "**Paso 1 - Identificar estructura de sumatoria:**",
                            "   Ecuación: t_avg(n)=(1/n)×σ[i=1ton]t(i),dondet(i)=t(i-1)+1,t(1)=1",
                            "   Factor multiplicativo: 1/n",
                            "   Límites de sumatoria: i = 1 hasta n",
                            "   Recurrencia interna: T(i) = t(i-1)+1",
                            "   Caso base: T(1) = 1",
                            "",
                            "**Paso 2 - Expandir recurrencia interna T(i):**",
                            "   T(i) = T(i-1) + 1",
                            "   Expandiendo desde T(1) = 1:",
                            "      T(1) = 1",
                            "      T(2) = T(1) + 1 = 2",
                            "      T(3) = T(2) + 1 = 3",
                            "      ...",
                            "      T(i) = 1 + 1·(i - 1)",
                            "",
                            "**Paso 3 - Calcular Σ[i=a to b] T(i):**",
                        ],
                        "explanation": "Sumatoria con recurrencia lineal simple. La suma de una progresión aritmética resulta en complejidad O(n).",
                        "details": {
                            "complexity": "O(n)",
                            "steps": [
                                "**Paso 1 - Identificar estructura de sumatoria:**",
                                "   Ecuación: t_avg(n)=(1/n)×σ[i=1ton]t(i),dondet(i)=t(i-1)+1,t(1)=1",
                                "   Factor multiplicativo: 1/n",
                                "   Límites de sumatoria: i = 1 hasta n",
                                "   Recurrencia interna: T(i) = t(i-1)+1",
                                "   Caso base: T(1) = 1",
                                "",
                                "**Paso 2 - Expandir recurrencia interna T(i):**",
                                "   T(i) = T(i-1) + 1",
                                "   Expandiendo desde T(1) = 1:",
                                "      T(1) = 1",
                                "      T(2) = T(1) + 1 = 2",
                                "      T(3) = T(2) + 1 = 3",
                                "      ...",
                                "      T(i) = 1 + 1·(i - 1)",
                                "",
                                "**Paso 3 - Calcular Σ[i=a to b] T(i):**",
                            ],
                            "explanation": "Sumatoria con recurrencia lineal simple. La suma de una progresión aritmética resulta en complejidad O(n).",
                            "applicable": True,
                            "method": "Ecuación Característica (Sumatoria)",
                        },
                        "classification_confidence": 0.9,
                        "classification_reasoning": "Sumatoria con recurrencia lineal T(i) = T(i-1) + c detectada. Trabajo adicional: t_avg(n)=(1/n)×σ[i=1ton],donde=+1,=1. La ecuación característica es ideal para resolver este tipo de recurrencia..",
                    },
                ],
            },
        )

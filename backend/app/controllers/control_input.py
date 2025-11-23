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
                        "Conclusión: La complejidad es O(log n)"
                    ],
                    "details": {
                        "theorem_case": 2,
                        "a": 1,
                        "b": 2,
                        "f_n": "O(1)",
                        "critical_exponent": 0,
                        "comparison": "f(n) = Θ(n^log_b(a))"
                    }
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
                                {"level": 0, "position": 0, "label": "T(n)", "children_count": 1},
                                {"level": 1, "position": 0, "label": "T(n/2)", "children_count": 1},
                                {"level": 2, "position": 0, "label": "T(n/4)", "children_count": 1},
                                {"level": 3, "position": 0, "label": "T(n/8)", "children_count": 1},
                                {"level": 4, "position": 0, "label": "T(1)", "children_count": 0}
                            ],
                            "tree_depth": 4,
                            "description": "Árbol lineal para búsqueda binaria. Cada nodo tiene un solo hijo, formando una cadena de profundidad log₂(n)."
                        }
                    ],
                    "summary": "Árbol de recursión lineal con un solo camino desde la raíz hasta las hojas, característico de divide y conquista con una sola rama activa."
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
                        "classification_confidence": 0.95
                    }
                ],
                "time_complexities": {
                    "single": "O(log n)"
                },
                "space_complexity": "O(log n) por la profundidad de la pila de recursión"
            }
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
            
            # ============================================================
            # ANÁLISIS DE COMPLEJIDAD LÍNEA POR LÍNEA (ComplexityLineAgent)
            # ============================================================
            # Cuando type_case=True → Lista de 3 diccionarios
            code_explain="Búsqueda lineal recursiva que recorre el array elemento por elemento hasta encontrar el objetivo.",
            
            complexity_line_to_line=[
                {
                    "case_type": "best_case",
                    "pseudocode_annotated": """busqueda_lineal(arr, objetivo, indice)
begin
    if (indice >= longitud(arr)) then         // O(1) - Comparación
        return -1                              // O(1) - Retorno
    if (arr[indice] = objetivo) then          // O(1) - Comparación y acceso ✓
        return indice                          // O(1) - Retorno (encontrado en primera posición)
end""",
                    "code_explanation": "Mejor caso: el elemento objetivo está en la primera posición del array.",
                    "complexity_explanation": "El elemento se encuentra en la primera comparación sin necesidad de llamadas recursivas.",
                    "total_complexity": "O(1)"
                },
                {
                    "case_type": "worst_case",
                    "pseudocode_annotated": """busqueda_lineal(arr, objetivo, indice)
begin
    if (indice >= longitud(arr)) then         // O(1) - Comparación
        return -1                              // O(1) - Retorno (elemento no existe)
    if (arr[indice] = objetivo) then          // O(1) - Comparación y acceso
        return indice                          // O(1) - Retorno
    else
        return busqueda_lineal(arr, objetivo, indice + 1)  // T(n-1) - Llamada recursiva
end""",
                    "code_explanation": "Peor caso: el elemento no existe o está en la última posición del array.",
                    "complexity_explanation": "Se requieren n comparaciones hasta llegar al final del array.",
                    "total_complexity": "O(n)"
                },
                {
                    "case_type": "average_case",
                    "pseudocode_annotated": """busqueda_lineal(arr, objetivo, indice)
begin
    if (indice >= longitud(arr)) then         // O(1) - Comparación
        return -1                              // O(1) - Retorno
    if (arr[indice] = objetivo) then          // O(1) - Comparación y acceso
        return indice                          // O(1) - Retorno
    else
        return busqueda_lineal(arr, objetivo, indice + 1)  // T(n-1) - Llamada recursiva
end""",
                    "code_explanation": "Caso promedio: el elemento se encuentra aproximadamente en la mitad del array.",
                    "complexity_explanation": "En promedio, se necesitan n/2 comparaciones para encontrar el elemento.",
                    "total_complexity": "O(n)"
                }
            ],
            
            explain_complexity=(
                "Mejor caso: O(1) cuando el elemento está en la primera posición. "
                "Peor caso: O(n) cuando el elemento no existe o está en la última posición. "
                "Caso promedio: O(n) por el recorrido secuencial del array."
            ),
            
            # ============================================================
            # ECUACIONES DE RECURRENCIA (RecurrenceEquationAgent)
            # ============================================================
            # Lista de 3 ecuaciones (una por caso)
            equation=[
                "T(n) = 1, T(1) = 1",           # Best case (sin recursión)
                "T(n) = T(n-1) + 1, T(1) = 1",  # Worst case
                "T(n) = T(n-1) + 1, T(1) = 1"   # Average case
            ],
            
            # ============================================================
            # MÉTODOS Y SOLUCIONES (RecurrenceMethods + Strategy)
            # ============================================================
            # Listas de 3 elementos (uno por caso)
            method_solution=[
                "Sustitución",
                "Sustitución",
                "Sustitución"
            ],
            
            solution_equation=[
                "O(1)",      # Best case (sin recursión efectiva)
                "O(n)",      # Worst case
                "O(n)"       # Average case
            ],
            
            # ============================================================
            # PASOS DETALLADOS DE RESOLUCIÓN (analysis_results)
            # ============================================================
            # Lista de 3 diccionarios con toda la info de cada caso
            explain_solution_steps=[
                {
                    "case_type": "best_case",
                    "equation": "T(n) = 1",
                    "method": "Sustitución",
                    "method_enum": "SUBSTITUTION",
                    "complexity": "O(1)",
                    "steps": [
                        "**Mejor caso: Elemento encontrado en primera posición**",
                        "",
                        "Paso 1: El elemento objetivo está en arr[0]",
                        "Paso 2: Se retorna inmediatamente sin llamadas recursivas",
                        "Paso 3: Complejidad final: O(1)"
                    ],
                    "explanation": (
                        "En el mejor caso, el elemento se encuentra en la primera posición del array, "
                        "por lo que no se realizan llamadas recursivas. La complejidad es constante O(1)."
                    ),
                    "details": {
                        "scenario": "best",
                        "recursive_calls": 0,
                        "iterations": 1
                    },
                    "classification_confidence": 0.98,
                    "classification_reasoning": "Caso trivial sin recursión efectiva."
                },
                {
                    "case_type": "worst_case",
                    "equation": "T(n) = T(n-1) + 1, T(1) = 1",
                    "method": "Sustitución",
                    "method_enum": "SUBSTITUTION",
                    "complexity": "O(n)",
                    "steps": [
                        "**Paso 1 - Expandir la recurrencia:**",
                        "   • T(n) = T(n-1) + 1",
                        "   • T(n) = [T(n-2) + 1] + 1 = T(n-2) + 2",
                        "   • T(n) = [T(n-3) + 1] + 2 = T(n-3) + 3",
                        "",
                        "**Paso 2 - Identificar el patrón:**",
                        "   • Después de k sustituciones:",
                        "   • T(n) = T(n-k) + k",
                        "",
                        "**Paso 3 - Determinar el caso base:**",
                        "   • Cuando n-k = 1 → k = n-1",
                        "   • T(n) = T(1) + (n-1)",
                        "",
                        "**Paso 4 - Sustituir el caso base:**",
                        "   • T(n) = 1 + (n-1) = n",
                        "",
                        "**Paso 5 - Complejidad final:**",
                        "   • T(n) = n → O(n)"
                    ],
                    "explanation": (
                        "Aplicando el método de sustitución, expandimos la recurrencia hasta identificar el patrón. "
                        "Cada llamada recursiva procesa un elemento menos, generando n llamadas en total. "
                        "Por lo tanto, T(n) = n, que resulta en una complejidad O(n)."
                    ),
                    "details": {
                        "recurrence_pattern": "T(n-k) + k",
                        "base_case_reached": "k = n-1",
                        "total_operations": "n",
                        "substitution_steps": "n-1"
                    },
                    "classification_confidence": 0.95,
                    "classification_reasoning": (
                        "Recurrencia lineal clásica con reducción de 1 en cada paso. "
                        "Patrón T(n) = T(n-1) + O(1) identificado con alta confianza."
                    )
                },
                {
                    "case_type": "average_case",
                    "equation": "T(n) = T(n-1) + 1, T(1) = 1",
                    "method": "Sustitución",
                    "method_enum": "SUBSTITUTION",
                    "complexity": "O(n)",
                    "steps": [
                        "**Caso promedio - Método de Sustitución:**",
                        "",
                        "Paso 1: Expandir → T(n) = T(n-1) + 1",
                        "Paso 2: T(n) = T(n-2) + 2",
                        "Paso 3: Patrón → T(n) = T(n-k) + k",
                        "Paso 4: Caso base (k = n-1) → T(n) = n",
                        "",
                        "**Complejidad final: O(n)**"
                    ],
                    "explanation": (
                        "El caso promedio tiene la misma complejidad que el peor caso O(n), "
                        "ya que la búsqueda lineal debe recorrer aproximadamente n/2 elementos en promedio, "
                        "lo que sigue siendo proporcional a n."
                    ),
                    "details": {
                        "expected_comparisons": "n/2",
                        "asymptotic_behavior": "O(n)",
                        "average_depth": "n/2"
                    },
                    "classification_confidence": 0.95,
                    "classification_reasoning": "Mismo patrón lineal para el caso promedio."
                }
            ],
            
            # ============================================================
            # DIAGRAMAS (RecurrenceTreeAgent)
            # ============================================================
            diagrams={
                "recursion_trees": {
                    "has_multiple_cases": True,
                    "trees": [
                        {
                            "case_type": "best_case",
                            "recurrence_equation": "T(n) = 1",
                            "tree_structure": [
                                {"level": 0, "position": 0, "label": "T(n)", "children_count": 0, "is_leaf": True}
                            ],
                            "tree_depth": "1",
                            "description": "Árbol trivial de un solo nodo: elemento encontrado en primera posición."
                        },
                        {
                            "case_type": "worst_case",
                            "recurrence_equation": "T(n) = T(n-1) + 1",
                            "tree_structure": [
                                {"level": 0, "position": 0, "label": "T(n)", "children_count": 1, "work": "O(1)"},
                                {"level": 1, "position": 0, "label": "T(n-1)", "children_count": 1, "work": "O(1)"},
                                {"level": 2, "position": 0, "label": "T(n-2)", "children_count": 1, "work": "O(1)"},
                                {"level": 3, "position": 0, "label": "T(n-3)", "children_count": 1, "work": "O(1)"},
                                {"level": 4, "position": 0, "label": "...", "children_count": 1, "work": "O(1)"},
                                {"level": 5, "position": 0, "label": "T(2)", "children_count": 1, "work": "O(1)"},
                                {"level": 6, "position": 0, "label": "T(1)", "children_count": 0, "work": "O(1)", "is_leaf": True}
                            ],
                            "tree_depth": "n",
                            "description": "Árbol lineal con reducción de 1 en cada nivel hasta llegar al caso base T(1). Hay n niveles."
                        },
                        {
                            "case_type": "average_case",
                            "recurrence_equation": "T(n) = T(n-1) + 1",
                            "tree_structure": [
                                {"level": 0, "position": 0, "label": "T(n)", "children_count": 1, "work": "O(1)"},
                                {"level": 1, "position": 0, "label": "T(n-1)", "children_count": 1, "work": "O(1)"},
                                {"level": 2, "position": 0, "label": "T(n-2)", "children_count": 1, "work": "O(1)"},
                                {"level": 3, "position": 0, "label": "...", "children_count": 1, "work": "O(1)"},
                                {"level": 4, "position": 0, "label": "T(1)", "children_count": 0, "work": "O(1)", "is_leaf": True}
                            ],
                            "tree_depth": "~n/2",
                            "description": "Árbol lineal con profundidad promedio n/2, representando el caso típico de búsqueda."
                        }
                    ],
                    "summary": "Se generaron 3 bosquejos de árboles de recursión (best, worst, average)."
                }
            },
            
            # ============================================================
            # INFORMACIÓN EXTRA
            # ============================================================
            extra={
                "has_multiple_cases": True,
                "analysis_details": "Análisis completo con 3 casos de búsqueda lineal recursiva",
                "algorithm_name": "Búsqueda Lineal Recursiva",
                "space_complexity": "O(n) por la pila de recursión en peor caso",
                "time_complexities": {
                    "best": "O(1)",
                    "worst": "O(n)",
                    "average": "O(n)"
                }
            }
        )

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
        Mock generado a partir de los logs de ejecución de Búsqueda Lineal Recursiva.
        Se ha corregido manualmente el error de JSON del agente de complejidad.
        """
        return Solution(
            type="Recursivo",
            algorithm_name="Busqueda Lineal Recursiva",
            algorithm_category="Búsqueda",
            
            # 1. Explicación General
            code_explain=(
                "El algoritmo recorre el arreglo recursivamente. "
                "En el mejor caso (elemento al inicio), retorna inmediatamente. "
                "En el peor caso (elemento al final o no existe), realiza n llamadas recursivas."
            ),

            # 2. Análisis Línea por Línea (Reconstruido correctamente)
            complexity_line_to_line="""=== MEJOR CASO ===
    busqueda_lineal_rec(A, x, i, n)
    begin
        if (i = n) then                    // c1
            return -1                      // 0
        else
            begin
                if (A[i] = x) then         // c2
                    return i               // c3
                else
                    return CALL...         // 0 (No ejecutado)
            end
    end

    index <-- CALL ...                     // c4
    return index                           // c5

    === PEOR CASO ===
    busqueda_lineal_rec(A, x, i, n)
    begin
        if (i = n) then                    // c1
            return -1                      // c2 (Solo en la última llamada)
        else
            begin
                if (A[i] = x) then         // c3
                    return i               // 0
                else
                    return CALL...         // T(n-1) + c4
            end
    end

    index <-- CALL ...                     // T(n)
    return index                           // c5

    === CASO PROMEDIO ===
    busqueda_lineal_rec(A, x, i, n)
    begin
        if (i = n) then                    // c1
            return -1                      // 0
        else
            begin
                if (A[i] = x) then         // c3
                    return i               // c4 (50% probabilidad)
                else
                    return CALL...         // T(n-1) + c5 (50% probabilidad)
            end
    end""",

            # 3. Notación Asintótica Final (Correcta según tus logs)
            asymptotic_notation={
                "best": "Ω(1)",
                "worst": "O(n)",
                "average": "Θ(n)",
                "explanation": "El algoritmo tiene una complejidad temporal de O(n) en el peor caso, ya que recorre todos los elementos una vez."
            },

            # 4. Ecuaciones Matemáticas (Extraídas de RecurrenceAnalysis)
            equation=[
                "T(n) = 1",                     # Mejor caso
                "T(n) = T(n-1) + 1",            # Peor caso
                "T(n) = T(n-1) + 1/2"           # Promedio (Simplificado)
            ],

            # 5. Métodos de Solución Usados
            method_solution=[
                "none",                         # Constante no requiere método
                "equation_characteristics",     # Ecuación Característica
                "intelligent_substitution"      # Sustitución Inteligente
            ],

            # 6. Resultados Matemáticos
            solution_equation=["1", "n", "O(n)"],

            # 7. Detalles Paso a Paso (Simplificados de tus logs)
            explain_solution_steps=[
                {
                    "case_type": "best_case",
                    "equation": "T(n) = 1",
                    "method": "none",
                    "complexity": "O(1)",
                    "explanation": "La expresión es constante, no depende de n.",
                    "steps": [
                        "Expresión: T(n) = 1",
                        "Término dominante: Constante",
                        "Simplificación: 1"
                    ]
                },
                {
                    "case_type": "worst_case",
                    "equation": "T(n) = T(n-1) + 1",
                    "method": "equation_characteristics",
                    "complexity": "O(n)",
                    "explanation": "Recurrencia lineal no homogénea de orden 1.",
                    "steps": [
                        "1. Identificar forma: T(n) - T(n-1) = 1",
                        "2. Ecuación característica: r - 1 = 0 -> r = 1",
                        "3. Solución homogénea: T_h(n) = C",
                        "4. Solución particular (por colisión con r=1): T_p(n) = An",
                        "5. Resolver A: An - A(n-1) = 1 -> A = 1",
                        "6. Solución general: T(n) = C + n",
                        "7. Condición inicial T(0)=1 -> C=1. Final: T(n) = n + 1"
                    ]
                },
                {
                    "case_type": "average_case",
                    "equation": "T(n) = T(n-1) + 1/2",
                    "method": "intelligent_substitution",
                    "complexity": "O(n)",
                    "explanation": "Sustitución iterativa revela patrón aritmético.",
                    "steps": [
                        "1. Expandir: T(n) = T(n-1) + 0.5",
                        "2. Sustituir: T(n) = (T(n-2) + 0.5) + 0.5 = T(n-2) + 2(0.5)",
                        "3. Patrón k-ésimo: T(n) = T(n-k) + k(0.5)",
                        "4. Caso base k=n: T(n) = T(0) + 0.5n",
                        "5. Complejidad: O(n)"
                    ]
                }
            ],

            # 8. Diagramas (Mermaid reconstruido de tus logs)
            diagrams={
                "recursion_trees": """graph TD
        %% Estilos
        classDef root fill:#f9f,stroke:#333,stroke-width:2px;
        classDef leaf fill:#dfd,stroke:#333,stroke-width:1px;
        classDef node fill:#fff,stroke:#333,stroke-width:1px;

        subgraph cluster_0 ["BEST: T(n) = 1"]
            direction TB
            T0_L0_P0("T(n)"):::root
        end

        subgraph cluster_1 ["WORST: T(n) = T(n-1) + 1"]
            direction TB
            T1_L0_P0("T(n)"):::root
            T1_L1_P0("T(n-1)"):::node
            T1_L0_P0 --> T1_L1_P0
            T1_L2_P0("T(n-2)"):::node
            T1_L1_P0 --> T1_L2_P0
            T1_L3_P0("T(n-3)"):::leaf
            T1_L2_P0 --> T1_L3_P0
        end

        subgraph cluster_2 ["AVERAGE: T(n) = T(n-1) + 1/2"]
            direction TB
            T2_L0_P0("T(n)"):::root
            T2_L1_P0("T(n-1)"):::node
            T2_L0_P0 --> T2_L1_P0
            T2_L2_P0("T(n-2)"):::node
            T2_L1_P0 --> T2_L2_P0
            T2_L3_P0("T(n-3)"):::leaf
            T2_L2_P0 --> T2_L3_P0
        end"""
            },
            
            # 9. Metadatos extra
            extra={
                "has_multiple_cases": True,
                "was_replicated": False
            }
        )
from app.parsers.parser import parser, TreeToDict
from app.models.solution import Solution
from lark import UnexpectedInput
# app/controllers/control_input.py

from app.parsers.parser import parse_pseudocode
from app.external_services.Agentes.NaturalLanguageToPseudocodeAgent import NaturalLanguageToPseudocodeAgent
from app.external_services.KnowledgeBase.AlgorithmKnowledgeBase import AlgorithmKnowledgeBase # <--- NUEVO


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
        Mock actualizado con la estructura EXACTA que retorna recursive.py.
        Basado en estructura_frontend.json generado por ejemplo_recursivo.py
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
                "T(n) = 1, T(1) = 1",
                "T(n) = T(n-1) + 1, T(1) = 1",
                "T(n) = T(n-1) + 1/2"
            ],

            # 5. Métodos de Solución Usados
            method_solution=[
                "none",
                "equation_characteristics",
                "intelligent_substitution"
            ],

            # 6. Resultados Matemáticos
            solution_equation=["1", "n", "O(n)"],

            # 7. Detalles Paso a Paso (Estructura COMPLETA como en JSON)
            explain_solution_steps=[
                {
                    "case_type": "best_case",
                    "equation": "T(n) = 1, T(1) = 1",
                    "original_equation": "T(n) = 1, T(1) = 1",
                    "simplification": None,
                    "method": "none",
                    "method_enum": "none",
                    "complexity": "1",
                    "steps": [
                        "Expresión: T(n) = 1, T(1) = 1",
                        "Término dominante: Constante",
                        "Simplificación: 1"
                    ],
                    "explanation": "La expresión es constante, no depende de n.",
                    "details": {
                        "complexity": "1",
                        "steps": [
                            "Expresión: T(n) = 1, T(1) = 1",
                            "Término dominante: Constante",
                            "Simplificación: 1"
                        ],
                        "explanation": "La expresión es constante, no depende de n.",
                        "applicable": True,
                        "method": "Análisis Directo",
                        "expression_type": "Constante",
                        "dominant_term": "1"
                    },
                    "classification_confidence": 1.0,
                    "classification_reasoning": "La ecuación T(n) = 1 no contiene ninguna llamada recursiva T(...). Por lo tanto, no es una recurrencia y se clasifica como NONE."
                },
                {
                    "case_type": "worst_case",
                    "equation": "T(n) = T(n-1) + 1, T(1) = 1",
                    "original_equation": "T(n) = T(n-1) + 1, T(1) = 1",
                    "simplification": None,
                    "method": "equation_characteristics",
                    "method_enum": "equation_characteristics",
                    "complexity": "n",
                    "steps": [
                        "1. Identificar forma: T(n) - T(n-1) = 1",
                        "2. Ecuación característica: r - 1 = 0 -> r = 1",
                        "3. Solución homogénea: T_h(n) = C",
                        "4. Solución particular (por colisión con r=1): T_p(n) = An",
                        "5. Resolver A: An - A(n-1) = 1 -> A = 1",
                        "6. Solución general: T(n) = C + n",
                        "7. Condición inicial T(1)=1 -> C=0. Final: T(n) = n"
                    ],
                    "explanation": "Recurrencia lineal no homogénea de orden 1.",
                    "details": {
                        "complexity": "n",
                        "steps": [
                            "**Solución Exacta (SymPy):** n",
                            "**Crecimiento asintótico:** n"
                        ],
                        "explanation": "1. **Identificación de la Recurrencia:** La recurrencia dada es T(n) = T(n-1) + 1. Es una recurrencia lineal no homogénea de primer orden.",
                        "applicable": True,
                        "method": "Ecuación Característica",
                        "final_solution": "n"
                    },
                    "classification_confidence": 0.9,
                    "classification_reasoning": "Recurrencia lineal de orden superior. Términos: T(n-1). Trabajo adicional: =+1,=1. La ecuación característica es ideal para resolver este tipo de recurrencia."
                },
                {
                    "case_type": "average_case",
                    "equation": "T(n) = T(n-1) + 1/2",
                    "original_equation": "T(n) = (1/(n+1)) × Σ[i=0 to n] T(i), donde T(i) = T(i-1) + 1, T(0) = 1",
                    "simplification": {
                        "original": "T(n) = (1/(n+1)) × Σ[i=0 to n] T(i), donde T(i) = T(i-1) + 1, T(0) = 1",
                        "simplified": "T(n) = T(n-1) + 1/2",
                        "steps": [
                            "Paso 1: Resolvemos T_int. Dada T(i) = T(i-1) + 1 con T(0)=1, la forma cerrada es T_int(i) = i + 1.",
                            "Paso 2: Evaluamos S(n) = sum[i=0 to n] T_int(i) = sum[i=0 to n] (i + 1).",
                            "Paso 3: Obtenemos la forma explícita de T(n). T(n) = (1/(n+1)) * S(n) = (n+2)/2.",
                            "Paso 4: Derivamos la recurrencia final g'(n) = T(n) - T(n-1) = 1/2."
                        ],
                        "explicit_form": "(n+2)/2",
                        "summation_resolved": "(n+1)(n+2)/2",
                        "confidence": 1.0,
                        "pattern_type": "linear"
                    },
                    "method": "intelligent_substitution",
                    "method_enum": "intelligent_substitution",
                    "complexity": "O(n)",
                    "steps": [
                        "1. Expandir: T(n) = T(n-1) + 1/2",
                        "2. Sustituir: T(n) = T(n-2) + 2 * (1/2)",
                        "3. Patrón k-ésimo: T(n) = T(n-k) + k * (1/2)",
                        "4. Caso base k=n-1: T(n) = T(1) + (n-1)/2",
                        "5. Complejidad: O(n)"
                    ],
                    "explanation": "Sustitución iterativa revela patrón aritmético.",
                    "details": {
                        "complexity": "O(n)",
                        "applicable": True,
                        "method": "Sustitución Inteligente",
                        "closed_form": "T(n) = T(1) + (n-1)/2",
                        "pattern": "T(n-k) + k * (1/2)"
                    },
                    "classification_confidence": 0.9,
                    "classification_reasoning": "Recurrencia lineal con UN solo término recursivo T(n-1). Trabajo adicional: =+1/2. La sustitución inteligente permite expandir iterativamente la recurrencia."
                }
            ],

            # 8. Diagramas (Mermaid con claves separadas por caso)
            diagrams={
                "tree_method_best_case": """graph TD
        %% Estilos
        classDef root fill:#f9f,stroke:#333,stroke-width:2px;
        classDef leaf fill:#dfd,stroke:#333,stroke-width:1px;
        classDef node fill:#fff,stroke:#333,stroke-width:1px;

        subgraph cluster_0 ["BEST: T(n) = 1, T(1) = 1"]
            direction TB
            T0_L0_P0("T(n)"):::root
        end""",
                "tree_method_worst_case": """graph TD
        %% Estilos
        classDef root fill:#f9f,stroke:#333,stroke-width:2px;
        classDef leaf fill:#dfd,stroke:#333,stroke-width:1px;
        classDef node fill:#fff,stroke:#333,stroke-width:1px;

        subgraph cluster_1 ["WORST: T(n) = T(n-1) + 1, T(1) = 1"]
            direction TB
            T1_L0_P0("T(n)"):::root
            T1_L1_P0("T(n-1)"):::node
            T1_L0_P0 --> T1_L1_P0
            T1_L2_P0("T(n-2)"):::node
            T1_L1_P0 --> T1_L2_P0
            T1_L3_P0("T(n-3)"):::leaf
            T1_L2_P0 --> T1_L3_P0
        end""",
                "tree_method_average_case": """graph TD
        %% Estilos
        classDef root fill:#f9f,stroke:#333,stroke-width:2px;
        classDef leaf fill:#dfd,stroke:#333,stroke-width:1px;
        classDef node fill:#fff,stroke:#333,stroke-width:1px;

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
                "analysis_details": [
                    {
                        "case_type": "best_case",
                        "equation": "T(n) = 1, T(1) = 1",
                        "method": "none",
                        "complexity": "1",
                        "classification_confidence": 1.0
                    },
                    {
                        "case_type": "worst_case",
                        "equation": "T(n) = T(n-1) + 1, T(1) = 1",
                        "method": "equation_characteristics",
                        "complexity": "n",
                        "classification_confidence": 0.9
                    },
                    {
                        "case_type": "average_case",
                        "equation": "T(n) = T(n-1) + 1/2",
                        "method": "intelligent_substitution",
                        "complexity": "O(n)",
                        "classification_confidence": 0.9
                    }
                ],
                "was_replicated": False
            }
        )
    @staticmethod
    def process_input(input_text: str, is_natural_language: bool = False):
        """
        Procesa la entrada usando estrategia RAG (Retrieval-Augmented Generation).
        """
        final_pseudocode = input_text
        source_origin = "strict_code" # strict_code, rag_retrieval, llm_translation

        # 🚀 RAMA LENGUAJE NATURAL
        if is_natural_language:
            print(f"\n🤖 [ControlInput] Procesando lenguaje natural: '{input_text[:30]}...'")
            
            # --- 1. INTENTO DE RECUPERACIÓN (RAG) ---
            kb = AlgorithmKnowledgeBase()
            # Threshold ajustable: 0.3-0.4 suele ser seguro para 'all-MiniLM-L6-v2'
            stored_code = kb.search_algorithm(input_text, threshold=0.7)
            
            if stored_code:
                # ¡ÉXITO! Encontramos el algoritmo perfecto en la BD
                final_pseudocode = stored_code
                source_origin = "rag_retrieval (ChromaDB)"
                print("✅ [ControlInput] Código recuperado de la Base de Conocimiento.")
            
            else:
                # --- 2. INTENTO DE GENERACIÓN (LLM) ---
                print("🤷 [ControlInput] No encontrado en BD. Invocando Agente Traductor (LLM)...")
                translator = NaturalLanguageToPseudocodeAgent(model_type="Gemini_Rapido")
                translation = translator.translate(input_text)
                
                if not translation.was_successful:
                    return {
                        "error": "No se pudo traducir la descripción.",
                        "details": translation.error_message
                    }
                
                final_pseudocode = translation.pseudocode
                source_origin = "llm_translation"
                print("✅ [ControlInput] Traducción por IA exitosa.")

        # 🚀 VALIDACIÓN SINTÁCTICA (Para todos los orígenes)
        parse_result = parse_pseudocode(final_pseudocode)
        
        if isinstance(parse_result, dict) and "error" in parse_result:
            return {
                "error": "Error de sintaxis en el código procesado.",
                "details": parse_result["error"],
                "generated_code": final_pseudocode if is_natural_language else None
            }

        return {
            "ast": parse_result,
            "pseudocode": final_pseudocode,
            "source_type": source_origin
        }

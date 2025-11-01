from typing import List


class AlgorithmPatterns:
    """
    Representa patrones algorítmicos conocidos.
    Ayuda a identificar y clasificar algoritmos basándose en estructuras comunes.
    """

    def __init__(self):
        self.pattern_name: str = ""
        self.description: str = ""
        self.complexity_hint: str = ""
        self.examples: List[str] = []

    def detect_pattern(self, tokens: List[str]) -> str:
        """
        Detecta el patrón algorítmico basado en los tokens del código.
        
        Args:
            tokens: Lista de tokens del pseudocódigo
            
        Returns:
            Nombre del patrón detectado
        """
        tokens_lower = [t.lower() for t in tokens]
        
        # Patrones comunes de algoritmos
        patterns = {
            "Búsqueda Binaria": ["while", "mitad", "izquierda", "derecha", "medio"],
            "Ordenamiento por Inserción": ["insertar", "ordenar", "while", "j"],
            "Ordenamiento por Burbuja": ["burbuja", "bubble", "swap", "intercambiar"],
            "Merge Sort": ["merge", "dividir", "mezclar", "mitad"],
            "Quick Sort": ["quick", "pivote", "pivot", "particion"],
            "Búsqueda Lineal": ["buscar", "recorrer", "encontrar", "for"],
            "DFS": ["dfs", "profundidad", "depth", "pila", "stack"],
            "BFS": ["bfs", "amplitud", "breadth", "cola", "queue"],
            "Programación Dinámica": ["dp", "memo", "tabla", "subproblema"],
            "Divide y Conquista": ["dividir", "divide", "conquista", "conquer"],
            "Greedy/Voraz": ["greedy", "voraz", "mejor", "optimo"],
            "Backtracking": ["backtrack", "retroceso", "vuelta"],
        }
        
        max_matches = 0
        detected_pattern = "Desconocido"
        
        for pattern_name, keywords in patterns.items():
            matches = sum(1 for keyword in keywords if keyword in tokens_lower)
            if matches > max_matches:
                max_matches = matches
                detected_pattern = pattern_name
        
        self.pattern_name = detected_pattern
        return detected_pattern

    def compare_with_known_patterns(self, algorithm) -> bool:
        """Compara con patrones conocidos (placeholder)."""
        return False

    def _load_pattern_info(self, pattern_name: str) -> None:
        """Carga información del patrón detectado."""
        patterns_info = {
            "Búsqueda Binaria": {
                "description": "Divide el espacio de búsqueda a la mitad en cada iteración",
                "complexity_hint": "O(log n)",
                "examples": ["Búsqueda en array ordenado"]
            },
            "Merge Sort": {
                "description": "Algoritmo de ordenamiento divide y conquista que divide el array, ordena recursivamente y luego mezcla",
                "complexity_hint": "O(n log n)",
                "examples": ["Ordenamiento estable", "Merge sort externo"]
            },
            "Quick Sort": {
                "description": "Algoritmo de ordenamiento que selecciona un pivote y particiona el array",
                "complexity_hint": "O(n log n) promedio, O(n²) peor caso",
                "examples": ["Ordenamiento in-place", "Selección de k-ésimo elemento"]
            },
            "Búsqueda Lineal": {
                "description": "Recorre secuencialmente todos los elementos hasta encontrar el objetivo",
                "complexity_hint": "O(n)",
                "examples": ["Búsqueda en array no ordenado", "Verificación de existencia"]
            },
            "DFS": {
                "description": "Recorrido en profundidad de grafos usando pila (o recursión)",
                "complexity_hint": "O(V + E) donde V=vértices, E=aristas",
                "examples": ["Detección de ciclos", "Componentes conexas", "Topological sort"]
            },
            "BFS": {
                "description": "Recorrido en amplitud de grafos usando cola",
                "complexity_hint": "O(V + E) donde V=vértices, E=aristas",
                "examples": ["Camino más corto sin pesos", "Nivel de nodos en árbol"]
            },
            "Programación Dinámica": {
                "description": "Resuelve problemas complejos dividiéndolos en subproblemas y almacenando resultados",
                "complexity_hint": "Varía según el problema (típicamente O(n²) o O(n³))",
                "examples": ["Fibonacci", "Knapsack", "Longest Common Subsequence", "Edit Distance"]
            },
            "Divide y Conquista": {
                "description": "Divide el problema en subproblemas, resuelve recursivamente y combina soluciones",
                "complexity_hint": "O(n log n) típicamente",
                "examples": ["Merge Sort", "Quick Sort", "Karatsuba Multiplication"]
            },
            "Greedy/Voraz": {
                "description": "Toma decisiones localmente óptimas esperando llegar a un óptimo global",
                "complexity_hint": "O(n log n) típicamente",
                "examples": ["Algoritmo de Dijkstra", "Huffman Coding", "Activity Selection"]
            },
            "Backtracking": {
                "description": "Explora todas las soluciones posibles retrocediendo cuando no hay progreso",
                "complexity_hint": "O(2^n) o O(n!) típicamente",
                "examples": ["N-Queens", "Sudoku Solver", "Subset Sum"]
            }
        }
        
        info = patterns_info.get(pattern_name, {})
        self.description = info.get("description", "Patrón no documentado")
        self.complexity_hint = info.get("complexity_hint", "O(?)")
        self.examples = info.get("examples", [])

    def suggest_optimization_strategies(self) -> List[str]:
        """Genera sugerencias de optimización según el patrón."""
        suggestions = []
        
        if "Cuadrático" in self.pattern_name or "O(n²)" in self.complexity_hint:
            suggestions.append("⚡ Considerar algoritmos O(n log n) como MergeSort o QuickSort")
            suggestions.append("💡 Evaluar si se puede usar hashing O(1) para búsquedas")
        
        elif "Lineal" in self.pattern_name or "O(n)" in self.complexity_hint:
            suggestions.append("✅ Complejidad lineal es óptima para recorrido completo")
            suggestions.append("💡 Si hay búsquedas frecuentes, considerar indexación")
        
        elif "Cúbico" in self.pattern_name or "O(n³)" in self.complexity_hint:
            suggestions.append("⚠️ Complejidad cúbica puede ser prohibitiva con n grande")
            suggestions.append("⚡ Revisar algoritmos de Strassen para multiplicación de matrices")
        
        else:
            suggestions.append("✅ Analizar si el patrón es necesario para el problema")
        
        return suggestions

# app/controllers/algorithm_type_controller.py
"""
from app.external_services.Agentes.AlgorithmTypeAgent import AlgorithmTypeAgent

def analyze_algorithm_type(pseudocode: str, ast: dict):
   
    Analiza el tipo del algoritmo usando el agente LLM AlgorithmTypeAgent.
    Recibe el pseudocódigo y el AST del parser.
    Retorna un diccionario con la respuesta del agente.
   
    try:
        agent = AlgorithmTypeAgent(model_type="Gemini_Rapido")

        print("\n=== 🤖 Invocando AlgorithmTypeAgent ===")
        response = agent.analyze_type(pseudocode=pseudocode)
        print(f"✅ Tipo detectado: {response.detected_type}")
        print(f"💡 Indicadores: {response.key_indicators}")
        print(f"📈 Confianza: {response.confidence_level}")
        print(f"🧩 Justificación: {response.justification}")

        return response.model_dump()

    except Exception as e:
        print("⚠️ Error al analizar el tipo de algoritmo:", e)
        return {"error": str(e)}

"""
"""
Clasificador Determinista Binario: ITERATIVO vs RECURSIVO
Análisis estructural del AST con precisión del 100%

REGLA SIMPLE:
- Si tiene recursión (directa o indirecta) → RECURSIVO
- Si NO tiene recursión → ITERATIVO
"""

from typing import Dict, List, Any, Set, Optional


class AlgorithmClassifier:
    """
    Clasificador binario determinista.
    
    Output:
        - "iterativo": Sin recursión (puede tener bucles o ser secuencial)
        - "recursivo": Con recursión (directa, indirecta, con o sin bucles)
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reinicia el estado para nuevo análisis"""
        self.has_recursion = False
        self.procedure_names = set()
        self.recursive_procedures = set()
        self.call_graph = {}
        self.current_procedure = None
    
    def classify(self, ast: List[Dict], pseudocode: str = "") -> Dict:
        """
        Clasificación binaria del algoritmo.
        
        Args:
            ast: Estructura del árbol sintáctico abstracto
            pseudocode: Código fuente (opcional)
        
        Returns:
            {
                "algorithm_type": "iterativo" | "recursivo",
                "has_recursion": bool,
                "recursive_functions": List[str],
                "confidence": 1.0,
                "reasoning": str
            }
        """
        
        self.reset()
        
        # PASO 1: Registrar todos los procedimientos
        self._register_procedures(ast)
        
        # PASO 2: Analizar y detectar recursión
        self._analyze_recursion(ast)
        
        # PASO 3: Detectar recursión indirecta
        self._detect_indirect_recursion()
        
        # PASO 4: Clasificar (SIMPLE: ¿Hay recursión? → recursivo, sino → iterativo)
        return self._make_classification()
    
    def _register_procedures(self, node: Any):
        """Registra todos los nombres de funciones/procedimientos"""
        if isinstance(node, dict):
            if node.get("type") == "procedure_def":
                proc_name = node.get("name")
                if proc_name:
                    self.procedure_names.add(proc_name)
            
            for value in node.values():
                self._register_procedures(value)
        
        elif isinstance(node, list):
            for item in node:
                self._register_procedures(item)
    
    def _analyze_recursion(self, node: Any, parent_proc: Optional[str] = None):
        """Analiza el AST buscando llamadas recursivas"""
        if isinstance(node, dict):
            node_type = node.get("type")
            
            # Cambiar contexto si entramos a un procedimiento
            if node_type == "procedure_def":
                proc_name = node.get("name")
                self.current_procedure = proc_name
                parent_proc = proc_name
                
                if proc_name not in self.call_graph:
                    self.call_graph[proc_name] = []
            
            # Detectar llamadas a funciones
            if node_type in ["call", "call_expr", "call_stmt"]:
                called_func = node.get("name")
                
                if called_func:
                    # RECURSIÓN DIRECTA: función se llama a sí misma
                    if parent_proc and called_func == parent_proc:
                        self.has_recursion = True
                        self.recursive_procedures.add(parent_proc)
                    
                    # Registrar en grafo para detectar recursión indirecta
                    if parent_proc:
                        if parent_proc not in self.call_graph:
                            self.call_graph[parent_proc] = []
                        self.call_graph[parent_proc].append(called_func)
            
            # Continuar recursivamente
            for value in node.values():
                self._analyze_recursion(value, parent_proc)
        
        elif isinstance(node, list):
            for item in node:
                self._analyze_recursion(item, parent_proc)
    
    def _detect_indirect_recursion(self):
        """
        Detecta recursión indirecta mediante búsqueda de ciclos en el grafo.
        Ejemplo: A → B → C → A
        """
        
        def has_cycle_dfs(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            """DFS para detectar ciclos"""
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.call_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle_dfs(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    # Ciclo encontrado = recursión indirecta
                    self.recursive_procedures.add(neighbor)
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for proc in self.procedure_names:
            if proc not in visited:
                if has_cycle_dfs(proc, visited, set()):
                    self.has_recursion = True
    
    def _make_classification(self) -> Dict:
        """
        Lógica de decisión SIMPLE:
        - ¿Hay recursión? → RECURSIVO
        - ¿No hay recursión? → ITERATIVO
        """
        
        if self.has_recursion:
            algorithm_type = "recursivo"
            reasoning = (
                f"Recursión detectada en: {sorted(list(self.recursive_procedures))}. "
                f"El algoritmo se clasifica como RECURSIVO."
            )
        else:
            algorithm_type = "iterativo"
            reasoning = (
                "No se detectó recursión. "
                "El algoritmo se clasifica como ITERATIVO (puede contener bucles o ser secuencial)."
            )
        
        return {
            "algorithm_type": algorithm_type,
            "has_recursion": self.has_recursion,
            "recursive_functions": sorted(list(self.recursive_procedures)),
            "confidence": 1.0,
            "reasoning": reasoning
        }


# ============================================================================
# 🧪 TESTS
# ============================================================================

def test_fibonacci_recursivo():
    """Fibonacci recursivo → RECURSIVO"""
    ast = [{
        'type': 'procedure_def',
        'name': 'fibonacci',
        'params': ['n'],
        'body': [
            {'type': 'if', 'cond': {'lhs': 'n', 'op': '<=', 'rhs': 1},
             'then': [{'type': 'return', 'value': 'n'}],
             'else': [
                 {'type': 'call', 'name': 'fibonacci', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}]},
                 {'type': 'call', 'name': 'fibonacci', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 2}]}
             ]}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    assert result["has_recursion"] == True
    print(f"✅ Fibonacci: {result['algorithm_type'].upper()}")


def test_bubble_sort_iterativo():
    """Bubble Sort con bucles → ITERATIVO"""
    ast = [{
        'type': 'procedure_def',
        'name': 'bubbleSort',
        'params': ['arr', 'n'],
        'body': [
            {'type': 'for_loop', 'var': 'i', 'start': 0, 'end': 'n',
             'body': [
                 {'type': 'for_loop', 'var': 'j', 'start': 0, 'end': 'n',
                  'body': [{'type': 'assign', 'lvalue': 'temp', 'value': 'x'}]}
             ]}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "iterativo"
    assert result["has_recursion"] == False
    print(f"✅ Bubble Sort: {result['algorithm_type'].upper()}")


def test_merge_sort_recursivo():
    """Merge Sort (recursivo con bucles internos) → RECURSIVO"""
    ast = [
        {
            'type': 'procedure_def',
            'name': 'mergeSort',
            'params': ['arr', 'left', 'right'],
            'body': [
                {'type': 'call', 'name': 'mergeSort', 'args': ['arr', 'left', 'mid']},
                {'type': 'call', 'name': 'mergeSort', 'args': ['arr', 'mid', 'right']},
                {'type': 'call', 'name': 'merge', 'args': ['arr', 'left', 'mid', 'right']}
            ]
        },
        {
            'type': 'procedure_def',
            'name': 'merge',
            'params': ['arr', 'left', 'mid', 'right'],
            'body': [
                {'type': 'while_loop', 'cond': {}, 'body': []}
            ]
        }
    ]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ Merge Sort: {result['algorithm_type'].upper()} (tiene bucles pero la recursión domina)")


def test_recursion_indirecta():
    """isEven/isOdd (recursión mutua) → RECURSIVO"""
    ast = [
        {
            'type': 'procedure_def',
            'name': 'isEven',
            'params': ['n'],
            'body': [
                {'type': 'call', 'name': 'isOdd', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}]}
            ]
        },
        {
            'type': 'procedure_def',
            'name': 'isOdd',
            'params': ['n'],
            'body': [
                {'type': 'call', 'name': 'isEven', 'args': [{'op': '-', 'lhs': 'n', 'rhs': 1}]}
            ]
        }
    ]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "recursivo"
    print(f"✅ Recursión Indirecta: {result['algorithm_type'].upper()}")


def test_secuencial_iterativo():
    """Swap (sin bucles ni recursión) → ITERATIVO"""
    ast = [{
        'type': 'procedure_def',
        'name': 'swap',
        'params': ['a', 'b'],
        'body': [
            {'type': 'assign', 'lvalue': 'temp', 'value': 'a'},
            {'type': 'assign', 'lvalue': 'a', 'value': 'b'},
            {'type': 'assign', 'lvalue': 'b', 'value': 'temp'}
        ]
    }]
    
    classifier = AlgorithmClassifier()
    result = classifier.classify(ast)
    
    assert result["algorithm_type"] == "iterativo"
    print(f"✅ Swap Secuencial: {result['algorithm_type'].upper()}")


def run_all_tests():
    print("="*60)
    print("🧪 TESTS - CLASIFICADOR BINARIO (ITERATIVO/RECURSIVO)")
    print("="*60 + "\n")
    
    test_fibonacci_recursivo()
    test_bubble_sort_iterativo()
    test_merge_sort_recursivo()
    test_recursion_indirecta()
    test_secuencial_iterativo()
    
    print("\n" + "="*60)
    print("✅ TODOS LOS TESTS PASARON")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
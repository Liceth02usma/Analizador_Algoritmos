"""
Controlador para el análisis de algoritmos recursivos.

Este módulo implementa ControlRecursive que orquesta el análisis completo
de algoritmos recursivos a partir del árbol sintáctico parseado.
"""

from typing import Dict, Any, Optional, List, Union
from lark import Tree

from app.controllers.control_algorithm import ControlAlgorithm
from app.models.recursive import Recursive
from app.models.complexity import Complexity
from app.models.tree import Tree as RecursionTree
from app.models.recurrence_method import RecurrenceMethods
from app.models.flowdiagram import FlowDiagram
from app.models.algorithm_pattern import AlgorithmPatterns
from app.parsers.parser import parser, TreeToDict


class ControlRecursive(ControlAlgorithm):
    """
    Controlador para el análisis de algoritmos recursivos.
    
    Funcionalidades:
    - Detecta casos base y recursivos
    - Extrae relaciones de recurrencia
    - Resuelve la recurrencia usando múltiples métodos
    - Calcula la profundidad de recursión
    - Construye árboles de recursión
    - Detecta patrones recursivos conocidos
    - Genera diagramas de flujo y árboles
    - Exporta resultados en múltiples formatos
    
    Attributes:
        base_cases (int): Número de casos base detectados
        recursion_depth (int): Profundidad máxima de recursión estimada
        recurrence_relation (str): Relación de recurrencia extraída
        complexity (Complexity): Objeto con análisis de complejidad
        algorithm (Recursive): Instancia del modelo Recursive
        recursive_calls (List[Dict]): Detalles de las llamadas recursivas
        base_case_details (List[Dict]): Detalles de los casos base
        pattern (Dict): Patrón algorítmico detectado
    """
    
    def __init__(self):
        """Inicializa el controlador recursivo."""
        super().__init__()  # Inicializa tree y complexity de la clase base
        self.base_cases: int = 0
        self.recursion_depth: int = 0
        self.recurrence_relation: str = ""
        self.algorithm: Optional[Recursive] = None
        self.recursive_calls: List[Dict[str, Any]] = []
        self.base_case_details: List[Dict[str, Any]] = []
        self.pattern: Dict[str, Any] = {}
        self.recursion_tree: Optional[RecursionTree] = None
        self.recurrence_solver: Optional[RecurrenceMethods] = None
    
    def analyze(self, tree: Tree, **kwargs) -> None:
        """
        Implementación del método abstracto analyze.
        
        Analiza el algoritmo recursivo a partir del árbol sintáctico.
        Este método actúa como wrapper para analyze_from_parsed_tree.
        
        Args:
            tree: Árbol sintáctico parseado
            **kwargs: Puede incluir 'algorithm_name', 'pseudocode', 'structure'
        """
        algorithm_name = kwargs.get('algorithm_name', 'UnknownAlgorithm')
        pseudocode = kwargs.get('pseudocode', '')
        structure = kwargs.get('structure', None)
        
        # Validar el árbol
        if not self._validate_tree(tree):
            raise ValueError("El árbol sintáctico proporcionado no es válido")
        
        # Almacenar el árbol en la clase base
        self.tree = tree
        
        # Realizar el análisis
        self.analyze_from_parsed_tree(
            algorithm_name=algorithm_name,
            pseudocode=pseudocode,
            parsed_tree=tree,
            structure=structure
        )
    
    def analyze_from_parsed_tree(
        self,
        algorithm_name: str,
        pseudocode: str,
        parsed_tree: Optional[Tree] = None,
        structure: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analiza un algoritmo recursivo a partir del árbol parseado.
        
        Este es el método principal que orquesta todo el análisis:
        1. Parsea el código si no se proporciona el árbol
        2. Crea instancia del modelo Recursive
        3. Extrae la relación de recurrencia
        4. Detecta casos base y llamadas recursivas
        5. Calcula la complejidad
        6. Resuelve la recurrencia con múltiples métodos
        7. Construye el árbol de recursión
        8. Detecta patrones
        9. Genera diagramas
        
        Args:
            algorithm_name: Nombre del algoritmo
            pseudocode: Código fuente en pseudocódigo
            parsed_tree: Árbol sintáctico pre-parseado (opcional)
            structure: Estructura dict pre-transformada (opcional)
        
        Returns:
            Dict con todos los resultados del análisis:
            {
                'algorithm': {nombre, tipo, código},
                'analysis': {casos_base, llamadas_recursivas, profundidad, relación},
                'complexity': {tiempo, espacio, notaciones},
                'recurrence_solutions': {métodos de resolución},
                'recursion_tree': {representación del árbol},
                'pattern': {patrón detectado},
                'diagrams': {diagramas generados},
                'summary': texto resumen,
                'optimizations': sugerencias
            }
        """
        # 1. Parsear si es necesario
        if parsed_tree is None:
            parsed_tree = parser.parse(pseudocode)
        
        if structure is None:
            transformer = TreeToDict()
            structure = transformer.transform(parsed_tree)
        
        # 2. Crear instancia del modelo Recursive
        self.algorithm = Recursive(algorithm_name, pseudocode)
        
        # 3. Extraer relación de recurrencia
        self.extract_recurrence(structure)
        
        # 4. Detectar casos base y llamadas recursivas
        self.detect_base_cases(structure)
        self.detect_recursive_calls(structure)
        
        # 5. Calcular complejidad
        self.calculate_complexity()
        
        # 6. Resolver recurrencia con múltiples métodos
        solutions = self.solve_recurrence_with_methods()
        
        # 7. Construir árbol de recursión
        self.build_recursion_tree()
        
        # 8. Detectar patrón
        self.detect_pattern()
        
        # 9. Generar diagramas
        diagrams = self.generate_diagrams()
        
        # 10. Exportar resultados completos
        return self.export_results(solutions, diagrams)
    
    def extract_recurrence(self, structure: Union[Dict, List, Tree]) -> None:
        """
        Extrae la relación de recurrencia del algoritmo.
        
        Analiza el árbol sintáctico para encontrar:
        - Llamadas recursivas y sus argumentos
        - Patrones de reducción del problema (n/2, n-1, etc.)
        - Trabajo no recursivo (operaciones constantes, lineales, etc.)
        
        Args:
            structure: Estructura del código (dict, list o Tree)
        """
        if self.algorithm:
            self.recurrence_relation = self.algorithm.extract_recurrence()
            
            # Analizar llamadas recursivas en la estructura
            self._analyze_recurrence_pattern(structure)
    
    def _analyze_recurrence_pattern(
        self, 
        node: Union[Dict, List, Tree], 
        depth: int = 0
    ) -> None:
        """
        Analiza el patrón de la recurrencia recursivamente.
        
        Args:
            node: Nodo actual del AST
            depth: Profundidad actual en el árbol
        """
        if isinstance(node, dict):
            # Buscar llamadas CALL (recursivas)
            if node.get('type') == 'call':
                call_info = {
                    'depth': depth,
                    'function': node.get('name', 'unknown'),
                    'arguments': node.get('arguments', [])
                }
                
                # Analizar los argumentos para detectar el patrón
                args = node.get('arguments', [])
                if args:
                    call_info['pattern'] = self._detect_argument_pattern(args)
                
                # No agregar si ya existe (evitar duplicados)
                if call_info not in self.recursive_calls:
                    self.recursive_calls.append(call_info)
            
            # Recursión en los valores
            for value in node.values():
                self._analyze_recurrence_pattern(value, depth + 1)
        
        elif isinstance(node, list):
            for item in node:
                self._analyze_recurrence_pattern(item, depth)
    
    def _detect_argument_pattern(self, arguments: List) -> str:
        """
        Detecta el patrón de reducción en los argumentos.
        
        Args:
            arguments: Lista de argumentos de la llamada recursiva
        
        Returns:
            Patrón detectado: 'divide_by_2', 'subtract_1', 'custom', etc.
        """
        # Convertir argumentos a string para análisis
        args_str = str(arguments).lower()
        
        if '/2' in args_str or '/ 2' in args_str or 'div 2' in args_str:
            return 'divide_by_2'
        elif '-1' in args_str or '- 1' in args_str:
            return 'subtract_1'
        elif '-2' in args_str or '- 2' in args_str:
            return 'subtract_2'
        elif '/3' in args_str or '/ 3' in args_str:
            return 'divide_by_3'
        else:
            return 'custom'
    
    def detect_base_cases(self, structure: Union[Dict, List, Tree]) -> None:
        """
        Detecta los casos base del algoritmo recursivo.
        
        Los casos base son condiciones que terminan la recursión,
        típicamente encontrados en estructuras if-return.
        
        Args:
            structure: Estructura del código
        """
        if self.algorithm:
            base_cases = self.algorithm.extract_base_case()
            self.base_cases = len(base_cases)
            self.base_case_details = base_cases
    
    def detect_recursive_calls(self, structure: Union[Dict, List, Tree]) -> None:
        """
        Detecta y cuenta las llamadas recursivas.
        
        Args:
            structure: Estructura del código
        """
        # Ya se analizan en _analyze_recurrence_pattern
        # Aquí calculamos la profundidad estimada
        if self.recursive_calls:
            # La profundidad se estima según el patrón
            patterns = [call.get('pattern', '') for call in self.recursive_calls]
            
            if 'divide_by_2' in patterns:
                self.recursion_depth = 'log(n)'  # O(log n)
            elif 'subtract_1' in patterns:
                self.recursion_depth = 'n'  # O(n)
            elif 'subtract_2' in patterns:
                self.recursion_depth = 'n/2'  # O(n/2)
            else:
                self.recursion_depth = 'variable'
    
    def calculate_complexity(self) -> None:
        """
        Calcula la complejidad del algoritmo recursivo.
        
        Utiliza el modelo Recursive para estimar la complejidad
        basándose en la relación de recurrencia.
        """
        if self.algorithm:
            self.complexity = self.algorithm.estimate_complexity()
            
            # Enriquecer con información adicional
            if self.complexity and hasattr(self.complexity, 'reasoning'):
                reasoning = f"\n\nAnálisis de Recursión:\n"
                reasoning += f"- Casos base detectados: {self.base_cases}\n"
                reasoning += f"- Llamadas recursivas: {len(self.recursive_calls)}\n"
                reasoning += f"- Relación de recurrencia: {self.recurrence_relation}\n"
                reasoning += f"- Profundidad estimada: {self.recursion_depth}\n"
                
                if hasattr(self.complexity, 'reasoning'):
                    self.complexity.reasoning += reasoning
    
    def solve_recurrence(self, method: str) -> str:
        """
        Resuelve la recurrencia usando el método especificado.
        
        Este método es requerido por la interfaz ControlAlgorithm y actúa
        como wrapper para métodos específicos de resolución.
        
        Args:
            method: Método a utilizar ('substitution', 'master_theorem', 
                   'recursion_tree', o 'all' para todos)
        
        Returns:
            String con la solución de la recurrencia
        """
        if not self.recurrence_relation:
            return "No se ha extraído una relación de recurrencia"
        
        # Si se pide 'all', usar solve_recurrence_with_methods
        if method == 'all':
            solutions = self.solve_recurrence_with_methods()
            result = []
            for m, sol in solutions.items():
                result.append(f"{m}: {sol}")
            return "\n".join(result)
        
        # Crear solver si no existe
        if not self.recurrence_solver:
            self.recurrence_solver = RecurrenceMethods(self.recurrence_relation)
        
        # Resolver según el método solicitado
        try:
            if method == 'substitution':
                return self.recurrence_solver.substitution_method()
            elif method == 'master_theorem':
                return self.recurrence_solver.master_theorem()
            elif method == 'recursion_tree':
                return self.recurrence_solver.recursion_tree_method()
            else:
                return f"Método desconocido: {method}. Use: substitution, master_theorem, recursion_tree, o all"
        except Exception as e:
            return f"Error al resolver con {method}: {str(e)}"
    
    def solve_recurrence_with_methods(self) -> Dict[str, Any]:
        """
        Resuelve la recurrencia usando múltiples métodos.
        
        Returns:
            Dict con soluciones de cada método:
            {
                'substitution': resultado,
                'master_theorem': resultado,
                'recursion_tree': resultado
            }
        """
        solutions = {}
        
        if self.recurrence_relation:
            # Crear instancia del solver
            self.recurrence_solver = RecurrenceMethods(self.recurrence_relation)
            
            # Método de sustitución
            try:
                solutions['substitution'] = self.recurrence_solver.substitution_method()
            except Exception as e:
                solutions['substitution'] = f"No aplicable: {str(e)}"
            
            # Teorema maestro
            try:
                solutions['master_theorem'] = self.recurrence_solver.master_theorem()
            except Exception as e:
                solutions['master_theorem'] = f"No aplicable: {str(e)}"
            
            # Método del árbol de recursión
            try:
                solutions['recursion_tree_method'] = self.recurrence_solver.recursion_tree_method()
            except Exception as e:
                solutions['recursion_tree_method'] = f"No aplicable: {str(e)}"
        
        return solutions
    
    def build_recursion_tree(self) -> None:
        """
        Construye la representación del árbol de recursión.
        """
        if self.recurrence_relation:
            # Extraer parámetros de la relación
            # Ejemplo: T(n) = 2T(n/2) + n
            # a=2, b=2, f(n)=n
            
            # Por simplicidad, usamos valores por defecto
            # En producción, se parsearía la relación
            a, b = self._extract_recurrence_params()
            
            self.recursion_tree = RecursionTree(
                recurrence_relation=self.recurrence_relation,
                branching_factor=a,
                reduction_factor=b
            )
    
    def _extract_recurrence_params(self) -> tuple:
        """
        Extrae parámetros a y b de la recurrencia.
        
        Returns:
            Tupla (a, b) donde:
            - a: número de llamadas recursivas
            - b: factor de reducción
        """
        # Contar llamadas recursivas (a)
        a = len(self.recursive_calls) if self.recursive_calls else 1
        
        # Detectar factor de reducción (b)
        b = 2  # Por defecto
        if self.recursive_calls:
            patterns = [call.get('pattern', '') for call in self.recursive_calls]
            if 'divide_by_2' in patterns:
                b = 2
            elif 'divide_by_3' in patterns:
                b = 3
            elif 'subtract_1' in patterns:
                b = 1
        
        return (a, b)
    
    def detect_pattern(self) -> None:
        """
        Detecta el patrón algorítmico recursivo.
        """
        if self.algorithm:
            pattern_detector = AlgorithmPatterns(
                algorithm_type='recursive',
                code=self.algorithm.code
            )
            
            # Detectar basándose en la relación de recurrencia
            if 'T(n) = 2T(n/2)' in self.recurrence_relation:
                detected = pattern_detector.match_pattern('Divide y Conquista (Binario)')
            elif 'T(n) = T(n-1)' in self.recurrence_relation:
                detected = pattern_detector.match_pattern('Recursión Lineal')
            elif 'T(n) = T(n-1) + T(n-2)' in self.recurrence_relation:
                detected = pattern_detector.match_pattern('Fibonacci (Recursión Múltiple)')
            else:
                detected = pattern_detector.match_pattern('Recursión General')
            
            self.pattern = {
                'name': detected['name'],
                'complexity_hint': detected['complexity_hint'],
                'characteristics': detected['characteristics']
            }
    
    def generate_diagrams(self) -> Dict[str, Any]:
        """
        Genera diagramas de flujo y árbol de recursión.
        
        Returns:
            Dict con los diagramas generados
        """
        diagrams = {}
        
        if self.algorithm:
            # Diagrama de flujo
            flow = FlowDiagram(
                algorithm_name=self.algorithm.name,
                code=self.algorithm.code
            )
            
            diagrams['flowchart'] = {
                'mermaid': flow.to_mermaid(),
                'text': flow.to_text_representation()
            }
        
        # Árbol de recursión
        if self.recursion_tree:
            diagrams['recursion_tree'] = {
                'structure': self.recursion_tree.build_tree(depth=4),
                'visualization': self.recursion_tree.visualize()
            }
        
        return diagrams
    
    def export_results(
        self,
        solutions: Dict[str, Any],
        diagrams: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Exporta todos los resultados del análisis.
        
        Args:
            solutions: Soluciones de la recurrencia
            diagrams: Diagramas generados
        
        Returns:
            Dict completo con todos los resultados
        """
        if not self.algorithm or not self.complexity:
            return {
                'error': 'No se ha realizado el análisis'
            }
        
        return {
            'algorithm': {
                'name': self.algorithm.name,
                'type': 'Recursivo',
                'code': self.algorithm.code,
                'language': 'pseudocode'
            },
            'analysis': {
                'base_cases': self.base_cases,
                'base_case_details': self.base_case_details,
                'recursive_calls': len(self.recursive_calls),
                'recursive_call_details': self.recursive_calls,
                'recursion_depth': self.recursion_depth,
                'recurrence_relation': self.recurrence_relation
            },
            'complexity': {
                'time': {
                    'worst_case': self.complexity.time_complexity.worst_case,
                    'best_case': self.complexity.time_complexity.best_case,
                    'average_case': self.complexity.time_complexity.average_case
                },
                'space': {
                    'worst_case': self.complexity.space_complexity.worst_case,
                    'best_case': self.complexity.space_complexity.best_case
                },
                'notation': {
                    'big_o': self.complexity.big_o_notation,
                    'big_omega': self.complexity.big_omega_notation,
                    'big_theta': self.complexity.big_theta_notation
                },
                'reasoning': getattr(self.complexity, 'reasoning', '')
            },
            'recurrence_solutions': solutions,
            'recursion_tree': diagrams.get('recursion_tree', {}),
            'pattern': self.pattern,
            'diagrams': diagrams,
            'summary': self._generate_summary(),
            'optimizations': self._suggest_optimizations()
        }
    
    def _generate_summary(self) -> str:
        """Genera un resumen textual del análisis."""
        summary = f"Análisis de Algoritmo Recursivo\n"
        summary += f"{'=' * 40}\n\n"
        
        if self.algorithm:
            summary += f"Algoritmo: {self.algorithm.name}\n"
        
        summary += f"Casos Base: {self.base_cases}\n"
        summary += f"Llamadas Recursivas: {len(self.recursive_calls)}\n"
        summary += f"Relación de Recurrencia: {self.recurrence_relation}\n"
        summary += f"Profundidad de Recursión: {self.recursion_depth}\n\n"
        
        if self.complexity:
            summary += f"Complejidad Temporal (Peor Caso): {self.complexity.time_complexity.worst_case}\n"
            summary += f"Complejidad Espacial: {self.complexity.space_complexity.worst_case}\n\n"
        
        if self.pattern:
            summary += f"Patrón Detectado: {self.pattern.get('name', 'Desconocido')}\n"
        
        return summary
    
    def _suggest_optimizations(self) -> List[str]:
        """Genera sugerencias de optimización."""
        suggestions = []
        
        # Memoización para recursión con subproblemas repetidos
        if 'T(n-1) + T(n-2)' in self.recurrence_relation:
            suggestions.append(
                "⚡ Usar memoización o programación dinámica para evitar "
                "recalcular subproblemas (ej: Fibonacci)"
            )
        
        # Tail recursion
        if self.base_cases > 0 and len(self.recursive_calls) == 1:
            suggestions.append(
                "🔄 Considerar optimización de tail recursion "
                "(convertir a iterativo si el lenguaje no optimiza)"
            )
        
        # Profundidad alta
        if isinstance(self.recursion_depth, str) and 'n' in self.recursion_depth:
            suggestions.append(
                "⚠️ Profundidad de recursión O(n) puede causar stack overflow "
                "con entradas grandes. Considerar versión iterativa."
            )
        
        # Divide y conquista sin combinar
        if len(self.recursive_calls) > 1 and 'divide' in str(self.pattern).lower():
            suggestions.append(
                "✅ Algoritmo divide y conquista eficiente. "
                "Asegurar que la fase de combinación sea óptima."
            )
        
        return suggestions
    
    def get_complexity_report(self, format: str = "text") -> str:
        """
        Obtiene el reporte de complejidad en el formato especificado.
        
        Args:
            format: 'text', 'json' o 'markdown'
        
        Returns:
            String con el reporte formateado
        """
        if not self.complexity:
            return "No hay análisis de complejidad disponible"
        
        if format == "json":
            import json
            return json.dumps({
                'time_complexity': {
                    'worst_case': self.complexity.time_complexity.worst_case,
                    'best_case': self.complexity.time_complexity.best_case,
                    'average_case': self.complexity.time_complexity.average_case
                },
                'space_complexity': {
                    'worst_case': self.complexity.space_complexity.worst_case,
                    'best_case': self.complexity.space_complexity.best_case
                },
                'recurrence': self.recurrence_relation,
                'recursion_depth': str(self.recursion_depth)
            }, indent=2)
        
        elif format == "markdown":
            md = "# Análisis de Complejidad - Recursivo\n\n"
            md += f"## Complejidad Temporal\n"
            md += f"- **Peor Caso**: `{self.complexity.time_complexity.worst_case}`\n"
            md += f"- **Mejor Caso**: `{self.complexity.time_complexity.best_case}`\n"
            md += f"- **Caso Promedio**: `{self.complexity.time_complexity.average_case}`\n\n"
            md += f"## Complejidad Espacial\n"
            md += f"- **Peor Caso**: `{self.complexity.space_complexity.worst_case}`\n\n"
            md += f"## Recursión\n"
            md += f"- **Relación**: `{self.recurrence_relation}`\n"
            md += f"- **Profundidad**: `{self.recursion_depth}`\n"
            md += f"- **Casos Base**: {self.base_cases}\n"
            md += f"- **Llamadas Recursivas**: {len(self.recursive_calls)}\n"
            return md
        
        else:  # text
            report = "=" * 50 + "\n"
            report += "  ANÁLISIS DE COMPLEJIDAD - RECURSIVO\n"
            report += "=" * 50 + "\n\n"
            report += f"Complejidad Temporal (Peor Caso): {self.complexity.time_complexity.worst_case}\n"
            report += f"Complejidad Temporal (Mejor Caso): {self.complexity.time_complexity.best_case}\n"
            report += f"Complejidad Espacial: {self.complexity.space_complexity.worst_case}\n"
            report += f"\nRelación de Recurrencia: {self.recurrence_relation}\n"
            report += f"Profundidad de Recursión: {self.recursion_depth}\n"
            report += f"Casos Base: {self.base_cases}\n"
            report += f"Llamadas Recursivas: {len(self.recursive_calls)}\n"
            return report
    
    def get_recursion_summary(self) -> str:
        """
        Obtiene un resumen detallado de la recursión.
        
        Returns:
            String con el resumen de la estructura recursiva
        """
        summary = "\n" + "=" * 60 + "\n"
        summary += "  RESUMEN DE ESTRUCTURA RECURSIVA\n"
        summary += "=" * 60 + "\n\n"
        
        summary += f"Total de casos base: {self.base_cases}\n"
        summary += f"Total de llamadas recursivas: {len(self.recursive_calls)}\n"
        summary += f"Relación de recurrencia: {self.recurrence_relation}\n"
        summary += f"Profundidad estimada: {self.recursion_depth}\n\n"
        
        # Detalles de casos base
        if self.base_case_details:
            summary += "--- Casos Base Detectados ---\n"
            for i, base in enumerate(self.base_case_details, 1):
                summary += f"  {i}. Condición: {base.get('condition', 'N/A')}\n"
                summary += f"     Retorno: {base.get('return_value', 'N/A')}\n"
        
        # Detalles de llamadas recursivas
        if self.recursive_calls:
            summary += "\n--- Llamadas Recursivas ---\n"
            for i, call in enumerate(self.recursive_calls, 1):
                summary += f"  {i}. Función: {call.get('function', 'N/A')}\n"
                summary += f"     Patrón: {call.get('pattern', 'N/A')}\n"
                summary += f"     Profundidad: {call.get('depth', 0)}\n"
        
        return summary
    
    def reset(self) -> None:
        """
        Reinicia el estado del controlador.
        
        Implementación del método abstracto que limpia todos los datos
        del análisis previo, incluyendo los atributos de la clase base.
        """
        # Reiniciar atributos de la clase base
        self.tree = None
        self.complexity = None
        
        # Reiniciar atributos específicos de ControlRecursive
        self.base_cases = 0
        self.recursion_depth = 0
        self.recurrence_relation = ""
        self.algorithm = None
        self.recursive_calls = []
        self.base_case_details = []
        self.pattern = {}
        self.recursion_tree = None
        self.recurrence_solver = None

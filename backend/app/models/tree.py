from typing import List, Dict, Optional


class Tree:
    """
    Representa un árbol de recursión o estructura de árbol general.
    Usado para visualizar y analizar algoritmos recursivos.
    """

    def __init__(self, root: str = "root"):
        self.root: str = root
        self.children: Dict[str, List[str]] = {root: []}  # Diccionario de nodo -> lista de hijos
        self.height: int = 0
        self.total_nodes: int = 1

    def add_node(self, parent: str, child: str) -> None:
        """
        Añade un nodo hijo a un nodo padre.
        
        Args:
            parent: Identificador del nodo padre
            child: Identificador del nodo hijo
        """
        if parent not in self.children:
            self.children[parent] = []
        
        self.children[parent].append(child)
        
        if child not in self.children:
            self.children[child] = []
            self.total_nodes += 1
        
        # Recalcular altura
        self.height = self.calculate_depth()

    def traverse(self, order: str = "preorder") -> List[str]:
        """
        Recorre el árbol en el orden especificado.
        
        Args:
            order: Tipo de recorrido ('preorder', 'postorder', 'levelorder')
            
        Returns:
            Lista de nodos en el orden especificado
        """
        if order == "preorder":
            return self._preorder_traversal(self.root)
        elif order == "postorder":
            return self._postorder_traversal(self.root)
        elif order == "levelorder":
            return self._levelorder_traversal()
        else:
            return self._preorder_traversal(self.root)

    def _preorder_traversal(self, node: str) -> List[str]:
        """
        Recorrido en preorden (raíz -> izquierda -> derecha).
        
        Args:
            node: Nodo actual
            
        Returns:
            Lista de nodos en preorden
        """
        result = [node]
        if node in self.children:
            for child in self.children[node]:
                result.extend(self._preorder_traversal(child))
        return result

    def _postorder_traversal(self, node: str) -> List[str]:
        """
        Recorrido en postorden (izquierda -> derecha -> raíz).
        
        Args:
            node: Nodo actual
            
        Returns:
            Lista de nodos en postorden
        """
        result = []
        if node in self.children:
            for child in self.children[node]:
                result.extend(self._postorder_traversal(child))
        result.append(node)
        return result

    def _levelorder_traversal(self) -> List[str]:
        """
        Recorrido por niveles (BFS).
        
        Returns:
            Lista de nodos por niveles
        """
        from collections import deque
        
        result = []
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            if node in self.children:
                queue.extend(self.children[node])
        
        return result

    def calculate_depth(self, node: Optional[str] = None) -> int:
        """
        Calcula la profundidad máxima del árbol.
        
        Args:
            node: Nodo desde el cual calcular (por defecto la raíz)
            
        Returns:
            Profundidad del árbol
        """
        if node is None:
            node = self.root
        
        if node not in self.children or not self.children[node]:
            return 0
        
        max_child_depth = 0
        for child in self.children[node]:
            child_depth = self.calculate_depth(child)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth + 1

    def visualize(self) -> str:
        """
        Genera una representación visual del árbol en formato texto.
        
        Returns:
            String con la representación visual del árbol
        """
        lines = []
        lines.append(f"Árbol de Recursión (Total: {self.total_nodes} nodos, Altura: {self.height})")
        lines.append("=" * 60)
        
        self._visualize_helper(self.root, "", True, lines)
        
        return "\n".join(lines)

    def _visualize_helper(self, node: str, prefix: str, is_last: bool, lines: List[str]) -> None:
        """
        Función auxiliar recursiva para visualizar el árbol.
        
        Args:
            node: Nodo actual
            prefix: Prefijo para la indentación
            is_last: Si es el último hijo
            lines: Lista de líneas del resultado
        """
        # Símbolo del nodo
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + str(node))
        
        # Prefijo para los hijos
        extension = "    " if is_last else "│   "
        
        if node in self.children and self.children[node]:
            children = self.children[node]
            for i, child in enumerate(children):
                is_last_child = (i == len(children) - 1)
                self._visualize_helper(child, prefix + extension, is_last_child, lines)

    def get_node_count_by_level(self) -> Dict[int, int]:
        """
        Cuenta el número de nodos por nivel.
        
        Returns:
            Diccionario con nivel -> cantidad de nodos
        """
        from collections import deque
        
        level_counts = {}
        queue = deque([(self.root, 0)])  # (nodo, nivel)
        
        while queue:
            node, level = queue.popleft()
            
            if level not in level_counts:
                level_counts[level] = 0
            level_counts[level] += 1
            
            if node in self.children:
                for child in self.children[node]:
                    queue.append((child, level + 1))
        
        return level_counts

    def calculate_work_at_level(self, work_per_node: int = 1) -> Dict[int, int]:
        """
        Calcula el trabajo total realizado en cada nivel del árbol.
        
        Args:
            work_per_node: Cantidad de trabajo por nodo
            
        Returns:
            Diccionario con nivel -> trabajo total
        """
        level_counts = self.get_node_count_by_level()
        return {level: count * work_per_node for level, count in level_counts.items()}


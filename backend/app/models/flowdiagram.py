from typing import List, Dict, Tuple


class FlowDiagram:
    """
    Representa un diagrama de flujo del algoritmo.
    Ayuda a visualizar la estructura y el flujo de ejecución del pseudocódigo.
    """

    def __init__(self):
        self.nodes: List[Dict] = []  # Lista de nodos: {id, type, label, content}
        self.edges: List[Tuple[str, str, str]] = []  # Lista de aristas: (from, to, label)
        self.start_node: str = ""
        self.end_node: str = ""
        self.diagram_type: str = "flowchart"  # flowchart, state_diagram, sequence

    def build_from_algorithm(self, algorithm) -> None:
        """
        Construye el diagrama de flujo a partir de un algoritmo.
        
        Args:
            algorithm: Objeto Algorithm del cual construir el diagrama
        """
        # Validar que algorithm tenga los atributos necesarios
        if not hasattr(algorithm, 'name') or not hasattr(algorithm, 'pseudocode'):
            raise ValueError("El objeto algorithm debe tener atributos 'name' y 'pseudocode'")
            
        self.start_node = "start"
        self.end_node = "end"
        
        # Agregar nodo inicial
        self._add_node("start", "start", "Inicio", algorithm.name)
        
        # Parsear el pseudocódigo y crear nodos
        lines = algorithm.pseudocode.split('\n')
        current_id = "start"
        node_counter = 1
        
        for line in lines:
            line_stripped = line.strip().lower()
            
            if not line_stripped:
                continue
            
            # Detectar tipo de instrucción
            if any(keyword in line_stripped for keyword in ['si', 'if']):
                # Nodo de decisión
                node_id = f"decision_{node_counter}"
                self._add_node(node_id, "decision", "Decisión", line.strip())
                self._add_edge(current_id, node_id, "")
                current_id = node_id
                node_counter += 1
            
            elif any(keyword in line_stripped for keyword in ['para', 'for', 'mientras', 'while']):
                # Nodo de ciclo
                node_id = f"loop_{node_counter}"
                self._add_node(node_id, "loop", "Ciclo", line.strip())
                self._add_edge(current_id, node_id, "")
                current_id = node_id
                node_counter += 1
            
            elif any(keyword in line_stripped for keyword in ['retornar', 'return']):
                # Nodo de retorno
                node_id = f"return_{node_counter}"
                self._add_node(node_id, "process", "Retornar", line.strip())
                self._add_edge(current_id, node_id, "")
                current_id = node_id
                node_counter += 1
            
            else:
                # Nodo de proceso normal
                node_id = f"process_{node_counter}"
                self._add_node(node_id, "process", "Proceso", line.strip())
                self._add_edge(current_id, node_id, "")
                current_id = node_id
                node_counter += 1
        
        # Agregar nodo final
        self._add_node("end", "end", "Fin", "")
        self._add_edge(current_id, "end", "")

    def _add_node(self, node_id: str, node_type: str, label: str, content: str) -> None:
        """
        Agrega un nodo al diagrama.
        
        Args:
            node_id: Identificador único del nodo
            node_type: Tipo de nodo (start, end, process, decision, loop)
            label: Etiqueta del nodo
            content: Contenido/descripción del nodo
        """
        node = {
            "id": node_id,
            "type": node_type,
            "label": label,
            "content": content
        }
        self.nodes.append(node)

    def _add_edge(self, from_node: str, to_node: str, label: str = "") -> None:
        """
        Agrega una arista (conexión) entre dos nodos.
        
        Args:
            from_node: ID del nodo origen
            to_node: ID del nodo destino
            label: Etiqueta de la arista (ej: "Sí", "No")
        """
        edge = (from_node, to_node, label)
        self.edges.append(edge)

    def highlight_paths(self) -> Dict[str, List[str]]:
        """
        Identifica y resalta caminos importantes en el diagrama.
        
        Returns:
            Diccionario con diferentes tipos de caminos
        """
        paths = {
            "main_path": [],  # Camino principal
            "loop_paths": [],  # Caminos con ciclos
            "decision_paths": []  # Caminos de decisiones
        }
        
        # Construir camino principal
        current = self.start_node
        visited = set()
        
        while current != self.end_node and current not in visited:
            paths["main_path"].append(current)
            visited.add(current)
            
            # Encontrar el siguiente nodo
            next_nodes = [edge[1] for edge in self.edges if edge[0] == current]
            if next_nodes:
                current = next_nodes[0]
            else:
                break
        
        paths["main_path"].append(self.end_node)
        
        # Identificar caminos con ciclos
        for node in self.nodes:
            if node["type"] == "loop":
                paths["loop_paths"].append(node["id"])
        
        # Identificar caminos de decisiones
        for node in self.nodes:
            if node["type"] == "decision":
                paths["decision_paths"].append(node["id"])
        
        return paths

    def export_diagram(self, format: str = "mermaid") -> str:
        """
        Exporta el diagrama en diferentes formatos.
        
        Args:
            format: Formato de salida ('mermaid', 'dot', 'text', 'plantuml')
            
        Returns:
            String con el diagrama en el formato especificado
        """
        if format == "mermaid":
            return self._export_mermaid()
        elif format == "dot":
            return self._export_dot()
        elif format == "plantuml":
            return self._export_plantuml()
        else:  # text
            return self._export_text()

    def _export_mermaid(self) -> str:
        """
        Exporta el diagrama en formato Mermaid.js
        
        Returns:
            String con sintaxis de Mermaid
        """
        lines = ["flowchart TD"]
        
        # Definir nodos
        for node in self.nodes:
            node_id = node["id"]
            label = node["content"] if node["content"] else node["label"]
            
            if node["type"] == "start" or node["type"] == "end":
                lines.append(f'    {node_id}(("{label}"))')
            elif node["type"] == "decision":
                lines.append(f'    {node_id}{{{label}}}')
            elif node["type"] == "process":
                lines.append(f'    {node_id}["{label}"]')
            elif node["type"] == "loop":
                lines.append(f'    {node_id}["{label}"]')
        
        # Definir aristas
        for from_node, to_node, label in self.edges:
            if label:
                lines.append(f'    {from_node} -->|{label}| {to_node}')
            else:
                lines.append(f'    {from_node} --> {to_node}')
        
        return "\n".join(lines)

    def _export_dot(self) -> str:
        """
        Exporta el diagrama en formato DOT (Graphviz).
        
        Returns:
            String con sintaxis DOT
        """
        lines = ["digraph FlowDiagram {"]
        lines.append("    rankdir=TD;")
        lines.append("    node [shape=box];")
        
        # Definir nodos
        for node in self.nodes:
            node_id = node["id"]
            label = node["content"] if node["content"] else node["label"]
            
            if node["type"] == "start" or node["type"] == "end":
                lines.append(f'    {node_id} [shape=oval, label="{label}"];')
            elif node["type"] == "decision":
                lines.append(f'    {node_id} [shape=diamond, label="{label}"];')
            else:
                lines.append(f'    {node_id} [shape=box, label="{label}"];')
        
        # Definir aristas
        for from_node, to_node, label in self.edges:
            if label:
                lines.append(f'    {from_node} -> {to_node} [label="{label}"];')
            else:
                lines.append(f'    {from_node} -> {to_node};')
        
        lines.append("}")
        return "\n".join(lines)

    def _export_plantuml(self) -> str:
        """
        Exporta el diagrama en formato PlantUML.
        
        Returns:
            String con sintaxis PlantUML
        """
        lines = ["@startuml"]
        lines.append("start")
        
        # Procesar nodos y aristas
        for node in self.nodes[1:-1]:  # Excluir start y end
            label = node["content"] if node["content"] else node["label"]
            
            if node["type"] == "decision":
                lines.append(f'if ({label}) then (yes)')
                lines.append('  :proceso;')
                lines.append('else (no)')
                lines.append('  :otro proceso;')
                lines.append('endif')
            elif node["type"] == "loop":
                lines.append(f'while ({label})')
                lines.append('  :proceso;')
                lines.append('endwhile')
            else:
                lines.append(f':{label};')
        
        lines.append("stop")
        lines.append("@enduml")
        return "\n".join(lines)

    def _export_text(self) -> str:
        """
        Exporta el diagrama en formato texto simple.
        
        Returns:
            String con representación textual
        """
        lines = ["=== Diagrama de Flujo ===\n"]
        lines.append("Nodos:")
        
        for i, node in enumerate(self.nodes, 1):
            lines.append(f"{i}. [{node['type'].upper()}] {node['label']}: {node['content']}")
        
        lines.append("\nConexiones:")
        for i, (from_node, to_node, label) in enumerate(self.edges, 1):
            label_str = f" ({label})" if label else ""
            lines.append(f"{i}. {from_node} -> {to_node}{label_str}")
        
        return "\n".join(lines)


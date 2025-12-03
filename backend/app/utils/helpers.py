from typing import List, Dict, Union
# Asumo que importas los modelos desde tu archivo de esquemas/modelos
from ..models.recursive.tree import RecurrenceTreeResponse, TreeNode 

def generate_recurrence_tree_mermaid(response: 'RecurrenceTreeResponse') -> str:
    """
    Genera código Mermaid para visualizar uno o múltiples árboles de recursión
    basado en la respuesta del RecurrenceTreeAgent (tree.py).
    
    IMPORTANTE: Esta función SOLO funciona con RecurrenceTreeResponse del agente tree.py.
    Para TreeMethodStrategy (tree_method.py), usa generate_tree_method_diagram() en su lugar.

    Args:
        response (RecurrenceTreeResponse): Objeto de respuesta que contiene la lista de árboles.

    Returns:
        str: Código en formato Mermaid (graph TD).
    """
    if not response.trees:
        return ""

    mermaid_lines = ["graph TD"]
    
    # Estilos básicos para mejorar la legibilidad
    mermaid_lines.append("    %% Estilos")
    mermaid_lines.append("    classDef root fill:#f9f,stroke:#333,stroke-width:2px;")
    mermaid_lines.append("    classDef leaf fill:#dfd,stroke:#333,stroke-width:1px;")
    mermaid_lines.append("    classDef node fill:#fff,stroke:#333,stroke-width:1px;")

    for tree_idx, tree in enumerate(response.trees):
        # Crear un subgrafo para cada caso (Best, Worst, Average, Single)
        # Limpiamos caracteres que puedan romper mermaid en el título
        safe_title = f"{tree.case_type.upper()}: {tree.recurrence_equation}".replace('"', "'")
        mermaid_lines.append(f"\n    subgraph cluster_{tree_idx} [\"{safe_title}\"]")
        mermaid_lines.append(f"    direction TB")

        # 1. Organizar nodos por nivel para poder reconstruir las relaciones
        nodes_by_level: Dict[int, List['TreeNode']] = {}
        for node in tree.tree_structure:
            if node.level not in nodes_by_level:
                nodes_by_level[node.level] = []
            nodes_by_level[node.level].append(node)

        # 2. Asegurar que los nodos estén ordenados por 'position' dentro de su nivel
        for lvl in nodes_by_level:
            nodes_by_level[lvl].sort(key=lambda x: x.position)

        # 3. Generar Nodos y Relaciones
        # Iteramos nivel por nivel para conectar padres (nivel i) con hijos (nivel i+1)
        sorted_levels = sorted(nodes_by_level.keys())
        
        for level in sorted_levels:
            current_nodes = nodes_by_level[level]
            
            # Dibujar nodos del nivel actual
            for node in current_nodes:
                # ID único: T(indice_arbol)_L(nivel)_P(posicion)
                node_id = f"T{tree_idx}_L{node.level}_P{node.position}"
                label = node.label.replace('"', "'") # Escapar comillas
                
                # Asignar estilo según tipo de nodo
                style_class = "node"
                if node.level == 0:
                    style_class = "root"
                elif node.children_count == 0:
                    style_class = "leaf"
                
                mermaid_lines.append(f'    {node_id}("{label}"):::{style_class}')

            # Crear conexiones desde el nivel anterior hacia este
            if level > 0:
                prev_nodes = nodes_by_level.get(level - 1, [])
                child_cursor = 0 # Puntero para recorrer los hijos disponibles en el nivel actual
                
                for parent in prev_nodes:
                    parent_id = f"T{tree_idx}_L{parent.level}_P{parent.position}"
                    
                    # Conectar con la cantidad de hijos que dice tener el padre
                    # Asumimos que los hijos están ordenados secuencialmente en el nivel actual
                    for _ in range(parent.children_count):
                        if child_cursor < len(current_nodes):
                            child = current_nodes[child_cursor]
                            child_id = f"T{tree_idx}_L{child.level}_P{child.position}"
                            mermaid_lines.append(f"    {parent_id} --> {child_id}")
                            child_cursor += 1

        mermaid_lines.append("    end") # Fin del subgraph

    return "\n".join(mermaid_lines)


def generate_tree_method_diagram(result: Dict[str, any]) -> str:
    """
    Genera un diagrama conceptual para TreeMethodStrategy (tree_method.py).
    
    Como TreeMethodStrategy NO retorna una estructura de árbol con nodos,
    esta función genera un diagrama simplificado que muestra:
    - Los niveles del árbol mencionados en levels_detail
    - La profundidad del árbol
    - El trabajo por nivel
    
    Args:
        result (Dict): Resultado del método solve() de TreeMethodStrategy
        
    Returns:
        str: Código Mermaid mostrando un diagrama conceptual
        
    Ejemplo de uso:
        strategy = TreeMethodStrategy()
        result = strategy.solve("T(n) = 2T(n/2) + n")
        mermaid_code = generate_tree_method_diagram(result)
    """
    if not result.get("applicable", False):
        return "graph TD\n    A[\"Método no aplicable\"]"
    
    mermaid_lines = ["graph TD"]
    mermaid_lines.append("    %% Diagrama conceptual del Método del Árbol")
    mermaid_lines.append("    classDef info fill:#e1f5ff,stroke:#333,stroke-width:2px;")
    
    # Título con la ecuación
    equation = result.get("method", "Método del Árbol")
    mermaid_lines.append(f'    title[\"{equation}\"]:::info')
    
    # Profundidad del árbol
    tree_depth = result.get("tree_depth", "desconocido")
    mermaid_lines.append(f'    depth[\"Profundidad: {tree_depth}\"]:::info')
    mermaid_lines.append("    title --> depth")
    
    # Niveles del árbol
    levels = result.get("levels_detail", [])
    work_per_level = result.get("work_per_level", [])
    
    # Mostrar solo los primeros 5 niveles para evitar diagramas muy grandes
    max_levels = min(5, len(levels))
    
    for i in range(max_levels):
        level_text = levels[i] if i < len(levels) else f"Nivel {i}"
        work_text = work_per_level[i] if i < len(work_per_level) else ""
        
        # Limpiar el texto para Mermaid
        level_clean = level_text.replace('"', "'").replace('\n', ' ')[:60]
        
        node_id = f"level{i}"
        if work_text:
            work_clean = work_text.replace('"', "'")[:40]
            mermaid_lines.append(f'    {node_id}[\"{level_clean}\\nTrabajo: {work_clean}\"]')
        else:
            mermaid_lines.append(f'    {node_id}[\"{level_clean}\"]')
        
        if i == 0:
            mermaid_lines.append(f"    depth --> {node_id}")
        else:
            mermaid_lines.append(f"    level{i-1} --> {node_id}")
    
    if len(levels) > max_levels:
        mermaid_lines.append(f'    more[\"... {len(levels) - max_levels} niveles más ...\"]')
        mermaid_lines.append(f"    level{max_levels-1} --> more")
    
    # Complejidad final
    complexity = result.get("complexity", "O(?)")
    mermaid_lines.append(f'    result[\"Complejidad: {complexity}\"]:::info')
    
    if len(levels) > 0:
        last_level = f"level{min(max_levels-1, len(levels)-1)}"
        mermaid_lines.append(f"    {last_level} --> result")
    else:
        mermaid_lines.append("    depth --> result")
    
    return "\n".join(mermaid_lines)


def generate_tree_visualization(data: Union['RecurrenceTreeResponse', Dict[str, any]]) -> str:
    """
    Función unificada que genera visualización Mermaid para AMBOS tipos de árboles.
    
    Detecta automáticamente el tipo de entrada y usa el generador apropiado:
    - Si es RecurrenceTreeResponse (del agente tree.py) → usa generate_recurrence_tree_mermaid()
    - Si es Dict (de TreeMethodStrategy) → usa generate_tree_method_diagram()
    
    Args:
        data: Puede ser RecurrenceTreeResponse o Dict[str, Any]
        
    Returns:
        str: Código Mermaid para visualización
        
    Ejemplo de uso:
        # Con RecurrenceTreeAgent
        agent = RecurrenceTreeAgent()
        response = agent.generate_tree_sketches(single_equation="T(n) = 2T(n/2) + n")
        mermaid = generate_tree_visualization(response)
        
        # Con TreeMethodStrategy  
        strategy = TreeMethodStrategy()
        result = strategy.solve("T(n) = 2T(n/2) + n")
        mermaid = generate_tree_visualization(result)
    """
    # Detectar el tipo de entrada
    if isinstance(data, dict):
        # Es resultado de TreeMethodStrategy
        return generate_tree_method_diagram(data)
    else:
        # Es RecurrenceTreeResponse del agente tree.py
        return generate_recurrence_tree_mermaid(data)

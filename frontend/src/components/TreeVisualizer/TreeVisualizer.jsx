import React from "react";

export default function TreeVisualizer({ trees, summary }) {
  if (!trees || trees.length === 0) {
    return (
      <div className="bg-gray-800 rounded-xl p-6">
        <p className="text-gray-400 text-center">No hay árboles de recursión disponibles</p>
      </div>
    );
  }

  const getCaseColor = (caseType) => {
    const colors = {
      best_case: "border-green-500",
      worst_case: "border-red-500",
      average_case: "border-yellow-500",
      single: "border-purple-500",
    };
    return colors[caseType] || "border-gray-500";
  };

  const getCaseBgColor = (caseType) => {
    const colors = {
      best_case: "bg-green-500/20",
      worst_case: "bg-red-500/20",
      average_case: "bg-yellow-500/20",
      single: "bg-purple-500/20",
    };
    return colors[caseType] || "bg-gray-500/20";
  };

  const getCaseLabel = (caseType) => {
    const labels = {
      best_case: "🟢 Mejor Caso",
      worst_case: "🔴 Peor Caso",
      average_case: "🟡 Caso Promedio",
      single: "📊 Análisis",
    };
    return labels[caseType] || caseType;
  };

  const renderTreeStructure = (treeStructure, caseType) => {
    // Agrupar nodos por nivel
    const nodesByLevel = {};
    treeStructure.forEach(node => {
      if (!nodesByLevel[node.level]) {
        nodesByLevel[node.level] = [];
      }
      nodesByLevel[node.level].push(node);
    });

    const levels = Object.keys(nodesByLevel).sort((a, b) => a - b);
    const maxLevel = Math.max(...levels.map(Number));

    return (
      <div className="space-y-4">
        {levels.map((level) => {
          const nodes = nodesByLevel[level];
          const levelNum = parseInt(level);
          const indent = levelNum * 30;

          return (
            <div key={level} className="space-y-2">
              {/* Etiqueta del nivel */}
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-gray-500 w-16">
                  Nivel {levelNum}:
                </span>
                <div className="flex-1 border-t border-gray-700"></div>
              </div>

              {/* Nodos en este nivel */}
              <div 
                className="flex flex-wrap gap-3 items-center"
                style={{ paddingLeft: `${indent}px` }}
              >
                {nodes.map((node, nodeIndex) => (
                  <div key={`${level}-${nodeIndex}`} className="flex flex-col items-center gap-2">
                    {/* Conectores visuales para hijos */}
                    {levelNum < maxLevel && node.children_count > 0 && (
                      <div className="flex gap-1 mb-1">
                        {Array.from({ length: node.children_count }).map((_, i) => (
                          <div 
                            key={i} 
                            className="w-px h-4 bg-purple-500/50"
                          />
                        ))}
                      </div>
                    )}

                    {/* Nodo */}
                    <div className={`${getCaseBgColor(caseType)} border-2 ${getCaseColor(caseType).replace('border-', 'border-')} px-4 py-2 rounded-lg shadow-lg`}>
                      <div className="flex flex-col items-center gap-1">
                        <span className="text-green-400 font-mono font-bold text-sm">
                          {node.label}
                        </span>
                        {node.work && (
                          <span className="text-xs text-gray-400">
                            Trabajo: {node.work}
                          </span>
                        )}
                        {node.children_count > 0 && (
                          <span className="text-xs text-purple-400">
                            ↓ {node.children_count} {node.children_count === 1 ? "hijo" : "hijos"}
                          </span>
                        )}
                        {node.children_count === 0 && (
                          <span className="text-xs text-yellow-400">
                            🍃 Hoja
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Línea visual hacia abajo */}
                    {levelNum < maxLevel && node.children_count > 0 && (
                      <div className="w-px h-6 bg-purple-500/50"></div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 space-y-6">
      <h3 className="text-2xl font-bold text-purple-400 flex items-center gap-2">
        🌳 Árboles de Recursión
      </h3>

      {trees.map((tree, treeIndex) => (
        <div
          key={treeIndex}
          className={`border-l-4 ${getCaseColor(tree.case_type)} bg-gray-900 rounded-lg p-5 space-y-4`}
        >
          {/* Header del árbol */}
          <div className="flex items-center justify-between border-b border-gray-700 pb-3">
            <h4 className="text-lg font-bold text-gray-200">
              {getCaseLabel(tree.case_type)}
            </h4>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400">
                📏 Profundidad: <span className="text-purple-400 font-mono">{tree.tree_depth}</span>
              </span>
            </div>
          </div>

          {/* Ecuación de recurrencia */}
          <div className="bg-gray-800 p-3 rounded-lg border border-gray-700">
            <p className="text-xs text-gray-500 mb-1">Ecuación de Recurrencia:</p>
            <p className="text-green-400 font-mono text-sm">{tree.recurrence_equation}</p>
          </div>

          {/* Visualización del árbol */}
          <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
            <p className="text-sm text-gray-400 mb-4 font-semibold">📐 Estructura del Árbol:</p>
            {renderTreeStructure(tree.tree_structure, tree.case_type)}
          </div>

          {/* Descripción */}
          {tree.description && (
            <div className="bg-blue-900/20 border border-blue-700/50 p-3 rounded-lg">
              <p className="text-sm text-blue-300">
                <span className="font-semibold">💡 Descripción:</span> {tree.description}
              </p>
            </div>
          )}
        </div>
      ))}

      {/* Resumen general */}
      {summary && (
        <div className="bg-purple-900/20 border border-purple-700 p-4 rounded-lg">
          <p className="text-sm font-semibold text-purple-300 mb-2">📝 Resumen General:</p>
          <p className="text-gray-300 text-sm">{summary}</p>
        </div>
      )}
    </div>
  );
}

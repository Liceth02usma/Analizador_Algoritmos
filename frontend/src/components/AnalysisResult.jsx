import React, { useState } from "react";
import MermaidDiagram from "./MermaidDiagram";
import TreeVisualizer from "./TreeVisualizer";
import { Calculator, Activity, GitBranch, Table } from "lucide-react";

export default function AnalysisResult({ data }) {
  const [activeTab, setActiveTab] = useState(0);

  if (!data || !data.analysis || !data.analysis.cases) return null;

  const { cases, general_explanation, math_summary, diagrams } = data.analysis;
  const currentCase = cases[activeTab];
  
  // Detectar si es recursivo basándose en la presencia de diagramas de árbol
  const isRecursive = diagrams && (diagrams.tree_method_best || diagrams.tree_method_worst || diagrams.tree_method_average);
  
  // Mapeo de nombres de casos a claves de diagramas
  const getCaseDiagramKey = (caseName) => {
    const lowerName = caseName.toLowerCase();
    if (lowerName.includes('mejor') || lowerName.includes('best')) return 'tree_method_best';
    if (lowerName.includes('peor') || lowerName.includes('worst')) return 'tree_method_worst';
    if (lowerName.includes('promedio') || lowerName.includes('average')) return 'tree_method_average';
    return null;
  };
  
  const currentDiagramKey = getCaseDiagramKey(currentCase.case_name);
  const currentTreeDiagram = isRecursive && currentDiagramKey ? diagrams[currentDiagramKey] : null;

  return (
    <div className="flex flex-col h-full space-y-6">
      
      {/* 1. Resumen General */}
      <div className="bg-gray-800 p-4 rounded-xl border-l-4 border-purple-500 shadow-md">
        <h3 className="text-white font-bold text-lg mb-1 flex items-center gap-2">
          <Activity size={20} className="text-purple-400"/> Resumen Ejecutivo
        </h3>
        <p className="text-gray-300 text-sm mb-2">{general_explanation}</p>
        <p className="text-indigo-300 text-sm font-semibold bg-indigo-900/30 p-2 rounded">
          💡 {math_summary}
        </p>
      </div>

      {/* 2. Pestañas de Casos */}
      <div className="flex space-x-2 border-b border-gray-700">
        {cases.map((c, idx) => (
          <button
            key={idx}
            onClick={() => setActiveTab(idx)}
            className={`px-4 py-2 text-sm font-medium transition-colors rounded-t-lg ${
              activeTab === idx
                ? "bg-purple-600 text-white border-b-2 border-purple-400"
                : "text-gray-400 hover:text-white hover:bg-gray-800"
            }`}
          >
            {c.case_name}
          </button>
        ))}
      </div>

      {/* 3. Contenido del Caso Seleccionado */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-6 animate-in fade-in duration-300">
        
        {/* Encabezado del Caso */}
        <div className="flex justify-between items-center">
          <div className="text-gray-400 text-sm">
            Condición: <span className="text-yellow-400 italic">{currentCase.condition}</span>
          </div>
          <div className="text-2xl font-bold text-white bg-gray-800 px-4 py-1 rounded-lg border border-gray-600">
            {currentCase.big_o}
          </div>
        </div>

        {/* Sección Matemática */}
        <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
          <h4 className="text-purple-300 font-semibold mb-3 flex items-center gap-2">
            <Calculator size={18} /> Análisis Matemático
          </h4>
          <div className="space-y-3 text-sm">
            <div>
              <p className="text-gray-500 text-xs uppercase mb-1">Sumatoria Cruda</p>
              <code className="block bg-black/30 p-2 rounded text-green-400 font-mono overflow-x-auto">
                {currentCase.raw_summation_str}
              </code>
            </div>
            <div>
              <p className="text-gray-500 text-xs uppercase mb-1">Función de Eficiencia T(n)</p>
              <code className="block bg-black/30 p-2 rounded text-blue-400 font-mono overflow-x-auto">
                T(n) = {currentCase.simplified_complexity}
              </code>
            </div>
          </div>
        </div>

        {/* Tabla de Costos */}
        <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
          <h4 className="text-purple-300 font-semibold mb-3 flex items-center gap-2">
            <Table size={18} /> Desglose Paso a Paso
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-gray-300">
              <thead className="text-xs text-gray-400 uppercase bg-gray-900/50">
                <tr>
                  <th className="px-3 py-2">Línea</th>
                  <th className="px-3 py-2">Costo</th>
                  <th className="px-3 py-2">Ejecuciones</th>
                  <th className="px-3 py-2">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {currentCase.line_analysis.map((line, i) => (
                  <tr key={i} className="hover:bg-gray-700/30">
                    <td className="px-3 py-2 font-mono text-yellow-500">{line.line}</td>
                    <td className="px-3 py-2 text-gray-400">{line.cost_constant}</td>
                    <td className="px-3 py-2 font-mono text-blue-300">{line.execution_count}</td>
                    <td className="px-3 py-2 font-mono text-green-300">{line.total_cost_expression}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Diagrama de Flujo / Árbol de Recursión */}
        {isRecursive && currentTreeDiagram ? (
          // Algoritmo Recursivo: Mostrar árbol de recursión
          <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
            <h4 className="text-purple-300 font-semibold mb-3 flex items-center gap-2">
              <GitBranch size={18} /> Árbol de Recursión
            </h4>
            <TreeVisualizer mermaidCode={currentTreeDiagram} isRecursive={true} />
          </div>
        ) : currentCase.trace_diagram ? (
          // Algoritmo Iterativo: Mostrar diagrama de seguimiento
          <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
            <h4 className="text-purple-300 font-semibold mb-3 flex items-center gap-2">
              <GitBranch size={18} /> Diagrama de Seguimiento
            </h4>
            <MermaidDiagram chart={currentCase.trace_diagram} />
          </div>
        ) : null}

      </div>
    </div>
  );
}
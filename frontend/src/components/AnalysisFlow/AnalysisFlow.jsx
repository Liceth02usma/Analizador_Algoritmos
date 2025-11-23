import React from "react";
import CodeViewer from "../CodeViewer";
import { CaseSelector } from "../CaseAnalysis";
import { ComplexitySummary } from "../ResultsSummary";

export default function AnalysisFlow({ analysis }) {
  if (!analysis) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <p className="text-gray-400 text-lg">No hay análisis disponible</p>
      </div>
    );
  }

  const {
    code_explain,
    complexity_line_to_line,
    explain_complexity,
    equation,
    method_solution,
    solution_equation,
    explain_solution_steps,
    diagrams,
    extra,
  } = analysis;

  // Detectar múltiples casos desde extra o desde diagrams
  const hasMultipleCases = 
    extra?.has_multiple_cases || 
    diagrams?.recursion_trees?.has_multiple_cases || 
    false;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-purple-400">
            Análisis de Algoritmo Recursivo
          </h1>
          {extra?.algorithm_name && (
            <p className="text-xl text-gray-300">{extra.algorithm_name}</p>
          )}
        </div>

        {/* 1. Mostrar el código */}
        <CodeViewer
          code={complexity_line_to_line}
          explanation={code_explain}
          complexity={explain_complexity}
        />

        {/* 2. Resumen de complejidades */}
        <ComplexitySummary
          equation={equation}
          method={method_solution}
          complexity={solution_equation}
          hasMultipleCases={hasMultipleCases}
        />

        {/* 3. Análisis por casos con árboles */}
        {explain_solution_steps && Array.isArray(explain_solution_steps) && (
          <div className="bg-gray-800 rounded-xl p-6">
            <h2 className="text-3xl font-bold text-purple-400 mb-6">
              📋 Análisis Detallado
            </h2>
            <CaseSelector analysisSteps={explain_solution_steps} diagrams={diagrams} />
          </div>
        )}

        {/* 4. Información adicional */}
        {extra && (
          <div className="bg-gray-800 rounded-xl p-6 space-y-4">
            <h3 className="text-2xl font-bold text-purple-400">ℹ️ Información Adicional</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {extra.space_complexity && (
                <div className="bg-gray-700 p-4 rounded-lg">
                  <p className="text-sm text-gray-400 mb-1">Complejidad Espacial:</p>
                  <p className="text-green-400 font-bold text-lg">{extra.space_complexity}</p>
                </div>
              )}
              
              {extra.time_complexities && (
                <div className="bg-gray-700 p-4 rounded-lg">
                  <p className="text-sm text-gray-400 mb-2">Complejidades por Caso:</p>
                  <div className="space-y-1">
                    {extra.time_complexities.best_case && (
                      <p className="text-sm">
                        <span className="text-green-400">🟢 Mejor:</span>{" "}
                        <span className="text-white font-mono">{extra.time_complexities.best_case}</span>
                      </p>
                    )}
                    {extra.time_complexities.worst_case && (
                      <p className="text-sm">
                        <span className="text-red-400">🔴 Peor:</span>{" "}
                        <span className="text-white font-mono">{extra.time_complexities.worst_case}</span>
                      </p>
                    )}
                    {extra.time_complexities.average_case && (
                      <p className="text-sm">
                        <span className="text-yellow-400">🟡 Promedio:</span>{" "}
                        <span className="text-white font-mono">{extra.time_complexities.average_case}</span>
                      </p>
                    )}
                    {extra.time_complexities.single && (
                      <p className="text-sm">
                        <span className="text-purple-400">🔵 Único:</span>{" "}
                        <span className="text-white font-mono">{extra.time_complexities.single}</span>
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>

            {extra.analysis_details && Array.isArray(extra.analysis_details) && (
              <div className="bg-gray-700 p-4 rounded-lg">
                <p className="text-sm text-gray-400 mb-2">Detalles del Análisis:</p>
                <div className="space-y-2">
                  {extra.analysis_details.map((detail, idx) => (
                    <div key={idx} className="bg-gray-800 p-3 rounded text-sm">
                      <p className="text-gray-300">
                        <span className="font-semibold text-purple-400">
                          {detail.case_type === 'single' ? 'Caso Único' : 
                           detail.case_type === 'best_case' ? 'Mejor Caso' :
                           detail.case_type === 'worst_case' ? 'Peor Caso' :
                           detail.case_type === 'average_case' ? 'Caso Promedio' : detail.case_type}:
                        </span>{" "}
                        {detail.complexity} (Confianza: {(detail.classification_confidence * 100).toFixed(0)}%)
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

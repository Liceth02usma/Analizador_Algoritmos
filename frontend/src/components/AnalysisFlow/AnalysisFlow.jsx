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
    asymptotic_notation,
    algorithm_name,
    algorithm_category,
    equation,
    method_solution,
    solution_equation,
    explain_solution_steps,
    diagrams,
    extra,
  } = analysis;

  // Detectar múltiples casos
  const hasMultipleCases = 
    extra?.has_multiple_cases || 
    (Array.isArray(equation) && equation.length > 1) ||
    false;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-purple-400">
            Análisis de Algoritmo Recursivo
          </h1>
          {algorithm_name && (
            <p className="text-xl text-gray-300">{algorithm_name}</p>
          )}
          {algorithm_category && (
            <p className="text-sm text-gray-400 uppercase tracking-wider">{algorithm_category}</p>
          )}
        </div>

        {/* Notación Asintótica */}
        {asymptotic_notation && (
          <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 rounded-xl p-6 border border-purple-700">
            <h3 className="text-2xl font-bold text-purple-400 mb-4">📈 Notación Asintótica</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {asymptotic_notation.best && (
                <div className="bg-gray-800/70 p-4 rounded-lg border-l-4 border-green-500">
                  <p className="text-sm text-gray-400 mb-1">Mejor Caso (Ω)</p>
                  <p className="text-green-400 font-bold text-2xl">{asymptotic_notation.best}</p>
                </div>
              )}
              {asymptotic_notation.worst && (
                <div className="bg-gray-800/70 p-4 rounded-lg border-l-4 border-red-500">
                  <p className="text-sm text-gray-400 mb-1">Peor Caso (O)</p>
                  <p className="text-red-400 font-bold text-2xl">{asymptotic_notation.worst}</p>
                </div>
              )}
              {asymptotic_notation.average && (
                <div className="bg-gray-800/70 p-4 rounded-lg border-l-4 border-yellow-500">
                  <p className="text-sm text-gray-400 mb-1">Caso Promedio (Θ)</p>
                  <p className="text-yellow-400 font-bold text-2xl">{asymptotic_notation.average}</p>
                </div>
              )}
            </div>
            {asymptotic_notation.explanation && asymptotic_notation.explanation !== "..." && (
              <div className="mt-4 bg-gray-800/70 p-4 rounded-lg">
                <p className="text-gray-300 text-sm">{asymptotic_notation.explanation}</p>
              </div>
            )}
          </div>
        )}

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
              
              {extra.analysis_details && typeof extra.analysis_details === 'string' && (
                <div className="bg-gray-700 p-4 rounded-lg">
                  <p className="text-sm text-gray-400 mb-1">Detalles:</p>
                  <p className="text-gray-300 text-sm">{extra.analysis_details}</p>
                </div>
              )}
            </div>

            {extra.analysis_details && Array.isArray(extra.analysis_details) && (
              <div className="bg-gray-700 p-4 rounded-lg">
                <p className="text-sm text-gray-400 mb-2">Detalles del Análisis por Caso:</p>
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
                        {detail.complexity} 
                        {detail.classification_confidence && (
                          <span className="text-gray-400"> (Confianza: {(detail.classification_confidence * 100).toFixed(0)}%)</span>
                        )}
                      </p>
                      {detail.equation && (
                        <p className="text-green-400 font-mono text-xs mt-1">{detail.equation}</p>
                      )}
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

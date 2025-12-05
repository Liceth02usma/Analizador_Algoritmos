import React, { useState } from "react";
import { StepsList } from "../SolutionSteps";
import TreeVisualizer from "../TreeVisualizer";

export default function CaseSelector({ analysisSteps, diagrams }) {
  const [activeCase, setActiveCase] = useState(0);

  // Verificar si no hay steps
  if (!analysisSteps || analysisSteps.length === 0) {
    return (
      <div className="bg-gray-700 rounded-lg p-6 text-center text-gray-400">
        <p>No hay pasos de análisis disponibles</p>
      </div>
    );
  }
  
  // Determinar casos disponibles directamente de analysisSteps
  const availableCases = analysisSteps.map(
    (step) => step.case_type || "single"
  );

  // Si solo hay un caso, mostrar sin tabs
  if (availableCases.length === 1) {
    const singleCase = availableCases[0];
    const singleStep = analysisSteps[0];

    return (
      <div className="space-y-6">
        {singleCase === "single" && (
          <div className="bg-purple-900/20 border border-purple-700 p-4 rounded-lg">
            <p className="text-purple-300 text-sm">
              ℹ️ Este análisis tiene un único caso (no se diferencia entre
              mejor, peor y promedio)
            </p>
          </div>
        )}

          {/* Información del caso */}
        <div className="bg-gray-700 rounded-lg p-6 space-y-4">
          {/* Condición del caso (si existe) */}
          {singleStep.condition && (
            <div className="bg-yellow-900/20 border border-yellow-700 p-4 rounded-lg">
              <p className="text-xs text-yellow-300 mb-1 font-semibold">📋 Condición del Caso:</p>
              <p className="text-yellow-200 text-sm italic">{singleStep.condition}</p>
            </div>
          )}

          {/* Big O Badge (si existe) */}
          {singleStep.big_o && (
            <div className="flex justify-end">
              <div className="bg-purple-600 text-white px-6 py-3 rounded-lg text-2xl font-bold shadow-lg">
                {singleStep.big_o}
              </div>
            </div>
          )}

          {/* Ecuación Original (si existe) */}
          {singleStep.original_equation && singleStep.original_equation !== singleStep.equation && (
            <div className="bg-blue-900/20 border border-blue-700 p-4 rounded-lg">
              <p className="text-xs text-blue-300 mb-1 font-semibold">📝 Ecuación Original:</p>
              <p className="text-blue-200 font-mono text-sm">
                {singleStep.original_equation}
              </p>
            </div>
          )}

          {/* Simplificación (si existe) */}
          {singleStep.simplification && (
            <div className="bg-green-900/20 border border-green-700 p-4 rounded-lg space-y-3">
              <h4 className="text-sm font-semibold text-green-300 mb-2">🔄 Proceso de Simplificación:</h4>
              
              <div className="bg-gray-800 p-3 rounded">
                <p className="text-xs text-gray-400 mb-1">Original:</p>
                <p className="text-gray-200 font-mono text-xs">{singleStep.simplification.original}</p>
              </div>
              
              <div className="bg-gray-800 p-3 rounded">
                <p className="text-xs text-gray-400 mb-1">Simplificada:</p>
                <p className="text-green-400 font-mono text-sm font-semibold">{singleStep.simplification.simplified}</p>
              </div>

              {singleStep.simplification.steps && singleStep.simplification.steps.length > 0 && (
                <div className="bg-gray-800 p-3 rounded">
                  <p className="text-xs text-gray-400 mb-2">Pasos:</p>
                  <div className="space-y-1">
                    {singleStep.simplification.steps.map((step, idx) => (
                      <p key={idx} className="text-gray-300 text-xs">{step}</p>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-2">
                {singleStep.simplification.explicit_form && (
                  <div className="bg-gray-800 p-2 rounded">
                    <p className="text-xs text-gray-400">Forma Explícita:</p>
                    <p className="text-green-400 font-mono text-xs">{singleStep.simplification.explicit_form}</p>
                  </div>
                )}
                {singleStep.simplification.confidence && (
                  <div className="bg-gray-800 p-2 rounded">
                    <p className="text-xs text-gray-400">Confianza:</p>
                    <p className="text-green-400 font-semibold text-xs">{(singleStep.simplification.confidence * 100).toFixed(0)}%</p>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">Ecuación:</p>
              <p className="text-green-400 font-mono text-sm">
                {singleStep.equation || singleStep.raw_summation_str}
              </p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">Método:</p>
              <p className="text-blue-400 text-sm capitalize">
                {singleStep.method || 'Conteo de Pasos'}
              </p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">Complejidad:</p>
              <p className="text-yellow-400 font-bold text-xl">
                {singleStep.complexity || singleStep.big_o}
              </p>
            </div>
          </div>

          {/* Proceso de Simplificación Iterativo */}
          {singleStep.raw_summation_str && singleStep.simplified_complexity && (
            <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-700 p-5 rounded-xl space-y-4">
              <h4 className="text-lg font-semibold text-blue-300 mb-3 flex items-center gap-2">
                🧮 Proceso de Simplificación
              </h4>
              
              {/* Ecuación original */}
              <div className="bg-gray-800 p-4 rounded-lg">
                <p className="text-xs text-gray-400 mb-2">1️⃣ Sumatoria Original:</p>
                <p className="text-gray-200 font-mono text-sm break-all">{singleStep.raw_summation_str}</p>
              </div>

              {/* Pasos matemáticos */}
              {singleStep.math_steps && (
                <div className="bg-gray-800 p-4 rounded-lg">
                  <p className="text-xs text-gray-400 mb-2">2️⃣ Desarrollo Matemático:</p>
                  <p className="text-blue-300 font-mono text-sm break-all">{singleStep.math_steps}</p>
                </div>
              )}

              {/* Forma simplificada */}
              <div className="bg-gray-800 p-4 rounded-lg border-2 border-green-500/50">
                <p className="text-xs text-gray-400 mb-2">3️⃣ Forma Simplificada:</p>
                <p className="text-green-400 font-mono text-base font-bold break-all">{singleStep.simplified_complexity}</p>
              </div>

              {/* Clase de complejidad */}
              <div className="flex items-center justify-between bg-gray-800 p-4 rounded-lg">
                <div>
                  <p className="text-xs text-gray-400 mb-1">Clase de Complejidad:</p>
                  <p className="text-purple-400 font-bold text-lg">{singleStep.complexity_class}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 mb-1">Notación Asintótica:</p>
                  <p className="text-purple-400 font-bold text-2xl">{singleStep.big_o}</p>
                </div>
              </div>
            </div>
          )}

          {/* Tabla de análisis línea por línea (iterativo) */}
          {singleStep.line_analysis && Array.isArray(singleStep.line_analysis) && singleStep.line_analysis.length > 0 && (
            <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
              <h4 className="text-purple-300 font-semibold mb-3 flex items-center gap-2">
                📊 Análisis Línea por Línea
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
                    {singleStep.line_analysis.map((line, i) => (
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
          )}

          {/* Pasos matemáticos (iterativo) */}
          {singleStep.math_steps && (
            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-sm font-semibold text-gray-300 mb-2">
                🧮 Pasos Matemáticos:
              </h4>
              <p className="text-green-400 font-mono text-sm whitespace-pre-wrap">
                {singleStep.math_steps}
              </p>
            </div>
          )}

          {singleStep.explanation && (
            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-sm font-semibold text-gray-300 mb-2">
                💡 Explicación:
              </h4>
              <p className="text-gray-300 text-sm whitespace-pre-line">
                {singleStep.explanation}
              </p>
            </div>
          )}

          {singleStep.steps && singleStep.steps.length > 0 && (
            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-sm font-semibold text-gray-300 mb-3">
                Pasos de Resolución:
              </h4>
              <div className="space-y-2">
                {singleStep.steps.map((step, idx) => (
                  <div
                    key={idx}
                    className="text-gray-300 text-sm font-mono whitespace-pre-line"
                  >
                    {step}
                  </div>
                ))}
              </div>
            </div>
          )}

          {singleStep.classification_reasoning && (
            <div className="bg-blue-900/20 border border-blue-700 p-3 rounded-lg">
              <p className="text-xs text-blue-300 mb-1">
                💡 Razonamiento de Clasificación
                {singleStep.classification_confidence && (
                  <span className="ml-2 text-blue-400 font-semibold">
                    (Confianza:{" "}
                    {(singleStep.classification_confidence * 100).toFixed(0)}%)
                  </span>
                )}
              </p>
              <p className="text-blue-200 text-sm">
                {singleStep.classification_reasoning}
              </p>
            </div>
          )}
        </div>

        {/* Diagrama de traza para caso único */}
        {singleStep.trace_diagram && (
          <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
            <h4 className="text-purple-300 font-semibold mb-3 flex items-center gap-2">
              🌳 Diagrama de Seguimiento
            </h4>
            <TreeVisualizer mermaidCode={singleStep.trace_diagram} isRecursive={false} />
          </div>
        )}

        {/* Diagramas adicionales (recursivo) */}
        {diagrams && Object.keys(diagrams).length > 0 && (
          <div className="space-y-4">
            {Object.entries(diagrams).map(([key, mermaidCode]) => (
              <div key={key} className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
                <h4 className="text-purple-300 font-semibold mb-3 flex items-center gap-2">
                  🌳 {key.includes('tree') ? 'Árbol de Recursión' : 'Diagrama'}
                </h4>
                <TreeVisualizer mermaidCode={mermaidCode} isRecursive={true} />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  const caseLabels = {
    best_case: { label: "🟢 Mejor Caso", color: "bg-green-600" },
    worst_case: { label: "🔴 Peor Caso", color: "bg-red-600" },
    average_case: { label: "🟡 Caso Promedio", color: "bg-yellow-600" },
  };

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-700 pb-2">
        {availableCases.map((caseType, index) => {
          const caseInfo = caseLabels[caseType] || {
            label: caseType,
            color: "bg-gray-600",
          };
          return (
            <button
              key={index}
              onClick={() => setActiveCase(index)}
              className={`px-6 py-3 rounded-t-lg font-semibold transition ${
                activeCase === index
                  ? `${caseInfo.color} text-white`
                  : "bg-gray-700 text-gray-400 hover:bg-gray-600"
              }`}
            >
              {caseInfo.label}
            </button>
          );
        })}
      </div>

      {/* Contenido del caso activo */}
      <div className="space-y-6">
        {(() => {
          const currentStep = analysisSteps[activeCase];

          return (
            <div className="bg-gray-700 rounded-lg p-6 space-y-4">
              {/* Condición del caso (si existe - típico de iterativo) */}
              {currentStep.condition && (
                <div className="bg-yellow-900/20 border border-yellow-700 p-4 rounded-lg">
                  <p className="text-xs text-yellow-300 mb-1 font-semibold">📋 Condición del Caso:</p>
                  <p className="text-yellow-200 text-sm italic">{currentStep.condition}</p>
                </div>
              )}

              {/* Big O Badge (si existe) */}
              {currentStep.big_o && (
                <div className="flex justify-end">
                  <div className="bg-purple-600 text-white px-6 py-3 rounded-lg text-2xl font-bold shadow-lg">
                    {currentStep.big_o}
                  </div>
                </div>
              )}

              {/* Ecuación Original (si existe y es diferente) */}
              {currentStep.original_equation && currentStep.original_equation !== currentStep.equation && (
                <div className="bg-blue-900/20 border border-blue-700 p-4 rounded-lg">
                  <p className="text-xs text-blue-300 mb-1 font-semibold">📝 Ecuación Original:</p>
                  <p className="text-blue-200 font-mono text-sm">
                    {currentStep.original_equation}
                  </p>
                </div>
              )}

              {/* Simplificación (si existe) */}
              {currentStep.simplification && (
                <div className="bg-green-900/20 border border-green-700 p-4 rounded-lg space-y-3">
                  <h4 className="text-sm font-semibold text-green-300 mb-2">🔄 Proceso de Simplificación:</h4>
                  
                  <div className="bg-gray-800 p-3 rounded">
                    <p className="text-xs text-gray-400 mb-1">Original:</p>
                    <p className="text-gray-200 font-mono text-xs">{currentStep.simplification.original}</p>
                  </div>
                  
                  <div className="bg-gray-800 p-3 rounded">
                    <p className="text-xs text-gray-400 mb-1">Simplificada:</p>
                    <p className="text-green-400 font-mono text-sm font-semibold">{currentStep.simplification.simplified}</p>
                  </div>

                  {currentStep.simplification.steps && currentStep.simplification.steps.length > 0 && (
                    <div className="bg-gray-800 p-3 rounded">
                      <p className="text-xs text-gray-400 mb-2">Pasos:</p>
                      <div className="space-y-1">
                        {currentStep.simplification.steps.map((step, idx) => (
                          <p key={idx} className="text-gray-300 text-xs">{step}</p>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-2">
                    {currentStep.simplification.explicit_form && (
                      <div className="bg-gray-800 p-2 rounded">
                        <p className="text-xs text-gray-400">Forma Explícita:</p>
                        <p className="text-green-400 font-mono text-xs">{currentStep.simplification.explicit_form}</p>
                      </div>
                    )}
                    {currentStep.simplification.confidence && (
                      <div className="bg-gray-800 p-2 rounded">
                        <p className="text-xs text-gray-400">Confianza:</p>
                        <p className="text-green-400 font-semibold text-xs">{(currentStep.simplification.confidence * 100).toFixed(0)}%</p>
                      </div>
                    )}
                    {currentStep.simplification.pattern_type && (
                      <div className="bg-gray-800 p-2 rounded">
                        <p className="text-xs text-gray-400">Patrón:</p>
                        <p className="text-purple-400 text-xs capitalize">{currentStep.simplification.pattern_type}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Información principal */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-800 p-4 rounded-lg">
                  <p className="text-xs text-gray-400 mb-1">Ecuación:</p>
                  <p className="text-green-400 font-mono text-sm">
                    {currentStep.equation || currentStep.raw_summation_str}
                  </p>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg">
                  <p className="text-xs text-gray-400 mb-1">Método:</p>
                  <p className="text-blue-400 text-sm capitalize">
                    {currentStep.method || 'Conteo de Pasos'}
                  </p>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg">
                  <p className="text-xs text-gray-400 mb-1">Complejidad:</p>
                  <p className="text-yellow-400 font-bold text-xl">
                    {currentStep.complexity || currentStep.big_o}
                  </p>
                </div>
              </div>

              {/* Proceso de Simplificación Iterativo */}
              {currentStep.raw_summation_str && currentStep.simplified_complexity && (
                <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-700 p-5 rounded-xl space-y-4">
                  <h4 className="text-lg font-semibold text-blue-300 mb-3 flex items-center gap-2">
                    🧮 Proceso de Simplificación
                  </h4>
                  
                  {/* Ecuación original */}
                  <div className="bg-gray-800 p-4 rounded-lg">
                    <p className="text-xs text-gray-400 mb-2">1️⃣ Sumatoria Original:</p>
                    <p className="text-gray-200 font-mono text-sm break-all">{currentStep.raw_summation_str}</p>
                  </div>

                  {/* Pasos matemáticos */}
                  {currentStep.math_steps && (
                    <div className="bg-gray-800 p-4 rounded-lg">
                      <p className="text-xs text-gray-400 mb-2">2️⃣ Desarrollo Matemático:</p>
                      <p className="text-blue-300 font-mono text-sm break-all">{currentStep.math_steps}</p>
                    </div>
                  )}

                  {/* Forma simplificada */}
                  <div className="bg-gray-800 p-4 rounded-lg border-2 border-green-500/50">
                    <p className="text-xs text-gray-400 mb-2">3️⃣ Forma Simplificada:</p>
                    <p className="text-green-400 font-mono text-base font-bold break-all">{currentStep.simplified_complexity}</p>
                  </div>

                  {/* Clase de complejidad */}
                  <div className="flex items-center justify-between bg-gray-800 p-4 rounded-lg">
                    <div>
                      <p className="text-xs text-gray-400 mb-1">Clase de Complejidad:</p>
                      <p className="text-purple-400 font-bold text-lg">{currentStep.complexity_class}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400 mb-1">Notación Asintótica:</p>
                      <p className="text-purple-400 font-bold text-2xl">{currentStep.big_o}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Tabla de análisis línea por línea (solo iterativo) */}
              {currentStep.line_analysis && currentStep.line_analysis.length > 0 && (
                <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
                  <h4 className="text-purple-300 font-semibold mb-3 flex items-center gap-2">
                    📊 Análisis Línea por Línea
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
                        {currentStep.line_analysis.map((line, i) => (
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
              )}

              {/* Pasos matemáticos (iterativo) */}
              {currentStep.math_steps && (
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">
                    🧮 Pasos Matemáticos:
                  </h4>
                  <p className="text-green-400 font-mono text-sm whitespace-pre-wrap">
                    {currentStep.math_steps}
                  </p>
                </div>
              )}

              {/* Explicación */}
              {currentStep.explanation && (
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">
                    Explicación:
                  </h4>
                  <p className="text-gray-300 text-sm whitespace-pre-line">
                    {currentStep.explanation}
                  </p>
                </div>
              )}

              {/* Pasos de resolución */}
              {currentStep.steps && currentStep.steps.length > 0 && (
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-300 mb-3">
                    Pasos de Resolución:
                  </h4>
                  <div className="space-y-2">
                    {currentStep.steps.map((step, idx) => (
                      <div
                        key={idx}
                        className="text-gray-300 text-sm font-mono whitespace-pre-line"
                      >
                        {step}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Razonamiento de clasificación */}
              {currentStep.classification_reasoning && (
                <div className="bg-blue-900/20 border border-blue-700 p-3 rounded-lg">
                  <p className="text-xs text-blue-300 mb-1">
                    💡 Razonamiento de Clasificación
                    {currentStep.classification_confidence && (
                      <span className="ml-2 text-blue-400 font-semibold">
                        (Confianza:{" "}
                        {(currentStep.classification_confidence * 100).toFixed(
                          0
                        )}
                        %)
                      </span>
                    )}
                  </p>
                  <p className="text-blue-200 text-sm">
                    {currentStep.classification_reasoning}
                  </p>
                </div>
              )}

              {/* Detalles adicionales */}
              {currentStep.details &&
                Object.keys(currentStep.details).length > 0 && (
                  <div className="bg-gray-800 p-4 rounded-lg">
                    <h4 className="text-sm font-semibold text-gray-300 mb-2">
                      🔍 Detalles Técnicos:
                    </h4>
                    <div className="space-y-2 text-sm">
                      {Object.entries(currentStep.details).map(
                        ([key, value]) => {
                          // Skip if it's steps or explanation (already shown elsewhere)
                          if (key === 'steps' || key === 'explanation') return null;
                          
                          return (
                            <div key={key} className="bg-gray-900 p-3 rounded">
                              <span className="text-gray-400 capitalize block mb-1 text-xs">
                                {key.replace(/_/g, " ")}:
                              </span>
                              {Array.isArray(value) ? (
                                <div className="space-y-1">
                                  {value.map((item, idx) => (
                                    <p key={idx} className="text-gray-200 text-xs pl-2">
                                      • {item}
                                    </p>
                                  ))}
                                </div>
                              ) : typeof value === "boolean" ? (
                                <span className={`text-sm font-semibold ${
                                  value ? 'text-green-400' : 'text-red-400'
                                }`}>
                                  {value ? '✓ Sí' : '✗ No'}
                                </span>
                              ) : typeof value === "object" && value !== null ? (
                                <pre className="text-gray-200 text-xs font-mono whitespace-pre-wrap">
                                  {JSON.stringify(value, null, 2)}
                                </pre>
                              ) : (
                                <span className="text-gray-200 font-mono text-sm">
                                  {String(value)}
                                </span>
                              )}
                            </div>
                          );
                        }
                      )}
                    </div>
                  </div>
                )}
            </div>
          );
        })()}

        {/* Diagrama de traza (iterativo) */}
        {analysisSteps[activeCase]?.trace_diagram && (
          <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
            <h4 className="text-purple-300 font-semibold mb-3 flex items-center gap-2">
              🌳 Diagrama de Seguimiento
            </h4>
            <TreeVisualizer 
              mermaidCode={analysisSteps[activeCase].trace_diagram} 
              isRecursive={false}
            />
          </div>
        )}

        {/* Árbol de recursión para el caso activo (recursivo) */}
        {diagrams && availableCases[activeCase] && diagrams[`tree_method_${availableCases[activeCase]}`] && (
          <div className="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
            <h4 className="text-purple-300 font-semibold mb-3 flex items-center gap-2">
              🌳 Árbol de Recursión
            </h4>
            <TreeVisualizer 
              mermaidCode={diagrams[`tree_method_${availableCases[activeCase]}`]} 
              isRecursive={true}
            />
          </div>
        )}
      </div>
    </div>
  );
}

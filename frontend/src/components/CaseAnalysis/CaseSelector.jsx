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
  const availableCases = analysisSteps.map(step => step.case_type || 'single');

  // Si solo hay un caso, mostrar sin tabs
  if (availableCases.length === 1) {
    const singleCase = availableCases[0];
    const singleStep = analysisSteps[0];

    return (
      <div className="space-y-6">
        {singleCase === 'single' && (
          <div className="bg-purple-900/20 border border-purple-700 p-4 rounded-lg">
            <p className="text-purple-300 text-sm">
              ℹ️ Este análisis tiene un único caso (no se diferencia entre mejor, peor y promedio)
            </p>
          </div>
        )}
        
        {/* Información del caso */}
        <div className="bg-gray-700 rounded-lg p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">Ecuación:</p>
              <p className="text-green-400 font-mono text-sm">{singleStep.equation}</p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">Método:</p>
              <p className="text-blue-400 text-sm capitalize">{singleStep.method}</p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-xs text-gray-400 mb-1">Complejidad:</p>
              <p className="text-yellow-400 font-bold text-xl">{singleStep.complexity}</p>
            </div>
          </div>

          {singleStep.explanation && (
            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-sm font-semibold text-gray-300 mb-2">Explicación:</h4>
              <p className="text-gray-300 text-sm whitespace-pre-line">{singleStep.explanation}</p>
            </div>
          )}

          {singleStep.steps && singleStep.steps.length > 0 && (
            <div className="bg-gray-800 p-4 rounded-lg">
              <h4 className="text-sm font-semibold text-gray-300 mb-3">Pasos de Resolución:</h4>
              <div className="space-y-2">
                {singleStep.steps.map((step, idx) => (
                  <div key={idx} className="text-gray-300 text-sm font-mono whitespace-pre-line">
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
                    (Confianza: {(singleStep.classification_confidence * 100).toFixed(0)}%)
                  </span>
                )}
              </p>
              <p className="text-blue-200 text-sm">{singleStep.classification_reasoning}</p>
            </div>
          )}
        </div>

        {diagrams?.recursion_trees?.trees && (
          <TreeVisualizer 
            trees={diagrams.recursion_trees.trees} 
            summary={diagrams.recursion_trees.summary}
          />
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
          const caseInfo = caseLabels[caseType] || { label: caseType, color: "bg-gray-600" };
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
              {/* Información principal */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-800 p-4 rounded-lg">
                  <p className="text-xs text-gray-400 mb-1">Ecuación:</p>
                  <p className="text-green-400 font-mono text-sm">{currentStep.equation}</p>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg">
                  <p className="text-xs text-gray-400 mb-1">Método:</p>
                  <p className="text-blue-400 text-sm capitalize">{currentStep.method}</p>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg">
                  <p className="text-xs text-gray-400 mb-1">Complejidad:</p>
                  <p className="text-yellow-400 font-bold text-xl">{currentStep.complexity}</p>
                </div>
              </div>

              {/* Explicación */}
              {currentStep.explanation && (
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">Explicación:</h4>
                  <p className="text-gray-300 text-sm whitespace-pre-line">{currentStep.explanation}</p>
                </div>
              )}

              {/* Pasos de resolución */}
              {currentStep.steps && currentStep.steps.length > 0 && (
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-300 mb-3">Pasos de Resolución:</h4>
                  <div className="space-y-2">
                    {currentStep.steps.map((step, idx) => (
                      <div key={idx} className="text-gray-300 text-sm font-mono whitespace-pre-line">
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
                        (Confianza: {(currentStep.classification_confidence * 100).toFixed(0)}%)
                      </span>
                    )}
                  </p>
                  <p className="text-blue-200 text-sm">{currentStep.classification_reasoning}</p>
                </div>
              )}

              {/* Detalles adicionales */}
              {currentStep.details && Object.keys(currentStep.details).length > 0 && (
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">Detalles Técnicos:</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {Object.entries(currentStep.details).map(([key, value]) => (
                      <div key={key} className="bg-gray-900 p-2 rounded">
                        <span className="text-gray-400 capitalize">{key.replace(/_/g, ' ')}:</span>
                        <span className="text-gray-200 ml-2 font-mono">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })()}

        {/* Árbol de recursión para el caso activo */}
        {diagrams?.recursion_trees?.trees && (
          <TreeVisualizer
            trees={diagrams.recursion_trees.trees.filter(
              (tree) => {
                const caseMap = {
                  'best_case': 'best',
                  'worst_case': 'worst',
                  'average_case': 'average'
                };
                return tree.case_type === caseMap[availableCases[activeCase]] || 
                       tree.case_type === availableCases[activeCase];
              }
            )}
            summary={diagrams.recursion_trees.summary}
          />
        )}
      </div>
    </div>
  );
}

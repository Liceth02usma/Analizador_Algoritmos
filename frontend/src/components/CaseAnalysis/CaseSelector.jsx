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

  // Agrupar steps por caso
  const caseSteps = {
    best_case: [],
    worst_case: [],
    average_case: [],
    single: [],
  };

  analysisSteps.forEach((step) => {
    const caseType = step.case_type || "single";
    if (caseSteps[caseType]) {
      caseSteps[caseType].push(step);
    }
  });

  // Determinar casos disponibles
  const availableCases = Object.entries(caseSteps)
    .filter(([, steps]) => steps.length > 0)
    .map(([caseType]) => caseType);

  // Si solo hay un caso, mostrar sin tabs
  if (availableCases.length === 1) {
    const singleCase = availableCases[0];
    return (
      <div className="space-y-6">
        {singleCase === 'single' && (
          <div className="bg-purple-900/20 border border-purple-700 p-4 rounded-lg">
            <p className="text-purple-300 text-sm">
              ℹ️ Este análisis tiene un único caso (no se diferencia entre mejor, peor y promedio)
            </p>
          </div>
        )}
        <StepsList steps={caseSteps[singleCase]} caseType={singleCase} />
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
          const caseInfo = caseLabels[caseType];
          return (
            <button
              key={caseType}
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
        <StepsList
          steps={caseSteps[availableCases[activeCase]]}
          caseType={availableCases[activeCase]}
        />

        {diagrams?.recursion_trees?.trees && (
          <TreeVisualizer
            trees={diagrams.recursion_trees.trees.filter(
              (tree) => tree.case_type === availableCases[activeCase]
            )}
            summary={diagrams.recursion_trees.summary}
          />
        )}
      </div>
    </div>
  );
}

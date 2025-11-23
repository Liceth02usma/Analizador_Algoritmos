import React, { useState } from "react";
import { CodeBlock } from "../shared";

export default function CodeViewer({ code, explanation, complexity }) {
  const [activeCase, setActiveCase] = useState(0);

  // Si code es un array de objetos (múltiples casos)
  if (Array.isArray(code)) {
    const caseLabels = [
      { type: "best_case", label: "🟢 Mejor Caso", color: "bg-green-600" },
      { type: "worst_case", label: "🔴 Peor Caso", color: "bg-red-600" },
      { type: "average_case", label: "🟡 Caso Promedio", color: "bg-yellow-600" },
    ];

    const currentCase = code[activeCase];

    return (
      <div className="bg-gray-800 rounded-xl p-6 space-y-4">
        <h3 className="text-2xl font-bold text-purple-400 flex items-center gap-2">
          📝 Código Anotado por Caso
        </h3>

        {/* Tabs para casos */}
        <div className="flex gap-2 border-b border-gray-700 pb-2">
          {code.map((caseData, index) => {
            const label = caseLabels.find(l => l.type === caseData.case_type) || 
                         { label: caseData.case_type, color: "bg-gray-600" };
            return (
              <button
                key={index}
                onClick={() => setActiveCase(index)}
                className={`px-6 py-3 rounded-t-lg font-semibold transition ${
                  activeCase === index
                    ? `${label.color} text-white`
                    : "bg-gray-700 text-gray-400 hover:bg-gray-600"
                }`}
              >
                {label.label}
              </button>
            );
          })}
        </div>

        {/* Explicación del caso */}
        {currentCase.code_explanation && (
          <div className="bg-gray-700 p-4 rounded-lg">
            <h4 className="text-lg font-semibold text-gray-200 mb-2">Descripción</h4>
            <p className="text-gray-300">{currentCase.code_explanation}</p>
          </div>
        )}

        {/* Código anotado */}
        <CodeBlock code={currentCase.pseudocode_annotated} />

        {/* Complejidad del caso */}
        {currentCase.complexity_explanation && (
          <div className="bg-gray-700 p-4 rounded-lg">
            <h4 className="text-lg font-semibold text-gray-200 mb-2">Análisis de Complejidad</h4>
            <p className="text-gray-300">{currentCase.complexity_explanation}</p>
            {currentCase.total_complexity && (
              <p className="text-yellow-400 font-bold text-xl mt-2">
                Complejidad Total: {currentCase.total_complexity}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }

  // Si code es un string (caso único)
  return (
    <div className="bg-gray-800 rounded-xl p-6 space-y-4">
      <h3 className="text-2xl font-bold text-purple-400 flex items-center gap-2">
        📝 Código del Algoritmo
      </h3>
      
      {explanation && (
        <div className="bg-gray-700 p-4 rounded-lg">
          <h4 className="text-lg font-semibold text-gray-200 mb-2">¿Qué hace este algoritmo?</h4>
          <p className="text-gray-300">{explanation}</p>
        </div>
      )}
      
      <CodeBlock code={code} />
      
      {complexity && (
        <div className="bg-gray-700 p-4 rounded-lg">
          <h4 className="text-lg font-semibold text-gray-200 mb-2">Explicación de Complejidad</h4>
          <p className="text-gray-300">{complexity}</p>
        </div>
      )}
    </div>
  );
}

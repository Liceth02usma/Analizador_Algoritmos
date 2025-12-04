// src/components/ResultAnalysis.jsx
import React from "react";

export default function ResultAnalysis({ analysis }) {
  if (!analysis) {
    return (
      <p className="text-gray-400 italic">
        Aquí se mostrará el análisis línea por línea...
      </p>
    );
  }

  if (analysis.error) {
    return (
      <p className="text-red-400 font-semibold">
        ❌ Error: {analysis.error}
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-purple-400">
        Tipo de algoritmo detectado: {analysis.detected_type?.toUpperCase()}
      </h3>

      <p>
        <span className="font-bold text-gray-300">Nivel de confianza:</span>{" "}
        {Math.round(analysis.confidence_level * 100)}%
      </p>

      <div>
        <span className="font-bold text-gray-300">Indicadores clave:</span>
        <ul className="list-disc ml-6 text-gray-300">
          {analysis.key_indicators?.map((ind, idx) => (
            <li key={idx}>{ind}</li>
          ))}
        </ul>
      </div>

      <div className="bg-gray-700 rounded-lg p-3 shadow-inner">
        <p className="font-bold text-gray-300 mb-2">Justificación técnica:</p>
        <p className="text-gray-200">{analysis.justification}</p>
      </div>
    </div>
  );
}

import React from "react";

export default function ResultClassifier({ analysis, classification }) {
  if (!analysis && !classification) {
    return (
      <div className="text-gray-400 italic text-center py-6">
        📄 Ingresa un pseudocódigo y ejecuta el análisis para ver los resultados aquí.
      </div>
    );
  }

  const detectedType = analysis?.detected_type || "No detectado";
  const typeConfidence = analysis?.confidence?.toFixed(2);
  const classData = classification || {};

  return (
    <div className="space-y-6">
      {/* 🧠 Tipo del algoritmo */}
      {analysis && (
        <section className="bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-700">
          <h3 className="text-lg font-semibold text-purple-400 mb-2">
            🧩 Tipo de Algoritmo
          </h3>
          <p className="text-gray-200 text-base">
            <strong>Clasificación:</strong> {detectedType}
          </p>
          {typeConfidence && (
            <p className="text-gray-400 text-sm">
              Confianza del modelo:{" "}
              <span className="text-green-400">{typeConfidence}</span>
            </p>
          )}
          {analysis?.justification && (
            <p className="mt-3 text-gray-400 text-sm italic">
              {analysis.justification}
            </p>
          )}
        </section>
      )}

      {/* ⚙️ Clasificación funcional y estructural */}
      {classification && (
        <section className="bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-700">
          <h3 className="text-lg font-semibold text-purple-400 mb-2">
            ⚙️ Clasificación Funcional y Estructural
          </h3>

          <div className="space-y-2 text-gray-200">
            <p><strong>Funcional:</strong> {classData.functional_class || "No detectada"}</p>
            <p><strong>Estructural:</strong> {classData.structural_pattern || "No detectada"}</p>
            {classData.confidence_level && (
              <p className="text-gray-400 text-sm">
                Confianza:{" "}
                <span className="text-green-400">
                  {classData.confidence_level.toFixed(2)}
                </span>
              </p>
            )}
          </div>

          {classData.possible_known_algorithms?.length > 0 && (
            <div className="mt-3">
              <strong className="text-gray-300">🔍 Posibles algoritmos:</strong>
              <ul className="list-disc list-inside text-gray-400 text-sm">
                {classData.possible_known_algorithms.map((algo, i) => (
                  <li key={i}>{algo}</li>
                ))}
              </ul>
            </div>
          )}

          {classData.key_features?.length > 0 && (
            <div className="mt-3">
              <strong className="text-gray-300">💡 Indicadores clave:</strong>
              <ul className="list-disc list-inside text-gray-400 text-sm">
                {classData.key_features.map((feat, i) => (
                  <li key={i}>{feat}</li>
                ))}
              </ul>
            </div>
          )}

          {classData.justification && (
            <div className="mt-4 text-gray-400 text-sm italic">
              {classData.justification}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

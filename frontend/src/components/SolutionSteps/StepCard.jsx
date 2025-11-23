import React from "react";
import { MarkdownRenderer } from "../shared";
import MethodBadge from "./MethodBadge";

export default function StepCard({ step, index }) {
  return (
    <div className="bg-gray-700 rounded-lg p-5 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-bold text-purple-400">
          Paso {index + 1}
        </h4>
        <MethodBadge method={step.method} />
      </div>

      <div className="bg-gray-800 p-3 rounded">
        <p className="text-sm text-gray-400 mb-1">Ecuación:</p>
        <p className="text-green-400 font-mono">{step.equation}</p>
      </div>

      <div className="bg-gray-800 p-3 rounded">
        <p className="text-sm text-gray-400 mb-1">Complejidad:</p>
        <p className="text-xl font-bold text-yellow-400">{step.complexity}</p>
      </div>

      {step.classification_confidence && (
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-400">Confianza:</span>
          <span className="text-green-400 font-semibold">
            {(step.classification_confidence * 100).toFixed(0)}%
          </span>
        </div>
      )}

      {step.steps && step.steps.length > 0 && (
        <div className="bg-gray-800 p-4 rounded space-y-2">
          <p className="text-sm font-semibold text-gray-300 mb-2">🔧 Pasos de Resolución:</p>
          <div className="space-y-2">
            {step.steps.map((line, i) => (
              <div key={i} className="flex gap-2">
                <span className="text-purple-400 font-bold text-xs mt-1">{i + 1}.</span>
                <span className="text-sm text-gray-300 whitespace-pre-wrap flex-1">{line}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {step.explanation && (
        <div className="bg-gray-800 p-4 rounded">
          <p className="text-sm font-semibold text-gray-300 mb-2">📖 Explicación Detallada:</p>
          <p className="text-gray-300 text-sm whitespace-pre-wrap leading-relaxed">{step.explanation}</p>
        </div>
      )}

      {step.details && Object.keys(step.details).length > 0 && (
        <div className="bg-gray-800 p-4 rounded">
          <p className="text-sm font-semibold text-gray-300 mb-2">🔍 Detalles Técnicos:</p>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(step.details).map(([key, value]) => (
              <div key={key} className="text-sm">
                <span className="text-gray-400">{key.replace(/_/g, ' ')}:</span>
                <span className="text-green-400 ml-2 font-mono">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {step.classification_reasoning && (
        <div className="bg-blue-900/20 border border-blue-700 p-3 rounded">
          <p className="text-sm text-blue-300">
            💡 <span className="font-semibold">Razonamiento:</span> {step.classification_reasoning}
          </p>
        </div>
      )}
    </div>
  );
}

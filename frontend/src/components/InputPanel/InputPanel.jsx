import React from "react";
import InputAlgorithm from "../InputAlgorithm";

export default function InputPanel({ 
  pseudocode, 
  setPseudocode, 
  onAnalyze,
  onTranslate,
  isTranslating,
  translationMessage
}) {
  return (
    <aside className="w-1/4 flex flex-col border-r border-gray-700 p-4 space-y-4 bg-gray-800">
      <h2 className="bg-black text-white text-center py-1 rounded font-semibold">
        INPUT
      </h2>

      <InputAlgorithm value={pseudocode} onChange={setPseudocode} />

      <button
        onClick={onTranslate}
        disabled={isTranslating}
        className="mt-2 bg-blue-700 hover:bg-blue-800 text-white py-2 px-4 rounded-lg transition self-center disabled:opacity-50"
      >
        {isTranslating
          ? "🔄 Traduciendo..."
          : "🌐 Traducir desde Lenguaje Natural"}
      </button>

      {translationMessage && (
        <div className="text-sm text-center py-2 px-3 bg-gray-700 rounded">
          {translationMessage}
        </div>
      )}

      <button
        onClick={onAnalyze}
        className="mt-2 bg-purple-700 hover:bg-purple-800 text-white py-2 px-4 rounded-lg transition self-center"
      >
        ⚙️ Analizar Algoritmo
      </button>
    </aside>
  );
}

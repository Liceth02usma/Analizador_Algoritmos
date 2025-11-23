import React from "react";

export default function AnalysisSteps() {
  return (
    <main className="flex-1 bg-gray-850 p-4 flex flex-col">
      <h2 className="text-center text-xl font-semibold mb-3">
        📊 Análisis paso a paso
      </h2>
      <div className="bg-gray-800 rounded-xl shadow-inner p-4 flex-1 overflow-y-auto">
        <p className="text-gray-400 italic">
          Aquí se mostrará el análisis línea por línea...
        </p>
      </div>
    </main>
  );
}

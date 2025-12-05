import React from "react";

export default function AnalysisHeader() {
  return (
    <header className="bg-purple-900 px-6 py-4 flex justify-between items-center shadow-lg">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        🔍 Analizador de Complejidad Algorítmica
      </h1>
      <button className="bg-black px-4 py-2 rounded-lg hover:bg-gray-800 transition">
        Mostrar análisis línea a línea
      </button>
    </header>
  );
}

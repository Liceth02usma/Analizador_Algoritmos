import React, { useState } from "react";
import InputAlgorithm from "../components/InputAlgorithm";
import OutputSolution from "../components/OutputSolution";

export default function HomePage() {
  const [pseudocode, setPseudocode] = useState("");
  const [output, setOutput] = useState("");

  const handleRun = async () => {
    try {
      const response = await fetch("http://localhost:8000/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pseudocode }),
      });
      const data = await response.json();
      setOutput(JSON.stringify(data.ast, null, 2));
    } catch (error) {
      console.error("Error al analizar:", error);
      setOutput("❌ Error al analizar el pseudocódigo.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white">
      {/* HEADER */}
      <header className="bg-purple-900 px-6 py-4 flex justify-between items-center shadow-lg">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          🔍 Analizador de Complejidad Algorítmica
        </h1>
        <button className="bg-black px-4 py-2 rounded-lg hover:bg-gray-800 transition">
          Mostrar análisis línea a línea
        </button>
      </header>

      {/* BODY GRID */}
      <div className="flex flex-1 overflow-hidden">
        {/* LEFT PANEL */}
        <aside className="w-1/4 flex flex-col border-r border-gray-700 p-4 space-y-4 bg-gray-800">
          <h2 className="bg-black text-white text-center py-1 rounded font-semibold">
            INPUT
          </h2>

          <InputAlgorithm value={pseudocode} onChange={setPseudocode} />

          <button
            onClick={handleRun}
            className="mt-2 bg-purple-700 hover:bg-purple-800 text-white py-2 px-4 rounded-lg transition self-center"
          >
            ⚙️ Comprobar Algoritmo
          </button>

          <h2 className="bg-black text-white text-center py-1 rounded font-semibold">
            OUTPUT
          </h2>
          <OutputSolution result={output} />
        </aside>

        {/* CENTER PANEL */}
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

        {/* RIGHT ACTION BAR */}
        <aside className="w-1/6 bg-gray-900 border-l border-gray-700 flex flex-col items-center justify-center gap-4 p-4">
          {[1, 2, 3, 4].map((i) => (
            <button
              key={i}
              className="bg-purple-700 hover:bg-purple-800 text-white px-4 py-2 rounded-full shadow-md text-sm w-40 text-center"
            >
              ⚙️ Comprobar Algoritmo
            </button>
          ))}
        </aside>
      </div>
    </div>
  );
}

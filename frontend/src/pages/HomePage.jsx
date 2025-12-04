// src/pages/HomePage.jsx
import React, { useState } from "react";
import InputAlgorithm from "../components/InputAlgorithm";
import OutputSolution from "../components/OutputSolution";
import ResultAnalysis from "../components/ResultAnalysis";
import ResultClassifier from "../components/ResultClassifier";


export default function HomePage() {
  const [pseudocode, setPseudocode] = useState("");
  const [output, setOutput] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [classification, setClassification] = useState(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationMessage, setTranslationMessage] = useState("");

  const handleTranslate = async () => {
    if (!pseudocode.trim()) {
      setTranslationMessage("❌ El input no puede estar vacío");
      return;
    }

    setIsTranslating(true);
    setTranslationMessage("🔄 Traduciendo...");

    try {
      const response = await fetch("http://localhost:8000/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: pseudocode }),
      });
      const data = await response.json();

      if (data.success) {
        // 🔹 Sobrescribir el input con el pseudocódigo generado
        setPseudocode(data.pseudocode);
        setTranslationMessage(`✅ ¡Traducción completada! Presiona "Comprobar Algoritmo" para continuar.`);
      } else {
        setTranslationMessage(`❌ Error: ${data.error}`);
      }
    } catch (error) {
      console.error("Error al traducir:", error);
      setTranslationMessage("❌ Error al conectarse con el servidor");
    } finally {
      setIsTranslating(false);
    }
  };

  const handleRun = async () => {
    try {
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pseudocode }),
      });
      const data = await response.json();

      // Mostrar AST en la parte izquierda
      setOutput(JSON.stringify(data.ast, null, 2));

      // Mostrar resultado del agente en el centro
      setAnalysis(data.algorithm_type);

        // 🔹 Mostrar resultado del segundo agente
      setClassification(data.algorithm_classification);

      console.log("📘 Respuesta completa:", data);
    } catch (error) {
      console.error("Error al analizar:", error);
      setOutput("❌ Error al analizar el pseudocódigo.");
      setAnalysis({ error: "Error al conectarse con el backend" });
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white">
      {/* HEADER */}
      <header className="bg-purple-900 px-6 py-4 flex justify-between items-center shadow-lg">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          🔍 Analizador de Complejidad Algorítmica
        </h1>
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
            onClick={handleTranslate}
            disabled={isTranslating}
            className="mt-2 bg-blue-700 hover:bg-blue-800 text-white py-2 px-4 rounded-lg transition self-center disabled:opacity-50"
          >
            {isTranslating ? "🔄 Traduciendo..." : "🌐 Traducir desde Lenguaje Natural"}
          </button>

          {translationMessage && (
            <div className="text-sm text-center py-2 px-3 bg-gray-700 rounded">
              {translationMessage}
            </div>
          )}

          <button
            onClick={handleRun}
            className="mt-2 bg-purple-700 hover:bg-purple-800 text-white py-2 px-4 rounded-lg transition self-center"
          >
            ⚙️ Comprobar Algoritmo
          </button>

          <h2 className="bg-black text-white text-center py-1 rounded font-semibold">
            OUTPUT (AST)
          </h2>
          <OutputSolution result={output} />
        </aside>

        {/* CENTER PANEL */}
        <main className="flex-1 bg-gray-850 p-4 flex flex-col">
          <h2 className="text-center text-xl font-semibold mb-3">
            📊 Análisis paso a paso
          </h2>
          <div className="bg-gray-800 rounded-xl shadow-inner p-4 flex-1 overflow-y-auto">
           { /*<ResultAnalysis analysis={analysis} /> */}
            <ResultClassifier analysis={analysis} classification={classification} />

          </div>
        </main>

        {/* RIGHT ACTION BAR */}
        <aside className="w-1/6 bg-gray-900 border-l border-gray-700 flex flex-col items-center justify-center gap-4 p-4">
          <button
            onClick={handleRun}
            className="bg-purple-700 hover:bg-purple-800 text-white px-4 py-2 rounded-full shadow-md text-sm w-40 text-center"
          >
            ⚙️ Analizar Tipo
          </button>
        </aside>
      </div>
    </div>
  );
}

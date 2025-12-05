import React, { useState, useEffect, useCallback } from "react";
import AnalysisFlow from "../AnalysisFlow/AnalysisFlow";
//import { analyzeRecursive } from "../../services/recursiveService";
import { analyzeIterative } from "../../services/iterative_service";

export default function AnalysisSteps({ pseudocode }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalysis = useCallback(async () => {
    // Extract actual pseudocode by removing timestamp if present
    const cleanPseudocode = pseudocode.includes("___") 
      ? pseudocode.substring(0, pseudocode.lastIndexOf("___"))
      : pseudocode;

    try {
      setLoading(true);
      setError(null);

      const result = await analyzeIterative(cleanPseudocode);

      console.log("[AnalysisSteps] Analysis result:", result);
      
      if (result.success) {
        // Extraer el análisis del wrapper  
        setAnalysis(result.data.analysis || result.data);
      } else {
        setError(result.error || "Error al analizar el algoritmo");
      }
    } catch (err) {
      setError(`Error inesperado: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [pseudocode]);

  useEffect(() => {
    // Extract clean pseudocode
    const cleanPseudocode = pseudocode.includes("___") 
      ? pseudocode.substring(0, pseudocode.lastIndexOf("___"))
      : pseudocode;

    if (!cleanPseudocode || cleanPseudocode.trim() === "") {
      setAnalysis(null);
      setError(null);
      setLoading(false);
      return;
    }

    handleAnalysis();
  }, [pseudocode, handleAnalysis]);

  return (
    <main className="flex-1 bg-gray-850 p-4 flex flex-col">
      <h2 className="text-center text-xl font-semibold mb-3">
        📊 Análisis paso a paso
      </h2>
      <div className="bg-gray-800 rounded-xl shadow-inner p-4 flex-1 overflow-y-auto">
        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-xl">Analizando algoritmo...</p>
          </div>
        )}

        {error && (
          <div className="text-center py-8">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <h3 className="text-xl font-bold mb-4 text-red-400">
              Error en el análisis
            </h3>
            <p className="text-gray-300">{error}</p>
          </div>
        )}

        {!loading && !error && !analysis && (
          <p className="text-gray-400 italic text-center py-8">
            Escribe o pega tu pseudocódigo y haz clic en "Analizar" para
            comenzar...
          </p>
        )}

        {!loading && !error && analysis && <AnalysisFlow analysis={analysis} />}
      </div>
    </main>
  );
}

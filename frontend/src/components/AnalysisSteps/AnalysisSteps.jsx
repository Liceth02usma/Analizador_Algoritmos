import React, { useState, useEffect, useCallback } from "react";
import AnalysisFlow from "../AnalysisFlow/AnalysisFlow";
import ComparisonView from "../ComparisonView/ComparisonView";
//import { analyzeRecursive } from "../../services/recursiveService";
import { analyzeIterative } from "../../services/iterative_service";
import comparisonService from "../../services/comparisonService";

export default function AnalysisSteps({ pseudocode }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showComparison, setShowComparison] = useState(false);
  const [comparisonData, setComparisonData] = useState(null);
  const [comparingLoading, setComparingLoading] = useState(false);
  const [algorithmName, setAlgorithmName] = useState("");
  const [currentPseudocode, setCurrentPseudocode] = useState("");

  const handleAnalysis = useCallback(async () => {
    // Extract actual pseudocode by removing timestamp if present
    const cleanPseudocode = pseudocode.includes("___") 
      ? pseudocode.substring(0, pseudocode.lastIndexOf("___"))
      : pseudocode;

    try {
      setLoading(true);
      setError(null);
      setShowComparison(false); // Reset comparison view

      const result = await analyzeIterative(cleanPseudocode);

      console.log("[AnalysisSteps] Analysis result:", result);
      
      if (result.success) {
        // Extraer el análisis del wrapper  
        const analysisData = result.data.analysis || result.data;
        setAnalysis(analysisData);
        
        // Guardar datos para comparación
        setCurrentPseudocode(cleanPseudocode);
        setAlgorithmName(result.data.classification?.name || "Algoritmo");
      } else {
        setError(result.error || "Error al analizar el algoritmo");
      }
    } catch (err) {
      setError(`Error inesperado: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [pseudocode]);

  const handleCompare = async () => {
    try {
      setComparingLoading(true);
      setError(null);

      console.log("🔬 Iniciando comparación...");
      const comparisonResult = await comparisonService.compareAnalysis(
        algorithmName,
        currentPseudocode
      );

      setComparisonData(comparisonResult);
      setShowComparison(true);
      console.log("✅ Comparación completada", comparisonResult);
    } catch (err) {
      setError(err.message || "Error al comparar análisis");
      console.error("❌ Error en comparación:", err);
    } finally {
      setComparingLoading(false);
    }
  };

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
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-xl font-semibold">
          📊 Análisis paso a paso
        </h2>
        
        {/* Botón de Comparación */}
        {!loading && !error && analysis && !showComparison && (
          <button
            onClick={handleCompare}
            disabled={comparingLoading}
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 px-4 py-2 rounded-lg transition flex items-center gap-2 text-sm"
          >
            {comparingLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                Comparando...
              </>
            ) : (
              <>
                📊 Comparar con Agente Completo
              </>
            )}
          </button>
        )}
        
        {/* Botón para volver al análisis */}
        {showComparison && (
          <button
            onClick={() => setShowComparison(false)}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition text-sm"
          >
            ← Ver Análisis Especializado
          </button>
        )}
      </div>
      
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

        {/* Mostrar comparación o análisis */}
        {!loading && !error && analysis && (
          showComparison ? (
            <ComparisonView comparisonData={comparisonData} />
          ) : (
            <AnalysisFlow analysis={analysis} />
          )
        )}
      </div>
    </main>
  );
}

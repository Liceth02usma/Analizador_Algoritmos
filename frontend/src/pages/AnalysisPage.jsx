 import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import AnalysisFlow from "../components/AnalysisFlow/AnalysisFlow";
import { analyzeRecursive } from "../services/recursiveService";

export default function AnalysisPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Verificar si tenemos el pseudocódigo
    if (!location.state?.pseudocode) {
      setError("No se encontró pseudocódigo para analizar");
      setLoading(false);
      return;
    }

    handleAnalysis();
  }, [location.state]);

  const handleAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);

      const { algorithmName, pseudocode } = location.state;
      const result = await analyzeRecursive(algorithmName, pseudocode);

      if (result.success) {
        setAnalysis(result.data);
      } else {
        setError(result.error || "Error al analizar el algoritmo");
      }
    } catch (err) {
      setError(`Error inesperado: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-xl">Analizando algoritmo...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center max-w-2xl mx-auto p-8">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold mb-4">Error en el análisis</h2>
          <p className="text-gray-300 mb-6">{error}</p>
          <button
            onClick={() => navigate("/")}
            className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg transition"
          >
            Volver al inicio
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <button
            onClick={() => navigate("/")}
            className="text-blue-400 hover:text-blue-300 transition flex items-center gap-2"
          >
            ← Volver al inicio
          </button>
        </div>
        
        <AnalysisFlow analysis={analysis} />
      </div>
    </div>
  );
}

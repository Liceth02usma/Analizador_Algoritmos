// src/pages/ResultsPage.jsx
import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import AnalysisFlow from "../components/AnalysisFlow/AnalysisFlow";

function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result;

  if (!result) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📭</div>
          <h2 className="text-2xl font-bold mb-4">No hay resultados disponibles</h2>
          <p className="text-gray-400 mb-6">Por favor, analiza un algoritmo primero</p>
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
        
        <AnalysisFlow analysis={result} />
      </div>
    </div>
  );
}

export default ResultsPage;


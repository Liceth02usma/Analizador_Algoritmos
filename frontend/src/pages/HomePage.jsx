import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AnalysisHeader from "../components/AnalysisHeader";
import InputPanel from "../components/InputPanel";
import AnalysisSteps from "../components/AnalysisSteps";
import ActionBar from "../components/ActionBar";

export default function HomePage() {
  const navigate = useNavigate();
  const [pseudocode, setPseudocode] = useState("");

  const handleAnalyze = () => {
    // Navegar a la página de análisis con el pseudocódigo
    navigate("/analysis", {
      state: {
        algorithmName: "Mi Algoritmo",
        pseudocode: pseudocode,
      },
    });
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white">
      <AnalysisHeader />
      
      <div className="flex flex-1 overflow-hidden">
        <InputPanel
          pseudocode={pseudocode}
          setPseudocode={setPseudocode}
          onAnalyze={handleAnalyze}
        />
        <AnalysisSteps />
        <ActionBar />
      </div>
    </div>
  );
}

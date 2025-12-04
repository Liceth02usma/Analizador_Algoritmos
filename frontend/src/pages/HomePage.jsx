// src/pages/HomePage.jsx
import React, { useState } from "react";
import AnalysisHeader from "../components/AnalysisHeader";
import InputPanel from "../components/InputPanel";
import AnalysisSteps from "../components/AnalysisSteps";

export default function HomePage() {
  const [pseudocode, setPseudocode] = useState("");
  const [triggerAnalysis, setTriggerAnalysis] = useState("");

  const handleAnalyze = () => {
    // Trigger analysis by updating the pseudocode passed to AnalysisSteps
    setTriggerAnalysis(pseudocode);
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
        <AnalysisSteps 
          pseudocode={triggerAnalysis} 
          algorithmName="Mi Algoritmo"
        />
      </div>
    </div>
  );
}


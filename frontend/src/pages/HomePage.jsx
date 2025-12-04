// src/pages/HomePage.jsx
import React, { useState } from "react";
import AnalysisHeader from "../components/AnalysisHeader";
import InputPanel from "../components/InputPanel";
import AnalysisSteps from "../components/AnalysisSteps";
import { translateToPseudocode } from "../services/translateService";

export default function HomePage() {
  const [pseudocode, setPseudocode] = useState("");
  const [triggerAnalysis, setTriggerAnalysis] = useState("");
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationMessage, setTranslationMessage] = useState("");

  const handleAnalyze = () => {
    // Trigger analysis by updating the pseudocode passed to AnalysisSteps
    // Force re-analysis by updating with timestamp to ensure it triggers even with same code
    setTriggerAnalysis(pseudocode);
  };

  const handleTranslate = async () => {
    if (!pseudocode.trim()) {
      setTranslationMessage("❌ El input no puede estar vacío");
      return;
    }

    setIsTranslating(true);
    setTranslationMessage("🔄 Traduciendo...");

    try {
      const result = await translateToPseudocode(pseudocode);

      if (result.success) {
        // Sobrescribir el input con el pseudocódigo generado
        setPseudocode(result.pseudocode);
        setTranslationMessage(
          '✅ ¡Traducción completada! Presiona "Comprobar Algoritmo" para continuar.'
        );
      } else {
        setTranslationMessage(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      console.error("Error al traducir:", error);
      setTranslationMessage("❌ Error inesperado al traducir");
    } finally {
      setIsTranslating(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-white">
      <AnalysisHeader />

      <div className="flex flex-1 overflow-hidden">
        <InputPanel
          pseudocode={pseudocode}
          setPseudocode={setPseudocode}
          onAnalyze={handleAnalyze}
          onTranslate={handleTranslate}
          isTranslating={isTranslating}
          translationMessage={translationMessage}
        />
        <AnalysisSteps 
          pseudocode={triggerAnalysis} 
          algorithmName="Mi Algoritmo"
        />
      </div>
    </div>
  );
}

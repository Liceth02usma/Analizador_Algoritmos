import React from "react";
import StepCard from "./StepCard";

export default function StepsList({ steps, caseType }) {
  const caseNames = {
    best_case: "Mejor Caso",
    worst_case: "Peor Caso",
    average_case: "Caso Promedio",
    single: "Análisis Único",
  };

  const caseName = caseNames[caseType] || caseType;

  return (
    <div className="space-y-4">
      <h3 className="text-2xl font-bold text-purple-400 flex items-center gap-2">
        🔍 {caseName}
      </h3>
      <div className="space-y-4">
        {steps.map((step, index) => (
          <StepCard key={index} step={step} index={index} />
        ))}
      </div>
    </div>
  );
}

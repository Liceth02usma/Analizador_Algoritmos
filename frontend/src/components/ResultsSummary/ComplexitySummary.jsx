import React from "react";

export default function ComplexitySummary({ equation, method, complexity, hasMultipleCases }) {
  const renderSingle = () => (
    <div className="bg-gray-700 p-5 rounded-lg space-y-3">
      <div>
        <p className="text-sm text-gray-400 mb-1">Ecuación de Recurrencia:</p>
        <p className="text-green-400 font-mono text-lg">{equation}</p>
      </div>
      <div>
        <p className="text-sm text-gray-400 mb-1">Método Utilizado:</p>
        <p className="text-blue-400 font-semibold">{method}</p>
      </div>
      <div>
        <p className="text-sm text-gray-400 mb-1">Complejidad Resultante:</p>
        <p className="text-yellow-400 font-bold text-3xl">{complexity}</p>
      </div>
    </div>
  );

  const renderMultiple = () => {
    // Convertir a arrays si no lo son
    const equations = Array.isArray(equation) ? equation : [equation, equation, equation];
    const methods = Array.isArray(method) ? method : [method, method, method];
    const complexities = Array.isArray(complexity) ? complexity : [complexity, complexity, complexity];

    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {["best_case", "worst_case", "average_case"].map((caseType, index) => {
          const caseLabels = {
            best_case: { label: "Mejor Caso", icon: "🟢", color: "green", borderColor: "border-green-500" },
            worst_case: { label: "Peor Caso", icon: "🔴", color: "red", borderColor: "border-red-500" },
            average_case: { label: "Caso Promedio", icon: "🟡", color: "yellow", borderColor: "border-yellow-500" },
          };
          const caseInfo = caseLabels[caseType];

          // Format method name for better display
          const formatMethod = (m) => {
            if (!m) return "N/A";
            return m.replace(/_/g, ' ')
              .split(' ')
              .map(word => word.charAt(0).toUpperCase() + word.slice(1))
              .join(' ');
          };

          return (
            <div
              key={caseType}
              className={`bg-gray-700 p-5 rounded-lg border-t-4 ${caseInfo.borderColor}`}
            >
              <h4 className="text-lg font-bold text-gray-200 mb-3">
                {caseInfo.icon} {caseInfo.label}
              </h4>
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-gray-400 mb-1">Ecuación:</p>
                  <p className="text-green-400 font-mono text-sm break-words">
                    {equations[index] || "N/A"}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 mb-1">Método:</p>
                  <p className="text-blue-400 text-sm">
                    {formatMethod(methods[index])}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-400 mb-1">Complejidad:</p>
                  <p className={`text-${caseInfo.color}-400 font-bold text-2xl`}>
                    {complexities[index] || "N/A"}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 space-y-4">
      <h3 className="text-2xl font-bold text-purple-400 flex items-center gap-2">
        📊 Resumen de Complejidad
      </h3>
      {hasMultipleCases ? renderMultiple() : renderSingle()}
    </div>
  );
}

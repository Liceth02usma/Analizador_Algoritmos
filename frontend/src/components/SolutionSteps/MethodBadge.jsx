import React from "react";

export default function MethodBadge({ method }) {
  // Mapeo de métodos del backend a nombres legibles
  const methodNames = {
    "master_theorem": "Teorema Maestro",
    "tree_method": "Método del Árbol",
    "equation_characteristics": "Ecuación Característica",
    "equation_characteristic": "Ecuación Característica",
    "none": "Análisis Directo",
    "direct_analysis": "Análisis Directo",
    // Nombres ya legibles
    "Teorema Maestro": "Teorema Maestro",
    "Método del Árbol": "Método del Árbol",
    "Ecuación Característica": "Ecuación Característica",
    "Análisis Directo": "Análisis Directo",
  };

  const methodColors = {
    "master_theorem": "bg-blue-600",
    "tree_method": "bg-green-600",
    "equation_characteristics": "bg-yellow-600",
    "equation_characteristic": "bg-yellow-600",
    "none": "bg-purple-600",
    "direct_analysis": "bg-purple-600",
    // Para nombres legibles
    "Teorema Maestro": "bg-blue-600",
    "Método del Árbol": "bg-green-600",
    "Ecuación Característica": "bg-yellow-600",
    "Análisis Directo": "bg-purple-600",
  };

  const methodIcons = {
    "master_theorem": "🎯",
    "tree_method": "🌳",
    "equation_characteristics": "📐",
    "equation_characteristic": "📐",
    "none": "📊",
    "direct_analysis": "📊",
  };

  const displayName = methodNames[method] || method;
  const color = methodColors[method] || "bg-gray-600";
  const icon = methodIcons[method] || "🔍";

  return (
    <span className={`${color} text-white px-3 py-1 rounded-full text-sm font-semibold inline-flex items-center gap-1`}>
      <span>{icon}</span>
      <span>{displayName}</span>
    </span>
  );
}

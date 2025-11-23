import React from "react";

export default function OutputSolution({ result }) {
  return (
    <pre className="bg-gray-800 text-green-400 p-3 rounded-md h-60 overflow-y-auto text-sm whitespace-pre-wrap border border-gray-700">
      {result || "El resultado del análisis aparecerá aquí..."}
    </pre>
  );
}


import React from "react";

export default function InputAlgorithm({ value, onChange }) {
  return (
    <textarea
      className="w-full h-60 p-3 bg-gray-700 border border-gray-600 text-white rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-purple-500"
      placeholder="Escribe tu pseudocódigo aquí..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}




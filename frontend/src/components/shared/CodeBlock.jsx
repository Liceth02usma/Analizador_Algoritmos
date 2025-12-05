import React, { useState } from "react";

export default function CodeBlock({ code, language = "pseudocode" }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative">
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 bg-purple-700 hover:bg-purple-600 text-white px-3 py-1 rounded text-sm transition"
      >
        {copied ? "✓ Copiado" : "Copiar"}
      </button>
      <pre className="bg-gray-800 p-4 rounded-lg overflow-x-auto text-green-400 text-sm border border-gray-700">
        <code>{code}</code>
      </pre>
    </div>
  );
}

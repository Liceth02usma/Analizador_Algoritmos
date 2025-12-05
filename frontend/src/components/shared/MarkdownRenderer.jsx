import React from "react";
import ReactMarkdown from "react-markdown";

export default function MarkdownRenderer({ content }) {
  return (
    <div className="prose prose-invert max-w-none">
      <ReactMarkdown
        components={{
          // Estilos personalizados para el markdown
          p: ({ children }) => <p className="text-gray-300 mb-2">{children}</p>,
          strong: ({ children }) => <strong className="text-purple-400 font-bold">{children}</strong>,
          code: ({ children }) => (
            <code className="bg-gray-800 px-2 py-1 rounded text-green-400 text-sm">{children}</code>
          ),
          pre: ({ children }) => (
            <pre className="bg-gray-800 p-3 rounded-lg overflow-x-auto mb-3">{children}</pre>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

import React, { useEffect, useRef } from "react";
import mermaid from "mermaid";

export default function TreeVisualizer({ mermaidCode }) {
  const mermaidRef = useRef(null);

  useEffect(() => {
    // Inicializar Mermaid una sola vez
    mermaid.initialize({
      startOnLoad: false,
      theme: "dark",
      themeVariables: {
        darkMode: true,
        background: "#1f2937",
        primaryColor: "#a855f7",
        primaryTextColor: "#fff",
        primaryBorderColor: "#8b5cf6",
        lineColor: "#8b5cf6",
        secondaryColor: "#4ade80",
        tertiaryColor: "#f59e0b",
        fontSize: "14px",
        fontFamily: "ui-monospace, monospace",
      },
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: "basis",
      },
    });
  }, []);

  useEffect(() => {
    let mounted = true;
    
    const renderDiagram = async () => {
      if (!mermaidCode || !mermaidRef.current) return;
      
      try {
        // Limpiar el contenedor
        mermaidRef.current.innerHTML = "";
        
        // Generar un ID único para este diagrama
        const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Renderizar el diagrama usando mermaid.render()
        const { svg } = await mermaid.render(id, mermaidCode);
        
        // Insertar el SVG en el contenedor solo si el componente sigue montado
        if (mounted && mermaidRef.current) {
          mermaidRef.current.innerHTML = svg;
        }
      } catch (error) {
        console.error("Error rendering Mermaid diagram:", error);
        if (mounted && mermaidRef.current) {
          mermaidRef.current.innerHTML = `<p class="text-red-400">Error al renderizar el diagrama: ${error.message}</p>`;
        }
      }
    };

    renderDiagram();
    
    return () => {
      mounted = false;
    };
  }, [mermaidCode]);

  if (!mermaidCode) {
    return (
      <div className="bg-gray-800 rounded-xl p-6">
        <p className="text-gray-400 text-center">No hay árboles de recursión disponibles</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 space-y-6">
      <h3 className="text-2xl font-bold text-purple-400 flex items-center gap-2">
        🌳 Árboles de Recursión
      </h3>

      <div className="bg-gray-900 rounded-lg p-6 overflow-x-auto">
        <div 
          ref={mermaidRef}
          className="flex justify-center items-center min-h-[400px]"
        />
      </div>

      <div className="bg-purple-900/20 border border-purple-700 p-4 rounded-lg">
        <p className="text-sm text-purple-300">
          <span className="font-semibold">💡 Tip:</span> El diagrama muestra la estructura de recursión con diferentes colores para cada caso (Mejor, Peor y Promedio).
        </p>
      </div>
    </div>
  );
}

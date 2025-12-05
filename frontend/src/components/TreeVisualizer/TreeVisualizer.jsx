import React, { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

/**
 * Sanitiza el código Mermaid para evitar errores de parsing
 */
const sanitizeMermaidCode = (code) => {
  if (!code || typeof code !== "string") return "";

  let sanitized = code;

  // 1. Eliminar comentarios Note que causan problemas
  sanitized = sanitized.replace(/^\s*Note\s+.+$/gm, '');

  // 2. PRIMERO: Reemplazar notación de array A[index] por A(index) en TODO el código
  // Esto debe hacerse ANTES de procesar los nodos
  sanitized = sanitized.replace(/(\w+)\[([^\]]+)\]/g, (match, varName, index) => {
    // Solo reemplazar si NO es un nodo de Mermaid (no tiene --> o -- antes)
    // Detectar si es notación de array (variable seguida de corchete con contenido simple)
    if (/^[a-zA-Z_]\w*$/.test(varName) && !/^["']/.test(index)) {
      return `${varName}(${index})`;
    }
    return match;
  });

  // 3. Procesar nodos rectangulares [...]
  // Ya no tienen corchetes de array dentro porque fueron reemplazados
  sanitized = sanitized.replace(/(\w+)\[([^\]]+)\]/g, (match, nodeId, content) => {
    // Si ya está correctamente entrecomillado, dejar como está
    if (content.trim().match(/^["'].*["']$/)) {
      return match;
    }
    
    // Si contiene caracteres problemáticos
    if (/[+\-*/()=<>!?]/.test(content)) {
      return `${nodeId}["${content}"]`;
    }
    
    return match;
  });

  // 4. Procesar nodos de decisión {...}
  sanitized = sanitized.replace(/(\w+)\{([^}]+)\}/g, (match, nodeId, content) => {
    // Si ya está correctamente entrecomillado, dejar como está
    if (content.trim().match(/^["'].*["']$/)) {
      return match;
    }
    
    // Si contiene caracteres problemáticos
    if (/[+\-*/()=<>!?]/.test(content)) {
      return `${nodeId}{"${content}"}`;
    }
    
    return match;
  });

  // 5. Normalizar nodos circulares ((texto)) -> ("texto")
  sanitized = sanitized.replace(/\(\(([^)]+)\)\)/g, '("$1")');

  // 6. Limpiar líneas vacías múltiples
  sanitized = sanitized.replace(/\n\s*\n\s*\n/g, '\n\n');

  return sanitized.trim();
};

export default function TreeVisualizer({ mermaidCode, isRecursive = true }) {
  const mermaidRef = useRef(null);
  const [debugInfo, setDebugInfo] = useState(null);

  useEffect(() => {
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
      securityLevel: "loose",
    });
  }, []);

  useEffect(() => {
    let mounted = true;

    const renderDiagram = async () => {
      if (!mermaidCode || !mermaidRef.current) return;

      try {
        mermaidRef.current.innerHTML = "";
        
        const sanitizedCode = sanitizeMermaidCode(mermaidCode);
        
        // Guardar info de debug
        setDebugInfo({
          original: mermaidCode,
          sanitized: sanitizedCode,
          success: true
        });

        const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const { svg } = await mermaid.render(id, sanitizedCode);

        if (mounted && mermaidRef.current) {
          mermaidRef.current.innerHTML = svg;
        }
      } catch (error) {
        console.error("[TreeVisualizer] Render error:", error);
        
        setDebugInfo({
          original: mermaidCode,
          sanitized: sanitizeMermaidCode(mermaidCode),
          error: error.message,
          success: false
        });

        if (mounted && mermaidRef.current) {
          mermaidRef.current.innerHTML = `
            <div class="bg-red-900/20 border border-red-500/50 rounded p-4">
              <p class="text-red-400 font-semibold mb-2">⚠️ Error al renderizar el diagrama:</p>
              <p class="text-gray-300 text-sm mb-3">${error.message}</p>
              
              <details class="mb-3">
                <summary class="cursor-pointer text-blue-400 text-sm hover:text-blue-300">
                  📋 Ver código original del backend
                </summary>
                <pre class="text-xs text-gray-400 mt-2 p-3 bg-gray-900 rounded overflow-x-auto max-h-60">${mermaidCode}</pre>
              </details>

              <details>
                <summary class="cursor-pointer text-blue-400 text-sm hover:text-blue-300">
                  🔧 Ver código sanitizado
                </summary>
                <pre class="text-xs text-green-400 mt-2 p-3 bg-gray-900 rounded overflow-x-auto max-h-60">${sanitizeMermaidCode(mermaidCode)}</pre>
              </details>

              <div class="mt-4 p-3 bg-blue-900/20 border border-blue-500/50 rounded">
                <p class="text-sm text-blue-300">
                  <strong>💡 Sugerencia:</strong> Copia el código original y pruébalo en 
                  <a href="https://mermaid.live" target="_blank" rel="noopener noreferrer" class="underline hover:text-blue-200">
                    mermaid.live
                  </a> 
                  para verificar si el problema está en el código generado por el backend.
                </p>
              </div>
            </div>
          `;
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
        <p className="text-gray-400 text-center">
          {isRecursive ? 'No hay árboles de recursión disponibles' : 'No hay diagrama de traza disponible'}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-bold text-purple-400 flex items-center gap-2">
          {isRecursive ? '🌳 Árboles de Recursión' : '📊 Diagrama de Traza'}
        </h3>

        {/* Botón de debug (solo en desarrollo) */}
        {import.meta.env.DEV && debugInfo && (
          <button
            onClick={() => console.log('Mermaid Debug Info:', debugInfo)}
            className="text-xs px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded transition"
            title="Ver info de debug en consola"
          >
            🐛 Debug
          </button>
        )}
      </div>

      <div className="bg-gray-900 rounded-lg p-6 overflow-x-auto">
        <div
          ref={mermaidRef}
          className="flex justify-center items-center min-h-[400px]"
        />
      </div>

      <div className="bg-purple-900/20 border border-purple-700 p-4 rounded-lg">
        <p className="text-sm text-purple-300">
          <span className="font-semibold">💡 Tip:</span> {isRecursive
            ? 'El diagrama muestra la estructura de recursión con diferentes colores para cada caso (Mejor, Peor y Promedio).'
            : 'El diagrama muestra el flujo de ejecución paso a paso del algoritmo iterativo.'}
        </p>
      </div>
    </div>
  );
}

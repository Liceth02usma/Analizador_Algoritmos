const API_URL = import.meta.env.API_URL || "http://localhost:8000";

/**
 * Analiza un algoritmo iterativo enviando el pseudocódigo al backend.
 * @param {string} algorithmName - El nombre del algoritmo
 * @param {string} pseudocode - El pseudocódigo a analizar
 * @returns {Promise<Object>} - Objeto con el análisis completo o error
 */
export const analyzeIterative = async (algorithmName, pseudocode) => {
  try {
    const response = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        pseudocode 
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { success: true, analysis: data, data };
  } catch (error) {
    console.error("Error al analizar algoritmo iterativo:", error);
    return { success: false, error: error.message };
  }
};
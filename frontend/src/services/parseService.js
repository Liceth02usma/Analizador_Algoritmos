const API_URL = import.meta.env.API_URL || "http://localhost:8000";

/**
 * Analiza pseudocódigo enviándolo al backend para parseo.
 * @param {string} pseudocode - El pseudocódigo a analizar
 * @returns {Promise<Object>} - Objeto con el AST parseado o error
 */
export const parsePseudocode = async (pseudocode) => {
  try {
    const response = await fetch(`${API_URL}/parse`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pseudocode }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { success: true, ast: data.ast, data };
  } catch (error) {
    console.error("Error al analizar:", error);
    return { success: false, error: error.message };
  }
};

const API_URL = import.meta.env.API_URL || "http://localhost:8000";

/**
 * Traduce lenguaje natural a pseudocódigo.
 * @param {string} text - El texto en lenguaje natural a traducir
 * @returns {Promise<Object>} - Objeto con el pseudocódigo traducido o error
 */
export const translateToPseudocode = async (text) => {
  try {
    const response = await fetch(`${API_URL}/translate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.success) {
      return { success: true, pseudocode: data.pseudocode };
    } else {
      return { success: false, error: data.error || "Error en la traducción" };
    }
  } catch (error) {
    console.error("Error al traducir:", error);
    return { success: false, error: error.message };
  }
};

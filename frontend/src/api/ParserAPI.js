// src/api/ParserAPI.js
const API_URL = "http://localhost:8000";

export async function parsePseudocode(pseudocode) {
  const response = await fetch(`${API_URL}/parse`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ pseudocode }),
  });

  if (!response.ok) {
    throw new Error("Error al parsear el pseudocódigo");
  }

  return await response.json(); // Devuelve el AST en JSON
}

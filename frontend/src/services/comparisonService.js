import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Servicio para comparación de análisis: Especializados vs Completo
 */
const comparisonService = {
  /**
   * Compara el análisis especializado con el agente completo
   * @param {string} algorithmName - Nombre del algoritmo
   * @param {string} pseudocode - Pseudocódigo del algoritmo
   * @returns {Promise<object>} Datos de comparación con gráficas
   */
  async compareAnalysis(algorithmName, pseudocode) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/compare`,
        {
          algorithm_name: algorithmName,
          pseudocode: pseudocode
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error al comparar análisis:', error);
      
      if (error.response?.status === 404) {
        throw new Error('No se encontró análisis especializado previo. Ejecute el análisis primero.');
      }
      
      throw error;
    }
  }
};

export default comparisonService;

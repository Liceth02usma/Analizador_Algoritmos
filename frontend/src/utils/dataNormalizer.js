/**
 * Normaliza los datos de análisis tanto de formato iterativo como recursivo
 * a una estructura común que los componentes puedan usar
 */

/**
 * Detecta el tipo de análisis basado en la estructura del JSON
 * @param {Object} data - Datos del backend
 * @returns {string} - 'iterative' | 'recursive' | 'unknown'
 */
export function detectAnalysisType(data) {
  if (!data) return 'unknown';
  
  // Si tiene la estructura de iterativo con extra.cases
  if (data?.extra?.cases && Array.isArray(data.extra.cases) && data.extra.cases.length > 0) {
    return 'iterative';
  }
  
  // Si tiene explain_solution_steps como array de objetos con case_type
  if (data?.explain_solution_steps && Array.isArray(data.explain_solution_steps) && 
      data.explain_solution_steps.length > 0 && data.explain_solution_steps[0]?.case_type) {
    return 'recursive';
  }
  
  // Si tiene el tipo explícitamente definido como "iterativo"
  if (data?.type === 'iterativo' && data?.extra?.cases) {
    return 'iterative';
  }
  
  // Si tiene el tipo explícitamente definido como "Recursivo"
  if ((data?.type === 'Recursivo' || data?.type === 'recursivo') && data?.explain_solution_steps) {
    return 'recursive';
  }
  
  return 'unknown';
}

/**
 * Normaliza datos de formato iterativo
 */
function normalizeIterativeData(data) {
  const { extra, ...rest } = data;
  
  // Los casos iterativos están en extra.cases
  const cases = extra?.cases || [];
  
  // Convertir casos iterativos al formato común
  const normalizedSteps = cases.map(caseData => ({
    case_type: caseData.case_name?.toLowerCase().includes('mejor') ? 'best_case' :
               caseData.case_name?.toLowerCase().includes('peor') ? 'worst_case' :
               caseData.case_name?.toLowerCase().includes('promedio') ? 'average_case' : 'single',
    case_name: caseData.case_name,
    condition: caseData.condition,
    equation: caseData.raw_summation_str || '',
    original_equation: caseData.raw_summation_str || '',
    method: 'Método de Conteo de Pasos + Sumatorias',
    method_enum: 'iterative_analysis',
    complexity: caseData.simplified_complexity || caseData.big_o || '',
    steps: caseData.math_steps ? [caseData.math_steps] : [],
    explanation: buildIterativeExplanation(caseData),
    big_o: caseData.big_o,
    complexity_class: caseData.complexity_class,
    notation_type: caseData.notation_type,
    line_analysis: parseLineAnalysis(caseData.line_analysis),
    trace_diagram: caseData.trace_diagram,
    raw_summation_str: caseData.raw_summation_str,
    math_steps: caseData.math_steps,
    simplified_complexity: caseData.simplified_complexity,
    classification_confidence: 1.0,
    classification_reasoning: `Análisis iterativo utilizando conteo de pasos. ${caseData.condition}`,
    details: {
      raw_summation: caseData.raw_summation_str,
      simplified: caseData.simplified_complexity,
      math_steps: caseData.math_steps,
      complexity_class: caseData.complexity_class,
      notation_type: caseData.notation_type,
    }
  }));

  return {
    ...rest,
    type: 'iterativo',
    explain_solution_steps: normalizedSteps,
    hasMultipleCases: normalizedSteps.length > 1,
    extra: {
      ...extra,
      has_multiple_cases: normalizedSteps.length > 1,
    }
  };
}

/**
 * Construye una explicación detallada para casos iterativos
 */
function buildIterativeExplanation(caseData) {
  let explanation = `Este caso representa: ${caseData.condition}\n\n`;
  
  explanation += `La complejidad resultante es de clase ${caseData.complexity_class || 'N/A'}, `;
  explanation += `con notación asintótica ${caseData.big_o}.\n\n`;
  
  if (caseData.math_steps) {
    explanation += `Pasos matemáticos:\n${caseData.math_steps}\n\n`;
  }
  
  explanation += `Función de complejidad simplificada:\nT(n) = ${caseData.simplified_complexity || 'N/A'}`;
  
  return explanation;
}

/**
 * Parsea line_analysis desde string o array
 */
function parseLineAnalysis(lineAnalysis) {
  if (!lineAnalysis) return [];
  
  // Si es un string, intentar parsearlo (por si viene como JSON o texto)
  if (typeof lineAnalysis === 'string') {
    // Si contiene "Error al analizar" o similar, retornar array vacío
    if (lineAnalysis.includes('Error') || lineAnalysis.includes('===')) {
      return [];
    }
    try {
      return JSON.parse(lineAnalysis);
    } catch {
      return [];
    }
  }
  
  // Si ya es un array, retornarlo directamente
  if (Array.isArray(lineAnalysis)) {
    return lineAnalysis;
  }
  
  return [];
}

/**
 * Normaliza datos de formato recursivo
 */
function normalizeRecursiveData(data) {
  // Los datos recursivos ya están en el formato correcto en explain_solution_steps
  return {
    ...data,
    type: 'recursivo',
    hasMultipleCases: data.explain_solution_steps?.length > 1,
    extra: {
      ...data.extra,
      has_multiple_cases: data.explain_solution_steps?.length > 1,
    }
  };
}

/**
 * Función principal que normaliza cualquier tipo de datos
 * @param {Object} data - Datos del backend
 * @returns {Object} - Datos normalizados
 */
export function normalizeAnalysisData(data) {
  if (!data) return null;

  const type = detectAnalysisType(data);

  switch (type) {
    case 'iterative':
      return normalizeIterativeData(data);
    case 'recursive':
      return normalizeRecursiveData(data);
    default:
      // Si no se detecta el tipo pero tiene error, retornar tal cual para manejo de errores
      if (data.error) return data;
      console.warn('[Normalizer] Unknown analysis type, returning data as-is');
      return data;
  }
}

/**
 * Obtiene los diagramas según el tipo de análisis
 */
export function getDiagrams(data, normalizedData) {
  const type = detectAnalysisType(data);
  
  if (type === 'iterative') {
    // Para iterativo, los diagramas están en cada caso
    const diagrams = {};
    normalizedData.explain_solution_steps?.forEach(step => {
      if (step.trace_diagram) {
        diagrams[`tree_method_${step.case_type}`] = step.trace_diagram;
      }
    });
    return diagrams;
  }
  
  if (type === 'recursive') {
    // Para recursivo, los diagramas ya están en data.diagrams
    return data.diagrams || {};
  }
  
  return {};
}

/**
 * Obtiene el código con anotaciones de línea
 */
export function getAnnotatedCode(data, normalizedData) {
  const type = detectAnalysisType(data);
  
  if (type === 'iterative') {
    // Para iterativo, construir una vista de casos
    return normalizedData.complexity_line_to_line || data.complexity_line_to_line || '';
  }
  
  if (type === 'recursive') {
    return data.complexity_line_to_line || '';
  }
  
  return '';
}

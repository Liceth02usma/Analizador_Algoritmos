"""
Agente de análisis de complejidad línea por línea.

Este agente analiza pseudocódigo y proporciona:
- Complejidad temporal por cada línea de código
- Explicación general del algoritmo
- Análisis detallado de la complejidad total
- Soporte para múltiples casos (mejor, peor, promedio)
"""

from typing import List, Optional, Dict, Any
import json
import re
from pydantic import BaseModel, Field
from ...external_services.Agentes.Agent import AgentBase


# ============================================================================
# SCHEMAS DE RESPUESTA
# ============================================================================


class ComplexityAnalysis(BaseModel):
    """Análisis de complejidad para un solo caso."""

    case_type: Optional[str] = Field(
        default=None,
        description="Tipo de caso: 'best', 'worst', 'average' o None para caso único",
    )
    pseudocode_annotated: str = Field(
        ..., description="Pseudocódigo con anotaciones de complejidad por línea"
    )
    code_explanation: str = Field(
        ..., description="Explicación breve de qué hace el algoritmo"
    )
    complexity_explanation: str = Field(
        ..., description="Explicación de la complejidad temporal total"
    )
    total_complexity: str = Field(
        ..., description="Complejidad total (ej: 'O(log n)', 'O(n²)')"
    )


class SingleCaseOutput(BaseModel):
    """Salida para algoritmos con un solo caso."""

    has_multiple_cases: bool = Field(
        default=False, description="Siempre False para caso único"
    )
    analysis: ComplexityAnalysis = Field(..., description="Análisis del caso único")


class MultipleCasesOutput(BaseModel):
    """Salida para algoritmos con múltiples casos."""

    has_multiple_cases: bool = Field(
        default=True, description="Siempre True para múltiples casos"
    )
    best_case: ComplexityAnalysis = Field(..., description="Análisis del mejor caso")
    worst_case: ComplexityAnalysis = Field(..., description="Análisis del peor caso")
    average_case: ComplexityAnalysis = Field(
        ..., description="Análisis del caso promedio"
    )


# ============================================================================
# AGENTE DE COMPLEJIDAD LÍNEA POR LÍNEA
# ============================================================================


class ComplexityLineByLineAgent(AgentBase):
    """
    Agente especializado en análisis de complejidad línea por línea.

    Analiza pseudocódigo y proporciona anotaciones de complejidad
    temporal para cada línea, junto con explicaciones detalladas.
    """

    def __init__(self, model_type: str = "Modelo_Codigo", enable_verbose: bool = False):
        """
        Inicializa el agente de complejidad línea por línea.

        Args:
            model_type: Tipo de modelo LLM a usar (por defecto "Modelo_Codigo")
            enable_verbose: Habilitar logs detallados
        """
        self.enable_verbose = enable_verbose
        # No llamamos super().__init__ todavía, lo haremos según el caso
        self.model_type = model_type
        self._agent_single = None
        self._agent_multiple = None

    def _get_or_create_agent(self, for_multiple_cases: bool):
        """Obtiene o crea el agente apropiado según el tipo de análisis."""
        if for_multiple_cases:
            if self._agent_multiple is None:
                # Crear agente para múltiples casos
                self.response_format = MultipleCasesOutput
                super().__init__(self.model_type)
                self._agent_multiple = self.agent
            return self._agent_multiple
        else:
            if self._agent_single is None:
                # Crear agente para caso único
                self.response_format = SingleCaseOutput
                super().__init__(self.model_type)
                self._agent_single = self.agent
            return self._agent_single

    def _extract_json_from_markdown(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extrae JSON de una respuesta que puede estar envuelta en bloques markdown.

        Args:
            text: Texto que puede contener ```json...``` o JSON directo

        Returns:
            Dict con el JSON parseado o None si falla
        """
        if not text:
            return None

        # Intentar parsear directamente como JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Buscar bloques de código JSON (```json ... ```)
        json_pattern = r"```(?:json)?\s*\n(.*?)\n```"
        matches = re.findall(json_pattern, text, re.DOTALL)

        if matches:
            # Intentar parsear cada bloque encontrado
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue

        # Buscar cualquier estructura que parezca JSON (con { ... })
        json_like_pattern = r"\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}"
        matches = re.findall(json_like_pattern, text, re.DOTALL)

        if matches:
            # Intentar parsear el JSON más grande encontrado
            matches_sorted = sorted(matches, key=len, reverse=True)
            for match in matches_sorted:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        return None

    def _configure(self) -> None:
        """Configura el agente según la clase base."""
        self.tools = []
        self.context_schema = None
        # response_format se establecerá dinámicamente antes de cada invocación

        self.SYSTEM_PROMPT = """Eres un experto en análisis de complejidad de algoritmos.

**TU TAREA:** Analizar pseudocódigo y anotar la complejidad temporal de cada línea.

**MUY IMPORTANTE:** Debes responder EXCLUSIVAMENTE con el formato JSON estructurado solicitado. NO respondas con texto libre, markdown ni explicaciones adicionales fuera del JSON.

**REGLAS DE ANOTACIÓN:**
1. **Operaciones básicas:** O(1)
   - Asignaciones: `x = 5` → O(1)
   - Comparaciones: `if (x > y)` → O(1)
   - Operaciones aritméticas: `a + b`, `x * y` → O(1)
   - Acceso a array: `arr[i]` → O(1)
   - Retornos: `return x` → O(1)

2. **Llamadas recursivas:** T(tamaño_subproblema)
   - División: `func(n/2)` → T(n/2)
   - Resta: `func(n-1)` → T(n-1)
   - Múltiples llamadas: suma de todas

3. **Ciclos:**
   - `for i = 1 to n` → O(n) para el ciclo completo
   - Línea del for: O(1) por iteración
   - Cuerpo del ciclo: suma de operaciones * n

4. **Formato de anotación en pseudocode_annotated:**
   ```
   linea_de_codigo    // O(complejidad) - Descripción breve
   ```

**EJEMPLO DE FORMATO DE RESPUESTA PARA CASO ÚNICO (SingleCaseOutput):**
```json
{
  "has_multiple_cases": false,
  "analysis": {
    "case_type": null,
    "pseudocode_annotated": "busqueda(arr, x, i)\\nbegin\\n    if (i >= length(arr)) then    // O(1) - Comparación\\n        return -1    // O(1) - Retorno\\n    if (arr[i] = x) then    // O(1) - Comparación\\n        return i    // O(1) - Retorno\\n    return busqueda(arr, x, i+1)    // T(n-1) - Llamada recursiva\\nend",
    "code_explanation": "Búsqueda lineal recursiva que recorre el arreglo elemento por elemento hasta encontrar el valor x o llegar al final.",
    "complexity_explanation": "En cada llamada se realiza trabajo constante O(1) y se reduce el problema en 1. El árbol de recursión tiene profundidad n, por lo tanto T(n) = T(n-1) + O(1) = O(n).",
    "total_complexity": "O(n)"
  }
}
```

**EJEMPLO DE FORMATO DE RESPUESTA PARA MÚLTIPLES CASOS (MultipleCasesOutput):**
```json
{
  "has_multiple_cases": true,
  "best_case": {
    "case_type": "best",
    "pseudocode_annotated": "busqueda(arr, x, i)\\nbegin\\n    if (i >= length(arr)) then    // O(1) - Comparación\\n        return -1    // O(1) - Retorno\\n    if (arr[i] = x) then    // O(1) - Comparación (elemento encontrado)\\n        return i    // O(1) - Retorno inmediato\\n    return busqueda(arr, x, i+1)    // No ejecutado\\nend",
    "code_explanation": "Búsqueda lineal recursiva. Mejor caso: elemento en primera posición.",
    "complexity_explanation": "El elemento está en la primera posición (i=0), por lo que se encuentra inmediatamente sin llamadas recursivas.",
    "total_complexity": "O(1)"
  },
  "worst_case": {
    "case_type": "worst",
    "pseudocode_annotated": "busqueda(arr, x, i)\\nbegin\\n    if (i >= length(arr)) then    // O(1) - Comparación (ejecutado en última llamada)\\n        return -1    // O(1) - Retorno\\n    if (arr[i] = x) then    // O(1) - Comparación (siempre falso)\\n        return i    // No ejecutado\\n    return busqueda(arr, x, i+1)    // T(n-1) - Llamada recursiva (n veces)\\nend",
    "code_explanation": "Búsqueda lineal recursiva. Peor caso: elemento no existe o está al final.",
    "complexity_explanation": "Se deben revisar todos los n elementos antes de determinar que x no existe. T(n) = T(n-1) + O(1) con n llamadas.",
    "total_complexity": "O(n)"
  },
  "average_case": {
    "case_type": "average",
    "pseudocode_annotated": "busqueda(arr, x, i)\\nbegin\\n    if (i >= length(arr)) then    // O(1) - Comparación\\n        return -1    // O(1) - Retorno\\n    if (arr[i] = x) then    // O(1) - Comparación (éxito en posición promedio n/2)\\n        return i    // O(1) - Retorno\\n    return busqueda(arr, x, i+1)    // T(n-1) - Llamada recursiva (~n/2 veces)\\nend",
    "code_explanation": "Búsqueda lineal recursiva. Caso promedio: elemento en posición media.",
    "complexity_explanation": "En promedio, el elemento se encuentra aproximadamente a mitad del arreglo (n/2 posiciones). La complejidad promedio sigue siendo O(n).",
    "total_complexity": "O(n)"
  }
}
```

**ANÁLISIS POR CASOS:**
- **Mejor caso:** Escenario más favorable (ej: elemento en primera posición)
- **Peor caso:** Escenario más desfavorable (ej: elemento no existe o al final)
- **Caso promedio:** Escenario típico esperado (ej: elemento en posición media)

**INSTRUCCIONES CRÍTICAS:**
1. DEBES responder SOLO con el objeto JSON solicitado (SingleCaseOutput o MultipleCasesOutput)
2. NO incluyas explicaciones adicionales fuera del JSON
3. NO uses formato markdown (```json o ```plaintext) - solo el JSON puro
4. Asegúrate de que el JSON sea válido y tenga todos los campos requeridos
5. En pseudocode_annotated, usa \\n para saltos de línea"""

    def analyze_single_case(
        self, pseudocode: str, algorithm_name: str = "Algoritmo"
    ) -> SingleCaseOutput:
        """
        Analiza pseudocódigo para un caso único.

        Args:
            pseudocode: Código a analizar
            algorithm_name: Nombre del algoritmo

        Returns:
            SingleCaseOutput con análisis completo
        """
        # Configurar para caso único
        agent = self._get_or_create_agent(for_multiple_cases=False)
        self.response_format = SingleCaseOutput

        if self.enable_verbose:
            print(f"\n{'='*70}")
            print(f"[ComplexityLineAgent] 📊 Analizando caso único")
            print(f"{'='*70}")
            print(f"Algoritmo: {algorithm_name}")

        content = f"""Analiza la complejidad línea por línea del siguiente pseudocódigo.

**Algoritmo:** {algorithm_name}

**Pseudocódigo:**
```
{pseudocode}
```

**INSTRUCCIONES CRÍTICAS:**
1. Anota CADA línea con su complejidad temporal
2. Explica brevemente qué hace el algoritmo
3. Calcula y explica la complejidad total
4. Formato en pseudocode_annotated: `linea_codigo    // O(complejidad) - Descripción`
5. **RESPONDE SOLO CON JSON ESTRUCTURADO - NO uses markdown ni texto libre**

**FORMATO REQUERIDO:** Objeto JSON SingleCaseOutput con estos campos:
- has_multiple_cases: false
- analysis.case_type: null
- analysis.pseudocode_annotated: string (código anotado con \\n para saltos)
- analysis.code_explanation: string (qué hace el algoritmo)
- analysis.complexity_explanation: string (explicación de la complejidad)
- analysis.total_complexity: string (ej: "O(n)", "O(log n)")"""

        try:
            thread_id = f"complexity_single_{abs(hash(pseudocode))}"
            result = self.invoke_simple(content=content, thread_id=thread_id)
            output = self.extract_response(result)

            if output is None:
                if self.enable_verbose:
                    print(
                        f"⚠️  No se pudo extraer respuesta estructurada, intentando parsear JSON de markdown..."
                    )
                    print(f"Result keys: {result.keys()}")

                # Intentar extraer JSON de la respuesta de texto
                if "messages" in result and len(result["messages"]) > 0:
                    last_message = result["messages"][-1]
                    if hasattr(last_message, "content"):
                        content_text = last_message.content

                        if self.enable_verbose:
                            print(
                                f"Contenido del mensaje (primeros 300 chars): {content_text[:300]}"
                            )

                        # Intentar extraer JSON del markdown
                        json_data = self._extract_json_from_markdown(content_text)

                        if json_data:
                            if self.enable_verbose:
                                print("✓ JSON extraído exitosamente del markdown")

                            # Validar y convertir a SingleCaseOutput
                            try:
                                output = SingleCaseOutput(**json_data)
                                if self.enable_verbose:
                                    print("✓ JSON validado como SingleCaseOutput")
                            except Exception as e:
                                if self.enable_verbose:
                                    print(f"✗ Error validando JSON: {e}")
                                raise ValueError(
                                    f"JSON extraído no es válido: {str(e)}"
                                )
                        else:
                            raise ValueError(f"No se pudo extraer JSON del contenido")

                if output is None:
                    raise ValueError("El agente no retornó una respuesta válida")

            if self.enable_verbose:
                print(f"\n✅ Análisis completado")
                print(f"   Complejidad total: {output.analysis.total_complexity}")

            return output

        except Exception as e:
            if self.enable_verbose:
                print(f"\n❌ ERROR: {str(e)}")

            # Fallback
            return SingleCaseOutput(
                has_multiple_cases=False,
                analysis=ComplexityAnalysis(
                    case_type=None,
                    pseudocode_annotated=pseudocode,
                    code_explanation=f"Algoritmo: {algorithm_name}",
                    complexity_explanation=f"Error en el análisis: {str(e)}",
                    total_complexity="O(?)",
                ),
            )

    def analyze_multiple_cases(
        self, pseudocode: str, algorithm_name: str = "Algoritmo"
    ) -> MultipleCasesOutput:
        """
        Analiza pseudocódigo para múltiples casos (mejor, peor, promedio).

        Args:
            pseudocode: Código a analizar
            algorithm_name: Nombre del algoritmo

        Returns:
            MultipleCasesOutput con análisis de los 3 casos
        """
        # Configurar para múltiples casos
        agent = self._get_or_create_agent(for_multiple_cases=True)
        self.response_format = MultipleCasesOutput

        if self.enable_verbose:
            print(f"\n{'='*70}")
            print(f"[ComplexityLineAgent] 📊 Analizando múltiples casos")
            print(f"{'='*70}")
            print(f"Algoritmo: {algorithm_name}")

        content = f"""Analiza la complejidad línea por línea del siguiente pseudocódigo para TRES casos.

**Algoritmo:** {algorithm_name}

**Pseudocódigo:**
```
{pseudocode}
```

**INSTRUCCIONES CRÍTICAS:**
Genera 3 análisis completos:

1. **MEJOR CASO (best_case):**
   - case_type: "best"
   - Escenario más favorable (ej: elemento en primera posición)
   - Pseudocódigo anotado con complejidades optimistas
   - Explicación del mejor escenario
   - Complejidad total del mejor caso

2. **PEOR CASO (worst_case):**
   - case_type: "worst"
   - Escenario más desfavorable (ej: elemento no existe)
   - Pseudocódigo anotado con complejidades pesimistas
   - Explicación del peor escenario
   - Complejidad total del peor caso

3. **CASO PROMEDIO (average_case):**
   - case_type: "average"
   - Escenario típico esperado (ej: elemento a mitad)
   - Pseudocódigo anotado con complejidades esperadas
   - Explicación del caso típico
   - Complejidad total promedio

**FORMATO en pseudocode_annotated:** `linea_codigo    // O(complejidad) - Descripción`

**MUY IMPORTANTE:** 
- RESPONDE SOLO CON JSON ESTRUCTURADO MultipleCasesOutput
- NO uses markdown (```json), NO uses texto libre
- has_multiple_cases: true
- Cada caso (best_case, worst_case, average_case) tiene: case_type, pseudocode_annotated, code_explanation, complexity_explanation, total_complexity
- Usa \\n para saltos de línea en pseudocode_annotated"""

        try:
            thread_id = f"complexity_multiple_{abs(hash(pseudocode))}"
            result = self.invoke_simple(content=content, thread_id=thread_id)
            output = self.extract_response(result)

            if output is None:
                if self.enable_verbose:
                    print(
                        f"⚠️  No se pudo extraer respuesta estructurada, intentando parsear JSON de markdown..."
                    )
                    print(f"Result keys: {result.keys()}")

                # Intentar extraer JSON de la respuesta de texto
                if "messages" in result and len(result["messages"]) > 0:
                    last_message = result["messages"][-1]
                    if hasattr(last_message, "content"):
                        content_text = last_message.content

                        if self.enable_verbose:
                            print(
                                f"Contenido del mensaje (primeros 300 chars): {content_text[:300]}"
                            )

                        # Intentar extraer JSON del markdown
                        json_data = self._extract_json_from_markdown(content_text)

                        if json_data:
                            if self.enable_verbose:
                                print("✓ JSON extraído exitosamente del markdown")

                            # Validar y convertir a MultipleCasesOutput
                            try:
                                output = MultipleCasesOutput(**json_data)
                                if self.enable_verbose:
                                    print("✓ JSON validado como MultipleCasesOutput")
                            except Exception as e:
                                if self.enable_verbose:
                                    print(f"✗ Error validando JSON: {e}")
                                raise ValueError(
                                    f"JSON extraído no es válido: {str(e)}"
                                )
                        else:
                            raise ValueError(f"No se pudo extraer JSON del contenido")

                if output is None:
                    raise ValueError("El agente no retornó una respuesta válida")

            if self.enable_verbose:
                print(f"\n✅ Análisis completado")
                print(f"   Mejor caso: {output.best_case.total_complexity}")
                print(f"   Peor caso: {output.worst_case.total_complexity}")
                print(f"   Caso promedio: {output.average_case.total_complexity}")

            return output

        except Exception as e:
            if self.enable_verbose:
                print(f"\n❌ ERROR: {str(e)}")

            # Fallback con análisis básico
            default_analysis = ComplexityAnalysis(
                case_type="error",
                pseudocode_annotated=pseudocode,
                code_explanation=f"Algoritmo: {algorithm_name}",
                complexity_explanation=f"Error en el análisis: {str(e)}",
                total_complexity="O(?)",
            )

            return MultipleCasesOutput(
                has_multiple_cases=True,
                best_case=default_analysis.model_copy(update={"case_type": "best"}),
                worst_case=default_analysis.model_copy(update={"case_type": "worst"}),
                average_case=default_analysis.model_copy(
                    update={"case_type": "average"}
                ),
            )


# ============================================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================================


def analyze_complexity_by_line(
    pseudocode: str,
    algorithm_name: str = "Algoritmo",
    multiple_cases: bool = False,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Función de conveniencia para analizar complejidad línea por línea.

    Args:
        pseudocode: Código a analizar
        algorithm_name: Nombre del algoritmo
        multiple_cases: True para analizar mejor/peor/promedio caso
        verbose: Mostrar logs

    Returns:
        Diccionario con el análisis completo

    Ejemplos:
        # Caso único
        >>> result = analyze_complexity_by_line(code, "BubbleSort")
        >>> print(result["analysis"]["total_complexity"])
        "O(n²)"

        # Múltiples casos
        >>> result = analyze_complexity_by_line(code, "QuickSort", multiple_cases=True)
        >>> print(result["best_case"]["total_complexity"])
        "O(n log n)"
    """
    agent = ComplexityLineByLineAgent(enable_verbose=verbose)

    if multiple_cases:
        output = agent.analyze_multiple_cases(pseudocode, algorithm_name)
        return output.model_dump()
    else:
        output = agent.analyze_single_case(pseudocode, algorithm_name)
        return output.model_dump()

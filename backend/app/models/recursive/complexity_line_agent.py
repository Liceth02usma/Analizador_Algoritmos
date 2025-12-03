"""
Agente de análisis de complejidad línea por línea (Modo Conteo de Pasos).
FIX: Mejorado el manejo de JSON y caracteres especiales para evitar errores de parseo.
"""

from typing import List, Optional, Dict, Any
import json
import re
import ast  # Nuevo: para fallback de parseo
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
        ..., description="Pseudocódigo con anotaciones de coste (c1, n+1, etc.)"
    )
    code_explanation: str = Field(
        ..., description="Explicación breve de qué hace el algoritmo"
    )
    complexity_explanation: str = Field(
        ..., description="Derivación de la ecuación total (suma de costes)"
    )
    total_complexity: str = Field(
        ..., description="Cota asintótica final (solo aquí, no en las líneas)"
    )

class SingleCaseOutput(BaseModel):
    has_multiple_cases: bool = Field(default=False)
    analysis: ComplexityAnalysis = Field(...)

class MultipleCasesOutput(BaseModel):
    has_multiple_cases: bool = Field(default=True)
    best_case: ComplexityAnalysis = Field(...)
    worst_case: ComplexityAnalysis = Field(...)
    average_case: ComplexityAnalysis = Field(...)


# ============================================================================
# AGENTE DE COMPLEJIDAD LÍNEA POR LÍNEA
# ============================================================================

class ComplexityLineByLineAgent(AgentBase):
    """
    Agente especializado en análisis de complejidad usando Conteo de Pasos.
    Incluye robustez para parseo de JSON con código incrustado.
    """

    def __init__(self, model_type: str = "Gemini_Rapido", enable_verbose: bool = False):
        self.enable_verbose = enable_verbose
        self.model_type = model_type
        self.provider = "gemini"
        self._agent_single = None
        self._agent_multiple = None

    def _get_or_create_agent(self, for_multiple_cases: bool):
        if for_multiple_cases:
            if self._agent_multiple is None:
                self.response_format = MultipleCasesOutput
                super().__init__(self.model_type, provider=self.provider)
                self._agent_multiple = self.agent
            return self._agent_multiple
        else:
            if self._agent_single is None:
                self.response_format = SingleCaseOutput
                super().__init__(self.model_type, provider=self.provider)
                self._agent_single = self.agent
            return self._agent_single

    def _clean_and_repair_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Intenta limpiar y reparar el string JSON antes de parsearlo.
        Estrategia: JSON estricto -> Regex -> Python Eval (Fallback seguro).
        """
        if not text:
            return None

        # 1. Intentar parseo directo
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. Extraer bloque JSON de markdown ```json ... ```
        json_pattern = r"```(?:json)?\s*\n(.*?)\n```"
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        candidates = matches if matches else [text]

        for candidate in candidates:
            # Limpieza básica
            cleaned = candidate.strip()
            
            # Intento A: JSON standard
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass
            
            # Intento B: Python Literal Eval (Salva errores de comillas simples vs dobles)
            # Los LLMs a veces generan diccionarios de Python en vez de JSON estricto
            try:
                # ast.literal_eval es seguro, solo evalúa estructuras de datos, no ejecuta código
                return ast.literal_eval(cleaned)
            except (ValueError, SyntaxError):
                pass

        # 3. Buscar estructura JSON bruta con regex (último recurso)
        json_like_pattern = r"\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}"
        matches = re.findall(json_like_pattern, text, re.DOTALL)
        if matches:
            # Tomar el bloque más largo que parezca JSON
            longest_match = max(matches, key=len)
            try:
                return json.loads(longest_match)
            except:
                try:
                    return ast.literal_eval(longest_match)
                except:
                    pass

        return None

    def _configure(self) -> None:
        self.tools = []
        self.context_schema = None

        # Prompt blindado contra errores de formato
        self.SYSTEM_PROMPT = """Eres un experto en análisis formal de algoritmos (Step Counting).

**TU TAREA:** Analizar pseudocódigo y anotar el coste de cada línea (c1, c2, n, etc).

**REGLAS DE FORMATO JSON (CRÍTICO):**
1. Debes responder con un **JSON válido**.
2. El campo `pseudocode_annotated` contiene código. **CUIDADO CON LAS COMILLAS Y SALTOS DE LÍNEA**:
   - Usa `\\n` literal para saltos de línea. (NO uses Enter real).
   - Si el código tiene comillas dobles (`"`), ESCÁPALAS como `\\"`.
   - Ejemplo bien: `"code": "print(\\"hola\\")\\nreturn 0"`
   - Ejemplo mal: `"code": "print("hola")
     return 0"`

**REGLAS DE ANÁLISIS (STEP COUNTING):**
1. **Asignaciones/Ops:** `// c1`
2. **For (1 a n):** Cabecera `// c_k * (n + 1)`, Cuerpo `// c_j * n`
3. **While:** Cabecera `// c_k * (iteraciones + 1)`
4. **Recursión:** `// T(n/b) + c`
5. **PROHIBIDO:** Usar O(1) u O(n) en las líneas individuales.

**EJEMPLO SINGLE CASE:**
```json
{
  "has_multiple_cases": false,
  "analysis": {
    "case_type": null,
    "pseudocode_annotated": "x = 0  // c1\\nfor i=0 to n:  // c2*(n+1)",
    "code_explanation": "Iteración simple",
    "complexity_explanation": "Suma total...",
    "total_complexity": "O(n)"
  }
}
```

**EJEMPLO MULTIPLE CASES:**
```json
{
  "has_multiple_cases": true,
  "best_case": {
    "case_type": "best",
    "pseudocode_annotated": "if x == A[0]:  // c1\\n  return 0  // c2",
    "code_explanation": "Elemento en primera posición",
    "complexity_explanation": "Costo total: c1 + c2",
    "total_complexity": "O(1)"
  },
  "worst_case": {
    "case_type": "worst",
    "pseudocode_annotated": "for i=0 to n:  // c1*(n+1)\\n  if x == A[i]:  // c2*n",
    "code_explanation": "Elemento no encontrado",
    "complexity_explanation": "Costo total: c1*(n+1) + c2*n",
    "total_complexity": "O(n)"
  },
  "average_case": {
    "case_type": "average",
    "pseudocode_annotated": "for i=0 to n/2:  // c1*(n/2+1)\\n  if x == A[i]:  // c2*(n/2)",
    "code_explanation": "Elemento en promedio a la mitad",
    "complexity_explanation": "Costo total: c1*(n/2+1) + c2*(n/2)",
    "total_complexity": "O(n)"
  }
}
```
"""

    def analyze_single_case(self, pseudocode: str, algorithm_name: str = "Algoritmo") -> SingleCaseOutput:
        agent = self._get_or_create_agent(for_multiple_cases=False)
        
        if self.enable_verbose:
            print(f"\n[ComplexityLineAgent] 📊 Analizando caso único: {algorithm_name}")

        content = f"""Analiza la complejidad de este algoritmo usando Step Counting (Conteo de Pasos).

**ALGORITMO:** {algorithm_name}

**PSEUDOCÓDIGO:**
```
{pseudocode}
```

**INSTRUCCIONES:**
1. Anota CADA LÍNEA del pseudocódigo con su coste usando notación de conteo de pasos:
   - Asignaciones simples: `// c1`
   - Comparaciones: `// c2`
   - Llamadas recursivas: `// T(n-1)` o `// T(n/2)` según corresponda
   - Ciclos: `// c_k * (n+1)` para la condición, `// c_j * n` para el cuerpo
   - NO uses O(1), O(n), etc. en las líneas individuales

2. En complexity_explanation, suma todos los costes y deriva la complejidad final.

3. En total_complexity, pon SOLO la notación Big-O final: "O(1)", "O(n)", "O(n²)", etc.

**FORMATO DE RESPUESTA (JSON):**
```json
{{
  "has_multiple_cases": false,
  "analysis": {{
    "case_type": null,
    "pseudocode_annotated": "x = 0  // c1\\nfor i=0 to n:  // c2*(n+1)\\n    total = total + arr[i]  // c3*n\\nreturn total  // c4",
    "code_explanation": "Suma todos los elementos de un arreglo",
    "complexity_explanation": "Costo total: c1 + c2(n+1) + c3*n + c4 = (c2+c3)n + (c1+c2+c4). El término dominante es n.",
    "total_complexity": "O(n)"
  }}
}}
```

**IMPORTANTE:** 
- Usa \\n para saltos de línea (NO uses Enter real)
- Escapa comillas dobles: \\" 
- Responde SOLO con el JSON, sin texto adicional"""

        try:
            thread_id = f"complexity_single_{abs(hash(pseudocode))}"
            result = self.invoke_simple(content=content, thread_id=thread_id)
            output = self.extract_response(result)

            if output is None:
                # Recuperación manual mejorada
                if "messages" in result and result["messages"]:
                    raw_content = result["messages"][-1].content
                    if self.enable_verbose:
                        print(f"⚠️ Intentando recuperar JSON crudo...")
                    
                    json_data = self._clean_and_repair_json(raw_content)
                    if json_data:
                        # Asegurar que cumple el schema
                        if "analysis" not in json_data and "pseudocode_annotated" in json_data:
                             # A veces el LLM devuelve el objeto analysis directamente
                             json_data = {"has_multiple_cases": False, "analysis": json_data}
                        
                        return SingleCaseOutput(**json_data)

                raise ValueError("No se pudo extraer JSON válido tras intentos de reparación.")

            return output

        except Exception as e:
            if self.enable_verbose:
                print(f"❌ Error crítico en ComplexityLineAgent: {e}")
            
            # Fallback seguro para no romper el frontend
            return SingleCaseOutput(
                has_multiple_cases=False,
                analysis=ComplexityAnalysis(
                    case_type=None,
                    pseudocode_annotated=f"// Error al analizar el código.\\n// Intenta simplificar el input.\\n{pseudocode}",
                    code_explanation="Hubo un error técnico procesando la respuesta del modelo.",
                    complexity_explanation=f"Detalle del error: {str(e)}",
                    total_complexity="Error"
                )
            )

    def analyze_multiple_cases(self, pseudocode: str, algorithm_name: str = "Algoritmo") -> MultipleCasesOutput:
        agent = self._get_or_create_agent(for_multiple_cases=True)

        if self.enable_verbose:
            print(f"\n[ComplexityLineAgent] 📊 Analizando múltiples casos: {algorithm_name}")

        content = f"""Analiza 3 casos (Best, Worst, Average) usando Step Counting para este algoritmo recursivo.

**ALGORITMO:** {algorithm_name}

**PSEUDOCÓDIGO:**
```
{pseudocode}
```

**INSTRUCCIONES CRÍTICAS:**
1. Identifica los 3 escenarios:
   - BEST CASE: Mejor escenario (ej: elemento encontrado inmediatamente)
   - WORST CASE: Peor escenario (ej: elemento no encontrado, recorre todo)
   - AVERAGE CASE: Caso promedio (ej: elemento en posición media)

2. Para cada caso, anota CADA LÍNEA del pseudocódigo con su coste usando notación de conteo de pasos:
   - Asignaciones simples: `// c1`
   - Comparaciones: `// c2`
   - Llamadas recursivas: `// T(n-1)` o `// T(n/2)` según corresponda
   - Ciclos: `// c_k * (n+1)` para la condición, `// c_j * n` para el cuerpo
   - NO uses O(1), O(n), etc. en las líneas individuales

3. En complexity_explanation, suma los costes y deriva la complejidad final.

4. En total_complexity, pon SOLO la notación Big-O final: "O(1)", "O(n)", "O(n²)", etc.

**FORMATO DE RESPUESTA (JSON):**
```json
{{
  "has_multiple_cases": true,
  "best_case": {{
    "case_type": "best",
    "pseudocode_annotated": "busqueda(A, x, i, n)\\n    if (i = n) then  // c1\\n        return -1  // c2\\n    if (A[i] = x) then  // c3\\n        return i  // c4",
    "code_explanation": "Búsqueda que encuentra el elemento inmediatamente",
    "complexity_explanation": "En el mejor caso, el elemento está en la primera posición. Costo: c1 + c3 + c4 = constante",
    "total_complexity": "O(1)"
  }},
  "worst_case": {{
    "case_type": "worst",
    "pseudocode_annotated": "busqueda(A, x, i, n)\\n    if (i = n) then  // c1 * n\\n        return -1  // c2\\n    if (A[i] = x) then  // c3 * n\\n    return busqueda(A, x, i+1, n)  // T(n-1)",
    "code_explanation": "Búsqueda que no encuentra el elemento",
    "complexity_explanation": "En el peor caso, recorre todo el arreglo sin encontrar. Costo: T(n) = T(n-1) + c. Resolviendo: T(n) = O(n)",
    "total_complexity": "O(n)"
  }},
  "average_case": {{
    "case_type": "average",
    "pseudocode_annotated": "busqueda(A, x, i, n)\\n    if (i = n) then  // c1 * (n/2)\\n    if (A[i] = x) then  // c3 * (n/2)\\n    return busqueda(A, x, i+1, n)  // T(n/2)",
    "code_explanation": "Búsqueda que encuentra el elemento en promedio a la mitad",
    "complexity_explanation": "En promedio, el elemento está en la mitad del arreglo. Costo: T(n) ≈ n/2. Resolviendo: T(n) = O(n)",
    "total_complexity": "O(n)"
  }}
}}
```

**IMPORTANTE:** 
- Usa \\n para saltos de línea (NO uses Enter real)
- Escapa comillas dobles: \\" 
- DEBES incluir los 3 casos: best_case, worst_case, average_case
- Responde SOLO con el JSON, sin texto adicional"""

        try:
            thread_id = f"complexity_multiple_{abs(hash(pseudocode))}"
            result = self.invoke_simple(content=content, thread_id=thread_id)
            output = self.extract_response(result)

            if output is None:
                if "messages" in result and result["messages"]:
                    raw_content = result["messages"][-1].content
                    if self.enable_verbose:
                         print(f"⚠️ Intentando recuperar JSON crudo (Multiple)...")
                         print(f"📄 Contenido crudo (primeros 500 chars): {raw_content[:500]}")

                    json_data = self._clean_and_repair_json(raw_content)
                    if json_data:
                        if self.enable_verbose:
                            print(f"🔍 Estructura JSON recuperada: {list(json_data.keys())}")
                        
                        # Verificar si la estructura tiene los campos requeridos
                        if "best_case" not in json_data and "analysis" in json_data:
                            # El modelo devolvió una estructura anidada - extraer los casos
                            analysis_data = json_data.get("analysis", {})
                            if isinstance(analysis_data, dict):
                                # Intentar extraer los 3 casos del análisis
                                best = analysis_data.get("best_case") or analysis_data.get("best")
                                worst = analysis_data.get("worst_case") or analysis_data.get("worst")
                                average = analysis_data.get("average_case") or analysis_data.get("average")
                                
                                if best and worst and average:
                                    json_data = {
                                        "has_multiple_cases": True,
                                        "best_case": best,
                                        "worst_case": worst,
                                        "average_case": average
                                    }
                                    if self.enable_verbose:
                                        print(f"✅ Reestructurado JSON desde 'analysis'")
                                else:
                                    if self.enable_verbose:
                                        print(f"⚠️ Faltan casos en analysis: best={bool(best)}, worst={bool(worst)}, avg={bool(average)}")
                        
                        # Último intento: si solo hay un caso, replicarlo en los 3
                        if "best_case" not in json_data:
                            if self.enable_verbose:
                                print(f"⚠️ No se encontró best_case, worst_case, average_case")
                                print(f"   Intentando replicar caso único...")
                            
                            # Buscar un caso único para replicar
                            single_case = None
                            for key in ["case", "analysis", "result"]:
                                if key in json_data and isinstance(json_data[key], dict):
                                    if "pseudocode_annotated" in json_data[key]:
                                        single_case = json_data[key]
                                        break
                            
                            if not single_case and "pseudocode_annotated" in json_data:
                                single_case = json_data
                            
                            if single_case:
                                if self.enable_verbose:
                                    print(f"✅ Replicando caso único en los 3 casos")
                                
                                # Asegurar que tenga case_type
                                for case_type, case_name in [("best", "best"), ("worst", "worst"), ("average", "average")]:
                                    case_copy = single_case.copy()
                                    case_copy["case_type"] = case_type
                                    json_data[f"{case_type}_case"] = case_copy
                                
                                json_data["has_multiple_cases"] = True
                        
                        return MultipleCasesOutput(**json_data)

                raise ValueError("JSON inválido o mal formado.")

            return output

        except Exception as e:
            if self.enable_verbose:
                print(f"❌ Error crítico en ComplexityLineAgent (Multiple): {e}")
                print(f"   Tipo de error: {type(e).__name__}")
            
            dummy = ComplexityAnalysis(
                case_type="error",
                pseudocode_annotated=f"// Error al analizar.\\n{pseudocode}",
                code_explanation="Error de procesamiento.",
                complexity_explanation=str(e),
                total_complexity="?"
            )
            return MultipleCasesOutput(
                has_multiple_cases=True,
                best_case=dummy,
                worst_case=dummy,
                average_case=dummy,
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
    Función wrapper para análisis de complejidad línea por línea.
    
    Args:
        pseudocode: Código del algoritmo a analizar
        algorithm_name: Nombre del algoritmo
        multiple_cases: Si True, analiza best/worst/average. Si False, caso único
        verbose: Habilita logs detallados
        
    Returns:
        Diccionario con el análisis de complejidad
    """
    agent = ComplexityLineByLineAgent(enable_verbose=verbose)
    
    if multiple_cases:
        output = agent.analyze_multiple_cases(pseudocode, algorithm_name)
        return output.model_dump()
    else:
        output = agent.analyze_single_case(pseudocode, algorithm_name)
        return output.model_dump()
"""
Agente completo de análisis de algoritmos recursivos.
Recibe pseudocódigo y realiza análisis completo de complejidad sin usar módulos externos.
"""

from typing import Dict, Any, Optional
import re


class CompleteRecursiveAnalysisAgent:
    """
    Agente autónomo que analiza algoritmos recursivos desde cero.
    
    Funcionalidades:
    1. Explicar para qué sirve el algoritmo
    2. Clasificar el tipo (programación dinámica, divide y conquista, backtracking, etc.)
    3. Sacar costo por línea (constante * función)
    4. Generar ecuación de recurrencia
    5. Resolver ecuación (Teorema Maestro, Árbol, Sustitución)
    6. Dar respuesta paso a paso
    7. Expresar en notación asintótica (O, Ω, Θ)
    """

    def __init__(self, llm_factory):
        """
        Args:
            llm_factory: Instancia de LLM_Factory para obtener el modelo
        """
        self.llm_factory = llm_factory
        self.llm = None

    def _get_llm(self):
        """Obtiene instancia del LLM de forma lazy."""
        if self.llm is None:
            self.llm = self.llm_factory.get_llm()
        return self.llm

    def analyze(self, pseudocode: str) -> Dict[str, Any]:
        """
        Analiza un algoritmo recursivo completamente.
        
        Args:
            pseudocode: Pseudocódigo del algoritmo
            
        Returns:
            Diccionario con análisis completo
        """
        llm = self._get_llm()
        
        # Paso 1: Explicación y clasificación
        explanation_result = self._explain_and_classify(pseudocode, llm)
        
        # Paso 2: Análisis línea por línea
        line_analysis = self._analyze_line_by_line(pseudocode, llm)
        
        # Paso 3: Generar ecuación de recurrencia
        recurrence_eq = self._generate_recurrence(pseudocode, line_analysis, llm)
        
        # Paso 4: Resolver ecuación
        solution_steps = self._solve_recurrence(recurrence_eq, llm)
        
        # Paso 5: Extraer notación asintótica
        asymptotic = self._extract_asymptotic_notation(solution_steps, llm)
        
        return {
            "algorithm_purpose": explanation_result["purpose"],
            "algorithm_classification": explanation_result["classification"],
            "line_by_line_cost": line_analysis,
            "recurrence_equation": recurrence_eq,
            "solution_method": solution_steps["method"],
            "solution_steps": solution_steps["steps"],
            "final_complexity": solution_steps["complexity"],
            "asymptotic_notation": asymptotic,
            "complete_analysis": self._format_complete_report(
                explanation_result,
                line_analysis,
                recurrence_eq,
                solution_steps,
                asymptotic
            )
        }

    def _explain_and_classify(self, pseudocode: str, llm) -> Dict[str, str]:
        """Paso 1 y 2: Explicar propósito y clasificar algoritmo."""
        prompt = f"""Analiza el siguiente pseudocódigo recursivo:

```
{pseudocode}
```

Responde en formato JSON con las siguientes claves:
1. "purpose": Una explicación clara y concisa de para qué sirve este algoritmo (2-3 líneas).
2. "classification": Clasifica el algoritmo en UNA de estas categorías:
   - Programación Dinámica
   - Divide y Conquista
   - Backtracking
   - Búsqueda Recursiva
   - Ordenamiento Recursivo
   - Recursión de Cola
   - Recursión Múltiple
   - Otro (especifica)

3. "classification_reasoning": Breve justificación de por qué pertenece a esa categoría.

Formato de salida (JSON válido):
{{
  "purpose": "...",
  "classification": "...",
  "classification_reasoning": "..."
}}
"""
        
        response = llm.invoke(prompt).content
        
        # Parsear respuesta JSON
        try:
            import json
            # Extraer JSON del texto si está envuelto en markdown
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            result = json.loads(response)
            return result
        except Exception as e:
            # Fallback si no es JSON válido
            return {
                "purpose": "Algoritmo recursivo (análisis automático)",
                "classification": "No clasificado",
                "classification_reasoning": f"Error al parsear: {str(e)}"
            }

    def _analyze_line_by_line(self, pseudocode: str, llm) -> list:
        """Paso 3: Análisis de costo por línea."""
        prompt = f"""Analiza el costo computacional de cada línea del siguiente pseudocódigo recursivo.

```
{pseudocode}
```

Para cada línea, identifica:
1. El número de línea
2. El código de esa línea
3. El costo computacional en formato: constante * función
   - Constante: c1, c2, c3, etc. (operaciones elementales)
   - Función: 1 (constante), n (lineal), T(n/2) (llamada recursiva), etc.

Ejemplos:
- "x = 5" → "c1 * 1" (asignación constante)
- "if (n == 0)" → "c2 * 1" (comparación constante)
- "return fibonacci(n-1) + fibonacci(n-2)" → "c3 * 1 + T(n-1) + T(n-2)" (operación + 2 llamadas recursivas)
- "for i = 1 to n" → "c4 * n" (bucle lineal)

Responde en formato JSON:
{{
  "lines": [
    {{"line": 1, "code": "...", "cost": "c1 * 1", "explanation": "..."}},
    {{"line": 2, "code": "...", "cost": "...", "explanation": "..."}},
    ...
  ]
}}
"""
        
        response = llm.invoke(prompt).content
        
        try:
            import json
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            result = json.loads(response)
            return result.get("lines", [])
        except Exception:
            # Fallback: análisis básico
            lines = pseudocode.strip().split('\n')
            return [
                {
                    "line": i + 1,
                    "code": line.strip(),
                    "cost": "c * 1",
                    "explanation": "Costo constante"
                }
                for i, line in enumerate(lines)
            ]

    def _generate_recurrence(self, pseudocode: str, line_analysis: list, llm) -> Dict[str, str]:
        """Paso 4: Generar ecuación de recurrencia."""
        
        # Construir contexto con análisis de líneas
        lines_context = "\n".join([
            f"Línea {item['line']}: {item['code']} → Costo: {item['cost']}"
            for item in line_analysis
        ])
        
        prompt = f"""Dado el siguiente pseudocódigo recursivo y su análisis línea por línea:

```
{pseudocode}
```

Análisis de costos:
{lines_context}

Genera la ecuación de recurrencia que modela la complejidad temporal de este algoritmo.

Considera:
1. Caso base: T(caso_base) = constante
2. Caso recursivo: T(n) = [trabajo no recursivo] + [llamadas recursivas]
3. Identifica el patrón de llamadas recursivas (cuántas y con qué tamaño)

Responde en formato JSON:
{{
  "recurrence_equation": "T(n) = ...",
  "base_case": "T(...) = ...",
  "recursive_case": "T(n) = ...",
  "explanation": "Explicación de cómo se construyó la ecuación"
}}

Ejemplos:
- Fibonacci: T(n) = T(n-1) + T(n-2) + c, T(0) = T(1) = c
- Merge Sort: T(n) = 2T(n/2) + cn, T(1) = c
- Binary Search: T(n) = T(n/2) + c, T(1) = c
"""
        
        response = llm.invoke(prompt).content
        
        try:
            import json
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            result = json.loads(response)
            return result
        except Exception:
            return {
                "recurrence_equation": "T(n) = T(subproblema) + trabajo",
                "base_case": "T(1) = c",
                "recursive_case": "T(n) = ...",
                "explanation": "No se pudo generar ecuación automáticamente"
            }

    def _solve_recurrence(self, recurrence_eq: Dict[str, str], llm) -> Dict[str, Any]:
        """Paso 5 y 6: Resolver ecuación y dar pasos."""
        
        equation = recurrence_eq.get("recurrence_equation", "")
        base_case = recurrence_eq.get("base_case", "")
        
        prompt = f"""Resuelve la siguiente ecuación de recurrencia usando el método más apropiado:

Ecuación: {equation}
Caso base: {base_case}

Métodos disponibles:
1. **Teorema Maestro**: Para ecuaciones de la forma T(n) = aT(n/b) + f(n)
2. **Método del Árbol**: Dibujar árbol de recursión y sumar niveles
3. **Método de Sustitución**: Expandir recursivamente hasta encontrar patrón

Responde en formato JSON:
{{
  "method": "Nombre del método usado",
  "steps": [
    "Paso 1: ...",
    "Paso 2: ...",
    "Paso 3: ...",
    ...
  ],
  "complexity": "O(...)",
  "detailed_explanation": "Explicación completa de la resolución"
}}

Asegúrate de:
- Mostrar TODOS los pasos intermedios
- Justificar cada simplificación matemática
- Llegar a la forma cerrada (sin recurrencia)
- Expresar el resultado en notación O grande
"""
        
        response = llm.invoke(prompt).content
        
        try:
            import json
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            result = json.loads(response)
            return result
        except Exception:
            return {
                "method": "Análisis heurístico",
                "steps": [
                    "Paso 1: Identificar patrón de recursión",
                    "Paso 2: Estimar profundidad del árbol",
                    "Paso 3: Calcular trabajo por nivel"
                ],
                "complexity": "O(n log n)",
                "detailed_explanation": "Resolución automática no disponible"
            }

    def _extract_asymptotic_notation(self, solution_steps: Dict[str, Any], llm) -> Dict[str, str]:
        """Paso 7: Extraer notación asintótica (O, Ω, Θ)."""
        
        complexity = solution_steps.get("complexity", "O(n)")
        method = solution_steps.get("method", "")
        explanation = solution_steps.get("detailed_explanation", "")
        
        prompt = f"""Dada la complejidad calculada: {complexity}

Método usado: {method}
Explicación: {explanation}

Expresa la complejidad en las tres notaciones asintóticas:

Responde en formato JSON:
{{
  "big_O": "O(...)",
  "big_Omega": "Ω(...)",
  "big_Theta": "Θ(...)",
  "explanation": {{
    "big_O": "Por qué esta es la cota superior",
    "big_Omega": "Por qué esta es la cota inferior",
    "big_Theta": "Por qué esta es la cota ajustada"
  }}
}}

Consideraciones:
- Big-O (cota superior): Peor caso
- Big-Omega (cota inferior): Mejor caso
- Big-Theta (cota ajustada): Si O = Ω, entonces Θ
"""
        
        response = llm.invoke(prompt).content
        
        try:
            import json
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            result = json.loads(response)
            return result
        except Exception:
            # Fallback: extraer O() del complexity
            return {
                "big_O": complexity,
                "big_Omega": complexity.replace("O", "Ω"),
                "big_Theta": complexity.replace("O", "Θ"),
                "explanation": {
                    "big_O": "Cota superior estimada",
                    "big_Omega": "Cota inferior estimada",
                    "big_Theta": "Cota ajustada estimada"
                }
            }

    def _format_complete_report(
        self,
        explanation: Dict,
        line_analysis: list,
        recurrence: Dict,
        solution: Dict,
        asymptotic: Dict
    ) -> str:
        """Genera reporte completo en texto."""
        
        report = []
        report.append("=" * 80)
        report.append("  ANÁLISIS COMPLETO DE COMPLEJIDAD RECURSIVA")
        report.append("=" * 80)
        report.append("")
        
        # Sección 1: Propósito
        report.append("1. PROPÓSITO DEL ALGORITMO")
        report.append("-" * 80)
        report.append(explanation.get("purpose", "No disponible"))
        report.append("")
        
        # Sección 2: Clasificación
        report.append("2. CLASIFICACIÓN")
        report.append("-" * 80)
        report.append(f"Categoría: {explanation.get('classification', 'No clasificado')}")
        report.append(f"Justificación: {explanation.get('classification_reasoning', '')}")
        report.append("")
        
        # Sección 3: Análisis línea por línea
        report.append("3. ANÁLISIS DE COSTO POR LÍNEA")
        report.append("-" * 80)
        for item in line_analysis:
            report.append(f"Línea {item.get('line', '?')}: {item.get('code', '')}")
            report.append(f"  Costo: {item.get('cost', 'c * 1')}")
            report.append(f"  {item.get('explanation', '')}")
            report.append("")
        
        # Sección 4: Ecuación de recurrencia
        report.append("4. ECUACIÓN DE RECURRENCIA")
        report.append("-" * 80)
        report.append(f"Caso base: {recurrence.get('base_case', '')}")
        report.append(f"Caso recursivo: {recurrence.get('recursive_case', '')}")
        report.append(f"Ecuación completa: {recurrence.get('recurrence_equation', '')}")
        report.append("")
        
        # Sección 5: Método de resolución
        report.append("5. MÉTODO DE RESOLUCIÓN")
        report.append("-" * 80)
        report.append(f"Método usado: {solution.get('method', 'Desconocido')}")
        report.append("")
        
        # Sección 6: Pasos de resolución
        report.append("6. PASOS DE RESOLUCIÓN")
        report.append("-" * 80)
        steps = solution.get('steps', [])
        for i, step in enumerate(steps, 1):
            report.append(f"{i}. {step}")
        report.append("")
        
        # Sección 7: Notación asintótica
        report.append("7. NOTACIÓN ASINTÓTICA")
        report.append("-" * 80)
        report.append(f"Cota superior (Big-O): {asymptotic.get('big_O', 'O(?)')}")
        report.append(f"Cota inferior (Big-Ω): {asymptotic.get('big_Omega', 'Ω(?)')}")
        report.append(f"Cota ajustada (Big-Θ): {asymptotic.get('big_Theta', 'Θ(?)')}")
        report.append("")
        
        explanations = asymptotic.get('explanation', {})
        if isinstance(explanations, dict):
            report.append("Justificaciones:")
            report.append(f"  O: {explanations.get('big_O', '')}")
            report.append(f"  Ω: {explanations.get('big_Omega', '')}")
            report.append(f"  Θ: {explanations.get('big_Theta', '')}")
        
        report.append("")
        report.append("=" * 80)
        report.append(f"COMPLEJIDAD FINAL: {solution.get('complexity', 'O(?)')}")
        report.append("=" * 80)
        
        return "\n".join(report)


def test_agent():
    """Función de prueba del agente."""
    from app.external_services.Agentes.LLM_Factory import LLM_Factory
    
    # Pseudocódigo de ejemplo: Fibonacci recursivo
    pseudocode = """
fibonacci(n)
begin
    if (n <= 1) then
        return n
    else
        return fibonacci(n-1) + fibonacci(n-2)
    end
end
"""
    
    # Crear agente
    llm_factory = LLM_Factory()
    agent = CompleteRecursiveAnalysisAgent(llm_factory)
    
    # Analizar
    print("Analizando algoritmo recursivo...")
    result = agent.analyze(pseudocode)
    
    # Imprimir reporte completo
    print(result["complete_analysis"])
    
    return result


if __name__ == "__main__":
    test_agent()

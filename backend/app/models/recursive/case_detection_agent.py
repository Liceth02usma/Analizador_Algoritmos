from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from ...external_services.Agentes.Agent import AgentBase


class CaseDetectionResponse(BaseModel):
    """Respuesta estructurada del agente de detección de casos."""
    
    has_multiple_cases: bool = Field(
        description="True si el algoritmo tiene mejor, peor y caso promedio. False si es un caso general."
    )
    reasoning: str = Field(
        description="Explicación detallada del razonamiento para la decisión."
    )
    detected_patterns: Dict[str, Any] = Field(
        default_factory=dict,
        description="Patrones detectados en el algoritmo que justifican la decisión."
    )


class CaseDetectionAgent(AgentBase[CaseDetectionResponse]):
    """
    Agente que determina si un algoritmo recursivo tiene múltiples casos
    (mejor, peor, promedio) o es un caso general.
    
    Analiza el AST y el pseudocódigo para identificar:
    - Condicionales que afectan el número de llamadas recursivas
    - Estructuras de datos de entrada que varían (listas ordenadas, pivotes, etc.)
    - Patrones conocidos (QuickSort, Binary Search, etc.)
    """

    def _configure(self) -> None:
        """Configura el agente con el prompt y el formato de respuesta."""
        
        self.response_format = CaseDetectionResponse
        
        self.SYSTEM_PROMPT = """Eres un experto en análisis de algoritmos recursivos y teoría de la complejidad.

Tu tarea es determinar si un algoritmo recursivo tiene MÚLTIPLES CASOS de complejidad 
(mejor caso, peor caso y caso promedio DIFERENTES) o si es un CASO GENERAL (un solo caso para todos).

**CRITERIOS PARA MÚLTIPLES CASOS:**

1. **Condicionales que afectan llamadas recursivas:**
   - El número de llamadas recursivas varía según la entrada
   - Ejemplo: QuickSort (pivote bueno vs malo), Binary Search (elemento encontrado rápido vs no encontrado)

2. **Estructura de datos de entrada:**
   - Algoritmos que dependen del orden de los datos (ordenado, parcialmente ordenado, aleatorio)
   - Algoritmos con pivotes o particiones que pueden ser óptimas o pésimas

3. **Patrones conocidos con múltiples casos:**
   - QuickSort: O(n log n) mejor, O(n²) peor
   - Binary Search: O(1) mejor, O(log n) peor
   - Merge Sort: O(n log n) todos los casos (CASO GENERAL - no tiene múltiples casos)
   - Torres de Hanoi: O(2^n) todos los casos (CASO GENERAL)

4. **Profundidad de recursión variable:**
   - La profundidad del árbol de recursión cambia significativamente según la entrada

**CRITERIOS PARA CASO GENERAL:**

1. **Complejidad constante sin importar entrada:**
   - Todos los datos se procesan igual (Merge Sort, Torres de Hanoi)
   - No hay condicionales que corten la recursión temprano

2. **Divide and Conquer balanceado:**
   - Siempre divide el problema de la misma manera

3. **Factoriales, Fibonacci, etc.:**
   - Complejidad fija según el parámetro n

**INSTRUCCIONES:**

1. Analiza el pseudocódigo y el AST cuidadosamente
2. Identifica si hay condicionales o pivotes que afecten la recursión
3. Determina si la complejidad varía significativamente según la entrada
4. Retorna `has_multiple_cases: true` SOLO si hay evidencia clara de múltiples casos
5. Por defecto, si no estás seguro, retorna `false` (caso general)

**FORMATO DE RESPUESTA:**

```json
{
  "has_multiple_cases": true/false,
  "reasoning": "Explicación detallada del razonamiento",
  "detected_patterns": {
    "has_conditionals": true/false,
    "has_pivot_or_partition": true/false,
    "recursion_depth_varies": true/false,
    "known_algorithm": "nombre del algoritmo si se reconoce"
  }
}
```

**IMPORTANTE:** Sé conservador. Solo marca `has_multiple_cases: true` si hay evidencia CLARA."""

    def detect_cases(
        self,
        pseudocode: str,
        ast_structure: Any,
        algorithm_name: Optional[str] = None,
        thread_id: str = "case_detection"
    ) -> bool:
        """
        Determina si el algoritmo tiene múltiples casos o es un caso general.
        
        Args:
            pseudocode: Código del algoritmo en pseudocódigo
            ast_structure: Estructura del AST del algoritmo
            algorithm_name: Nombre del algoritmo (opcional)
            thread_id: ID del thread para tracking
            
        Returns:
            bool: True si tiene múltiples casos, False si es caso general
        """
        
        # Convertir AST a string legible
        ast_str = str(ast_structure)
        if len(ast_str) > 2000:
            ast_str = ast_str[:2000] + "... (truncado)"
        
        # Construir el mensaje para el agente
        user_message = f"""Analiza el siguiente algoritmo recursivo y determina si tiene múltiples casos de complejidad.

**NOMBRE DEL ALGORITMO:** {algorithm_name or "No especificado"}

**PSEUDOCÓDIGO:**
```
{pseudocode}
```

**ESTRUCTURA AST (simplificada):**
```
{ast_str}
```

Analiza cuidadosamente y determina si este algoritmo tiene:
- **MÚLTIPLES CASOS** (mejor, peor, promedio diferentes) → `has_multiple_cases: true`
- **CASO GENERAL** (misma complejidad para todas las entradas) → `has_multiple_cases: false`

Retorna tu análisis en formato JSON."""

        # Invocar el agente
        result = self.invoke_simple(
            content=user_message,
            thread_id=thread_id
        )
        
        # Extraer la respuesta estructurada
        response = self.extract_response(result)
        
        if response is None:
            print("⚠️ [CaseDetectionAgent] No se pudo parsear la respuesta. Asumiendo caso general.")
            return False
        
        # Log del resultado
        print(f"\n{'='*70}")
        print(f"🔍 DETECCIÓN DE CASOS - {algorithm_name or 'Algoritmo'}")
        print(f"{'='*70}")
        print(f"✓ Tiene múltiples casos: {'SÍ' if response.has_multiple_cases else 'NO'}")
        print(f"\n📝 Razonamiento:")
        print(f"   {response.reasoning}")
        print(f"\n🔎 Patrones detectados:")
        for key, value in response.detected_patterns.items():
            print(f"   - {key}: {value}")
        print(f"{'='*70}\n")
        
        return response.has_multiple_cases

    def detect_cases_verbose(
        self,
        pseudocode: str,
        ast_structure: Any,
        algorithm_name: Optional[str] = None,
        thread_id: str = "case_detection"
    ) -> CaseDetectionResponse:
        """
        Versión verbose que retorna el objeto completo con razonamiento.
        
        Args:
            pseudocode: Código del algoritmo en pseudocódigo
            ast_structure: Estructura del AST del algoritmo
            algorithm_name: Nombre del algoritmo (opcional)
            thread_id: ID del thread para tracking
            
        Returns:
            CaseDetectionResponse: Objeto con el resultado y razonamiento completo
        """
        
        # Convertir AST a string legible
        ast_str = str(ast_structure)
        if len(ast_str) > 2000:
            ast_str = ast_str[:2000] + "... (truncado)"
        
        # Construir el mensaje para el agente
        user_message = f"""Analiza el siguiente algoritmo recursivo y determina si tiene múltiples casos de complejidad.

**NOMBRE DEL ALGORITMO:** {algorithm_name or "No especificado"}

**PSEUDOCÓDIGO:**
```
{pseudocode}
```

**ESTRUCTURA AST (simplificada):**
```
{ast_str}
```

Analiza cuidadosamente y determina si este algoritmo tiene:
- **MÚLTIPLES CASOS** (mejor, peor, promedio diferentes) → `has_multiple_cases: true`
- **CASO GENERAL** (misma complejidad para todas las entradas) → `has_multiple_cases: false`

Retorna tu análisis en formato JSON."""

        # Invocar el agente
        result = self.invoke_simple(
            content=user_message,
            thread_id=thread_id
        )
        
        # Extraer la respuesta estructurada
        response = self.extract_response(result)
        
        if response is None:
            # Fallback en caso de error
            print("⚠️ [CaseDetectionAgent] No se pudo parsear la respuesta. Retornando caso general.")
            return CaseDetectionResponse(
                has_multiple_cases=False,
                reasoning="Error al analizar. Se asume caso general por defecto.",
                detected_patterns={}
            )
        
        # Log del resultado
        print(f"\n{'='*70}")
        print(f"🔍 DETECCIÓN DE CASOS - {algorithm_name or 'Algoritmo'}")
        print(f"{'='*70}")
        print(f"✓ Tiene múltiples casos: {'SÍ' if response.has_multiple_cases else 'NO'}")
        print(f"\n📝 Razonamiento:")
        print(f"   {response.reasoning}")
        print(f"\n🔎 Patrones detectados:")
        for key, value in response.detected_patterns.items():
            print(f"   - {key}: {value}")
        print(f"{'='*70}\n")
        
        return response

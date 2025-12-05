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

    def __init__(self, model_type: str = "Gemini_Rapido", provider: Optional[str] = None):
        """Inicializa el agente con optimización de tokens."""
        # Ignorar provider por ahora (compatibilidad con tests)
        super().__init__(model_type, override={"max_tokens": 1000})

    def _configure(self) -> None:
        """Configura el agente con el prompt y el formato de respuesta."""
        
        self.response_format = CaseDetectionResponse
        
        self.SYSTEM_PROMPT = """Determina si un algoritmo tiene MÚLTIPLES CASOS (mejor/peor/promedio diferentes) o CASO GENERAL (misma complejidad siempre).

**MÚLTIPLES CASOS (has_multiple_cases=true):**
- QuickSort: pivote causa particiones desbalanceadas → O(n log n) mejor, O(n²) peor
- Búsqueda Lineal: elemento puede estar en cualquier posición

**CASO GENERAL (has_multiple_cases=false):**
- Binary Search: SIEMPRE O(log n) - divide a la mitad siempre
- Merge Sort: SIEMPRE O(n log n) - divide igual siempre
- Fibonacci: SIEMPRE O(2^n) - dos llamadas siempre

**CLAVE para QuickSort:** Si ves "partition", "pivote", o "quicksort" → casi siempre es has_multiple_cases=true porque el pivote afecta las particiones.

**Responde en JSON:**
{"has_multiple_cases": bool, "reasoning": "1-2 líneas", "detected_patterns": {"has_pivot_or_partition": bool, "known_algorithm": "nombre"}}

**Sé breve. Solo marca true si hay evidencia clara de complejidad variable."""

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
        
        # Detección determinista rápida para algoritmos conocidos
        pseudocode_lower = pseudocode.lower()
        name_lower = (algorithm_name or "").lower()
        
        # CASO: QuickSort - SIEMPRE tiene múltiples casos
        if any(keyword in pseudocode_lower or keyword in name_lower 
               for keyword in ["quicksort", "partition", "pivote"]):
            print(f"\n{'='*70}")
            print(f"🔍 DETECCIÓN DE CASOS - {algorithm_name or 'Algoritmo'}")
            print(f"{'='*70}")
            print(f"✓ Tiene múltiples casos: SÍ")
            print(f"\n📝 Razonamiento:")
            print(f"   QuickSort detectado: pivote causa particiones desbalanceadas → múltiples casos")
            print(f"\n🔎 Patrones detectados:")
            print(f"   - has_pivot_or_partition: True")
            print(f"   - known_algorithm: QuickSort")
            print(f"{'='*70}\n")
            return True
        
        # CASO: Merge Sort - SIEMPRE caso general
        if any(keyword in pseudocode_lower or keyword in name_lower 
               for keyword in ["mergesort", "merge sort"]):
            print(f"\n{'='*70}")
            print(f"🔍 DETECCIÓN DE CASOS - {algorithm_name or 'Algoritmo'}")
            print(f"{'='*70}")
            print(f"✓ Tiene múltiples casos: NO")
            print(f"\n📝 Razonamiento:")
            print(f"   MergeSort detectado: siempre divide a la mitad → caso general")
            print(f"\n🔎 Patrones detectados:")
            print(f"   - known_algorithm: MergeSort")
            print(f"{'='*70}\n")
            return False
        
        # CASO: Binary Search - caso general (siempre O(log n))
        if any(keyword in pseudocode_lower or keyword in name_lower 
               for keyword in ["binarysearch", "binary search", "búsqueda binaria"]):
            print(f"\n{'='*70}")
            print(f"🔍 DETECCIÓN DE CASOS - {algorithm_name or 'Algoritmo'}")
            print(f"{'='*70}")
            print(f"✓ Tiene múltiples casos: NO")
            print(f"\n📝 Razonamiento:")
            print(f"   Binary Search: siempre divide a la mitad, O(log n) constante")
            print(f"\n🔎 Patrones detectados:")
            print(f"   - known_algorithm: BinarySearch")
            print(f"{'='*70}\n")
            return False
        
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

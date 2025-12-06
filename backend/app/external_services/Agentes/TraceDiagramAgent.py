import os
import re
import sys
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
sys.path.append(os.getenv("PYTHONPATH", "backend"))

from app.external_services.Agentes.Agent import AgentBase

# ============================================================================
# 📘 SCHEMAS
# ============================================================================


class TraceRequest(BaseModel):
    pseudocode: str = Field(description="Pseudocódigo del algoritmo.")
    algorithm_name: str = Field(description="Nombre del algoritmo.")
    # Recibimos los casos detectados por el agente anterior para saber qué graficar
    cases_summary: str = Field(
        description="Resumen de los casos (Mejor/Peor) y sus condiciones."
    )


class DiagramDetail(BaseModel):
    case_name: str = Field(description="Ej: 'Mejor Caso', 'Peor Caso'.")
    description: str = Field(
        description="Breve descripción del flujo (ej: 'El bucle termina inmediatamente')."
    )
    mermaid_code: str = Field(
        description="Código fuente Mermaid.js (graph TD) del diagrama de flujo."
    )


class TraceResponse(BaseModel):
    algorithm_name: str
    diagrams: List[DiagramDetail] = Field(description="Lista de diagramas generados.")


# ============================================================================
# 🎨 AGENTE DE DIAGRAMACIÓN
# ============================================================================


class TraceDiagramAgent(AgentBase[TraceResponse]):
    """
    Agente visualizador. Convierte la lógica de ejecución en diagramas de flujo Mermaid.js.
    """

    def _configure(self) -> None:
        self.tools = []
        self.context_schema = TraceRequest
        self.response_format = TraceResponse

        self.SYSTEM_PROMPT = """
Eres un Experto en Visualización de Algoritmos y sintaxis Mermaid.js.
Tu tarea es generar **Diagramas de Flujo (Flowcharts)** que representen el seguimiento de la ejecución de un algoritmo.

### 🎯 OBJETIVO
Generar código `mermaid` (graph TD) para visualizar el flujo de control en diferentes escenarios (Mejor, Peor, Promedio).

### 🎨 REGLAS ESTRICTAS DE SINTAXIS MERMAID
1. **PRIMERA LÍNEA:** Siempre `graph TD` (Top-Down) o `graph LR` (Left-Right)
2. **IDs DE NODOS:**
   - Solo alfanuméricos sin espacios: `Start`, `node1`, `check2`, `end1`
   - ❌ NUNCA: `nodo 1`, `check final`, espacios o caracteres especiales
3. **TIPOS DE NODOS:**
   - Inicio/Fin: `Start((Inicio))` / `End((Fin))`
   - Procesos: `node1[Texto del proceso]`
   - Decisiones: `check1{Condición?}`
   - Notas: `note1[Nota: explicación]`
4. **CONEXIONES:**
   - Simple: `A --> B`
   - Con etiqueta: `A -->|Sí| B` o `A -- Sí --> B`
   - Multiples salidas: 
     ```
     decision1{x > 0?}
     decision1 -->|Sí| procesar
     decision1 -->|No| finalizar
     ```
5. **TEXTO EN NODOS:**
   - Usa comillas si hay caracteres especiales: `node1["x := x + 1"]`
   - Escapa corchetes internos: `node1["A[i] = x"]`
6. **SUBGRAFOS (opcional):**
   ```
   subgraph bucle["Bucle principal"]
       loop1[Iteración]
   end
   ```

### 📋 CHECKLIST DE VALIDACIÓN (Auto-verifica antes de responder)
✅ Primera línea es `graph TD` o `graph LR`
✅ Todos los IDs sin espacios (Start, node1, check2)
✅ Nodos inicio/fin con `(( ))` doble paréntesis
✅ Decisiones con `{ }` llaves
✅ Procesos con `[ ]` corchetes
✅ Todas las conexiones tienen formato correcto: `A --> B` o `A -->|etiqueta| B`
✅ No hay caracteres especiales sin escapar
✅ Todos los nodos referenciados están definidos

### 🧠 LÓGICA DE SEGUIMIENTO (TRACE)
Debes adaptar el diagrama según el caso:
- **Mejor Caso:** Camino más corto (ej: elemento encontrado inmediatamente)
- **Peor Caso:** Camino completo (ej: todas las iteraciones)
- **Caso Promedio:** Camino intermedio

### ✅ EJEMPLO CORRECTO (Búsqueda Lineal - Mejor Caso)
```mermaid
graph TD
    Start((Inicio)) --> Init["i := 0"]
    Init --> CheckBounds{i < n?}
    CheckBounds -->|Sí| CheckFound{"A[i] = x?"}
    CheckFound -->|Sí| ReturnFound[Return i]
    ReturnFound --> End((Fin))
    CheckFound -->|No| Increment["i := i + 1"]
    Increment --> CheckBounds
    CheckBounds -->|No| ReturnNotFound[Return -1]
    ReturnNotFound --> End
```

### ❌ ERRORES COMUNES A EVITAR
1. ❌ `nodo 1` → ✅ `node1`
2. ❌ `check final` → ✅ `checkFinal`
3. ❌ `A -> B` → ✅ `A --> B` (doble guión)
4. ❌ `node1(Texto)` para proceso → ✅ `node1[Texto]`
5. ❌ `Start(Inicio)` → ✅ `Start((Inicio))` (doble paréntesis)
6. ❌ Olvidar definir nodo antes de usarlo

### 📤 FORMATO DE SALIDA JSON
Devuelve lista de diagramas. Cada `mermaid_code` debe ser sintácticamente correcto y completo.
"""

    def _validate_mermaid_syntax(self, mermaid_code: str) -> tuple[bool, str]:
        """
        Valida sintaxis básica de Mermaid para flowcharts.

        Returns:
            tuple[bool, str]: (es_valido, mensaje_error)
        """
        lines = mermaid_code.strip().split("\n")

        # 1. Verificar primera línea
        if not lines or not lines[0].strip().startswith("graph "):
            return False, "Debe empezar con 'graph TD' o 'graph LR'"

        # 2. Verificar IDs sin espacios
        node_id_pattern = re.compile(r"^[a-zA-Z0-9_]+")
        for i, line in enumerate(lines[1:], start=2):
            line = line.strip()
            if not line or line.startswith("subgraph") or line.startswith("end"):
                continue

            # Extraer ID del nodo (antes de cualquier símbolo)
            match = node_id_pattern.match(line)
            if match:
                node_id = match.group(0)
                # Verificar que no tenga espacios
                if " " in node_id:
                    return (
                        False,
                        f"Línea {i}: ID '{node_id}' contiene espacios. Use CamelCase o snake_case",
                    )

        # 3. Verificar sintaxis de conexiones
        connection_pattern = re.compile(r"-->")
        for i, line in enumerate(lines[1:], start=2):
            if "-->" in line:
                # Verificar formato correcto
                if "->" in line and "-->" not in line:
                    return False, f"Línea {i}: Use '-->' (doble guión) no '->' (simple)"

        # 4. Verificar paréntesis balanceados
        open_chars = ["(", "[", "{"]
        close_chars = [")", "]", "}"]
        for i, line in enumerate(lines[1:], start=2):
            stack = []
            for char in line:
                if char in open_chars:
                    stack.append(char)
                elif char in close_chars:
                    if not stack:
                        return False, f"Línea {i}: Paréntesis/corchetes desbalanceados"
                    expected = open_chars[close_chars.index(char)]
                    if stack[-1] != expected:
                        return False, f"Línea {i}: Paréntesis/corchetes mal emparejados"
                    stack.pop()

        return True, "Sintaxis válida"

    def _fix_common_errors(self, mermaid_code: str) -> str:
        """
        Corrige errores comunes en código Mermaid.
        """
        # Reemplazar guiones simples por dobles en conexiones
        mermaid_code = re.sub(r"(\s)->\s", r"\1--> ", mermaid_code)

        # Eliminar espacios en IDs (básico)
        lines = mermaid_code.split("\n")
        fixed_lines = []

        for line in lines:
            # Si es una definición de nodo, quitar espacios del ID
            if "-->" not in line and any(symbol in line for symbol in ["((", "[", "{"]):
                # Detectar ID antes del primer símbolo
                for symbol in ["((", "[", "{"]:
                    if symbol in line:
                        parts = line.split(symbol, 1)
                        node_id = parts[0].strip().replace(" ", "_")
                        line = node_id + symbol + parts[1]
                        break
            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def generate_diagrams(
        self, pseudocode: str, algorithm_name: str, cases_summary: str
    ) -> TraceResponse:

        context = TraceRequest(
            pseudocode=pseudocode,
            algorithm_name=algorithm_name,
            cases_summary=cases_summary,
        )

        content = f"""
Genera los diagramas de flujo para: {algorithm_name}.

--- CÓDIGO ---
{pseudocode}

--- ESCENARIOS A GRAFICAR ---
{cases_summary}

IMPORTANTE:
1. Verifica que todos los IDs de nodos NO tengan espacios (usa CamelCase o snake_case)
2. Asegúrate de que todas las conexiones usen '-->' (doble guión)
3. Verifica que los paréntesis estén balanceados: (( )) para inicio/fin, [ ] para procesos, {{ }} para decisiones
4. No uses caracteres especiales sin escapar en los textos

Crea el código Mermaid para visualizar el flujo en el Mejor y Peor caso (y Promedio si aplica).
"""

        # Intentar generar con hasta 2 reintentos si hay errores de sintaxis
        max_attempts = 3
        for attempt in range(max_attempts):
            result = self.invoke_simple(
                content=(
                    content
                    if attempt == 0
                    else f"{content}\n\n⚠️ INTENTO {attempt + 1}: El código anterior tenía errores. Corrígelos y genera código válido."
                ),
                context=context.model_dump(),
                thread_id=f"trace_{algorithm_name}_attempt{attempt}",
            )

            response = self.extract_response(result)
            if not response:
                if attempt == max_attempts - 1:
                    raise ValueError(
                        "Error generando diagramas después de múltiples intentos."
                    )
                continue

            # Validar y corregir cada diagrama
            all_valid = True
            for diagram in response.diagrams:
                # Intentar corrección automática
                original_code = diagram.mermaid_code
                fixed_code = self._fix_common_errors(original_code)

                # Validar
                is_valid, error_msg = self._validate_mermaid_syntax(fixed_code)

                if is_valid:
                    diagram.mermaid_code = fixed_code
                else:
                    print(f"⚠️ Validación falló para {diagram.case_name}: {error_msg}")
                    all_valid = False
                    # Agregar feedback al prompt para el siguiente intento
                    content += f"\n\n❌ ERROR en '{diagram.case_name}': {error_msg}\nCódigo problemático:\n{original_code[:200]}..."
                    break

            if all_valid:
                print(
                    f"✅ Todos los diagramas validados correctamente (Intento {attempt + 1})"
                )
                return response

            if attempt == max_attempts - 1:
                print(
                    f"⚠️ Devolviendo diagramas con posibles errores después de {max_attempts} intentos"
                )
                return response

        raise ValueError("Error generando diagramas.")

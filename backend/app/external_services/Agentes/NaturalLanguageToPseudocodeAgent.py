import os
import sys
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from app.external_services.Agentes.Agent import AgentBase

load_dotenv()
sys.path.append(os.getenv("PYTHONPATH", "backend"))

# --- INPUT SCHEMA ---
class TranslationInput(BaseModel):
    user_input: str = Field(description="Texto en lenguaje natural o código en otro lenguaje.")

# --- OUTPUT SCHEMA ---
class TranslationResponse(BaseModel):
    pseudocode: str = Field(description="El pseudocódigo traducido que CUMPLE ESTRICTAMENTE la gramática.")
    was_successful: bool = Field(description="True si se pudo traducir, False si la entrada no tenía sentido algorítmico.")
    error_message: Optional[str] = Field(description="Mensaje de error si no se pudo traducir.")

class NaturalLanguageToPseudocodeAgent(AgentBase[TranslationResponse]):
    """
    Agente traductor. Convierte lenguaje natural/código externo a la Gramática Interna (Lark).
    """

    def _configure(self) -> None:
        self.tools = []
        self.context_schema = TranslationInput
        self.response_format = TranslationResponse

        # Le inyectamos las reglas clave de tu gramática Lark en el prompt
        self.SYSTEM_PROMPT = """
Eres un Compilador Experto y Traductor de Algoritmos.
Tu misión es convertir descripciones en lenguaje natural o código (Python/C/Java) a un **Pseudocódigo Estricto** que cumpla con una gramática específica (Pascal-like).

### 📜 REGLAS GRAMATICALES (ESTRICTAS)
1. **Bloques:** Usa `begin` y `end` para TODOS los bloques.
2. **Asignación:** Usa SIEMPRE la flecha `🡨` (copia este caracter).
   - INCORRECTO: `x = 5`. CORRECTO: `x 🡨 5`.
3. **Comparación (MUY IMPORTANTE):**
   - Igualdad: Usa `=` (NO uses `==`).
   - Diferencia: Usa `≠` (NO uses `!=` ni `<>`).
   - Ejemplo: `if (n = 0) then ...`
4. **Ciclo FOR:** `for var 🡨 inicio to fin do begin ... end`
5. **Ciclo WHILE:** `while (condicion) do begin ... end`
6. **Ciclo REPEAT:** `repeat ... until (condicion)`
7. **Condicional IF:** `if (condicion) then begin ... end else begin ... end`
8. **Procedimientos:** `nombre(p1, p2) begin ... end`
9. **Llamadas:** Usa `CALL nombre_funcion(args)`.
10. **Retorno:** `return valor`.

### 🧠 EJEMPLO DE TRADUCCIÓN
**Input:** "Haz un algoritmo que si x es igual a 0 retorne true"
**Output:**
check_zero(x)
begin
    if (x = 0) then  ► Nota el uso de un solo igual
    begin
        return T
    end
    return F
end

### 🚫 RESTRICCIONES
- Si el input es vago (ej: "Fibonacci"), genera la versión ITERATIVA estándar.
- Asegúrate de cerrar todos los bloques `begin` con `end`.
"""

    def translate(self, user_input: str) -> TranslationResponse:
        content = f"Traduce esto a la gramática estricta:\n\n{user_input}"
        
        # Usamos un modelo rápido pero capaz (Flash)
        result = self.invoke_simple(
            content=content,
            context={"user_input": user_input},
            thread_id="translator_session"
        )
        
        response = self.extract_response(result)
        if not response:
            return TranslationResponse(
                pseudocode="", 
                was_successful=False, 
                error_message="El modelo no generó una respuesta válida."
            )
        return response
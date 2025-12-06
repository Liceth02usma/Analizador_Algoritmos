import os
import sys
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from app.external_services.Agentes.Agent import AgentBase
import json
from app.data.seed_algorithms import KNOWN_ALGORITHMS  # ✅ Agregar import

load_dotenv()
sys.path.append(os.getenv("PYTHONPATH", "backend"))


# --- INPUT SCHEMA ---
class TranslationInput(BaseModel):
    user_input: str = Field(
        description="Texto en lenguaje natural o código en otro lenguaje."
    )


# --- OUTPUT SCHEMA ---
class TranslationResponse(BaseModel):
    pseudocode: str = Field(
        description="El pseudocódigo traducido que CUMPLE ESTRICTAMENTE la gramática."
    )
    was_successful: bool = Field(
        description="True si se pudo traducir, False si la entrada no tenía sentido algorítmico."
    )
    error_message: Optional[str] = Field(
        description="Mensaje de error si no se pudo traducir."
    )
    from_cache: bool = Field(
        default=False, description="True si fue obtenido de ChromaDB"
    )


class NaturalLanguageToPseudocodeAgent(AgentBase[TranslationResponse]):
    """
    Agente traductor. Convierte lenguaje natural/código externo a la Gramática Interna (Lark).
    PRIMERO consulta ChromaDB, LUEGO traduce si no existe.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar cliente de ChromaDB
        self._init_chroma_db()

    def _init_chroma_db(self):
        """Inicializa la conexión a ChromaDB (nueva configuración)."""
        try:
            import chromadb

            chroma_db_path = os.path.join(
                os.path.dirname(__file__), "../../../chroma_db"
            )

            # ✅ NUEVA FORMA: Usar PersistentClient directamente
            self.chroma_client = chromadb.PersistentClient(path=chroma_db_path)

            # Obtener o crear colección de algoritmos traducidos
            self.algorithms_collection = self.chroma_client.get_or_create_collection(
                name="translated_algorithms",
                metadata={"description": "Algoritmos ya traducidos a pseudocódigo"},
            )
            print(
                f"[ChromaDB] ✅ Conectado a colección 'translated_algorithms' en {chroma_db_path}"
            )
        except Exception as e:
            print(f"[ChromaDB] ⚠️ Error inicializando ChromaDB: {e}")
            self.chroma_client = None
            self.algorithms_collection = None

    def _search_in_chroma_db(self, user_input: str) -> Optional[str]:
        """
        Busca el pseudocódigo en ChromaDB.

        Returns:
            Pseudocódigo si existe, None si no.
        """
        if not self.algorithms_collection:
            return None

        try:
            # Buscar por similitud semántica (max_results=1)
            results = self.algorithms_collection.query(
                query_texts=[user_input],
                n_results=1,
                where_document={
                    "$contains": user_input.lower()
                },  # Búsqueda adicional exacta
            )

            if results and results["documents"] and len(results["documents"][0]) > 0:
                # Encontró un resultado
                doc = results["documents"][0][0]
                print(f"[ChromaDB] ✅ Algoritmo encontrado en cache: {doc[:50]}...")
                return doc

            return None
        except Exception as e:
            print(f"[ChromaDB] ⚠️ Error buscando en ChromaDB: {e}")
            return None

    def _store_in_chroma_db(
        self, user_input: str, pseudocode: str, algorithm_name: str = ""
    ):
        """
        Almacena el pseudocódigo traducido en ChromaDB.
        """
        if not self.algorithms_collection:
            return

        try:
            # Generar ID único basado en hash del input
            import hashlib

            doc_id = hashlib.md5(user_input.encode()).hexdigest()

            self.algorithms_collection.add(
                ids=[doc_id],
                documents=[pseudocode],
                metadatas=[
                    {
                        "original_input": user_input,
                        "algorithm_name": algorithm_name,
                        "timestamp": str(__import__("datetime").datetime.now()),
                    }
                ],
            )
            print(f"[ChromaDB] ✅ Algoritmo almacenado en cache con ID: {doc_id}")
        except Exception as e:
            print(f"[ChromaDB] ⚠️ Error almacenando en ChromaDB: {e}")

    def _configure(self) -> None:
        self.tools = []
        self.context_schema = TranslationInput
        self.response_format = TranslationResponse

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

    def _search_known_algorithms(self, user_input: str) -> Optional[str]:
        """
        Busca en KNOWN_ALGORITHMS por coincidencia de keywords.

        Returns:
            Pseudocódigo si encuentra coincidencia, None si no.
        """
        user_input_lower = user_input.lower()

        for algo in KNOWN_ALGORITHMS:
            keywords = algo.get("keywords", "").lower()
            name = algo.get("name", "").lower()

            # Búsqueda por keywords o nombre
            if (
                user_input_lower in keywords
                or user_input_lower in name
                or any(kw in user_input_lower for kw in keywords.split(","))
            ):
                print(f"[KNOWN_ALGORITHMS] ✅ Encontrado: {algo['name']}")
                return algo["pseudocode"]

        return None

    def translate(self, user_input: str) -> TranslationResponse:
        """
        Traduce lenguaje natural a pseudocódigo.
        ORDEN DE BÚSQUEDA:
        1️⃣ KNOWN_ALGORITHMS (más rápido)
        2️⃣ ChromaDB (búsquedas previas)
        3️⃣ LLM (traducción nueva)
        """

        # 1️⃣ BUSCAR EN KNOWN_ALGORITHMS
        print(f"\n🔍 [TRANSLATE] Buscando en KNOWN_ALGORITHMS: '{user_input}'")
        known_pseudocode = self._search_known_algorithms(user_input)

        if known_pseudocode:
            print(f"✅ [TRANSLATE] Algoritmo encontrado en semilla")
            return TranslationResponse(
                pseudocode=known_pseudocode,
                was_successful=True,
                error_message=None,
                from_cache=True,
            )

        # 2️⃣ BUSCAR EN CHROMA DB
        print(f"🔍 [TRANSLATE] Buscando en ChromaDB: '{user_input}'")
        cached_pseudocode = self._search_in_chroma_db(user_input)

        if cached_pseudocode:
            print(f"✅ [TRANSLATE] Algoritmo encontrado en cache")
            return TranslationResponse(
                pseudocode=cached_pseudocode,
                was_successful=True,
                error_message=None,
                from_cache=True,
            )

        # 3️⃣ SI NO EXISTE, TRADUCIR CON LLM
        print(f"📝 [TRANSLATE] No encontrado. Traduciendo con LLM...")
        content = f"Traduce esto a la gramática estricta:\n\n{user_input}"

        result = self.invoke_simple(
            content=content,
            context={"user_input": user_input},
            thread_id="translator_session",
        )

        response = self.extract_response(result)
        if not response:
            return TranslationResponse(
                pseudocode="",
                was_successful=False,
                error_message="El modelo no generó una respuesta válida.",
                from_cache=False,
            )

        # 4️⃣ ALMACENAR EN CHROMA DB
        if response.was_successful and response.pseudocode:
            print(f"💾 [TRANSLATE] Almacenando resultado en ChromaDB...")
            # Extraer nombre del algoritmo del pseudocódigo
            algo_name = (
                response.pseudocode.split("(")[0].strip()
                if "(" in response.pseudocode
                else "unknown"
            )
            self._store_in_chroma_db(user_input, response.pseudocode, algo_name)
            response.from_cache = False

        return response

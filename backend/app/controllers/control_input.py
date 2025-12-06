from app.parsers.parser import parser, TreeToDict
from app.models.solution import Solution
from lark import UnexpectedInput


from app.parsers.parser import parse_pseudocode
from app.external_services.Agentes.NaturalLanguageToPseudocodeAgent import (
    NaturalLanguageToPseudocodeAgent,
)
from app.external_services.KnowledgeBase.AlgorithmKnowledgeBase import (
    AlgorithmKnowledgeBase,
)


class ControlInput:

    @staticmethod
    def parse_pseudocode(pseudocode: str):
        try:
            tree = parser.parse(pseudocode)
            transformer = TreeToDict()
            result = transformer.transform(tree)
            return result
        except UnexpectedInput as e:
            return {"error": f"Error al parsear el pseudocódigo: {str(e)}"}

    @staticmethod
    def process_input(input_text: str, is_natural_language: bool = False):
        """
        Procesa la entrada usando estrategia RAG (Retrieval-Augmented Generation).
        """
        final_pseudocode = input_text
        source_origin = "strict_code"

        if is_natural_language:
            print(
                f"\n🤖 [ControlInput] Procesando lenguaje natural: '{input_text[:30]}...'"
            )

            kb = AlgorithmKnowledgeBase()

            stored_code = kb.search_algorithm(input_text, threshold=0.7)

            if stored_code:

                final_pseudocode = stored_code
                source_origin = "rag_retrieval (ChromaDB)"
                print("✅ [ControlInput] Código recuperado de la Base de Conocimiento.")

            else:

                print(
                    "🤷 [ControlInput] No encontrado en BD. Invocando Agente Traductor (LLM)..."
                )
                translator = NaturalLanguageToPseudocodeAgent(
                    model_type="Gemini_Rapido"
                )
                translation = translator.translate(input_text)

                if not translation.was_successful:
                    return {
                        "error": "No se pudo traducir la descripción.",
                        "details": translation.error_message,
                    }

                final_pseudocode = translation.pseudocode
                source_origin = "llm_translation"
                print("✅ [ControlInput] Traducción por IA exitosa.")

        parse_result = parse_pseudocode(final_pseudocode)

        if isinstance(parse_result, dict) and "error" in parse_result:
            return {
                "error": "Error de sintaxis en el código procesado.",
                "details": parse_result["error"],
                "generated_code": final_pseudocode if is_natural_language else None,
            }

        return {
            "ast": parse_result,
            "pseudocode": final_pseudocode,
            "source_type": source_origin,
        }

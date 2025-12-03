# app/controllers/control_input.py

from app.parsers.parser import parse_pseudocode
from app.external_services.Agentes.NaturalLanguageToPseudocodeAgent import NaturalLanguageToPseudocodeAgent
from app.external_services.KnowledgeBase.AlgorithmKnowledgeBase import AlgorithmKnowledgeBase # <--- NUEVO

class ControlInput:
    
    @staticmethod
    def process_input(input_text: str, is_natural_language: bool = False):
        """
        Procesa la entrada usando estrategia RAG (Retrieval-Augmented Generation).
        """
        final_pseudocode = input_text
        source_origin = "strict_code" # strict_code, rag_retrieval, llm_translation

        # 🚀 RAMA LENGUAJE NATURAL
        if is_natural_language:
            print(f"\n🤖 [ControlInput] Procesando lenguaje natural: '{input_text[:30]}...'")
            
            # --- 1. INTENTO DE RECUPERACIÓN (RAG) ---
            kb = AlgorithmKnowledgeBase()
            # Threshold ajustable: 0.3-0.4 suele ser seguro para 'all-MiniLM-L6-v2'
            stored_code = kb.search_algorithm(input_text, threshold=0.7)
            
            if stored_code:
                # ¡ÉXITO! Encontramos el algoritmo perfecto en la BD
                final_pseudocode = stored_code
                source_origin = "rag_retrieval (ChromaDB)"
                print("✅ [ControlInput] Código recuperado de la Base de Conocimiento.")
            
            else:
                # --- 2. INTENTO DE GENERACIÓN (LLM) ---
                print("🤷 [ControlInput] No encontrado en BD. Invocando Agente Traductor (LLM)...")
                translator = NaturalLanguageToPseudocodeAgent(model_type="Gemini_Rapido")
                translation = translator.translate(input_text)
                
                if not translation.was_successful:
                    return {
                        "error": "No se pudo traducir la descripción.",
                        "details": translation.error_message
                    }
                
                final_pseudocode = translation.pseudocode
                source_origin = "llm_translation"
                print("✅ [ControlInput] Traducción por IA exitosa.")

        # 🚀 VALIDACIÓN SINTÁCTICA (Para todos los orígenes)
        parse_result = parse_pseudocode(final_pseudocode)
        
        if isinstance(parse_result, dict) and "error" in parse_result:
            return {
                "error": "Error de sintaxis en el código procesado.",
                "details": parse_result["error"],
                "generated_code": final_pseudocode if is_natural_language else None
            }

        return {
            "ast": parse_result,
            "pseudocode": final_pseudocode,
            "source_type": source_origin
        }
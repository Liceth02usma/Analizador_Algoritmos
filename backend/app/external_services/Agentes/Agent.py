from abc import abstractmethod, ABC
from .LLM_Factory import LLM_Factory
from langchain.agents import create_agent
from typing import List, Dict, Any, Optional, TypeVar, Generic
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class AgentBase(ABC, Generic[T]):
    """
    Clase base para agentes con LangChain.

    Cambios principales respecto a la versión anterior:
    - __init__ acepta **factory_options opcionales que se pasan a LLM_Factory.
      Ejemplos: fallback=True, provider="gemini", override={...}
    - Mantiene compatibilidad: si no se pasan factory_options, se comporta exactamente igual.
    """

    def __init__(self, model_type: str, **factory_options):
        """
        Args:
            model_type: Perfil lógico (ej. "Modelo_Razonamiento") que LLM_Factory usará como `profile`.
            **factory_options: Opciones opcionales para LLM_Factory:
                - fallback=True (intenta gemini -> openai)
                - provider="gemini" | "openai"
                - override={...} (mapa con keys como model_name, temperature, max_tokens)
        """

        # Crear la fábrica pasándole el profile y cualquier opción adicional
        # (esto mantiene compatibilidad con llamadas previas que sólo pasan model_type).
        factory = LLM_Factory(profile=model_type, **factory_options)

        # Guardar el model_type para uso en subclases
        self.model_type = model_type
        # Exponer .model (legacy) como antes
        self.model = factory.model

        # Checkpointer para agentes que usen checkpointing
        self.checkpointer = InMemorySaver()

        # Inicializar atributos que serán configurados por subclases
        self.tools: List[Any] = []
        self.context_schema: Optional[type[BaseModel]] = None
        self.response_format: Optional[type[T]] = None
        self.SYSTEM_PROMPT: str = ""

        # Hook para que la subclase configure prompt, tools y schemas
        self._configure()

        # Crear el agente concreto (create_agent de langchain)
        self.agent = self._create_agent()

    @abstractmethod
    def _configure(self) -> None:
        """
        Configura el agente (SYSTEM_PROMPT, tools, schemas).
        DEBE ser implementado por subclases.
        """
        pass

    def _create_agent(self):
        """Crea el agente con la configuración establecida."""
        return create_agent(
            model=self.model,
            system_prompt=self.SYSTEM_PROMPT,
            tools=self.tools,
            context_schema=self.context_schema,
            response_format=self.response_format,
            checkpointer=self.checkpointer,
        )

    def invoke(
        self,
        messages: List[Dict[str, str]],
        config: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Invoca el agente de forma flexible.

        Args:
            messages: Lista de mensajes (formato LangChain)
            config: Configuración (ej: thread_id)
            context: Contexto adicional opcional

        Returns:
            Respuesta del agente
        """
        invoke_params = {
            "messages": messages,
        }

        if context:
            result = self.agent.invoke(invoke_params, config=config, context=context)
        else:
            result = self.agent.invoke(invoke_params, config=config)
        
        # 📊 LOG DE TOKENS
        self._log_token_usage(result)
        
        return result
    
    def _log_token_usage(self, result: Dict[str, Any]):
        """Extrae e imprime información de tokens de la respuesta."""
        try:
            if not isinstance(result, dict) or "messages" not in result:
                return
            
            messages = result.get("messages", [])
            if not isinstance(messages, list) or len(messages) < 2:
                return
            
            # El AIMessage con tokens está típicamente en messages[-2]
            # (antes del ToolMessage final)
            ai_message = None
            for msg in reversed(messages):
                if hasattr(msg, "usage_metadata") and msg.usage_metadata:
                    ai_message = msg
                    break
            
            if not ai_message:
                return
            
            usage = ai_message.usage_metadata
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            total_tokens = input_tokens + output_tokens
            
            print(f"\n📊 [TOKENS] {self.__class__.__name__}:")
            print(f"   ├─ Input:  {input_tokens:,} tokens")
            print(f"   ├─ Output: {output_tokens:,} tokens")
            print(f"   └─ Total:  {total_tokens:,} tokens")
        
        except Exception as e:
            # Fallar silenciosamente si hay problemas
            print(f"⚠️ Error al extraer uso de tokens: {e}")

    def invoke_simple(
        self,
        content: str,
        thread_id: str = "default",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Método de conveniencia para invocaciones simples de un solo mensaje.
        """
        messages = [{"role": "user", "content": content}]
        config = {"configurable": {"thread_id": thread_id}}
        return self.invoke(messages, config, context)

    def extract_response(self, result: Dict[str, Any] | Any) -> Optional[T]:
            content = ""

            # CASO 1: El resultado es directamente un AIMessage (común en invoke simple)
            if hasattr(result, 'content'):
                content = result.content

            # CASO 2: Resultado de un Agente (Dict con keys "output", "messages", etc)
            elif isinstance(result, dict):
                # Si LangChain ya parseó la estructura (structured_response)
                if "structured_response" in result and isinstance(result["structured_response"], self.response_format):
                    return result["structured_response"]
                
                # Buscar el último mensaje del historial
                if "messages" in result and isinstance(result["messages"], list) and result["messages"]:
                    last_msg = result["messages"][-1]
                    content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
                
                # Buscar output directo
                elif "output" in result:
                    content = result["output"]
                
                # Buscar content en dict simple
                elif "content" in result:
                    content = result["content"]

            if not content:
                return None

            # CASO 3: Parsing manual del JSON (Texto a Pydantic)
            import json
            import re
            
            try:
                text = str(content).strip()
                # Limpieza defensiva extra por si quedaron backticks
                if "```" in text:
                    text = re.sub(r"```[a-zA-Z]*", "", text).replace("```", "").strip()

                # Intentar parsear
                data = json.loads(text)
                return self.response_format.model_validate(data)

            except json.JSONDecodeError:
                # Fallback: Intentar encontrar el JSON dentro del texto
                try:
                    start = text.find('{')
                    end = text.rfind('}')
                    if start != -1 and end != -1:
                        json_str = text[start:end+1]
                        data = json.loads(json_str)
                        return self.response_format.model_validate(data)
                except:
                    pass
                print(f"⚠️ No se pudo parsear JSON del contenido: {text[:50]}...")
                return None
            except Exception as e:
                print(f"⚠️ Error validando modelo Pydantic: {e}")
                return None
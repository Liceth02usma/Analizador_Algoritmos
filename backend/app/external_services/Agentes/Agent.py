from abc import abstractmethod, ABC
from .LLM_Factory import LLM_Factory
from langchain.agents import create_agent
from typing import List, Dict, Any, Optional
from langgraph.checkpoint.memory import InMemorySaver
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class AgentBase(ABC, Generic[T]):
    """
    Clase base para agentes con LangChain.
    
    Responsabilidades:
    - Gestionar el ciclo de vida del agente
    - Proporcionar utilidades comunes
    - Estandarizar la configuración
    """
    
    def __init__(self, model_type: str):
        factory = LLM_Factory(model_type)
        self.model = factory.model
        self.checkpointer = InMemorySaver()
        
        # Inicializar atributos que serán configurados
        self.tools: List[Any] = []
        self.context_schema: Optional[type[BaseModel]] = None
        self.response_format: Optional[type[T]] = None
        self.SYSTEM_PROMPT: str = ""
        
        # Configurar y crear
        self._configure()
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
            return self.agent.invoke(invoke_params, config=config, context=context)
        return self.agent.invoke(invoke_params, config=config)
    
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
    
    def extract_response(self, result: Dict[str, Any]) -> Optional[T]:
        """
        Extrae la respuesta estructurada del resultado.
        
        Returns:
            Instancia del response_format o None
        """
        if "structured_response" in result and isinstance(
            result["structured_response"], self.response_format
        ):
            return result["structured_response"]
        return None
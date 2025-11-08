from abc import abstractmethod, ABC
from .LLM_Factory import LLM_Factory
from langchain.agents import create_agent
from typing import List, Dict, Any, Optional
from langgraph.checkpoint.memory import InMemorySaver


class AgentBase(ABC):

    def __init__(self, model_type):
        factory = LLM_Factory(model_type)
        self.model = factory.model
        
        self.checkpointer = InMemorySaver()
        self.tools: List = []
        self.context_schema: Optional[Any] = None
        self.response_format: Optional[Any] = None
        self.SYSTEM_PROMPT = ""
        
        self._configure()
        self.agent = self._create_agent()

    @abstractmethod
    def _configure(self):
        """
        Configura el agente específico (SYSTEM_PROMPT, tools, etc.)
        Debe ser implementado por las subclases
        """
        pass

    @abstractmethod
    def invoke_agent(self):
        pass

    @abstractmethod
    def execute_agent(self):
        pass

    def _create_agent(self):
        return create_agent(
            model=self.model,
            system_prompt=self.SYSTEM_PROMPT,
            # El orden de las herramientas no es crucial, pero las listamos
            tools=self.tools,
            context_schema=self.context_schema,
            response_format=self.response_format,
            checkpointer=self.checkpointer,
        )
    
    def _invoke_agent(self,content, config, context_data):
        return self.agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{content}"
                        }
                    ]
                },
                config=config,
                context=context_data
            )
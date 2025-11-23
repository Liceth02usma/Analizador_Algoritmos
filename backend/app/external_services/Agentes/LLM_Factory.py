from langchain_openai import ChatOpenAI
import os

class LLM_Factory:
    """Fábrica para crear instancias de modelos LLM optimizados para diferentes casos de uso"""
    
    MODEL_CONFIGS = {
        "Modelo_Razonamiento": {
            "model_name": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 2000,
            "description": "Modelo potente para razonamiento complejo y análisis profundo"
        },
        "Modelo_Rapido": {
            "model_name": "gpt-4o-mini",
            "temperature": 0.5,
            "max_tokens": 500,
            "description": "Modelo ligero y rápido para respuestas simples"
        },
        "Modelo_Creativo": {
            "model_name": "gpt-4o",
            "temperature": 0.9,
            "max_tokens": 1500,
            "description": "Alta temperatura para contenido creativo y original"
        },
        "Modelo_Preciso": {
            "model_name": "gpt-4o",
            "temperature": 0.1,
            "max_tokens": 1000,
            "description": "Baja temperatura para respuestas determinísticas y precisas"
        },
        "Modelo_Conversacional": {
            "model_name": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 800,
            "description": "Optimizado para diálogos naturales y chatbots"
        },
        "Modelo_Clasificacion": {
            "model_name": "gpt-4o-mini",
            "temperature": 0.2,
            "max_tokens": 100,
            "description": "Para tareas de clasificación y categorización"
        },
        "Modelo_Extraccion": {
            "model_name": "gpt-4o-mini",
            "temperature": 0.0,
            "max_tokens": 300,
            "description": "Extracción de información estructurada"
        },
        "Modelo_Resumen": {
            "model_name": "gpt-4o-mini",
            "temperature": 0.3,
            "max_tokens": 500,
            "description": "Para generar resúmenes concisos"
        },
        "Modelo_Traduccion": {
            "model_name": "gpt-4o",
            "temperature": 0.3,
            "max_tokens": 1000,
            "description": "Traducciones precisas y contextuales"
        },
        "Modelo_Codigo": {
            "model_name": "gpt-4o",
            "temperature": 0.2,
            "max_tokens": 2000,
            "description": "Generación y análisis de código"
        },
        "Modelo_Largo": {
            "model_name": "gpt-4o",
            "temperature": 0.6,
            "max_tokens": 4000,
            "description": "Para respuestas extensas y documentación"
        }
    }
    
    def __init__(self, model: str = "Modelo_Razonamiento"):
        self.model_type = model
        self.model = self._create_model()
    
    def _create_model(self):
        if self.model_type not in self.MODEL_CONFIGS:
            raise ValueError(
                f"Modelo '{self.model_type}' no soportado. "
                f"Modelos disponibles: {', '.join(self.MODEL_CONFIGS.keys())}"
            )
        
        config = self.MODEL_CONFIGS[self.model_type].copy()
        config.pop('description', None)
        
        
        return self._create_openai_model(**config)
    
    def _create_openai_model(
        self, 
        model_name: str,
        temperature: float = 0.7, 
        timeout: int = 30, 
        max_tokens: int = 1000
    ):
        """Crea una instancia de ChatOpenAI con la configuración especificada"""
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY no está configurada en las variables de entorno")
        
        config = {
            "model": model_name,
            "temperature": temperature,
            "timeout": timeout,
            "max_tokens": max_tokens,
            "api_key": api_key,
            "base_url": base_url
        }
        
        return ChatOpenAI(**config)
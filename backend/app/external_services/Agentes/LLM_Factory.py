"""
from langchain_openai import ChatOpenAI
import os

class LLM_Factory:
    Fábrica para crear instancias de modelos LLM optimizados para diferentes casos de uso
    
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
        Crea una instancia de ChatOpenAI con la configuración especificada
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
        }
        
        return ChatOpenAI(**config)

"""



# app/external_services/Agentes/LLM_Factory.py
import os
from typing import Any, Dict, List, Optional

# ------------------------------------------------------------------------
# 1. BLOQUE DE IMPORTACIONES DE LANGCHAIN
# ------------------------------------------------------------------------

# OpenAI
try:
    from langchain_openai import ChatOpenAI
    HAS_OPENAI = True
except ImportError:
    ChatOpenAI = None
    HAS_OPENAI = False

# Google Gemini (Librería Oficial)
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    HAS_GEMINI = True
except ImportError:
    ChatGoogleGenerativeAI = None
    HAS_GEMINI = False

# ----------------- FÁBRICA MULTI-PROVIDER -----------------
class LLM_Factory:
    """
    Multi-provider:
    - OpenAI (usa langchain_openai)
    - Gemini (usa langchain_google_genai)
    - Fallback automático Gemini -> OpenAI
    """

    DEFAULT_MODEL_CONFIGS = {
        "Modelo_Razonamiento": ("openai", "gpt-4o", 0.1, 2000),
        "Modelo_Rapido": ("openai", "gpt-4o-mini", 0.3, 600),
        "Modelo_Preciso": ("openai", "gpt-4o", 0.0, 1200),
        "Modelo_Extraccion": ("openai", "gpt-4o-mini", 0.0, 400),
        # Perfiles Gemini
        "Gemini_Rapido": ("gemini", "gemini-2.5-flash", 0.0, 8000),
        "Gemini_Largo": ("gemini", "gemini-2.5-pro", 0.1, 8000),
        "Gemini_Ultra": ("gemini", "gemini-2.0-flash-lite", 0.0, 8000),
    }

    def __init__(
        self,
        profile: str = "Modelo_Razonamiento",
        provider: Optional[str] = None,
        override: Optional[Dict[str, Any]] = None,
        fallback: bool = False
    ):
        self.profile = profile
        self.override = override or {}
        self.fallback = fallback

        # provider explícito, o el del perfil
        base_provider = self.DEFAULT_MODEL_CONFIGS.get(profile, ("openai",))[0]
        self.provider = provider or base_provider

        # Crear el cliente (con opción de fallback)
        if fallback:
            self._client = self._create_with_fallback(["gemini", "openai"])
        else:
            self._client = self._create_client()

        # Exponer el cliente como .model
        self.model = self._client

    def _create_with_fallback(self, providers_priority: List[str]):
        last_error = None
        for p in providers_priority:
            try:
                print(f"[LLM_Factory] Intentando proveedor: {p}")
                self.provider = p
                client = self._create_client()
                print(f"[LLM_Factory] → Éxito con {p}")
                return client
            except Exception as e:
                print(f"[LLM_Factory] Falló proveedor {p}: {e}")
                last_error = e
        raise RuntimeError(f"No se logró inicializar ningún proveedor LLM. Error final: {last_error}")

    def _create_client(self):
        if self.profile not in self.DEFAULT_MODEL_CONFIGS:
            raise ValueError(f"Perfil '{self.profile}' no válido.")

        base_provider, model_name, temperature, max_tokens = self.DEFAULT_MODEL_CONFIGS[self.profile]
        provider = self.provider or base_provider

        # Sobreescritura de configuración
        model_name = self.override.get("model_name", model_name)
        temperature = self.override.get("temperature", temperature)
        max_tokens = self.override.get("max_tokens", max_tokens)

        # -------------------- OPENAI --------------------
        if provider == "openai":
            if not HAS_OPENAI:
                raise ImportError("langchain_openai no instalado. pip install langchain-openai")

            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL")

            if not api_key:
                raise ValueError("OPENAI_API_KEY no encontrada")

            cfg = {
                "model": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "api_key": api_key,
            }
            if base_url:
                cfg["base_url"] = base_url

            return ChatOpenAI(**cfg)

        # -------------------- GEMINI (OFICIAL) --------------------
        if provider == "gemini":
            if not HAS_GEMINI:
                raise ImportError("langchain_google_genai no instalado. pip install langchain-google-genai")

            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY no encontrada")

            # Instanciamos la clase oficial de LangChain
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=temperature,
                max_output_tokens=max_tokens,
                # convert_system_message_to_human=True # A veces necesario en versiones viejas, pero la 1.5 ya soporta system nativo
            )

        raise ValueError(f"Provider desconocido: {provider}")

    def get_client(self):
        return self._client
    
    





# Backend - Analizador de Algoritmos

Sistema de análisis de complejidad de algoritmos con soporte para código en pseudocódigo. Detecta automáticamente si un algoritmo es iterativo o recursivo y calcula su complejidad temporal y espacial.

---






### Dependencias Principales
- **FastAPI**: Framework web
- **Lark**: Parser de pseudocódigo
- **Pydantic**: Validación de datos
- **pytest**: Testing
- **black**: Formateo de código

---

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/Liceth02usma/Analizador_Algoritmos.git
cd Analizador_Algoritmos/backend
```

### 2. Crear entorno virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## 🚀 Uso Rápido

### Iniciar el servidor
```bash
uvicorn app.main:app --reload
```

python backend/app/external_services/Agentes/AlgorithmClassifierAgent.py

El servidor estará disponible en:
- **API**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc



## 🛣️ API Endpoints

### Documentación Interactiva
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Endpoints Principales

#### `/api/analysis/analyze` (POST)
Analiza un algoritmo y devuelve su complejidad.

**Request:**
```json
{
  "name": "BubbleSort",
  "code": "for i 🡨 0 to n do...",
}
```

**Response:**
```json
{
  "algorithm": {...},
  "complexity": {
    "time": {"worst_case": "O(n²)"},
    "space": {"worst_case": "O(1)"}
  },
  "pattern": {...},
  "optimizations": [...]
}
```

#### `/api/iterative/analyze` (POST)
Análisis específico para algoritmos iterativos.

#### `/api/recursive/analyze` (POST)
Análisis específico para algoritmos recursivos.

---

## 🎨 Formato de Código

### Formatear código con Black
```bash
# Verificar formato
black --check .

# Aplicar formato
black .
```

### Verificar estilo con flake8
```bash
flake8 app/ tests/
```

---

## 🔄 Generación de Requirements

Para actualizar las dependencias:

```bash
  pip freeze > requirements.txt
```

---


# tasks

# Solucionar el analisis de ambos modelos y hacer que se guarde por cache




# Hacer que se muestre tanto el arbol como el flujo 
# Mejorar el agente para identificar si tiene caso promedio, mejor peor etc
# Crear un agente para detectar recurrencia indirecta
# Solucionar el LLM del output para que tome como herramienta Lark para validar


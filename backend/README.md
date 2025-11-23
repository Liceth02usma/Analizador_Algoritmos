

# 🚀 Backend - Analizador de Algoritmos

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

El servidor estará disponible en:
- **API**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Ejemplo básico (Python)

#### Algoritmo Iterativo
```python
from app.controllers.controller_iterative import ControlIterative

controller = ControlIterative()

pseudocodigo = """
for i 🡨 0 to n do
begin
    suma 🡨 suma + array[i]
end
"""

results = controller.analyze_from_parsed_tree(
    "SumaArray",
    pseudocodigo
)

print(f"Complejidad: {results['complexity']['time']['worst_case']}")
# Output: O(n)
```

#### Algoritmo Recursivo
```python
from app.controllers.controller_recursive import ControlRecursive

controller = ControlRecursive()

pseudocodigo = """
FUNCTION factorial(n)
begin
    if (n <= 1) then return 1
    else return n * CALL factorial(n - 1)
end
"""

results = controller.analyze_from_parsed_tree(
    "Factorial",
    pseudocodigo
)

print(f"Complejidad: {results['complexity']['time']['worst_case']}")
# Output: O(n)

print(f"Relación: {results['analysis']['recurrence_relation']}")
# Output: T(n) = T(n-1) + O(1)
```

---


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
  "language": "pseudocode"
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



# 🚀 Backend - Analizador de Algoritmos

Sistema de análisis de complejidad de algoritmos con soporte para código en pseudocódigo. Detecta automáticamente si un algoritmo es iterativo o recursivo y calcula su complejidad temporal y espacial.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Uso Rápido](#-uso-rápido)
- [Controladores](#-controladores)
- [Ejemplos](#-ejemplos)
- [Tests](#-tests)
- [Documentación](#-documentación)
- [API Endpoints](#-api-endpoints)

---

## ✨ Características

### 🔍 Análisis de Algoritmos
- ✅ **Detección automática** de tipo (iterativo/recursivo)
- ✅ **Análisis de complejidad** temporal y espacial
- ✅ **Notaciones asintóticas** (O, Ω, Θ)
- ✅ **Detección de patrones** algorítmicos conocidos
- ✅ **Sugerencias de optimización** automáticas

### 📊 Algoritmos Iterativos
- Detección de ciclos (for, while, repeat)
- Análisis de niveles de anidamiento
- Cálculo de complejidad por estructura
- Identificación de patrones (lineal, cuadrático, etc.)

### 🔄 Algoritmos Recursivos
- Extracción de relaciones de recurrencia
- Detección de casos base
- Resolución con múltiples métodos:
  - Método de sustitución
  - Teorema maestro
  - Método del árbol de recursión
- Construcción de árboles de recursión

### 📈 Visualizaciones
- Diagramas de flujo (Mermaid, texto)
- Árboles de recursión
- Reportes en múltiples formatos (JSON, Markdown, texto)

### 🎯 Patrones Detectados
- **Iterativos:** Búsqueda lineal, ordenamiento burbuja, matrices
- **Recursivos:** Divide y conquista, Fibonacci, backtracking
- **Complejidades:** O(1), O(log n), O(n), O(n log n), O(n²), O(2^n)

---

## 🏗️ Arquitectura

```
backend/
├── app/
│   ├── controllers/          # 🎮 Lógica de control
│   │   ├── controller_iterative.py   # Análisis iterativo
│   │   └── controller_recursive.py   # Análisis recursivo
│   │
│   ├── models/              # 📦 Modelos de dominio
│   │   ├── algorithm.py            # Clase base abstracta
│   │   ├── iterative.py            # Algoritmos iterativos
│   │   ├── recursive.py            # Algoritmos recursivos
│   │   ├── complexity.py           # Cálculo de complejidad
│   │   ├── tree.py                 # Árboles de recursión
│   │   ├── recurrence_method.py    # Resolución de recurrencias
│   │   ├── algorithm_pattern.py    # Detección de patrones
│   │   └── flowdiagram.py          # Diagramas de flujo
│   │
│   ├── parsers/             # 🔧 Parser de pseudocódigo
│   │   ├── parser.py               # Parser Lark
│   │   └── pseudocode.lark         # Gramática
│   │
│   ├── routers/             # 🛣️ Endpoints API
│   ├── schemas/             # 📝 Schemas Pydantic
│   ├── crud/                # 💾 Operaciones BD
│   └── utils/               # 🛠️ Utilidades
│
├── tests/                   # 🧪 Tests unitarios
├── ejemplo_controller_iterative.py   # 📖 Ejemplos iterativos
├── ejemplo_controller_recursive.py   # 📖 Ejemplos recursivos
└── requirements.txt         # 📦 Dependencias
```

---

## 📋 Requisitos Previos

- [Python 3.10+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/)
- [Uvicorn](https://www.uvicorn.org/) (servidor ASGI)

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

## 🎮 Controladores

### ControlIterative
Analiza algoritmos con ciclos (for, while, repeat).

**Características:**
- Detección de bucles y anidamiento
- Cálculo de complejidad por niveles
- Identificación de patrones iterativos

**Documentación:** [`CONTROLLER_ITERATIVE_DOCUMENTACION.md`](./CONTROLLER_ITERATIVE_DOCUMENTACION.md)

### ControlRecursive
Analiza algoritmos con llamadas recursivas.

**Características:**
- Extracción de relaciones de recurrencia
- Detección de casos base
- Resolución con Teorema Maestro
- Construcción de árboles de recursión

**Documentación:** [`CONTROLLER_RECURSIVE_DOCUMENTACION.md`](./CONTROLLER_RECURSIVE_DOCUMENTACION.md)

### Comparación
Ver [`COMPARACION_CONTROLADORES.md`](./COMPARACION_CONTROLADORES.md) para una comparación detallada.

---

## 📖 Ejemplos

### Ejecutar ejemplos completos

#### Algoritmos Iterativos (10 ejemplos)
```bash
python ejemplo_controller_iterative.py
```

Incluye:
1. Suma simple de array
2. Uso con parser explícito
3. Ordenamiento burbuja
4. Exportación de reportes (texto/JSON/Markdown)
5. Generación de diagramas de flujo
6. Ciclos anidados complejos (3 niveles)
7. Diferentes tipos de ciclos (while, repeat)
8. Detección de patrones
9. Y más...

#### Algoritmos Recursivos (10 ejemplos)
```bash
python ejemplo_controller_recursive.py
```

Incluye:
1. Factorial recursivo
2. Fibonacci (con sugerencias de optimización)
3. Búsqueda binaria
4. MergeSort
5. Torres de Hanoi
6. QuickSort
7. Exportación de reportes
8. Comparación de complejidades
9. Y más...

---

## 🧪 Tests

### Ejecutar todos los tests
```bash
pytest tests/ -v
```

### Tests por controlador
```bash
# Tests de ControlIterative
pytest tests/test_controller_iterative.py -v

# Tests de ControlRecursive
pytest tests/test_controller_recursive.py -v

# Test específico
pytest tests/test_controller_iterative.py::TestControlIterative::test_analisis_ciclo_simple -v
```

### Cobertura de tests
```bash
pytest --cov=app tests/
```

### Tests rápidos (sin verbose)
```bash
pytest -q
```

---

## 📚 Documentación

### Documentos Principales

1. **[MODELOS_DOCUMENTACION.md](./MODELOS_DOCUMENTACION.md)**
   - Documentación completa de todos los modelos
   - Clases: Algorithm, Iterative, Recursive, Complexity, etc.

2. **[RESUMEN_IMPLEMENTACION.md](./RESUMEN_IMPLEMENTACION.md)**
   - Resumen de la implementación del sistema
   - Arquitectura y decisiones de diseño

3. **[CONTROLLER_ITERATIVE_DOCUMENTACION.md](./CONTROLLER_ITERATIVE_DOCUMENTACION.md)**
   - Guía completa del controlador iterativo
   - Ejemplos y casos de uso

4. **[CONTROLLER_RECURSIVE_DOCUMENTACION.md](./CONTROLLER_RECURSIVE_DOCUMENTACION.md)**
   - Guía completa del controlador recursivo
   - Métodos de resolución de recurrencias

5. **[COMPARACION_CONTROLADORES.md](./COMPARACION_CONTROLADORES.md)**
   - Comparación detallada entre controladores
   - Cuándo usar cada uno

### Gramática del Pseudocódigo

Ver [`app/parsers/pseudocode.lark`](./app/parsers/pseudocode.lark) para la gramática completa.

**Características:**
- Asignación: `🡨` o `:=`
- Comentarios: `►` o `//`
- Ciclos: `for`, `while`, `repeat-until`
- Condicionales: `if-then-else`
- Llamadas: `CALL function(args)`
- Bloques: `begin...end`

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

## 📊 Ejemplos de Complejidades

| Algoritmo | Tipo | Complejidad | Patrón |
|-----------|------|-------------|---------|
| Suma de array | Iterativo | O(n) | Lineal |
| Búsqueda lineal | Iterativo | O(n) | Lineal |
| Ordenamiento burbuja | Iterativo | O(n²) | Cuadrático |
| Multiplicación matrices | Iterativo | O(n³) | Cúbico |
| Factorial | Recursivo | O(n) | Lineal |
| Fibonacci | Recursivo | O(2^n) | Exponencial |
| Búsqueda binaria | Recursivo | O(log n) | Logarítmico |
| MergeSort | Recursivo | O(n log n) | Divide y Conquista |
| QuickSort | Recursivo | O(n log n) | Divide y Conquista |
| Torres de Hanoi | Recursivo | O(2^n) | Exponencial |

---

## 🚦 Estado del Proyecto

### ✅ Completado
- [x] Modelos de dominio (8 clases)
- [x] Parser de pseudocódigo (Lark)
- [x] ControlIterative completo
- [x] ControlRecursive completo
- [x] Tests unitarios
- [x] Documentación completa
- [x] Ejemplos de uso

### 🔜 En Desarrollo
- [ ] ControlAnalysis (orquestador)
- [ ] ControlInput (preprocesamiento)
- [ ] ControlSolution (reportes finales)
- [ ] ControlClasification + ModeLLM (IA)
- [ ] Endpoints REST completos
- [ ] Frontend web

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto es parte del curso de Análisis de Algoritmos.

---

## 👥 Autores

- **Liceth Usma** - [GitHub](https://github.com/Liceth02usma)

---

## 📞 Contacto

- **Repository**: https://github.com/Liceth02usma/Analizador_Algoritmos
- **Branch actual**: `feature/s1-t7-test-parser`

---

## 🎓 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Lark Parser](https://lark-parser.readthedocs.io/)
- [Introduction to Algorithms (CLRS)](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Teorema Maestro](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))

---

**Última actualización:** Octubre 2025
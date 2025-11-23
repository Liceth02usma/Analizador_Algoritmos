

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


# Tareas Pendientes
# 1. Crear el agente que saque el costo por linea de un algoritmo recursivo, que lo haga para mejor, peor y promedio o para un caso unico si es que no varian.


# 2.1 arreglar el agente que saque correctamente la ecuacion del caso promedio




# 2. Ajustar el solution para que acepte que complexxity line to line tenga 3 pseudocodigos diferentes (mejor, peor, promedio) si se  da el caso


# 3. Ajustar el front end para se pueda realizar el cambio de manejar 3 pseudocodigos diferentes en complexity line to line y se pueda ver cuando cambia de pestaña
# 4. Verificar que el front end distinga cuando solution va con mejor, peor y promedio y lo muestre correctamente y cuando no que tambien se adapte




# Vamos a pedirle mejor, peor y promedio a todos los algoritmos y los que se comporten igual le ponemos la misma ecuacion de recurrencia y la misma solucion



complexity_line_to_line = [
    {
        "case_type": "best_case",
        "pseudocode_annotated": "quicksort(arr, low, high)\nbegin\n    if (low < high) then                      // O(1) - Comparación\n        pivot = partition(arr, low, high)     // O(n) - Mejor caso: pivote balanceado\n        quicksort(arr, low, pivot - 1)        // T(n/2) - Mitad izquierda\n        quicksort(arr, pivot + 1, high)       // T(n/2) - Mitad derecha\nend",
        "code_explanation": "QuickSort con pivote óptimo (elemento medio)",
        "complexity_explanation": "Mejor caso: el pivote divide el array en dos mitades iguales en cada recursión",
        "total_complexity": "O(n log n)"
    },
    {
        "case_type": "worst_case",
        "pseudocode_annotated": "quicksort(arr, low, high)\nbegin\n    if (low < high) then                      // O(1) - Comparación\n        pivot = partition(arr, low, high)     // O(n) - Peor caso: pivote desbalanceado\n        quicksort(arr, low, pivot - 1)        // T(n-1) - Subarray casi completo\n        quicksort(arr, pivot + 1, high)       // T(0) - Subarray vacío\nend",
        "code_explanation": "QuickSort con pivote pésimo (elemento extremo)",
        "complexity_explanation": "Peor caso: el pivote es siempre el menor o mayor elemento, generando particiones desbalanceadas",
        "total_complexity": "O(n²)"
    },
    {
        "case_type": "average_case",
        "pseudocode_annotated": "quicksort(arr, low, high)\nbegin\n    if (low < high) then                      // O(1) - Comparación\n        pivot = partition(arr, low, high)     // O(n) - Partición típica\n        quicksort(arr, low, pivot - 1)        // T(~n/2) - Subarray variable\n        quicksort(arr, pivot + 1, high)       // T(~n/2) - Subarray variable\nend",
        "code_explanation": "QuickSort con pivotes aleatorios",
        "complexity_explanation": "Caso promedio: las particiones son razonablemente balanceadas en la mayoría de las recursiones",
        "total_complexity": "O(n log n)"
    }
]

complexity_line_to_line = "busqueda_binaria(arr, objetivo, inicio, fin)\nbegin\n    if (inicio > fin) then                    // O(1) - Comparación\n        return -1                              // O(1) - Retorno\n    medio = (inicio + fin) / 2                // O(1) - Cálculo\n    if (arr[medio] = objetivo) then           // O(1) - Comparación\n        return medio                           // O(1) - Retorno\n    else if (arr[medio] > objetivo) then      // O(1) - Comparación\n        return busqueda_binaria(arr, objetivo, inicio, medio - 1)  // T(n/2)\n    else\n        return busqueda_binaria(arr, objetivo, medio + 1, fin)     // T(n/2)\nend"


{
  "type": "Recursivo",
  "code_explain": "Este algoritmo implementa la búsqueda binaria recursiva. Divide el array en mitades y busca el elemento objetivo en la mitad correspondiente. El caso base ocurre cuando el elemento es encontrado o el subarreglo está vacío.",
  complexity_line_to_line = [
    {
        "case_type": "best_case",
        "pseudocode_annotated": "quicksort(arr, low, high)\nbegin\n    if (low < high) then                      // O(1) - Comparación\n        pivot = partition(arr, low, high)     // O(n) - Mejor caso: pivote balanceado\n        quicksort(arr, low, pivot - 1)        // T(n/2) - Mitad izquierda\n        quicksort(arr, pivot + 1, high)       // T(n/2) - Mitad derecha\nend",
        "code_explanation": "QuickSort con pivote óptimo (elemento medio)",
        "complexity_explanation": "Mejor caso: el pivote divide el array en dos mitades iguales en cada recursión",
        "total_complexity": "O(n log n)"
    },
    {
        "case_type": "worst_case",
        "pseudocode_annotated": "quicksort(arr, low, high)\nbegin\n    if (low < high) then                      // O(1) - Comparación\n        pivot = partition(arr, low, high)     // O(n) - Peor caso: pivote desbalanceado\n        quicksort(arr, low, pivot - 1)        // T(n-1) - Subarray casi completo\n        quicksort(arr, pivot + 1, high)       // T(0) - Subarray vacío\nend",
        "code_explanation": "QuickSort con pivote pésimo (elemento extremo)",
        "complexity_explanation": "Peor caso: el pivote es siempre el menor o mayor elemento, generando particiones desbalanceadas",
        "total_complexity": "O(n²)"
    },
    {
        "case_type": "average_case",
        "pseudocode_annotated": "quicksort(arr, low, high)\nbegin\n    if (low < high) then                      // O(1) - Comparación\n        pivot = partition(arr, low, high)     // O(n) - Partición típica\n        quicksort(arr, low, pivot - 1)        // T(~n/2) - Subarray variable\n        quicksort(arr, pivot + 1, high)       // T(~n/2) - Subarray variable\nend",
        "code_explanation": "QuickSort con pivotes aleatorios",
        "complexity_explanation": "Caso promedio: las particiones son razonablemente balanceadas en la mayoría de las recursiones",
        "total_complexity": "O(n log n)"
    }
]
  "explain_complexity": "La complejidad del algoritmo es logarítmica O(log n) porque divide el problema a la mitad en cada llamada recursiva.",
  "equation": [
    "T(n) = T(n/2) + 1, T(1) = 1",
    "T(n) = T(n/2) + 1, T(1) = 1",
    "T(n) = T(n/2) + 1, T(1) = 1"
  ],
  "method_solution": [
    "Teorema Maestro",
    "Teorema Maestro",
    "Teorema Maestro"
  ],
  "solution_equation": [
    "O(log n)",
    "O(log n)",
    "O(log n)"
  ],
  "explain_solution_steps": [
    {
      "case_type": "best_case",
      "equation": "T(n) = T(n/2) + 1, T(1) = 1",
      "method": "Teorema Maestro",
      "method_enum": "master_theorem",
      "complexity": "O(log n)",
      "steps": [
        "**Paso 1 - Identificar parámetros:**",
        "   a = 1 (un subproblema)",
        "   b = 2 (tamaño dividido por 2)",
        "   f(n) = 1 (trabajo constante)",
        "",
        "**Paso 2 - Calcular n^(log_b(a)):**",
        "   n^(log_2(1)) = n^0 = 1",
        "",
        "**Paso 3 - Comparar f(n) con n^(log_b(a)):**",
        "   f(n) = 1 = Θ(n^0)",
        "   Caso 2 del Teorema Maestro",
        "",
        "**Paso 4 - Aplicar fórmula:**",
        "   T(n) = Θ(n^0 * log n) = Θ(log n)",
        "",
        "**Paso 5 - Complejidad final:**",
        "   O(log n)"
      ],
      "explanation": "Aplicando el Teorema Maestro: a=1, b=2, f(n)=1. Como f(n) = Θ(n^(log_b(a))), estamos en el Caso 2. Por lo tanto, T(n) = Θ(n^(log_b(a)) * log n) = Θ(log n).",
      "details": {
        "a": 1,
        "b": 2,
        "f_n": "1",
        "case": 2,
        "n_logb_a": "n^0 = 1"
      },
      "classification_confidence": 0.95,
      "classification_reasoning": "Recurrencia de división clásica con trabajo constante por nivel."
    },
    {
      "case_type": "worst_case",
      "equation": "T(n) = T(n/2) + 1, T(1) = 1",
      "method": "Teorema Maestro",
      "method_enum": "master_theorem",
      "complexity": "O(log n)",
      "steps": [
        "**Paso 1 - Identificar parámetros:**",
        "   a = 1, b = 2, f(n) = 1",
        "",
        "**Paso 2 - Aplicar Teorema Maestro Caso 2:**",
        "   T(n) = Θ(log n)",
        "",
        "**Paso 3 - Complejidad final:**",
        "   O(log n)"
      ],
      "explanation": "Mismo análisis que el mejor caso, la búsqueda binaria siempre divide a la mitad.",
      "details": {
        "a": 1,
        "b": 2,
        "f_n": "1",
        "case": 2
      },
      "classification_confidence": 0.95,
      "classification_reasoning": "Patrón de división constante independiente del caso."
    },
    {
      "case_type": "average_case",
      "equation": "T(n) = T(n/2) + 1, T(1) = 1",
      "method": "Teorema Maestro",
      "method_enum": "master_theorem",
      "complexity": "O(log n)",
      "steps": [
        "**Paso 1 - Teorema Maestro:**",
        "   a=1, b=2, f(n)=1",
        "   Caso 2: T(n) = Θ(log n)"
      ],
      "explanation": "El caso promedio también es O(log n) por la naturaleza determinística de la división.",
      "details": {
        "a": 1,
        "b": 2,
        "f_n": "1"
      },
      "classification_confidence": 0.95,
      "classification_reasoning": "Mismo patrón para todos los casos."
    }
  ],
  "diagrams": {
    "recursion_trees": {
      "has_multiple_cases": true,
      "trees": [
        {
          "case_type": "best_case",
          "recurrence_equation": "T(n) = T(n/2) + 1",
          "tree_structure": [
            {
              "level": 0,
              "position": 0,
              "label": "T(n)",
              "children_count": 1
            },
            {
              "level": 1,
              "position": 0,
              "label": "T(n/2)",
              "children_count": 1
            },
            {
              "level": 2,
              "position": 0,
              "label": "T(n/4)",
              "children_count": 1
            },
            {
              "level": 3,
              "position": 0,
              "label": "T(n/8)",
              "children_count": 1
            },
            {
              "level": 4,
              "position": 0,
              "label": "T(1)",
              "children_count": 0
            }
          ],
          "tree_depth": "log n",
          "description": "Árbol lineal con división por 2 en cada nivel hasta llegar al caso base."
        },
        {
          "case_type": "worst_case",
          "recurrence_equation": "T(n) = T(n/2) + 1",
          "tree_structure": [
            {
              "level": 0,
              "position": 0,
              "label": "T(n)",
              "children_count": 1
            },
            {
              "level": 1,
              "position": 0,
              "label": "T(n/2)",
              "children_count": 1
            },
            {
              "level": 2,
              "position": 0,
              "label": "T(n/4)",
              "children_count": 1
            },
            {
              "level": 3,
              "position": 0,
              "label": "T(1)",
              "children_count": 0
            }
          ],
          "tree_depth": "log n",
          "description": "Mismo patrón que el mejor caso, búsqueda binaria siempre divide a la mitad."
        },
        {
          "case_type": "average_case",
          "recurrence_equation": "T(n) = T(n/2) + 1",
          "tree_structure": [
            {
              "level": 0,
              "position": 0,
              "label": "T(n)",
              "children_count": 1
            },
            {
              "level": 1,
              "position": 0,
              "label": "T(n/2)",
              "children_count": 1
            },
            {
              "level": 2,
              "position": 0,
              "label": "T(n/4)",
              "children_count": 1
            }
          ],
          "tree_depth": "log n",
          "description": "Árbol de división logarítmica estándar."
        }
      ],
      "summary": "Se generaron bosquejos de árboles de recursión para los tres casos de análisis."
    }
  },
  "extra": {
    "has_multiple_cases": true,
    "analysis_details": "Análisis completo de búsqueda binaria con tres casos",
    "algorithm_name": "Búsqueda Binaria Recursiva",
    "space_complexity": "O(log n) por la pila de recursión"
  }
}
# Gramática para Pseudocódigo - Documentación Completa

## Resumen del Proyecto

Este proyecto implementa una gramática completa para pseudocódigo que soporta las estructuras de control básicas necesarias para el análisis de complejidad de algoritmos: FOR, WHILE e IF-ELSE.

## Características Implementadas

### ✅ Estructuras de Control Básicas
- **IF-ELSE**: Condicionales con sintaxis en español e inglés
- **WHILE**: Bucles con condición en español e inglés  
- **FOR**: Bucles con rango en español e inglés

### ✅ Declaraciones y Tipos de Datos
- Declaración de variables con tipos (ENTERO/int, REAL/float, etc.)
- Arrays unidimensionales y multidimensionales
- Declaraciones múltiples en una línea (`int i, j;`)
- Inicialización de variables

### ✅ Expresiones y Operadores
- Operadores aritméticos: `+`, `-`, `*`, `/`, `%`, `MOD`
- Operadores relacionales: `=`, `<>`, `!=`, `<`, `>`, `<=`, `>=`
- Operadores lógicos: `Y/AND`, `O/OR`, `NO/NOT`
- Operadores de asignación: `=`, `<-`

### ✅ Características Adicionales
- Acceso a arrays multidimensionales (`matrix[i][j]`)
- Llamadas a funciones con argumentos
- Literales (números, cadenas, booleanos)
- Comentarios con `#`
- Bloques con `INICIO/FIN` o `{}`

## Componentes del Sistema

### 1. Lexer (Analizador Léxico)
- **Archivo**: `src/lexer.py`
- **Función**: Convierte el código fuente en tokens
- **Características**:
  - Soporte bilingüe (español/inglés)
  - Manejo de comentarios
  - Tokenización de literales y operadores

### 2. Parser (Analizador Sintáctico)
- **Archivo**: `src/parser.py`  
- **Función**: Convierte tokens en Abstract Syntax Tree (AST)
- **Método**: Recursive Descent Parser
- **Características**:
  - Precedencia de operadores
  - Manejo de errores de sintaxis
  - Soporte para gramática bilingüe

### 3. AST (Abstract Syntax Tree)
- **Archivo**: `src/ast_nodes.py`
- **Función**: Representación en árbol del código parseado
- **Características**:
  - Patrón Visitor para recorrido del árbol
  - Nodos específicos para cada estructura
  - Impresión para debugging

## Sintaxis Soportada

### Declaraciones de Variables
```pseudocode
ENTERO x = 5;
REAL arr[100];
int matrix[10][10];
BOOLEANO flag = VERDADERO;
```

### Estructuras IF-ELSE
```pseudocode
# Español
SI x > 0 ENTONCES
    print("Positivo");
SINO
    print("No positivo");
FIN_SI

# Inglés
IF x > 0 THEN
    print("Positive");
ELSE
    print("Not positive");
END_IF
```

### Bucles WHILE
```pseudocode
# Español
MIENTRAS i < 10 HACER
    i = i + 1;
FIN_MIENTRAS

# Inglés
WHILE i < 10 DO
    i = i + 1;
END_WHILE
```

### Bucles FOR
```pseudocode
# Español
PARA i = 1 HASTA 10 HACER
    suma = suma + i;
FIN_PARA

PARA i = 1 HASTA 10 PASO 2 HACER
    print(i);
FIN_PARA

# Inglés
FOR i = 1 TO 10 DO
    sum = sum + i;
END_FOR

FOR i = 1 TO 10 STEP 2 DO
    print(i);
END_FOR
```

## Ejemplos de Uso

El sistema incluye ejemplos completos en la carpeta `examples/`:

1. **Búsqueda Lineal** (`busqueda_lineal.pseudo`) - O(n)
2. **Ordenamiento Burbuja** (`ordenamiento_burbuja.pseudo`) - O(n²)
3. **Factorial Iterativo** (`factorial_iterativo.pseudo`) - O(n)
4. **Suma de Matriz** (`matrix_sum_english.pseudo`) - O(n²)

## Cómo Usar

### Ejecutar Tests
```bash
python test_grammar.py
```

### Usar Programáticamente
```python
from src.parser import parse_pseudocode
from src.ast_nodes import ASTPrinter

# Parsear código
codigo = """
ENTERO x = 5;
SI x > 0 ENTONCES
    print("Positivo");
FIN_SI
"""

ast = parse_pseudocode(codigo)
printer = ASTPrinter()
printer.visit(ast)
```

## Resultados de Testing

✅ **Lexer**: Tokenización correcta de todos los elementos
✅ **Parser Simple**: Declaraciones y asignaciones  
✅ **IF Statement**: Condicionales con/sin ELSE
✅ **WHILE Loop**: Bucles con condición
✅ **FOR Loop**: Bucles con rango y paso opcional
✅ **Sintaxis Inglés**: Palabras clave en inglés
✅ **Archivos de Ejemplo**: Todos los ejemplos se parsean correctamente

## Complejidad de la Gramática

La gramática está optimizada para análisis de complejidad:

- **Bucles FOR**: Límites explícitos facilitan análisis O(n)
- **Bucles WHILE**: Condiciones claras para análisis de terminación  
- **Anidamiento**: Soporte para análisis de complejidad cuadrática/cúbica
- **Acceso a Arrays**: Fundamental para algoritmos de ordenamiento y búsqueda

## Extensibilidad

El diseño modular permite fácil extensión:
- Nuevas estructuras de control
- Tipos de datos adicionales
- Operadores específicos
- Análisis semántico
- Generación de código

Esta implementación proporciona una base sólida para el analizador de complejidad de algoritmos.
# Analizador_Algoritmos

El proyecto es un analizador de complejidades para algoritmos recursivos e iterativos, el cual dado un algoritmo en pseudocódigo debe dar como resultado la complejidad en el peor caso, en el mejor caso y en el caso promedio para dicho algoritmo.

## Sprint 1 - Tarea 4: Gramática Inicial del Pseudocódigo ✅

Se ha implementado la gramática inicial del pseudocódigo que soporta las estructuras básicas:

### Estructuras Implementadas
- **FOR loops**: Con sintaxis `PARA...HASTA...HACER` y `FOR...TO...DO`
- **WHILE loops**: Con sintaxis `MIENTRAS...HACER` y `WHILE...DO`  
- **IF-ELSE statements**: Con sintaxis `SI...ENTONCES...SINO` y `IF...THEN...ELSE`

### Características Adicionales
- Soporte bilingüe (español/inglés)
- Declaraciones de variables con tipos
- Arrays multidimensionales
- Expresiones aritméticas y lógicas
- Llamadas a funciones

## Estructura del Proyecto

```
├── src/                    # Código fuente
│   ├── lexer.py           # Analizador léxico
│   ├── parser.py          # Analizador sintáctico
│   └── ast_nodes.py       # Definiciones del AST
├── grammar/               # Definición de la gramática
│   └── pseudocode_grammar.bnf
├── examples/              # Ejemplos de pseudocódigo
│   ├── busqueda_lineal.pseudo
│   ├── ordenamiento_burbuja.pseudo
│   ├── factorial_iterativo.pseudo
│   └── matrix_sum_english.pseudo
├── docs/                  # Documentación
│   ├── README.md
│   └── grammar_specification.md
└── test_grammar.py        # Script de pruebas

```

## Uso

### Ejecutar Tests
```bash
python test_grammar.py
```

### Ejemplo de Código Soportado
```pseudocode
INICIO
    ENTERO n = 100;
    ENTERO suma = 0;
    
    PARA i = 1 HASTA n HACER
        suma = suma + i;
    FIN_PARA
    
    SI suma > 0 ENTONCES
        print("Suma positiva: " + suma);
    FIN_SI
FIN
```

## Documentación Completa

Ver [docs/README.md](docs/README.md) para documentación completa de la gramática y ejemplos de uso.

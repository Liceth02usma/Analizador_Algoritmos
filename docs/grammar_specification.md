# Especificación de la Gramática para Pseudocódigo
# Pseudocode Grammar Specification

## Descripción General
Esta gramática define la sintaxis para un lenguaje de pseudocódigo que soporta las estructuras de control básicas necesarias para el análisis de complejidad de algoritmos.

## Estructuras Soportadas

### 1. Declaración de Variables
```
ENTERO x;
REAL y = 3.14;
int contador = 0;
```

### 2. Asignación
```
x = 5;
y <- x + 1;
```

### 3. Estructura IF-ELSE
```
SI condicion ENTONCES
    statement1;
    statement2;
SINO
    statement3;
FIN_SI

# Versión en inglés
IF condition THEN
    statement1;
ELSE
    statement2;
END_IF
```

### 4. Bucle WHILE
```
MIENTRAS x < 10 HACER
    x = x + 1;
FIN_MIENTRAS

# Versión en inglés
WHILE x < 10 DO
    x = x + 1;
END_WHILE
```

### 5. Bucle FOR
```
PARA i = 1 HASTA 10 HACER
    suma = suma + i;
FIN_PARA

PARA i = 1 HASTA 10 PASO 2 HACER
    print(i);
FIN_PARA

# Versión en inglés
FOR i = 1 TO 10 DO
    sum = sum + i;
END_FOR

FOR i = 1 TO 10 STEP 2 DO
    print(i);
END_FOR
```

### 6. Expresiones
- Aritméticas: +, -, *, /, %, MOD
- Relacionales: =, <>, !=, <, >, <=, >=
- Lógicas: Y, O, NO, AND, OR, NOT

### 7. Tipos de Datos
- ENTERO / int: Números enteros
- REAL / float: Números decimales
- CADENA / string: Cadenas de texto
- BOOLEANO / boolean: Valores lógicos
- CARACTER / char: Caracteres individuales

### 8. Funciones
```
resultado = funcion(arg1, arg2);
print("Hola mundo");
```

## Palabras Reservadas (Español)
- SI, ENTONCES, SINO, FIN_SI
- MIENTRAS, HACER, FIN_MIENTRAS
- PARA, HASTA, PASO, FIN_PARA
- INICIO, FIN
- Y, O, NO
- VERDADERO, FALSO
- ENTERO, REAL, CADENA, BOOLEANO, CARACTER

## Palabras Reservadas (Inglés)
- IF, THEN, ELSE, END_IF
- WHILE, DO, END_WHILE
- FOR, TO, STEP, END_FOR
- AND, OR, NOT
- TRUE, FALSE
- int, float, string, boolean, char

## Operadores
- Asignación: =, <-
- Aritméticos: +, -, *, /, %, MOD
- Relacionales: =, <>, !=, <, >, <=, >=
- Lógicos: Y, O, NO, AND, OR, NOT
- Agrupación: (, )
- Delimitadores: ;, {, }

## Comentarios sobre Complejidad
Esta gramática está diseñada para facilitar el análisis de complejidad temporal:
- Los bucles FOR tienen límites explícitos para facilitar el análisis
- Las estructuras anidadas son soportadas para análisis de complejidad cuadrática o superior
- Las expresiones condicionales permiten análisis de mejor/peor caso
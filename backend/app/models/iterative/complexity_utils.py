import re


def calculate_elementary_operations(line: str) -> int:
    """
    Calcula el costo elemental (C) de una línea basándose en reglas estrictas de conteo.

    REGLAS DE CONTEO:
    1. Operadores (+, -, *, /, mod, div, and, or, not): 1 c/u
    2. Asignación (🡨): 1 c/u
    3. Comparación (<, >, =, ≠, <=, >=): 1 c/u
    4. Acceso a Memoria/Arreglo ([]): 1 c/u
    5. Acceso a Objeto (.): 1 c/u
    6. Return: 1 op
    7. Call: 1 op (costo de la invocación)

    REGLAS DE ESTRUCTURAS DE CONTROL:
    8. FOR: Se le suman +2 costos implícitos (1 Comparación de límite + 1 Incremento de variable).
       La asignación inicial ya se cuenta por el símbolo '🡨'.
       Ej: "for i 🡨 0 to n" -> '🡨' (1) + Comp (1) + Inc (1) = 3 ops.

    9. WHILE / IF / REPEAT: Su costo es la suma de las operaciones en su condición.
       Ej: "while (i < n)" -> '<' (1) = 1 op.
    """

    # 1. Limpieza (quitar comentarios y espacios extra)
    clean_line = line.split("►")[0].strip()

    # Líneas vacías o solo estructurales (begin, end, else solo) tienen costo 0
    if not clean_line or clean_line in ["begin", "end", "else", "then", "do"]:
        return 0

    cost = 0
    lower_line = clean_line.lower()

    # --- A. DETECCIÓN DE OPERADORES VISIBLES ---

    # Lista de tokens a buscar (ordenados por longitud para evitar falsos positivos, ej: <= antes que <)
    tokens_to_count = [
        # Asignación
        r"🡨",
        # Comparadores (Ojo: ≠ puede venir como != o <>)
        r"<=",
        r">=",
        r"≠",
        r"!=",
        r"<>",
        r"==",
        r"=",
        r"<",
        r">",
        # Aritmética
        r"\+",
        r"\-",
        r"\*",
        r"/",
        r"\bmod\b",
        r"\bdiv\b",
        # Lógica
        r"\band\b",
        r"\bor\b",
        r"\bnot\b",
        # Estructuras de datos
        r"\[",  # Acceso a arreglo A[i] cuenta como 1
        r"\.",  # Acceso a propiedad objeto x.y cuenta como 1
    ]

    for token in tokens_to_count:
        cost += len(re.findall(token, lower_line))

    # --- B. PALABRAS RESERVADAS CON COSTO ---

    # CALL: Cuenta como 1 operación de salto/stack
    if "call " in lower_line or "call(" in lower_line:
        cost += 1

    # RETURN: Cuenta como 1 operación de retorno
    if lower_line.startswith("return"):
        cost += 1

    # --- C. REGLAS IMPLÍCITAS POR ESTRUCTURA ---

    # REGLA DEL FOR:
    # Un 'for' típico tiene: Asignación (ya contada arriba por '🡨'), Comparación (Implícita), Incremento (Implícito)
    # Por lo tanto, agregamos +2 al costo detectado.
    if lower_line.startswith("for "):
        cost += 2

    # REGLA DEL WHILE / IF / REPEAT:
    # Su costo es puramente la evaluación de la condición.
    # Ya contamos los operadores (<, >, =, and...), así que no sumamos base extra,
    # salvo que la línea no tenga operadores visibles pero sí evalúe algo (ej: "while valid do")
    # En ese caso booleano simple, se asume 1 evaluación.
    if lower_line.startswith(("while ", "if ", "until ")) and cost == 0:
        cost = 1

    # Costo mínimo de seguridad: Si hay texto pero dio 0 (ej: llamada a función sin 'call' explícito o asignación rara)
    # y no es una palabra reservada ignorada.
    if cost == 0 and not lower_line.startswith(("begin", "end", "else")):
        # Asumimos que es una instrucción simple (ej: "print(x)")
        cost = 1

    return cost

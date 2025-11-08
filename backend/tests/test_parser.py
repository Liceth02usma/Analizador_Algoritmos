from __future__ import annotations

from importlib import import_module
from typing import Any
from lark import Tree
import pytest
from lark.exceptions import LarkError, UnexpectedInput, UnexpectedCharacters


def parse_and_transform(src: str) -> list[dict[str, Any]]:
    """
    Parsea y transforma código pseudocódigo a una lista de dicts.
    
    Args:
        src: Código fuente en pseudocódigo
        
    Returns:
        Lista de diccionarios con la estructura del código parseado
        
    Raises:
        TypeError: Si el resultado no es Tree ni list
    """
    pm = import_module("app.parsers.parser")
    # Obtener parser usando el método get_parser()
    transformer = pm.TreeToDict()
    parser_instance = transformer.get_parser()
    tree = parser_instance.parse(src)  
    result = transformer.transform(tree)  
    if isinstance(result, Tree) and result.data == "start":
        return list(result.children)
    elif isinstance(result, list):
        return result
    else:
        raise TypeError(f"Resultado inesperado: {type(result)}")


def _find_first(nodes: list[dict[str, Any]], typ: str) -> dict[str, Any] | None:
    """
    Busca el primer nodo con el tipo especificado en una lista de nodos.
    
    Args:
        nodes: Lista de nodos (diccionarios) del árbol parseado
        typ: Tipo de nodo a buscar (ej: 'for', 'while', 'if')
        
    Returns:
        El primer nodo que coincida con el tipo, o None si no se encuentra
    """
    for n in nodes:
        if isinstance(n, dict) and n.get("type") == typ:
            return n
    return None


def test_for_loop_structure():
    """
    Valida la estructura de un ciclo for con asignación y retorno.
    Verifica que se extraigan correctamente: variable, inicio, fin y cuerpo.
    """
    code = (
        "sum 🡨 1\n"
        "for i 🡨 1 to n do begin\n"
        "  sum 🡨 sum * i\n"
        "end\n"
        "return sum\n"
    )
    nodes = parse_and_transform(code)
    for_node = _find_first(nodes, "for")
    assert for_node is not None
    assert for_node["var"] == "i"
    assert for_node["from"] == 1
    assert for_node["to"] == "n"
    body = for_node["body"]
    assert any(b.get("type") == "assign" and b["var"] == "sum" for b in body)


def test_while_loop_structure():
    """
    Valida la estructura de un ciclo while con condición y cuerpo.
    Verifica que se capture correctamente la condición y las operaciones del cuerpo.
    """
    code = (
        "i 🡨 0\n"
        "while (i < n) do begin\n"
        "  i 🡨 i + 1\n"
        "end\n"
    )
    nodes = parse_and_transform(code)
    while_node = _find_first(nodes, "while")
    assert while_node is not None
    cond = while_node["cond"]
    assert cond["lhs"] == "i" and cond["op"] == "<" and cond["rhs"] == "n"
    body = while_node["body"]
    assert any(b.get("type") == "assign" and b["var"] == "i" for b in body)


def test_repeat_until_structure():
    """
    Valida la estructura de un ciclo repeat-until.
    Verifica que se capture el cuerpo y la condición de salida correctamente.
    """
    code = (
        "i 🡨 0\n"
        "repeat\n"
        "  i 🡨 i + 2\n"
        "until (i = n)\n"
    )
    nodes = parse_and_transform(code)
    repeat_node = _find_first(nodes, "repeat")
    assert repeat_node is not None
    cond = repeat_node["cond"]
    assert cond["lhs"] == "i" and cond["op"] == "=" and cond["rhs"] == "n"


def test_procedure_def_and_call():
    """
    Valida la definición de un procedimiento y su llamada.
    Verifica parámetros, cuerpo del procedimiento y argumentos de la llamada.
    """
    code = (
        "suma(x, y)\n"
        "begin\n"
        "  z 🡨 x + y\n"
        "  return z\n"
        "end\n"
        "CALL suma(5, 10)\n"
    )
    nodes = parse_and_transform(code)
    proc = _find_first(nodes, "procedure_def")
    assert proc is not None
    assert proc["name"] == "suma"
    assert proc["params"] == ["x", "y"]
    assert any(n.get("type") == "return" for n in proc["body"])

    call = _find_first(nodes, "call")
    assert call is not None
    assert call["name"] == "suma"
    assert call["args"] == [5, 10]


def test_if_else_with_boolean_logic():
    """
    Valida estructuras condicionales if-else con lógica booleana.
    Verifica operadores lógicos (and, not) y bloques then/else.
    """
    code = (
        "if (T and not F) then\n"
        "  begin\n"
        "    return 1\n"
        "  end\n"
        "else\n"
        "  begin\n"
        "    return -1\n"
        "  end\n"
    )
    nodes = parse_and_transform(code)
    ifn = _find_first(nodes, "if")
    assert ifn is not None
    cond = ifn["cond"]
    assert cond["op"] == "and"
    assert cond["lhs"] is True
    assert cond["rhs"]["op"] == "not" and cond["rhs"]["value"] is False
    assert any(n.get("type") == "return" for n in ifn["then"])
    assert any(n.get("type") == "return" for n in ifn["else"])


def test_class_and_object_declarations():
    """
    Valida la declaración de clases y la instanciación de objetos.
    Verifica nombre de clase, atributos y declaración de objetos.
    """
    code = (
        "Clase Persona {nombre edad}\n"
        "Clase Persona p\n"
    )
    nodes = parse_and_transform(code)
    cls = _find_first(nodes, "class_def")
    obj = _find_first(nodes, "object_decl")
    assert cls is not None and obj is not None
    assert cls["name"] == "Persona"
    assert set(cls["attributes"]) == {"nombre", "edad"}
    assert obj["class"] == "Persona" and obj["name"] == "p"


def test_recursive_skeleton_and_call():
    """
    Valida la estructura de un procedimiento recursivo (factorial).
    Verifica que se detecte la llamada recursiva dentro del cuerpo.
    """
    code = (
        "fact(n)\n"
        "begin\n"
        "  if (n <= 1) then\n"
        "    begin\n"
        "      return 1\n"
        "    end\n"
        "  else\n"
        "    begin\n"
        "      CALL fact(n - 1)\n"
        "      return 0\n"
        "    end\n"
        "end\n"
        "CALL fact(5)\n"
    )
    nodes = parse_and_transform(code)
    proc = _find_first(nodes, "procedure_def")
    assert proc is not None and proc["name"] == "fact"
    ifn = next(n for n in proc["body"] if n.get("type") == "if")
    assert any(n.get("type") == "return" and n["value"] == 1 for n in ifn["then"])
    assert any(n.get("type") == "call" and n["name"] == "fact" for n in ifn["else"])
    top_call = _find_first(nodes, "call")
    assert top_call is not None and top_call["name"] == "fact"


def test_divide_and_conquer_pattern_mergesort():
    """
    Valida un algoritmo divide y vencerás (mergeSort).
    Verifica las llamadas recursivas y la llamada a merge.
    """
    code = (
        "mergeSort(A, l, r)\n"
        "begin\n"
        "  if (l >= r) then\n"
        "    begin\n"
        "      return 0\n"
        "    end\n"
        "  else\n"
        "    begin\n"
        "      m 🡨 (l + r) div 2\n"
        "      CALL mergeSort(A, l, m)\n"
        "      CALL mergeSort(A, m + 1, r)\n"
        "      CALL merge(A, l, m, r)\n"
        "      return 0\n"
        "    end\n"
        "end\n"
    )
    nodes = parse_and_transform(code)
    proc = _find_first(nodes, "procedure_def")
    assert proc is not None and proc["name"] == "mergeSort"
    ifn = next(n for n in proc["body"] if n.get("type") == "if")
    else_body = ifn["else"]
    calls = [n for n in else_body if n.get("type") == "call"]
    assert {c["name"] for c in calls} == {"mergeSort", "merge"}


def test_missing_begin_in_for_loop():
    """
    Test negativo: valida que falte 'begin' después de 'do' en un for.
    Debe lanzar excepción de parsing.
    """
    code = (
        "for i 🡨 1 to n do\n"
        "  sum 🡨 sum + i\n"
        "end\n"
    )
    with pytest.raises((UnexpectedInput, LarkError)):
        parse_and_transform(code)


def test_missing_end_in_while_loop():
    """
    Test negativo: valida que falte 'end' para cerrar un while.
    Debe lanzar excepción de parsing.
    """
    code = (
        "while (i < n) do begin\n"
        "  i 🡨 i + 1\n"
    )
    with pytest.raises((UnexpectedInput, LarkError)):
        parse_and_transform(code)


def test_invalid_operator_in_assignment():
    """
    Test negativo: valida que se use '=' en lugar del operador correcto '🡨'.
    Debe lanzar excepción de parsing.
    """
    code = "x = 5\n"
    with pytest.raises((UnexpectedCharacters, LarkError)):
        parse_and_transform(code)


def test_missing_parentheses_in_condition():
    """
    Test negativo: valida que falten paréntesis en una condición.
    Las condiciones deben estar entre paréntesis.
    """
    code = (
        "if x > 5 then\n"
        "  begin\n"
        "    return x\n"
        "  end\n"
    )
    with pytest.raises((UnexpectedInput, LarkError)):
        parse_and_transform(code)


def test_invalid_keyword_spelling():
    """
    Test negativo: valida palabra clave mal escrita ('retun' en lugar de 'return').
    Debe lanzar excepción de parsing.
    """
    code = "retun 5\n"
    with pytest.raises((UnexpectedInput, LarkError)):
        parse_and_transform(code)


def test_unmatched_begin_end_blocks():
    """
    Test negativo: valida bloque 'begin' sin su correspondiente 'end'.
    Debe lanzar excepción de parsing.
    """
    code = (
        "if (x > 0) then\n"
        "  begin\n"
        "    x 🡨 x - 1\n"
    )
    with pytest.raises((UnexpectedInput, LarkError)):
        parse_and_transform(code)


def test_call_without_call_keyword():
    """
    Test negativo: valida llamada a procedimiento sin la palabra 'CALL'.
    La gramática lo interpreta como definición sin cuerpo, causando error.
    """
    code = "suma(5, 10)\n"
    with pytest.raises((UnexpectedInput, LarkError)):
        parse_and_transform(code)


def test_repeat_without_until():
    """
    Test negativo: valida 'repeat' sin su correspondiente 'until (cond)'.
    Debe lanzar excepción de parsing.
    """
    code = (
        "repeat\n"
        "  i 🡨 i + 1\n"
    )
    with pytest.raises((UnexpectedInput, LarkError)):
        parse_and_transform(code)


def test_procedure_with_missing_begin():
    """
    Test negativo: valida procedimiento sin 'begin...end'.
    Los procedimientos requieren bloques begin/end.
    """
    code = (
        "foo(x)\n"
        "  return x\n"
        "end\n"
    )
    with pytest.raises((UnexpectedInput, LarkError)):
        parse_and_transform(code)


def test_invalid_comparator():
    """
    Test negativo: valida operador de comparación no soportado ('===').
    Solo se soportan: =, <, >, <=, >=, !=
    """
    code = (
        "if (x === 5) then\n"
        "  begin\n"
        "    return 1\n"
        "  end\n"
    )
    with pytest.raises((UnexpectedCharacters, LarkError)):
        parse_and_transform(code)


def test_class_definition_missing_braces():
    """
    Test negativo: valida definición de clase sin llaves.
    Las clases requieren: Clase Nombre {atributos}
    """
    code = "Clase Persona nombre edad\n"
    with pytest.raises((UnexpectedInput, LarkError)):
        parse_and_transform(code)


def test_array_access_missing_bracket():
    """
    Test negativo: valida acceso a array sin cerrar corchete.
    Debe lanzar excepción de parsing.
    """
    code = "x 🡨 A[i\n"
    with pytest.raises((UnexpectedInput, LarkError)):
        parse_and_transform(code)


def test_nested_statements_without_block():
    """
    Test negativo: valida if anidado sin bloques 'begin...end' correctos.
    Los if anidados requieren bloques explícitos.
    """
    code = (
        "if (x > 0) then\n"
        "  if (x < 10) then\n"
        "    return x\n"
        "  end\n"
    )
    with pytest.raises((UnexpectedInput, LarkError)):
        parse_and_transform(code)


def test_incomplete_expression():
    """
    Test negativo: valida expresión aritmética incompleta.
    Debe lanzar excepción de parsing.
    """
    code = "x 🡨 5 +\n"
    with pytest.raises((UnexpectedInput, LarkError)):
        parse_and_transform(code)


def test_random_garbage_input():
    """
    Test negativo: valida entrada completamente inválida.
    Caracteres no reconocidos deben causar error de parsing.
    """
    code = "@#$%^&*()\n"
    with pytest.raises((UnexpectedCharacters, LarkError)):
        parse_and_transform(code)


def test_call_assignment_in_expression():
    """
    Valida que se pueda asignar el resultado de una llamada a función.
    Esto es necesario para algoritmos recursivos como Fibonacci.
    """
    code = (
        "fibonacci(n)\n"
        "begin\n"
        "  n1 🡨 n - 1\n"
        "  fib1 🡨 CALL fibonacci(n1)\n"
        "  return fib1\n"
        "end\n"
    )
    nodes = parse_and_transform(code)
    proc = _find_first(nodes, "procedure_def")
    assert proc is not None
    assert proc["name"] == "fibonacci"
    
    # Buscar la asignación de fib1
    body = proc["body"]
    fib1_assign = next((n for n in body if n.get("type") == "assign" and n.get("var") == "fib1"), None)
    assert fib1_assign is not None, "No se encontró la asignación fib1 🡨 CALL fibonacci(n1)"
    
    # Verificar que el valor es una llamada
    value = fib1_assign["value"]
    assert isinstance(value, dict), f"El valor debería ser un dict, pero es {type(value)}"
    assert value.get("type") == "call", f"El tipo debería ser 'call', pero es {value.get('type')}"
    assert value.get("name") == "fibonacci", f"El nombre debería ser 'fibonacci', pero es {value.get('name')}"
    assert value.get("args") == ["n1"], f"Los argumentos deberían ser ['n1'], pero son {value.get('args')}"


def test_multiple_call_assignments_fibonacci():
    """
    Valida múltiples asignaciones de llamadas recursivas (patrón Fibonacci).
    Verifica que se puedan asignar dos llamadas diferentes y luego sumar sus resultados.
    """
    code = (
        "fibonacci(n)\n"
        "begin\n"
        "  if (n <= 1) then\n"
        "    begin\n"
        "      return n\n"
        "    end\n"
        "  else\n"
        "    begin\n"
        "      n1 🡨 n - 1\n"
        "      n2 🡨 n - 2\n"
        "      fib1 🡨 CALL fibonacci(n1)\n"
        "      fib2 🡨 CALL fibonacci(n2)\n"
        "      resultado 🡨 fib1 + fib2\n"
        "      return resultado\n"
        "    end\n"
        "end\n"
    )
    nodes = parse_and_transform(code)
    proc = _find_first(nodes, "procedure_def")
    assert proc is not None and proc["name"] == "fibonacci"
    
    # Verificar estructura if-else
    ifn = next(n for n in proc["body"] if n.get("type") == "if")
    assert ifn is not None
    
    # Verificar el bloque else
    else_body = ifn.get("else", [])
    assert len(else_body) > 0, "El bloque else no debería estar vacío"
    
    # Buscar las dos asignaciones de llamadas
    fib1_assign = next((n for n in else_body if n.get("type") == "assign" and n.get("var") == "fib1"), None)
    fib2_assign = next((n for n in else_body if n.get("type") == "assign" and n.get("var") == "fib2"), None)
    
    assert fib1_assign is not None, "No se encontró fib1 🡨 CALL fibonacci(n1)"
    assert fib2_assign is not None, "No se encontró fib2 🡨 CALL fibonacci(n2)"
    
    # Verificar fib1
    assert fib1_assign["value"].get("type") == "call"
    assert fib1_assign["value"].get("name") == "fibonacci"
    assert fib1_assign["value"].get("args") == ["n1"]
    
    # Verificar fib2
    assert fib2_assign["value"].get("type") == "call"
    assert fib2_assign["value"].get("name") == "fibonacci"
    assert fib2_assign["value"].get("args") == ["n2"]
    
    # Verificar que se suma fib1 + fib2
    resultado_assign = next((n for n in else_body if n.get("type") == "assign" and n.get("var") == "resultado"), None)
    assert resultado_assign is not None, "No se encontró resultado 🡨 fib1 + fib2"
    
    # Verificar que es una suma
    value = resultado_assign["value"]
    assert value.get("op") == "+", f"Debería ser suma (+), pero es {value.get('op')}"
    assert value.get("lhs") == "fib1", f"El operando izquierdo debería ser 'fib1', pero es {value.get('lhs')}"
    assert value.get("rhs") == "fib2", f"El operando derecho debería ser 'fib2', pero es {value.get('rhs')}"
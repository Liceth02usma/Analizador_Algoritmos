from html import parser
from lark import Lark, Transformer
import os
from lark.lexer import Token

# Ruta de la gramática
GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), "pseudocode.lark")


class TreeToDict(Transformer):
    # ---------------------------
    # Estructuras principales
    # ---------------------------

    def get_parser(self) -> Lark:
        with open(GRAMMAR_FILE, "r", encoding="utf-8") as f:
            grammar = f.read()

        parser = Lark(grammar, start="start", parser="lalr")
        return parser

    def assign(self, items):
        return {"type": "assign", "var": str(items[0]), "value": items[1]}

    def for_loop(self, items):
        return {
            "type": "for",
            "var": str(items[0]),
            "from": items[1],
            "to": items[2],
            "body": list(items[3:]),
        }

    def while_loop(self, items):
        return {"type": "while", "cond": items[0], "body": list(items[1:])}

    def repeat_loop(self, items):
        cond = items[-1]
        body = list(items[:-1])
        return {"type": "repeat", "body": body, "cond": cond}

    def if_stmt(self, items):
        cond = items[0]
        then_body = []
        else_body = None
        for part in items[1:]:
            if isinstance(part, list):
                else_body = part
            else:
                then_body.append(part)
        node = {"type": "if", "cond": cond, "then": then_body}
        if else_body:
            node["else"] = else_body
        return node

    def else_block(self, items):
        return list(items)

    # ✅ Ahora 'args' es un método explícito que devuelve directamente la lista
    def args(self, items):
        return list(items)

    # ✅ FIX: simplificar el manejo de args dentro del call
    def call_stmt(self, items):
        name = str(items[0])
        args = []
        for x in items[1:]:
            if isinstance(x, list):
                args.extend(x)
            elif hasattr(x, "data") and x.data == "args":
                args.extend(x.children)
            elif not isinstance(x, Token):
                args.append(x)
        return {"type": "call", "name": name, "args": args}

    def return_stmt(self, items):
        return {"type": "return", "value": items[0]}

    # ---------------------------
    # Clases, objetos y procedimientos
    # ---------------------------
    def class_def(self, items):
        name = str(items[0])
        attrs = [str(x) for x in items[1:] if str(x) not in ["{", "}"]]
        return {"type": "class_def", "name": name, "attributes": attrs}

    def object_decl(self, items):
        return {"type": "object_decl", "class": str(items[0]), "name": str(items[1])}

    def procedure_def(self, items):
        name = str(items[0])
        params = []
        body = []
        for item in items[1:]:
            if isinstance(item, list) and not body:
                params = item
            elif isinstance(item, dict):
                body.append(item)
        return {"type": "procedure_def", "name": name, "params": params, "body": body}

    def param_list(self, items):
        return [str(i) for i in items]

    # ---------------------------
    # Condiciones y comparadores
    # ---------------------------
    def condition(self, items):
        return {"lhs": items[0], "op": items[1], "rhs": items[2]}

    def and_op(self, items):
        return {"op": "and", "lhs": items[0], "rhs": items[1]}

    def or_op(self, items):
        return {"op": "or", "lhs": items[0], "rhs": items[1]}

    def not_op(self, items):
        return {"op": "not", "value": items[0]}

    def bool_true(self, _):
        return True

    def bool_false(self, _):
        return False

    def COMPARATOR(self, token):
        return str(token)

    # ---------------------------
    # Expresiones aritméticas
    # ---------------------------
    def number(self, items):
        return int(items[0])

    def var(self, items):
        return str(items[0])

    def array_access(self, items):
        return {"type": "array_access", "array": str(items[0]), "index": items[1]}

    def field_access(self, items):
        return {"type": "field_access", "object": str(items[0]), "field": str(items[1])}

    def add(self, items):
        return {"op": "+", "lhs": items[0], "rhs": items[1]}

    def sub(self, items):
        return {"op": "-", "lhs": items[0], "rhs": items[1]}

    def mul(self, items):
        return {"op": "*", "lhs": items[0], "rhs": items[1]}

    def div(self, items):
        return {"op": "/", "lhs": items[0], "rhs": items[1]}

    def mod(self, items):
        return {"op": "mod", "lhs": items[0], "rhs": items[1]}

    def intdiv(self, items):
        return {"op": "div", "lhs": items[0], "rhs": items[1]}

    def ceil(self, items):
        return {"op": "ceil", "value": items[0]}

    def floor(self, items):
        return {"op": "floor", "value": items[0]}

    def grouped(self, items):
        return items[0]

    def comment(self, items):
        return {"type": "comment", "text": str(items[0]).strip()}


def pretty_print(obj, indent=0):
    space = "  " * indent
    if isinstance(obj, dict):
        print(space + "{")
        for k, v in obj.items():
            print(space + f"  {k!r}:")
            pretty_print(v, indent + 2)
        print(space + "}")
    elif isinstance(obj, list):
        print(space + "[")
        for item in obj:
            pretty_print(item, indent + 1)
        print(space + "]")
    else:
        print(space + repr(obj))


if __name__ == "__main__":
    code = """
    Clase Persona {nombre edad}
    Clase Persona p

    suma(x, y)
    begin
        z 🡨 x + y
        return z
    end

    CALL suma(5, 10)

    if (T and not F) then
        begin
            return 1
        end
    else
        begin
            return -1
        end

    """

    try:
        transformer = TreeToDict()
        tree = transformer.get_parser().parse(code)

        result = transformer.transform(tree)
        print("\n=== Árbol resultante ===")
        pretty_print(result)
    except Exception as e:
        print("Error al parsear:", e)
        raise

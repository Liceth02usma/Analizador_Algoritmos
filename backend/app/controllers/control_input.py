from app.parsers.parser import parser, TreeToDict
from lark import UnexpectedInput

class ControlInput:
    @staticmethod
    def parse_pseudocode(pseudocode: str):
        try:
            tree = parser.parse(pseudocode)
            transformer = TreeToDict()
            result = transformer.transform(tree)
            return result
        except UnexpectedInput as e:
            return {"error": f"Error al parsear el pseudocódigo: {str(e)}"}

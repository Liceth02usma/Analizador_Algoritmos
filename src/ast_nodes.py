"""
Abstract Syntax Tree (AST) definitions for pseudocode
Defines the node types for representing parsed pseudocode
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union, Any


class ASTNode(ABC):
    """Base class for all AST nodes"""
    pass


class Statement(ASTNode):
    """Base class for all statements"""
    pass


class Expression(ASTNode):
    """Base class for all expressions"""
    pass


# Program structure
class Program(ASTNode):
    def __init__(self, statements: List[Statement]):
        self.statements = statements


class Block(Statement):
    def __init__(self, statements: List[Statement]):
        self.statements = statements


# Statements
class DeclarationStatement(Statement):
    def __init__(self, var_type: str, identifier: str, initial_value: Optional[Expression] = None):
        self.var_type = var_type
        self.identifier = identifier
        self.initial_value = initial_value


class AssignmentStatement(Statement):
    def __init__(self, identifier: str, expression: Expression):
        self.identifier = identifier
        self.expression = expression


class IfStatement(Statement):
    def __init__(self, condition: Expression, then_block: List[Statement], 
                 else_block: Optional[List[Statement]] = None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: List[Statement]):
        self.condition = condition
        self.body = body


class ForStatement(Statement):
    def __init__(self, variable: str, start_expr: Expression, end_expr: Expression,
                 step_expr: Optional[Expression], body: List[Statement]):
        self.variable = variable
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.step_expr = step_expr
        self.body = body


class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression


# Expressions
class BinaryOperation(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right


class UnaryOperation(Expression):
    def __init__(self, operator: str, operand: Expression):
        self.operator = operator
        self.operand = operand


class Identifier(Expression):
    def __init__(self, name: str):
        self.name = name


class ArrayAccess(Expression):
    def __init__(self, array: Expression, index: Expression):
        self.array = array
        self.index = index


class FunctionCall(Expression):
    def __init__(self, name: str, arguments: List[Expression]):
        self.name = name
        self.arguments = arguments


class Literal(Expression):
    def __init__(self, value: Any, literal_type: str):
        self.value = value
        self.literal_type = literal_type  # 'integer', 'real', 'string', 'boolean'


# AST Visitor pattern for traversing the tree
class ASTVisitor(ABC):
    """Base class for AST visitors"""
    
    @abstractmethod
    def visit_program(self, node: Program):
        pass
    
    @abstractmethod
    def visit_block(self, node: Block):
        pass
    
    @abstractmethod
    def visit_declaration_statement(self, node: DeclarationStatement):
        pass
    
    @abstractmethod
    def visit_assignment_statement(self, node: AssignmentStatement):
        pass
    
    @abstractmethod
    def visit_if_statement(self, node: IfStatement):
        pass
    
    @abstractmethod
    def visit_while_statement(self, node: WhileStatement):
        pass
    
    @abstractmethod
    def visit_for_statement(self, node: ForStatement):
        pass
    
    @abstractmethod
    def visit_expression_statement(self, node: ExpressionStatement):
        pass
    
    @abstractmethod
    def visit_binary_operation(self, node: BinaryOperation):
        pass
    
    @abstractmethod
    def visit_unary_operation(self, node: UnaryOperation):
        pass
    
    @abstractmethod
    def visit_identifier(self, node: Identifier):
        pass
    
    @abstractmethod
    def visit_array_access(self, node: ArrayAccess):
        pass
    
    @abstractmethod
    def visit_function_call(self, node: FunctionCall):
        pass
    
    @abstractmethod
    def visit_literal(self, node: Literal):
        pass


class ASTPrinter(ASTVisitor):
    """Prints the AST structure for debugging"""
    
    def __init__(self):
        self.indent_level = 0
    
    def _print_indented(self, text: str):
        print("  " * self.indent_level + text)
    
    def _indent(self):
        self.indent_level += 1
    
    def _dedent(self):
        self.indent_level = max(0, self.indent_level - 1)
    
    def visit_program(self, node: Program):
        self._print_indented("Program:")
        self._indent()
        for stmt in node.statements:
            self.visit(stmt)
        self._dedent()
    
    def visit_block(self, node: Block):
        self._print_indented("Block:")
        self._indent()
        for stmt in node.statements:
            self.visit(stmt)
        self._dedent()
    
    def visit_declaration_statement(self, node: DeclarationStatement):
        text = f"Declaration: {node.var_type} {node.identifier}"
        if node.initial_value:
            text += " = "
        self._print_indented(text)
        if node.initial_value:
            self._indent()
            self.visit(node.initial_value)
            self._dedent()
    
    def visit_assignment_statement(self, node: AssignmentStatement):
        self._print_indented(f"Assignment: {node.identifier} =")
        self._indent()
        self.visit(node.expression)
        self._dedent()
    
    def visit_if_statement(self, node: IfStatement):
        self._print_indented("If Statement:")
        self._indent()
        self._print_indented("Condition:")
        self._indent()
        self.visit(node.condition)
        self._dedent()
        self._print_indented("Then:")
        self._indent()
        for stmt in node.then_block:
            self.visit(stmt)
        self._dedent()
        if node.else_block:
            self._print_indented("Else:")
            self._indent()
            for stmt in node.else_block:
                self.visit(stmt)
            self._dedent()
        self._dedent()
    
    def visit_while_statement(self, node: WhileStatement):
        self._print_indented("While Statement:")
        self._indent()
        self._print_indented("Condition:")
        self._indent()
        self.visit(node.condition)
        self._dedent()
        self._print_indented("Body:")
        self._indent()
        for stmt in node.body:
            self.visit(stmt)
        self._dedent()
        self._dedent()
    
    def visit_for_statement(self, node: ForStatement):
        self._print_indented(f"For Statement: {node.variable}")
        self._indent()
        self._print_indented("Start:")
        self._indent()
        self.visit(node.start_expr)
        self._dedent()
        self._print_indented("End:")
        self._indent()
        self.visit(node.end_expr)
        self._dedent()
        if node.step_expr:
            self._print_indented("Step:")
            self._indent()
            self.visit(node.step_expr)
            self._dedent()
        self._print_indented("Body:")
        self._indent()
        for stmt in node.body:
            self.visit(stmt)
        self._dedent()
        self._dedent()
    
    def visit_expression_statement(self, node: ExpressionStatement):
        self._print_indented("Expression Statement:")
        self._indent()
        self.visit(node.expression)
        self._dedent()
    
    def visit_binary_operation(self, node: BinaryOperation):
        self._print_indented(f"Binary Operation: {node.operator}")
        self._indent()
        self._print_indented("Left:")
        self._indent()
        self.visit(node.left)
        self._dedent()
        self._print_indented("Right:")
        self._indent()
        self.visit(node.right)
        self._dedent()
        self._dedent()
    
    def visit_unary_operation(self, node: UnaryOperation):
        self._print_indented(f"Unary Operation: {node.operator}")
        self._indent()
        self.visit(node.operand)
        self._dedent()
    
    def visit_identifier(self, node: Identifier):
        self._print_indented(f"Identifier: {node.name}")
    
    def visit_array_access(self, node: ArrayAccess):
        self._print_indented("Array Access:")
        self._indent()
        self._print_indented("Array:")
        self._indent()
        self.visit(node.array)
        self._dedent()
        self._print_indented("Index:")
        self._indent()
        self.visit(node.index)
        self._dedent()
        self._dedent()
    
    def visit_function_call(self, node: FunctionCall):
        self._print_indented(f"Function Call: {node.name}")
        if node.arguments:
            self._indent()
            self._print_indented("Arguments:")
            self._indent()
            for arg in node.arguments:
                self.visit(arg)
            self._dedent()
            self._dedent()
    
    def visit_literal(self, node: Literal):
        self._print_indented(f"Literal ({node.literal_type}): {node.value}")
    
    def visit(self, node: ASTNode):
        """Dynamic dispatch to the appropriate visit method"""
        # Convert class name to snake_case and add visit_ prefix
        class_name = type(node).__name__
        # Convert camelCase to snake_case
        method_name = 'visit_'
        for i, char in enumerate(class_name):
            if i > 0 and char.isupper():
                method_name += '_'
            method_name += char.lower()
        
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            raise ValueError(f"No visit method for {type(node).__name__}: expected {method_name}")
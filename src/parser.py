"""
Parser for Pseudocode Grammar
Implements a recursive descent parser for the defined pseudocode grammar
"""

from typing import List, Optional
from lexer import Lexer, Token, TokenType
from ast_nodes import *


class ParseError(Exception):
    """Exception raised when parsing fails"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parse error at line {token.line}, column {token.column}: {message}")


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type not in (TokenType.COMMENT, TokenType.NEWLINE)]
        self.current = 0
    
    def current_token(self) -> Token:
        if self.current >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.current]
    
    def peek_token(self, offset: int = 1) -> Token:
        pos = self.current + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[pos]
    
    def advance(self) -> Token:
        token = self.current_token()
        if self.current < len(self.tokens) - 1:
            self.current += 1
        return token
    
    def match(self, *token_types: TokenType) -> bool:
        return self.current_token().type in token_types
    
    def consume(self, token_type: TokenType, message: str = "") -> Token:
        if self.current_token().type == token_type:
            return self.advance()
        
        if not message:
            message = f"Expected {token_type.value}"
        raise ParseError(message, self.current_token())
    
    def parse(self) -> Program:
        """Parse the entire program"""
        statements = self.parse_statement_list()
        self.consume(TokenType.EOF, "Expected end of file")
        return Program(statements)
    
    def parse_statement_list(self) -> List[Statement]:
        """Parse a list of statements"""
        statements = []
        
        while not self.match(TokenType.EOF, TokenType.FIN, TokenType.FIN_SI, TokenType.FIN_MIENTRAS, 
                           TokenType.FIN_PARA, TokenType.RIGHT_BRACE, TokenType.END_IF, 
                           TokenType.END_WHILE, TokenType.END_FOR, TokenType.ELSE, TokenType.SINO):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def parse_statement(self) -> Optional[Statement]:
        """Parse a single statement"""
        
        # Block statement
        if self.match(TokenType.INICIO, TokenType.LEFT_BRACE):
            return self.parse_block_statement()
        
        # Declaration statement
        if self.match(TokenType.ENTERO, TokenType.REAL, TokenType.CADENA, TokenType.BOOLEANO, 
                     TokenType.CARACTER, TokenType.INT, TokenType.FLOAT, TokenType.STRING, 
                     TokenType.BOOLEAN, TokenType.CHAR):
            return self.parse_declaration_statement()
        
        # Control flow statements
        if self.match(TokenType.SI, TokenType.IF):
            return self.parse_if_statement()
        
        if self.match(TokenType.MIENTRAS, TokenType.WHILE):
            return self.parse_while_statement()
        
        if self.match(TokenType.PARA, TokenType.FOR):
            return self.parse_for_statement()
        
        # Assignment or expression statement
        if self.match(TokenType.IDENTIFIER):
            # Look ahead to determine if it's an assignment
            if self.peek_token().type in (TokenType.ASSIGN, TokenType.ASSIGN_LEFT):
                return self.parse_assignment_statement()
            else:
                return self.parse_expression_statement()
        
        # Expression statement
        return self.parse_expression_statement()
    
    def parse_block_statement(self) -> Block:
        """Parse a block statement"""
        if self.match(TokenType.INICIO):
            self.consume(TokenType.INICIO)
            statements = self.parse_statement_list()
            self.consume(TokenType.FIN)
        else:
            self.consume(TokenType.LEFT_BRACE)
            statements = self.parse_statement_list()
            self.consume(TokenType.RIGHT_BRACE)
        
        return Block(statements)
    
    def parse_declaration_statement(self) -> DeclarationStatement:
        """Parse a variable declaration"""
        var_type = self.advance().value
        identifier = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        
        # Check for array declaration (including multi-dimensional)
        while self.match(TokenType.LEFT_BRACKET):
            self.advance()  # consume [
            array_size = self.parse_expression()
            self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after array size")
            var_type = f"{var_type}[]"
        
        initial_value = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initial_value = self.parse_expression()
        
        # Handle multiple variable declarations (e.g., "int i, j;")
        # For now, we'll just parse the first one and ignore the rest
        while self.match(TokenType.COMMA):
            self.advance()  # consume comma
            self.consume(TokenType.IDENTIFIER, "Expected variable name")  # consume next identifier
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after declaration")
        return DeclarationStatement(var_type, identifier, initial_value)
    
    def parse_assignment_statement(self) -> AssignmentStatement:
        """Parse an assignment statement"""
        identifier = self.consume(TokenType.IDENTIFIER).value
        self.advance()  # consume = or <-
        expression = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after assignment")
        return AssignmentStatement(identifier, expression)
    
    def parse_if_statement(self) -> IfStatement:
        """Parse an IF statement"""
        # Consume IF/SI
        is_spanish = self.match(TokenType.SI)
        self.advance()
        
        # Parse condition
        condition = self.parse_expression()
        
        # Consume THEN/ENTONCES
        if is_spanish:
            self.consume(TokenType.ENTONCES, "Expected 'ENTONCES' after condition")
        else:
            self.consume(TokenType.THEN, "Expected 'THEN' after condition")
        
        # Parse then block
        then_block = self.parse_statement_list()
        
        # Check for else block
        else_block = None
        if self.match(TokenType.SINO, TokenType.ELSE):
            self.advance()
            else_block = self.parse_statement_list()
        
        # Consume end marker
        if is_spanish:
            self.consume(TokenType.FIN_SI, "Expected 'FIN_SI'")
        else:
            self.consume(TokenType.END_IF, "Expected 'END_IF'")
        
        return IfStatement(condition, then_block, else_block)
    
    def parse_while_statement(self) -> WhileStatement:
        """Parse a WHILE statement"""
        # Consume WHILE/MIENTRAS
        is_spanish = self.match(TokenType.MIENTRAS)
        self.advance()
        
        # Parse condition
        condition = self.parse_expression()
        
        # Consume DO/HACER
        if is_spanish:
            self.consume(TokenType.HACER, "Expected 'HACER' after condition")
        else:
            self.consume(TokenType.DO, "Expected 'DO' after condition")
        
        # Parse body
        body = self.parse_statement_list()
        
        # Consume end marker
        if is_spanish:
            self.consume(TokenType.FIN_MIENTRAS, "Expected 'FIN_MIENTRAS'")
        else:
            self.consume(TokenType.END_WHILE, "Expected 'END_WHILE'")
        
        return WhileStatement(condition, body)
    
    def parse_for_statement(self) -> ForStatement:
        """Parse a FOR statement"""
        # Consume FOR/PARA
        is_spanish = self.match(TokenType.PARA)
        self.advance()
        
        # Parse variable
        variable = self.consume(TokenType.IDENTIFIER, "Expected loop variable").value
        self.consume(TokenType.ASSIGN, "Expected '=' in for loop")
        
        # Parse start expression
        start_expr = self.parse_expression()
        
        # Consume TO/HASTA
        if is_spanish:
            self.consume(TokenType.HASTA, "Expected 'HASTA'")
        else:
            self.consume(TokenType.TO, "Expected 'TO'")
        
        # Parse end expression
        end_expr = self.parse_expression()
        
        # Optional step
        step_expr = None
        if self.match(TokenType.PASO, TokenType.STEP):
            self.advance()
            step_expr = self.parse_expression()
        
        # Consume DO/HACER
        if is_spanish:
            self.consume(TokenType.HACER, "Expected 'HACER'")
        else:
            self.consume(TokenType.DO, "Expected 'DO'")
        
        # Parse body
        body = self.parse_statement_list()
        
        # Consume end marker
        if is_spanish:
            self.consume(TokenType.FIN_PARA, "Expected 'FIN_PARA'")
        else:
            self.consume(TokenType.END_FOR, "Expected 'END_FOR'")
        
        return ForStatement(variable, start_expr, end_expr, step_expr, body)
    
    def parse_expression_statement(self) -> ExpressionStatement:
        """Parse an expression statement"""
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExpressionStatement(expr)
    
    def parse_expression(self) -> Expression:
        """Parse an expression (logical OR has lowest precedence)"""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> Expression:
        """Parse logical OR expression"""
        expr = self.parse_logical_and()
        
        while self.match(TokenType.O, TokenType.OR):
            operator = self.advance().value
            right = self.parse_logical_and()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_logical_and(self) -> Expression:
        """Parse logical AND expression"""
        expr = self.parse_equality()
        
        while self.match(TokenType.Y, TokenType.AND):
            operator = self.advance().value
            right = self.parse_equality()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_equality(self) -> Expression:
        """Parse equality/relational expressions"""
        expr = self.parse_comparison()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL_1, TokenType.NOT_EQUAL_2):
            operator = self.advance().value
            right = self.parse_comparison()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_comparison(self) -> Expression:
        """Parse comparison expressions"""
        expr = self.parse_addition()
        
        while self.match(TokenType.LESS_THAN, TokenType.GREATER_THAN, 
                        TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            operator = self.advance().value
            right = self.parse_addition()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_addition(self) -> Expression:
        """Parse addition/subtraction expressions"""
        expr = self.parse_multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.advance().value
            right = self.parse_multiplication()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_multiplication(self) -> Expression:
        """Parse multiplication/division expressions"""
        expr = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO, TokenType.MOD):
            operator = self.advance().value
            right = self.parse_unary()
            expr = BinaryOperation(expr, operator, right)
        
        return expr
    
    def parse_unary(self) -> Expression:
        """Parse unary expressions"""
        if self.match(TokenType.MINUS, TokenType.PLUS, TokenType.NO, TokenType.NOT):
            operator = self.advance().value
            expr = self.parse_unary()
            return UnaryOperation(operator, expr)
        
        return self.parse_primary()
    
    def parse_primary(self) -> Expression:
        """Parse primary expressions"""
        
        # Literals
        if self.match(TokenType.INTEGER):
            value = int(self.advance().value)
            return Literal(value, "integer")
        
        if self.match(TokenType.REAL_NUMBER):
            value = float(self.advance().value)
            return Literal(value, "real")
        
        if self.match(TokenType.STRING_LITERAL):
            value = self.advance().value
            return Literal(value, "string")
        
        if self.match(TokenType.VERDADERO, TokenType.TRUE):
            self.advance()
            return Literal(True, "boolean")
        
        if self.match(TokenType.FALSO, TokenType.FALSE):
            self.advance()
            return Literal(False, "boolean")
        
        # Parenthesized expression
        if self.match(TokenType.LEFT_PAREN):
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr
        
        # Identifier (variable or function call)
        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            
            # Function call
            if self.match(TokenType.LEFT_PAREN):
                self.advance()
                arguments = []
                
                if not self.match(TokenType.RIGHT_PAREN):
                    arguments.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        arguments.append(self.parse_expression())
                
                self.consume(TokenType.RIGHT_PAREN, "Expected ')' after function arguments")
                return FunctionCall(name, arguments)
            
            # Array access (possibly chained for multi-dimensional arrays)
            expr = Identifier(name)
            while self.match(TokenType.LEFT_BRACKET):
                self.advance()
                index = self.parse_expression()
                self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after array index")
                expr = ArrayAccess(expr, index)
            
            return expr
        
        raise ParseError("Expected expression", self.current_token())


def parse_pseudocode(source_code: str) -> Program:
    """Convenience function to parse pseudocode source"""
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()
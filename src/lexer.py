"""
Lexer (Analizador Léxico) para Pseudocódigo
Tokenizes pseudocode according to the defined grammar
"""

import re
from enum import Enum
from typing import List, NamedTuple


class TokenType(Enum):
    # Keywords (Spanish)
    SI = "SI"
    ENTONCES = "ENTONCES"
    SINO = "SINO"
    FIN_SI = "FIN_SI"
    MIENTRAS = "MIENTRAS"
    HACER = "HACER"
    FIN_MIENTRAS = "FIN_MIENTRAS"
    PARA = "PARA"
    HASTA = "HASTA"
    PASO = "PASO"
    FIN_PARA = "FIN_PARA"
    INICIO = "INICIO"
    FIN = "FIN"
    Y = "Y"
    O = "O"
    NO = "NO"
    VERDADERO = "VERDADERO"
    FALSO = "FALSO"
    
    # Keywords (English)
    IF = "IF"
    THEN = "THEN"
    ELSE = "ELSE"
    END_IF = "END_IF"
    WHILE = "WHILE"
    DO = "DO"
    END_WHILE = "END_WHILE"
    FOR = "FOR"
    TO = "TO"
    STEP = "STEP"
    END_FOR = "END_FOR"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    TRUE = "TRUE"
    FALSE = "FALSE"
    
    # Data types
    ENTERO = "ENTERO"
    REAL = "REAL"
    CADENA = "CADENA"
    BOOLEANO = "BOOLEANO"
    CARACTER = "CARACTER"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    CHAR = "char"
    
    # Operators
    ASSIGN = "="
    ASSIGN_LEFT = "<-"
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    MOD = "MOD"
    
    # Comparison operators
    EQUAL = "="
    NOT_EQUAL_1 = "<>"
    NOT_EQUAL_2 = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    
    # Delimiters
    SEMICOLON = ";"
    COMMA = ","
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    
    # Literals
    IDENTIFIER = "IDENTIFIER"
    INTEGER = "INTEGER"
    REAL_NUMBER = "REAL_NUMBER"
    STRING_LITERAL = "STRING_LITERAL"
    
    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    COMMENT = "COMMENT"


class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # Keywords mapping
        self.keywords = {
            # Spanish keywords
            'SI': TokenType.SI,
            'ENTONCES': TokenType.ENTONCES,
            'SINO': TokenType.SINO,
            'FIN_SI': TokenType.FIN_SI,
            'MIENTRAS': TokenType.MIENTRAS,
            'HACER': TokenType.HACER,
            'FIN_MIENTRAS': TokenType.FIN_MIENTRAS,
            'PARA': TokenType.PARA,
            'HASTA': TokenType.HASTA,
            'PASO': TokenType.PASO,
            'FIN_PARA': TokenType.FIN_PARA,
            'INICIO': TokenType.INICIO,
            'FIN': TokenType.FIN,
            'Y': TokenType.Y,
            'O': TokenType.O,
            'NO': TokenType.NO,
            'VERDADERO': TokenType.VERDADERO,
            'FALSO': TokenType.FALSO,
            'ENTERO': TokenType.ENTERO,
            'REAL': TokenType.REAL,
            'CADENA': TokenType.CADENA,
            'BOOLEANO': TokenType.BOOLEANO,
            'CARACTER': TokenType.CARACTER,
            'MOD': TokenType.MOD,
            
            # English keywords
            'IF': TokenType.IF,
            'THEN': TokenType.THEN,
            'ELSE': TokenType.ELSE,
            'END_IF': TokenType.END_IF,
            'WHILE': TokenType.WHILE,
            'DO': TokenType.DO,
            'END_WHILE': TokenType.END_WHILE,
            'FOR': TokenType.FOR,
            'TO': TokenType.TO,
            'STEP': TokenType.STEP,
            'END_FOR': TokenType.END_FOR,
            'AND': TokenType.AND,
            'OR': TokenType.OR,
            'NOT': TokenType.NOT,
            'TRUE': TokenType.TRUE,
            'FALSE': TokenType.FALSE,
            'int': TokenType.INT,
            'float': TokenType.FLOAT,
            'string': TokenType.STRING,
            'boolean': TokenType.BOOLEAN,
            'char': TokenType.CHAR,
        }
    
    def current_char(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]
    
    def peek_char(self, offset=1):
        peek_pos = self.pos + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def advance(self):
        if self.current_char() == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def read_number(self):
        start_pos = self.pos
        start_col = self.column
        
        while self.current_char() and self.current_char().isdigit():
            self.advance()
        
        if self.current_char() == '.':
            self.advance()
            while self.current_char() and self.current_char().isdigit():
                self.advance()
            return Token(TokenType.REAL_NUMBER, self.text[start_pos:self.pos], self.line, start_col)
        
        return Token(TokenType.INTEGER, self.text[start_pos:self.pos], self.line, start_col)
    
    def read_string(self, quote_char):
        start_col = self.column
        self.advance()  # Skip opening quote
        start_pos = self.pos
        
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()  # Skip escape character
                if self.current_char():
                    self.advance()  # Skip escaped character
            else:
                self.advance()
        
        value = self.text[start_pos:self.pos]
        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote
        
        return Token(TokenType.STRING_LITERAL, value, self.line, start_col)
    
    def read_identifier(self):
        start_pos = self.pos
        start_col = self.column
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() == '_')):
            self.advance()
        
        value = self.text[start_pos:self.pos]
        token_type = self.keywords.get(value, TokenType.IDENTIFIER)
        
        return Token(token_type, value, self.line, start_col)
    
    def read_comment(self):
        start_col = self.column
        start_pos = self.pos
        
        while self.current_char() and self.current_char() != '\n':
            self.advance()
        
        return Token(TokenType.COMMENT, self.text[start_pos:self.pos], self.line, start_col)
    
    def tokenize(self) -> List[Token]:
        while self.current_char():
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            current = self.current_char()
            current_col = self.column
            
            # Comments
            if current == '#':
                self.tokens.append(self.read_comment())
                continue
            
            # Newlines
            if current == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, current, self.line, current_col))
                self.advance()
                continue
            
            # Numbers
            if current.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Strings
            if current in '"\'':
                self.tokens.append(self.read_string(current))
                continue
            
            # Identifiers and keywords
            if current.isalpha() or current == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Two-character operators
            if current == '<':
                if self.peek_char() == '-':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.ASSIGN_LEFT, '<-', self.line, current_col))
                    continue
                elif self.peek_char() == '>':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.NOT_EQUAL_1, '<>', self.line, current_col))
                    continue
                elif self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', self.line, current_col))
                    continue
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.LESS_THAN, '<', self.line, current_col))
                    continue
            
            if current == '>':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', self.line, current_col))
                    continue
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.GREATER_THAN, '>', self.line, current_col))
                    continue
            
            if current == '!':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.NOT_EQUAL_2, '!=', self.line, current_col))
                    continue
            
            # Single-character tokens
            single_char_tokens = {
                '=': TokenType.ASSIGN,
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '%': TokenType.MODULO,
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA,
                '(': TokenType.LEFT_PAREN,
                ')': TokenType.RIGHT_PAREN,
                '{': TokenType.LEFT_BRACE,
                '}': TokenType.RIGHT_BRACE,
                '[': TokenType.LEFT_BRACKET,
                ']': TokenType.RIGHT_BRACKET,
            }
            
            if current in single_char_tokens:
                self.tokens.append(Token(single_char_tokens[current], current, self.line, current_col))
                self.advance()
                continue
            
            # Unknown character
            self.advance()
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
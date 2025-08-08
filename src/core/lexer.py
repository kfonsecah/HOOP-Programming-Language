"""
Analizador Léxico para el lenguaje HOOP
======================================

Este módulo se encarga de convertir el código fuente de HOOP en una secuencia de tokens.
Un token es la unidad mínima con significado en el lenguaje (palabra reservada, identificador, operador, etc.)

Proceso: Código fuente (string) → Lista de tokens
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    """Tipos de tokens que reconoce el lenguaje HOOP"""
    # Palabras reservadas
    CLASS = "CLASS"
    DEF = "DEF"
    IF = "IF"
    ELSE = "ELSE"
    ELIF = "ELIF"
    FOR = "FOR"
    WHILE = "WHILE"
    CYCLE = "CYCLE"
    SHOW = "SHOW"
    INPUT = "INPUT"
    RETURN = "RETURN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    IN = "IN"
    TRUE = "TRUE"
    FALSE = "FALSE"
    NONE = "NONE"
    
    # Tipos de datos
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    
    # Identificadores y literales
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING_LITERAL = "STRING_LITERAL"
    
    # Operadores
    PLUS = "PLUS"           # +
    MINUS = "MINUS"         # -
    MULTIPLY = "MULTIPLY"   # *
    DIVIDE = "DIVIDE"       # /
    MODULO = "MODULO"       # %
    ASSIGN = "ASSIGN"       # =
    EQUAL = "EQUAL"         # ==
    NOT_EQUAL = "NOT_EQUAL" # !=
    LESS = "LESS"           # <
    GREATER = "GREATER"     # >
    LESS_EQUAL = "LESS_EQUAL"     # <=
    GREATER_EQUAL = "GREATER_EQUAL" # >=
    
    # Delimitadores
    LPAREN = "LPAREN"       # (
    RPAREN = "RPAREN"       # )
    LBRACE = "LBRACE"       # {
    RBRACE = "RBRACE"       # }
    LBRACKET = "LBRACKET"   # [
    RBRACKET = "RBRACKET"   # ]
    COMMA = "COMMA"         # ,
    COLON = "COLON"         # :
    SEMICOLON = "SEMICOLON" # ;
    DOT = "DOT"             # .
    
    # Especiales
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"
    
    # Comentarios
    COMMENT = "COMMENT"

@dataclass
class Token:
    """Representa un token individual"""
    type: TokenType
    value: str
    line: int
    column: int

class HoopLexer:
    """
    Analizador léxico para el lenguaje HOOP
    
    Responsabilidades:
    - Dividir el código fuente en tokens
    - Identificar palabras reservadas, operadores, identificadores
    - Manejar literales (números, strings)
    - Gestionar indentación (importante para la sintaxis de HOOP)
    - Reportar errores léxicos
    """
    
    def __init__(self):
        # Palabras reservadas del lenguaje HOOP
        self.keywords = {
            'class': TokenType.CLASS,
            'def': TokenType.DEF,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'elif': TokenType.ELIF,
            'for': TokenType.FOR,
            'while': TokenType.WHILE,
            'cycle': TokenType.CYCLE,
            'show': TokenType.SHOW,
            'input': TokenType.INPUT,
            'return': TokenType.RETURN,
            'break': TokenType.BREAK,
            'continue': TokenType.CONTINUE,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
            'in': TokenType.IN,
            'True': TokenType.TRUE,
            'False': TokenType.FALSE,
            'None': TokenType.NONE,
        }
        
        # Operadores de dos caracteres (deben verificarse antes que los de uno)
        self.two_char_operators = {
            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
        }
        
        # Operadores de un caracter
        self.single_char_operators = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '=': TokenType.ASSIGN,
            '<': TokenType.LESS,
            '>': TokenType.GREATER,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ',': TokenType.COMMA,
            ':': TokenType.COLON,
            ';': TokenType.SEMICOLON,
            '.': TokenType.DOT,
        }
        
        self.reset()
    
    def reset(self):
        """Reinicia el estado del lexer"""
        self.text = ""
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.indent_stack = [0]  # Stack para manejar niveles de indentación
    
    def tokenize(self, text: str) -> List[Token]:
        """
        Convierte el código fuente en una lista de tokens
        
        Args:
            text: Código fuente del programa HOOP
            
        Returns:
            Lista de tokens
            
        Raises:
            SyntaxError: Si se encuentra un caracter no reconocido
        """
        self.reset()
        self.text = text
        
        # TODO: Implementar la lógica de tokenización
        # 1. Recorrer caracter por caracter
        # 2. Identificar patrones (números, strings, identificadores)
        # 3. Manejar espacios en blanco e indentación
        # 4. Crear tokens apropiados
        
        while self.position < len(self.text):
            self._skip_whitespace()
            
            if self.position >= len(self.text):
                break
                
            # TODO: Implementar lógica para cada tipo de token
            # - Números
            # - Strings (con comillas simples y dobles)
            # - Identificadores y palabras reservadas
            # - Operadores
            # - Comentarios
            # - Saltos de línea e indentación
            
            self.position += 1  # Placeholder - remover cuando se implemente
        
        # Agregar token EOF al final
        self._add_token(TokenType.EOF, "")
        return self.tokens
    
    def _skip_whitespace(self):
        """Omite espacios en blanco (excepto saltos de línea)"""
        while (self.position < len(self.text) and 
               self.text[self.position] in ' \t'):
            if self.text[self.position] == '\t':
                self.column += 4  # Tratar tab como 4 espacios
            else:
                self.column += 1
            self.position += 1
    
    def _peek(self, offset: int = 0) -> str:
        """Obtiene el caracter en la posición actual + offset sin avanzar"""
        pos = self.position + offset
        if pos >= len(self.text):
            return '\0'
        return self.text[pos]
    
    def _advance(self) -> str:
        """Avanza al siguiente caracter y lo retorna"""
        if self.position >= len(self.text):
            return '\0'
        
        char = self.text[self.position]
        self.position += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
            
        return char
    
    def _add_token(self, token_type: TokenType, value: str):
        """Agrega un token a la lista"""
        token = Token(token_type, value, self.line, self.column - len(value))
        self.tokens.append(token)
    
    def _scan_number(self) -> Token:
        """
        Escanea un literal numérico (entero o flotante)
        
        TODO: Implementar
        - Detectar números enteros
        - Detectar números flotantes (con punto decimal)
        - Manejar números negativos
        """
        pass
    
    def _scan_string(self, quote_char: str) -> Token:
        """
        Escanea un literal string
        
        Args:
            quote_char: El caracter de comilla usado (' o ")
            
        TODO: Implementar
        - Manejar strings con comillas simples y dobles
        - Procesar secuencias de escape (\n, \t, \\, etc.)
        - Detectar strings no cerrados
        """
        pass
    
    def _scan_identifier(self) -> Token:
        """
        Escanea un identificador o palabra reservada
        
        TODO: Implementar
        - Identificar patrones válidos para nombres de variables/funciones
        - Distinguir entre identificadores y palabras reservadas
        - Validar que no empiecen con número
        """
        pass
    
    def _handle_indentation(self):
        """
        Maneja los tokens de indentación (INDENT/DEDENT)
        
        TODO: Implementar
        - Calcular nivel de indentación actual
        - Generar tokens INDENT cuando aumenta la indentación
        - Generar tokens DEDENT cuando disminuye
        - Manejar errores de indentación inconsistente
        """
        pass

# Función de utilidad para pruebas rápidas
def tokenize_hoop_code(code: str) -> List[Token]:
    """
    Función de conveniencia para tokenizar código HOOP
    
    Args:
        code: Código fuente en HOOP
        
    Returns:
        Lista de tokens
    """
    lexer = HoopLexer()
    return lexer.tokenize(code)

if __name__ == "__main__":
    # Ejemplo de uso básico
    sample_code = """
    def greet(name):
        show("Hello, " + name)
    
    greet("World")
    """
    
    lexer = HoopLexer()
    tokens = lexer.tokenize(sample_code)
    
    print("Tokens generados:")
    for token in tokens:
        print(f"{token.type.value}: '{token.value}' (línea {token.line}, columna {token.column})")
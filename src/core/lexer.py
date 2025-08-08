import re
from enum import Enum

#############################
# --- Elementos Lexicos --- #
#############################

# Palabras reservadas del lenguaje HOOP
RESERVADAS = {
    "mold",     # class
    "bond",     # interface
    "listing",  # enum
    "layout",   # struct
    "unit",     # package
    "when",     # if
    "otherwise", # else
    "cycle",    # for
    "repeat",   # while
    "halt",     # break
    "skip",     # continue
    "answer",   # return
    "select",   # switch
    "forge",    # new
    "self",     # this
    "void",     # null
    "parent",   # super
    "open",     # public
    "sealed",   # private
    "linked",   # protected
    "attempt",  # try
    "rescue",   # catch
    "ensure",   # finally
    "throw",    # throw
    "fixed",    # const
    "data",     # var
    "action",   # fun
    "display"   # print, printf
}

# Tipos de datos
TIPOS = {
    # Simples
    "logic",  # boolean
    "whole",  # integer
    "fract",  # decimal / float
    "text",   # string
    "char",
    # Compuestos
    "grid",   # matrix
    "chain"   # linked list
}

# Palabras pregonadas (built-in functions)
PALABRAS_PREGONADAS = {
    "length", "size", "type", "convert", "input", "output", 
    "read", "write", "open", "close", "max", "min", 
    "abs", "sqrt", "pow", "random"
}

# Delimitadores
DELIMITADORES = {
    '(': 'LPAREN',
    ')': 'RPAREN', 
    '{': 'LBRACE',
    '}': 'RBRACE',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    ';': 'SEMICOLON',
    ',': 'COMMA',
    '.': 'DOT',
    ':': 'COLON'
}

# Operadores
OPERADORES = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MULTIPLY',
    '/': 'DIVIDE',
    '%': 'MODULO',
    '=': 'ASSIGN',
    '==': 'EQUALS',
    '!=': 'NOT_EQUALS',
    '<': 'LESS_THAN',
    '>': 'GREATER_THAN',
    '<=': 'LESS_EQUAL',
    '>=': 'GREATER_EQUAL',
    '&&': 'AND',
    '||': 'OR',
    '!': 'NOT'
}

#############################
# --- Creador de Tokens --- #
#############################

# Tipos de tokens
class TokenType(Enum):
    # Literales
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    CHARACTER = "CHARACTER"
    BOOLEAN = "BOOLEAN"
    
    # Palabras clave
    KEYWORD = "KEYWORD"
    TYPE = "TYPE"
    BUILTIN = "BUILTIN"
    
    # Operadores y delimitadores
    OPERATOR = "OPERATOR"
    DELIMITER = "DELIMITER"
    
    # Comentarios y espacios
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"
    NEWLINE = "NEWLINE"
    
    # Control
    EOF = "EOF"
    ERROR = "ERROR"

# Clase Token (elemento léico)
class Token:
    def __init__(self, tipo, valor, linea, columna, posicion=0):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna
        self.posicion = posicion
    
    def __str__(self):
        return f"Token({self.tipo.name}, '{self.valor}', {self.linea}:{self.columna})"
    
    def __repr__(self):
        return self.__str__()

"""
Analizador Sintáctico para el lenguaje HOOP
==========================================

Este módulo se encarga de analizar la estructura sintáctica del código HOOP.
Recibe una lista de tokens del lexer y construye un Árbol de Sintaxis Abstracta (AST).

Proceso: Lista de tokens → AST (Abstract Syntax Tree)
"""

from typing import List, Optional, Union, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from core.lexer import Token, TokenType, HoopLexer

# ============================================================================
# NODOS DEL AST (Abstract Syntax Tree)
# ============================================================================

class ASTNode(ABC):
    """Clase base para todos los nodos del AST"""
    pass

class Expression(ASTNode):
    """Clase base para todas las expresiones"""
    pass

class Statement(ASTNode):
    """Clase base para todas las declaraciones/sentencias"""
    pass

# --- Expresiones ---

@dataclass
class LiteralExpression(Expression):
    """Representa un valor literal (número, string, booleano)"""
    value: Any
    token: Token

@dataclass
class IdentifierExpression(Expression):
    """Representa un identificador (nombre de variable)"""
    name: str
    token: Token

@dataclass
class BinaryExpression(Expression):
    """Representa una expresión binaria (a + b, a == b, etc.)"""
    left: Expression
    operator: Token
    right: Expression

@dataclass
class UnaryExpression(Expression):
    """Representa una expresión unaria (-x, not x)"""
    operator: Token
    operand: Expression

@dataclass
class CallExpression(Expression):
    """Representa una llamada a función"""
    function: Expression
    arguments: List[Expression]
    token: Token

@dataclass
class ListExpression(Expression):
    """Representa una lista [1, 2, 3]"""
    elements: List[Expression]
    token: Token

# --- Declaraciones/Sentencias ---

@dataclass
class ExpressionStatement(Statement):
    """Una expresión usada como sentencia"""
    expression: Expression

@dataclass
class AssignmentStatement(Statement):
    """Asignación de variable: x = 5"""
    target: IdentifierExpression
    value: Expression
    token: Token

@dataclass
class FunctionDeclaration(Statement):
    """Declaración de función: def name(params): body"""
    name: str
    parameters: List[str]
    body: List[Statement]
    token: Token

@dataclass
class ClassDeclaration(Statement):
    """Declaración de clase: class Name: body"""
    name: str
    body: List[Statement]
    token: Token

@dataclass
class IfStatement(Statement):
    """Declaración if: if condition: then_branch else: else_branch"""
    condition: Expression
    then_branch: List[Statement]
    else_branch: Optional[List[Statement]]
    token: Token

@dataclass
class WhileStatement(Statement):
    """Bucle while: while condition: body"""
    condition: Expression
    body: List[Statement]
    token: Token

@dataclass
class ForStatement(Statement):
    """Bucle for: for var in iterable: body"""
    variable: str
    iterable: Expression
    body: List[Statement]
    token: Token

@dataclass
class ReturnStatement(Statement):
    """Declaración return: return expression"""
    value: Optional[Expression]
    token: Token

@dataclass
class ShowStatement(Statement):
    """Declaración show: show(expression)"""
    expression: Expression
    token: Token

@dataclass
class BreakStatement(Statement):
    """Declaración break"""
    token: Token

@dataclass
class ContinueStatement(Statement):
    """Declaración continue"""
    token: Token

@dataclass
class Program(ASTNode):
    """Nodo raíz que representa todo el programa"""
    statements: List[Statement]

# ============================================================================
# ANALIZADOR SINTÁCTICO
# ============================================================================

class ParseError(Exception):
    """Excepción para errores de análisis sintáctico"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Error de sintaxis en línea {token.line}, columna {token.column}: {message}")

class HoopParser:
    """
    Analizador sintáctico para el lenguaje HOOP
    
    Implementa un parser recursivo descendente que construye un AST
    a partir de la lista de tokens proporcionada por el lexer.
    
    Responsabilidades:
    - Verificar que la secuencia de tokens siga las reglas gramaticales de HOOP
    - Construir un AST que represente la estructura del programa
    - Reportar errores de sintaxis con información de ubicación
    - Manejar precedencia de operadores
    """
    
    def __init__(self):
        self.tokens: List[Token] = []
        self.current = 0
    
    def parse(self, tokens: List[Token]) -> Program:
        """
        Analiza una lista de tokens y devuelve un AST
        
        Args:
            tokens: Lista de tokens del lexer
            
        Returns:
            Program: Nodo raíz del AST
            
        Raises:
            ParseError: Si hay errores de sintaxis
        """
        self.tokens = tokens
        self.current = 0
        
        statements = []
        
        while not self._is_at_end():
            if self._peek().type == TokenType.NEWLINE:
                self._advance()
                continue
                
            # TODO: Implementar parsing de cada tipo de declaración
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return Program(statements)
    
    def _parse_statement(self) -> Optional[Statement]:
        """
        Analiza una declaración/sentencia
        
        TODO: Implementar el análisis de:
        - Declaraciones de función (def)
        - Declaraciones de clase (class) 
        - Declaraciones de control de flujo (if, while, for)
        - Asignaciones (x = y)
        - Declaraciones de expresión
        - Declaraciones especiales (return, break, continue, show)
        """
        try:
            # Ignorar líneas vacías
            if self._peek().type == TokenType.NEWLINE:
                self._advance()
                return None
                
            # Declaración de función
            if self._match(TokenType.DEF):
                return self._parse_function_declaration()
            
            # Declaración de clase
            if self._match(TokenType.CLASS):
                return self._parse_class_declaration()
            
            # Declaración if
            if self._match(TokenType.IF):
                return self._parse_if_statement()
            
            # Declaración while
            if self._match(TokenType.WHILE):
                return self._parse_while_statement()
            
            # Declaración for
            if self._match(TokenType.FOR):
                return self._parse_for_statement()
            
            # Declaración return
            if self._match(TokenType.RETURN):
                return self._parse_return_statement()
            
            # Declaración show
            if self._match(TokenType.SHOW):
                return self._parse_show_statement()
            
            # Declaración break
            if self._match(TokenType.BREAK):
                return BreakStatement(self._previous())
            
            # Declaración continue
            if self._match(TokenType.CONTINUE):
                return ContinueStatement(self._previous())
            
            # Asignación o expresión
            return self._parse_assignment_or_expression()
            
        except ParseError:
            # Recuperación de errores: saltar al siguiente statement
            self._synchronize()
            return None
    
    def _parse_function_declaration(self) -> FunctionDeclaration:
        """
        Analiza una declaración de función
        
        Gramática: def IDENTIFIER(parameters): NEWLINE INDENT body DEDENT
        
        TODO: Implementar
        - Parsing del nombre de la función
        - Parsing de la lista de parámetros
        - Parsing del cuerpo de la función (con manejo de indentación)
        """
        # Placeholder - implementar lógica completa
        name = "placeholder"
        parameters = []
        body = []
        token = self._previous()
        return FunctionDeclaration(name, parameters, body, token)
    
    def _parse_class_declaration(self) -> ClassDeclaration:
        """
        Analiza una declaración de clase
        
        Gramática: class IDENTIFIER: NEWLINE INDENT body DEDENT
        
        TODO: Implementar
        """
        # Placeholder
        name = "placeholder"
        body = []
        token = self._previous()
        return ClassDeclaration(name, body, token)
    
    def _parse_if_statement(self) -> IfStatement:
        """
        Analiza una declaración if
        
        Gramática: if expression: NEWLINE INDENT body DEDENT [else: NEWLINE INDENT body DEDENT]
        
        TODO: Implementar
        - Parsing de la condición
        - Parsing del bloque then
        - Parsing opcional del bloque else
        - Manejo de elif
        """
        # Placeholder
        condition = LiteralExpression(True, self._previous())
        then_branch = []
        else_branch = None
        token = self._previous()
        return IfStatement(condition, then_branch, else_branch, token)
    
    def _parse_while_statement(self) -> WhileStatement:
        """
        Analiza una declaración while
        
        TODO: Implementar
        """
        # Placeholder
        condition = LiteralExpression(True, self._previous())
        body = []
        token = self._previous()
        return WhileStatement(condition, body, token)
    
    def _parse_for_statement(self) -> ForStatement:
        """
        Analiza una declaración for
        
        Gramática: for IDENTIFIER in expression: NEWLINE INDENT body DEDENT
        
        TODO: Implementar
        """
        # Placeholder
        variable = "placeholder"
        iterable = LiteralExpression([], self._previous())
        body = []
        token = self._previous()
        return ForStatement(variable, iterable, body, token)
    
    def _parse_return_statement(self) -> ReturnStatement:
        """
        Analiza una declaración return
        
        TODO: Implementar
        """
        # Placeholder
        value = None
        token = self._previous()
        return ReturnStatement(value, token)
    
    def _parse_show_statement(self) -> ShowStatement:
        """
        Analiza una declaración show
        
        TODO: Implementar
        """
        # Placeholder
        expression = LiteralExpression("", self._previous())
        token = self._previous()
        return ShowStatement(expression, token)
    
    def _parse_assignment_or_expression(self) -> Statement:
        """
        Analiza una asignación o una expresión
        
        TODO: Implementar
        - Detectar si es asignación (IDENTIFIER = expression)
        - Si no, tratar como expresión
        """
        # Placeholder
        expr = self._parse_expression()
        return ExpressionStatement(expr)
    
    def _parse_expression(self) -> Expression:
        """
        Analiza una expresión
        
        Implementa precedencia de operadores:
        1. or
        2. and  
        3. not
        4. ==, !=, <, >, <=, >=
        5. +, -
        6. *, /, %
        7. unary -, not
        8. call, indexing
        9. primary (literals, identifiers, parentheses)
        
        TODO: Implementar cada nivel de precedencia
        """
        return self._parse_or()
    
    def _parse_or(self) -> Expression:
        """Analiza expresiones OR (menor precedencia)"""
        # TODO: Implementar
        return self._parse_and()
    
    def _parse_and(self) -> Expression:
        """Analiza expresiones AND"""
        # TODO: Implementar
        return self._parse_equality()
    
    def _parse_equality(self) -> Expression:
        """Analiza expresiones de igualdad (==, !=)"""
        # TODO: Implementar
        return self._parse_comparison()
    
    def _parse_comparison(self) -> Expression:
        """Analiza expresiones de comparación (<, >, <=, >=)"""
        # TODO: Implementar
        return self._parse_term()
    
    def _parse_term(self) -> Expression:
        """Analiza términos (+ -)"""
        # TODO: Implementar
        return self._parse_factor()
    
    def _parse_factor(self) -> Expression:
        """Analiza factores (*, /, %)"""
        # TODO: Implementar
        return self._parse_unary()
    
    def _parse_unary(self) -> Expression:
        """Analiza expresiones unarias (-, not)"""
        # TODO: Implementar
        return self._parse_call()
    
    def _parse_call(self) -> Expression:
        """Analiza llamadas a función y acceso a índices"""
        # TODO: Implementar
        return self._parse_primary()
    
    def _parse_primary(self) -> Expression:
        """
        Analiza expresiones primarias (literales, identificadores, paréntesis)
        
        TODO: Implementar
        - Números
        - Strings
        - Booleanos (True, False)
        - None
        - Identificadores
        - Expresiones entre paréntesis
        - Listas
        """
        # Placeholder - devolver literal simple
        if self._is_at_end():
            raise ParseError("Expresión esperada", self._peek())
        
        token = self._advance()
        return LiteralExpression(token.value, token)
    
    # ========================================================================
    # MÉTODOS AUXILIARES
    # ========================================================================
    
    def _match(self, *types: TokenType) -> bool:
        """Verifica si el token actual coincide con alguno de los tipos dados"""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _check(self, token_type: TokenType) -> bool:
        """Verifica si el token actual es del tipo dado"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _advance(self) -> Token:
        """Consume el token actual y devuelve el anterior"""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """Verifica si hemos llegado al final de los tokens"""
        return self._peek().type == TokenType.EOF
    
    def _peek(self) -> Token:
        """Devuelve el token actual sin consumirlo"""
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """Devuelve el token anterior"""
        return self.tokens[self.current - 1]
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """
        Consume un token del tipo esperado o lanza error
        
        Args:
            token_type: Tipo de token esperado
            message: Mensaje de error si no coincide
            
        Returns:
            Token consumido
            
        Raises:
            ParseError: Si el token no es del tipo esperado
        """
        if self._check(token_type):
            return self._advance()
        
        current_token = self._peek()
        raise ParseError(message, current_token)
    
    def _synchronize(self):
        """
        Recuperación de errores: avanza hasta encontrar el inicio de la siguiente declaración
        """
        self._advance()
        
        while not self._is_at_end():
            if self._previous().type == TokenType.NEWLINE:
                return
            
            # Palabras clave que típicamente inician declaraciones
            if self._peek().type in [
                TokenType.CLASS, TokenType.DEF, TokenType.IF,
                TokenType.FOR, TokenType.WHILE, TokenType.RETURN
            ]:
                return
            
            self._advance()

# ============================================================================
# FUNCIÓN DE UTILIDAD
# ============================================================================

def parse_hoop_code(code: str) -> Program:
    """
    Función de conveniencia para analizar código HOOP completo
    
    Args:
        code: Código fuente en HOOP
        
    Returns:
        Program: AST del programa
    """
    # Tokenizar primero
    lexer = HoopLexer()
    tokens = lexer.tokenize(code)
    
    # Luego analizar
    parser = HoopParser()
    return parser.parse(tokens)

if __name__ == "__main__":
    # Ejemplo de uso básico
    sample_code = """
    def greet(name):
        show("Hello, " + name)
    
    x = 5
    if x > 0:
        greet("World")
    """
    
    try:
        ast = parse_hoop_code(sample_code)
        print("AST generado exitosamente")
        print(f"Número de declaraciones: {len(ast.statements)}")
    except ParseError as e:
        print(f"Error de sintaxis: {e}")
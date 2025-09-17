
"""
Parser Oficial HOOP - Implementación basada en gramática BNF oficial
"""

from core.lexer import TokenType
from core.ast_nodes import (
    ASTNode, ProgramaNode, DeclaracionNode, FuncionNode, ParametroNode,
    ClaseNode, IfStatementNode, CycleStatementNode, OperacionNode,
    LiteralNode, IdentificadorNode, LlamadaFuncionNode, AttributeAccessNode,
    AssignmentNode, ReturnNode, DisplayNode
)

class ParseError(Exception):
    """Excepción para errores de parsing"""
    def __init__(self, mensaje, token=None):
        self.mensaje = mensaje
        self.token = token
        super().__init__(mensaje)

class ParserOficial:
    """Parser que sigue la gramática BNF oficial de HOOP"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def error(self, mensaje):
        """Lanza un error de parsing con información del token actual"""
        token_info = f" en línea {self.current_token.linea}" if self.current_token else ""
        raise ParseError(f"{mensaje}{token_info}", self.current_token)
    
    def advance(self):
        """Avanza al siguiente token"""
        if self.current < len(self.tokens) - 1:
            self.current += 1
            self.current_token = self.tokens[self.current]
        return self.current_token
    
    def peek(self):
        """Mira el siguiente token sin avanzar"""
        if self.current + 1 < len(self.tokens):
            return self.tokens[self.current + 1]
        return None
    
    def match(self, tipo, valor=None):
        """Verifica si el token actual coincide con el tipo y valor especificados"""
        if not self.current_token:
            return False
        if self.current_token.tipo != tipo:
            return False
        if valor is not None and self.current_token.valor != valor:
            return False
        return True
    
    def expect(self, tipo, valor=None):
        """Espera un token específico y avanza, o lanza error"""
        if not self.match(tipo, valor):
            expected = f"{tipo.value}"
            if valor:
                expected += f" '{valor}'"
            actual = f"{self.current_token.tipo.value} '{self.current_token.valor}'" if self.current_token else "EOF"
            self.error(f"Esperado {expected}, encontrado {actual}")
        
        token = self.current_token
        self.advance()
        return token
    
    def skip_newlines(self):
        """Salta tokens de nueva línea, comentarios y espacios en blanco"""
        while (self.current_token and 
               self.current_token.tipo in [TokenType.NEWLINE, TokenType.WHITESPACE, TokenType.COMMENT]):
            self.advance()
    
    # ==========================================
    # IMPLEMENTACION DE GRAMaTICA BNF OFICIAL
    # ==========================================
    
    def parse(self):
        """<programa> ::= (<declaracion> | <clase> | <funcion> | <statement>)* <EOF>"""
        declaraciones = []
        self.skip_newlines()
        
        while self.current_token and self.current_token.tipo != TokenType.EOF:
            self.skip_newlines()
            if not self.current_token or self.current_token.tipo == TokenType.EOF:
                break
                
            if self.match(TokenType.KEYWORD, "data"):
                declaraciones.append(self.parse_declaracion())
            elif self.match(TokenType.KEYWORD, "mold"):
                declaraciones.append(self.parse_clase())
            elif self.match(TokenType.KEYWORD, "action"):
                declaraciones.append(self.parse_funcion())
            else:
                declaraciones.append(self.parse_statement())
            
            self.skip_newlines()
        
        return ProgramaNode(declaraciones)
    
    def parse_declaracion(self):
        """<declaracion> ::= "data" <IDENTIFIER> "set" <expresion> ";" """
        self.expect(TokenType.KEYWORD, "data")
        nombre = self.expect(TokenType.IDENTIFIER).valor
        self.expect(TokenType.WORD_OPERATOR, "set")
        valor = self.parse_expresion()
        self.expect(TokenType.DELIMITER, ";")
        return DeclaracionNode(nombre, valor)
    
    def parse_funcion(self):
        """<funcion> ::= "action" <IDENTIFIER> "(" <parametros>? ")" "{" <statements> "}" """
        self.expect(TokenType.KEYWORD, "action")
        nombre = self.expect(TokenType.IDENTIFIER).valor
        self.expect(TokenType.DELIMITER, "(")
        
        parametros = []
        if not self.match(TokenType.DELIMITER, ")"):
            parametros = self.parse_parametros()
        
        self.expect(TokenType.DELIMITER, ")")
        self.expect(TokenType.DELIMITER, "{")
        self.skip_newlines()
        cuerpo = self.parse_statements()
        self.expect(TokenType.DELIMITER, "}")
        
        return FuncionNode(nombre, parametros, cuerpo)
    
    def parse_parametros(self):
        """<parametros> ::= <TIPO> <IDENTIFIER> ("," <TIPO> <IDENTIFIER>)*"""
        parametros = []
        
        # Primer parametro
        tipo = self.expect(TokenType.TYPE).valor
        nombre = self.expect(TokenType.IDENTIFIER).valor
        parametros.append(ParametroNode(tipo, nombre))
        
        # Parametros adicionales
        while self.match(TokenType.DELIMITER, ","):
            self.advance()
            tipo = self.expect(TokenType.TYPE).valor
            nombre = self.expect(TokenType.IDENTIFIER).valor
            parametros.append(ParametroNode(tipo, nombre))
        
        return parametros
    
    def parse_clase(self):
        """<clase> ::= "mold" <IDENTIFIER> "{" <clase_cuerpo> "}" """
        self.expect(TokenType.KEYWORD, "mold")
        nombre = self.expect(TokenType.IDENTIFIER).valor
        self.expect(TokenType.DELIMITER, "{")
        self.skip_newlines()
        cuerpo = self.parse_clase_cuerpo()
        self.expect(TokenType.DELIMITER, "}")
        return ClaseNode(nombre, cuerpo)
    
    def parse_clase_cuerpo(self):
        """<clase_cuerpo> ::= (<atributo> | <metodo>)*"""
        elementos = []
        while self.current_token and not self.match(TokenType.DELIMITER, "}"):
            self.skip_newlines()
            if self.match(TokenType.DELIMITER, "}"):
                break
                
            if self.match(TokenType.KEYWORD, "data"):
                elementos.append(self.parse_declaracion())
            elif self.match(TokenType.KEYWORD, "action"):
                elementos.append(self.parse_funcion())
            else:
                self.error(f"Elemento de clase inválido: {self.current_token.valor}")
            
            self.skip_newlines()
        return elementos
    
    def parse_statements(self):
        """<statements> ::= (<statement>)*"""
        statements = []
        while self.current_token and not self.match(TokenType.DELIMITER, "}"):
            self.skip_newlines()
            if self.match(TokenType.DELIMITER, "}"):
                break
            statements.append(self.parse_statement())
            self.skip_newlines()
        return statements
    
    def parse_statement(self):
        """<statement> ::= <if_statement> | <cycle_statement> | <simple_statement> | <declaracion>"""
        if self.match(TokenType.KEYWORD, "when"):
            return self.parse_if_statement()
        elif self.match(TokenType.KEYWORD, "cycle"):
            return self.parse_cycle_statement()
        elif self.match(TokenType.KEYWORD, "data"):
            return self.parse_declaracion()
        elif self.match(TokenType.KEYWORD, "answer"):
            return self.parse_return_statement()
        elif self.match(TokenType.KEYWORD, "display"):
            return self.parse_display_statement()
        else:
            return self.parse_simple_statement()
    
    def parse_if_statement(self):
        """<if_statement> ::= "when" <condicion> "{" <statements> "}" ["otherwise" "{" <statements> "}"]"""
        self.expect(TokenType.KEYWORD, "when")
        condicion = self.parse_expresion()
        self.expect(TokenType.DELIMITER, "{")
        self.skip_newlines()
        bloque_then = self.parse_statements()
        self.expect(TokenType.DELIMITER, "}")
        
        bloque_else = None
        if self.match(TokenType.KEYWORD, "otherwise"):
            self.advance()
            self.expect(TokenType.DELIMITER, "{")
            self.skip_newlines()
            bloque_else = self.parse_statements()
            self.expect(TokenType.DELIMITER, "}")
        
        return IfStatementNode(condicion, bloque_then, bloque_else)
    
    def parse_cycle_statement(self):
        """<cycle_statement> ::= "cycle" <IDENTIFIER> ["from" <expresion>] ["to" <expresion>] "{" <statements> "}" """
        self.expect(TokenType.KEYWORD, "cycle")
        variable = self.expect(TokenType.IDENTIFIER).valor
        
        inicio = None
        if self.match(TokenType.KEYWORD, "from"):
            self.advance()
            inicio = self.parse_expresion()
        
        fin = None
        if self.match(TokenType.KEYWORD, "to"):
            self.advance()
            fin = self.parse_expresion()
        
        self.expect(TokenType.DELIMITER, "{")
        self.skip_newlines()
        cuerpo = self.parse_statements()
        self.expect(TokenType.DELIMITER, "}")
        
        return CycleStatementNode(variable, inicio, fin, cuerpo)
    
    def parse_return_statement(self):
        """return statement: answer <expresion>;"""
        self.expect(TokenType.KEYWORD, "answer")
        valor = self.parse_expresion()
        self.expect(TokenType.DELIMITER, ";")
        return ReturnNode(valor)
    
    def parse_display_statement(self):
        """display statement: display <expresion>;"""
        self.expect(TokenType.KEYWORD, "display")
        expresion = self.parse_expresion()
        self.expect(TokenType.DELIMITER, ";")
        return DisplayNode(expresion)
    
    def parse_simple_statement(self):
        """<simple_statement> ::= <asignacion> | <expresion> ";" """
        # Verificar si es una asignacion (identificador set expresion)
        if (self.match(TokenType.IDENTIFIER) or 
            (self.match(TokenType.KEYWORD) and self.current_token.valor == "self")):
            
            
            checkpoint = self.current
            
            # Intentar parsear como asignacion
            try:
             
                if self.current_token.valor == "self":
                    self.advance()  # consumir 'self'
                    self.expect(TokenType.DELIMITER, ".")
                    atributo = self.expect(TokenType.IDENTIFIER).valor
                    izquierda = AttributeAccessNode(IdentificadorNode("self"), atributo)
                else:
                    nombre = self.current_token.valor
                    self.advance()
                    izquierda = IdentificadorNode(nombre)
                
                # Verificar si es asignación con 'set'
                if self.match(TokenType.WORD_OPERATOR, "set"):
                    self.advance()  # consumir 'set'
                    valor = self.parse_expresion()
                    self.expect(TokenType.DELIMITER, ";")
                    return AssignmentNode(izquierda, valor)
                else:
                    # No es asignacion, hacer backtrack y parsear como expresion
                    self.current = checkpoint
                    self.current_token = self.tokens[self.current] if self.current < len(self.tokens) else None
                    
            except:
                # Error en parsing, hacer backtrack
                self.current = checkpoint
                self.current_token = self.tokens[self.current] if self.current < len(self.tokens) else None
        
       
        expresion = self.parse_expresion()
        self.expect(TokenType.DELIMITER, ";")
        return expresion
    
    # ==========================================
    # PARSING DE EXPRESIONES CON PALABRAS
    # ==========================================
    
    def parse_expresion(self):
        """<expresion> ::= <operacion> | <literal>"""
        return self.parse_operacion_logica()
    
    def parse_operacion_logica(self):
        """Operaciones lógicas: and, or"""
        left = self.parse_operacion_comparacion()
        
        while (self.current_token and 
               self.current_token.tipo == TokenType.WORD_OPERATOR and
               self.current_token.valor in ["and", "or"]):
            operador = self.current_token.valor
            self.advance()
            right = self.parse_operacion_comparacion()
            left = OperacionNode(left, operador, right)
        
        return left
    
    def parse_operacion_comparacion(self):
        """Operaciones de comparación: equals, greater, less, etc."""
        left = self.parse_operacion_aritmetica()
        
        while (self.current_token and 
               self.current_token.tipo == TokenType.WORD_OPERATOR and
               self.current_token.valor in ["equals", "notequals", "greater", "less", "greatereq", "lesseq"]):
            operador = self.current_token.valor
            self.advance()
            right = self.parse_operacion_aritmetica()
            left = OperacionNode(left, operador, right)
        
        return left
    
    def parse_operacion_aritmetica(self):
        """Operaciones aritméticas: plus, minus"""
        left = self.parse_operacion_multiplicativa()
        
        while (self.current_token and 
               self.current_token.tipo == TokenType.WORD_OPERATOR and
               self.current_token.valor in ["plus", "minus"]):
            operador = self.current_token.valor
            self.advance()
            right = self.parse_operacion_multiplicativa()
            left = OperacionNode(left, operador, right)
        
        return left
    
    def parse_operacion_multiplicativa(self):
        """Operaciones multiplicativas: times, divide, mod"""
        left = self.parse_operacion_unaria()
        
        while (self.current_token and 
               self.current_token.tipo == TokenType.WORD_OPERATOR and
               self.current_token.valor in ["times", "divide", "mod"]):
            operador = self.current_token.valor
            self.advance()
            right = self.parse_operacion_unaria()
            left = OperacionNode(left, operador, right)
        
        return left
    
    def parse_operacion_unaria(self):
        """Operaciones unarias: not, minus unario"""
        if (self.current_token and 
            self.current_token.tipo == TokenType.WORD_OPERATOR and
            self.current_token.valor in ["not", "minus"]):
            operador = self.current_token.valor
            self.advance()
            operando = self.parse_operacion_unaria()
            return OperacionNode(None, operador, operando)
        
        return self.parse_primary()
    
    def parse_primary(self):
        """<literal> ::= <STRING> | <NUMBER> | <BOOLEAN> | <IDENTIFIER> | <llamada_funcion>"""
        if self.match(TokenType.STRING):
            valor = self.current_token.valor
            self.advance()
            return LiteralNode("STRING", valor)
        
        elif self.match(TokenType.NUMBER):
            valor = self.current_token.valor
            self.advance()
            return LiteralNode("NUMBER", valor)
        
        elif self.match(TokenType.BOOLEAN):
            valor = self.current_token.valor
            self.advance()
            return LiteralNode("BOOLEAN", valor)
        
        elif self.match(TokenType.IDENTIFIER) or self.match(TokenType.BUILTIN) or (self.match(TokenType.KEYWORD) and self.current_token.valor == "self"):
            nombre = self.current_token.valor
            self.advance()
            
            # Manejar acceso a atributos
            if self.match(TokenType.DELIMITER, "."):
                self.advance() 
                atributo = self.expect(TokenType.IDENTIFIER).valor
                return AttributeAccessNode(IdentificadorNode(nombre), atributo)
            
            # Verificar si es una llamada a funcion
            elif self.match(TokenType.DELIMITER, "("):
                self.advance() 
                argumentos = []
                
                if not self.match(TokenType.DELIMITER, ")"):
                    argumentos.append(self.parse_expresion())
                    while self.match(TokenType.DELIMITER, ","):
                        self.advance()  
                        argumentos.append(self.parse_expresion())
                
                self.expect(TokenType.DELIMITER, ")")
                return LlamadaFuncionNode(nombre, argumentos)
            
            else:
                return IdentificadorNode(nombre)
        
        elif self.match(TokenType.DELIMITER, "("):
            self.advance()  
            expresion = self.parse_expresion()
            self.expect(TokenType.DELIMITER, ")")
            return expresion
        
        else:
            self.error(f"Expresión inválida: {self.current_token.valor if self.current_token else 'EOF'}")

def parse_hoop_oficial(tokens):
    """Función principal para parsing de código HOOP"""
    parser = ParserOficial(tokens)
    return parser.parse()

def parse_tokens(tokens):
    """Función de compatibilidad con la interfaz GUI existente"""
    try:
        parser = ParserOficial(tokens)
        ast = parser.parse()
        return ast, []  # Sin errores
    except ParseError as e:
        return None, [str(e)]  # AST nulo, lista de errores
    except Exception as e:
        return None, [f"Error inesperado: {str(e)}"]
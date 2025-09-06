#!/usr/bin/env python3
"""
Nodos del Árbol de Sintaxis Abstracta (AST) para HOOP
Implementación basada en las especificaciones oficiales HOOP.pdf
"""

class ASTNode:
    """Clase base para todos los nodos del AST"""
    pass

class ProgramaNode(ASTNode):
    """<programa> ::= (<declaracion> | <clase> | <funcion> | <statement>)* <EOF>"""
    def __init__(self, declaraciones):
        self.declaraciones = declaraciones
    
    def __repr__(self):
        return f"Programa({len(self.declaraciones)} elementos)"

class DeclaracionNode(ASTNode):
    """<declaracion> ::= "data" <IDENTIFIER> "set" <expresion> ";" """
    def __init__(self, nombre, valor):
        self.nombre = nombre
        self.valor = valor
    
    def __repr__(self):
        return f"Declaracion({self.nombre} = {self.valor})"

class FuncionNode(ASTNode):
    """<funcion> ::= "action" <IDENTIFIER> "(" <parametros>? ")" "{" <statements> "}" """
    def __init__(self, nombre, parametros, cuerpo):
        self.nombre = nombre
        self.parametros = parametros if parametros else []
        self.cuerpo = cuerpo
    
    def __repr__(self):
        params = f"{len(self.parametros)} parámetros" if self.parametros else "sin parámetros"
        return f"Funcion({self.nombre}, {params})"

class ParametroNode(ASTNode):
    """<parametros> ::= <TIPO> <IDENTIFIER> ("," <TIPO> <IDENTIFIER>)*"""
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre
    
    def __repr__(self):
        return f"Parametro({self.tipo} {self.nombre})"

class ClaseNode(ASTNode):
    """<clase> ::= "mold" <IDENTIFIER> "{" <clase_cuerpo> "}" """
    def __init__(self, nombre, cuerpo):
        self.nombre = nombre
        self.cuerpo = cuerpo
    
    def __repr__(self):
        return f"Clase({self.nombre}, {len(self.cuerpo)} elementos)"

class IfStatementNode(ASTNode):
    """<if_statement> ::= "when" <condicion> "{" <statements> "}" ["otherwise" "{" <statements> "}"]"""
    def __init__(self, condicion, bloque_then, bloque_else=None):
        self.condicion = condicion
        self.bloque_then = bloque_then
        self.bloque_else = bloque_else
    
    def __repr__(self):
        else_part = " con else" if self.bloque_else else ""
        return f"If({self.condicion}{else_part})"

class CycleStatementNode(ASTNode):
    """<cycle_statement> ::= "cycle" <IDENTIFIER> ["from" <expresion>] ["to" <expresion>] "{" <statements> "}" """
    def __init__(self, variable, inicio, fin, cuerpo):
        self.variable = variable
        self.inicio = inicio
        self.fin = fin
        self.cuerpo = cuerpo
    
    def __repr__(self):
        return f"Cycle({self.variable}, {self.inicio} to {self.fin})"

class OperacionNode(ASTNode):
    """<operacion> ::= <IDENTIFIER> <OPERADOR> <IDENTIFIER>"""
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha
    
    def __repr__(self):
        return f"Operacion({self.izquierda} {self.operador} {self.derecha})"

class IdentificadorNode(ASTNode):
    def __init__(self, nombre):
        self.nombre = nombre
    
    def __repr__(self):
        return f"Id({self.nombre})"

class AttributeAccessNode(ASTNode):
    def __init__(self, objeto, atributo):
        self.objeto = objeto
        self.atributo = atributo
    
    def __repr__(self):
        return f"{self.objeto}.{self.atributo}"

class AssignmentNode(ASTNode):
    def __init__(self, izquierda, valor):
        self.izquierda = izquierda
        self.valor = valor
    
    def __repr__(self):
        return f"Assignment({self.izquierda} = {self.valor})"

class LiteralNode(ASTNode):
    """<literal> ::= <STRING> | <NUMBER> | <BOOLEAN>"""
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor
    
    def __repr__(self):
        return f"Literal({self.tipo}: {self.valor})"

class IdentificadorNode(ASTNode):
    """Referencia a una variable o identificador"""
    def __init__(self, nombre):
        self.nombre = nombre
    
    def __repr__(self):
        return f"Id({self.nombre})"

class LlamadaFuncionNode(ASTNode):
    """Llamada a función: nombre(argumentos)"""
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos if argumentos else []
    
    def __repr__(self):
        return f"Llamada({self.nombre}, {len(self.argumentos)} args)"

class AccesoMiembroNode(ASTNode):
    """Acceso a miembro: objeto.miembro"""
    def __init__(self, objeto, miembro):
        self.objeto = objeto
        self.miembro = miembro
    
    def __repr__(self):
        return f"Acceso({self.objeto}.{self.miembro})"

class BloqueNode(ASTNode):
    """Bloque de statements: { ... }"""
    def __init__(self, statements):
        self.statements = statements if statements else []
    
    def __repr__(self):
        return f"Bloque({len(self.statements)} statements)"

class ReturnNode(ASTNode):
    """Statement de retorno: answer <expresion>;"""
    def __init__(self, valor):
        self.valor = valor
    
    def __repr__(self):
        return f"Return({self.valor})"

class DisplayNode(ASTNode):
    """Statement de impresión: display <expresion>;"""
    def __init__(self, expresion):
        self.expresion = expresion
    
    def __repr__(self):
        return f"Display({self.expresion})"

class AsignacionNode(ASTNode):
    """Asignación: variable set valor;"""
    def __init__(self, variable, valor):
        self.variable = variable
        self.valor = valor
    
    def __repr__(self):
        return f"Asignacion({self.variable} = {self.valor})"

# Excepción para errores de parsing
class ParseError(Exception):
    def __init__(self, mensaje, token=None):
        self.mensaje = mensaje
        self.token = token
        super().__init__(self.mensaje)
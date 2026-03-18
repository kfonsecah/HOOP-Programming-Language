#!/usr/bin/env python3

class ASTNode:
    """Clase base abstracta para todos los nodos del AST
    
    Todos los nodos heredan de esta clase y deben implementar __repr__
    para facilitar la depuracionn.
    """
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

class ConstanteNode(ASTNode):
    """<constante> ::= "fixed" <IDENTIFIER> "set" <expresion> ";" """
    def __init__(self, nombre, valor):
        self.nombre = nombre
        self.valor = valor
    
    def __repr__(self):
        return f"Constante({self.nombre} = {self.valor})"

class FuncionNode(ASTNode):
    """<funcion> ::= "action" <IDENTIFIER> "(" <parametros>? ")" "{" <statements> "}" """
    def __init__(self, nombre, parametros, cuerpo):
        self.nombre = nombre
        self.parametros = parametros if parametros else []
        self.cuerpo = cuerpo
    
    def __repr__(self):
        params = f"{len(self.parametros)} parametros" if self.parametros else "sin parametros"
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
    """Nodo para estructuras condicionales
    
    Sintaxis: when <condicion> { <statements> } [otherwise { <statements> }]
    Gramatica: <if_statement> ::= "when" <condicion> "{" <statements> "}" ["otherwise" "{" <statements> "}"]
    """
    def __init__(self, condicion, bloque_then, bloque_else=None):
        self.condicion = condicion
        self.bloque_then = bloque_then
        self.bloque_else = bloque_else
    
    def __repr__(self):
        else_part = " con else" if self.bloque_else else ""
        return f"If({self.condicion}{else_part})"

class CycleStatementNode(ASTNode):
    """Nodo para bucles iterativos
    
    Sintaxis: cycle <variable> [from <inicio>] [to <fin>] { <statements> }
    Gramatica: <cycle_statement> ::= "cycle" <IDENTIFIER> ["from" <expresion>] ["to" <expresion>] "{" <statements> "}"
    """
    def __init__(self, variable, inicio, fin, cuerpo):
        self.variable = variable
        self.inicio = inicio
        self.fin = fin
        self.cuerpo = cuerpo
    
    def __repr__(self):
        return f"Cycle({self.variable}, {self.inicio} to {self.fin})"

class RepeatStatementNode(ASTNode):
    """Nodo para bucles tipo while: repeat <condicion> { <statements> }"""
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo
    
    def __repr__(self):
        return f"Repeat({self.condicion})"

class OperacionNode(ASTNode):
    """Nodo para operaciones binarias
    """
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha
    
    def __repr__(self):
        if self.izquierda is None:
            return f"Operacion({self.operador} {self.derecha})"
        return f"Operacion({self.izquierda} {self.operador} {self.derecha})"

class LiteralNode(ASTNode):
    """Nodo para valores literales
       STRING, NUMBER, BOOLEAN, CHARACTER
    """
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor
    
    def __repr__(self):
        return f"Literal({self.tipo}: {self.valor})"

class IdentificadorNode(ASTNode):
    """Nodo para identificadores (variables, funciones, clases)
    """
    def __init__(self, nombre):
        self.nombre = nombre
    
    def __repr__(self):
        return f"Id({self.nombre})"

class LlamadaFuncionNode(ASTNode):
    """Nodo para llamadas a funcion o metodo
    """
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos if argumentos else []
    
    def __repr__(self):
        return f"Llamada({self.nombre}, {len(self.argumentos)} args)"

class AccesoMiembroNode(ASTNode):
    """Nodo para acceso a atributos o metodos
    """
    def __init__(self, objeto, miembro):
        self.objeto = objeto
        self.miembro = miembro
    
    def __repr__(self):
        return f"Acceso({self.objeto}.{self.miembro})"


AttributeAccessNode = AccesoMiembroNode

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
    """
    
    Sintaxis: display <expresion>;
    """
    def __init__(self, expresion):
        self.expresion = expresion
    
    def __repr__(self):
        return f"Display({self.expresion})"

class AsignacionNode(ASTNode):
    """Nodo para asignacion
    """
    def __init__(self, variable, valor):
        self.variable = variable
        self.valor = valor
    
    def __repr__(self):
        return f"Asignacion({self.variable} = {self.valor})"

AssignmentNode = AsignacionNode

class OperacionUnaria(ASTNode):
    """Nodo para operaciones unarias
    Sintaxis: operador <expresion>
    """
    def __init__(self, operador, expresion):
        self.operador = operador
        self.expresion = expresion
    
    def __repr__(self):
        return f"OperacionUnaria({self.operador} {self.expresion})"

class ForgeNode(ASTNode):
    """Nodo para objetos
    
    Sintaxis: forge Clase(arg1, arg2, ...)
    """
    def __init__(self, clase, argumentos):
        self.clase = clase
        self.argumentos = argumentos if argumentos else []
    
    def __repr__(self):
        return f"Forge({self.clase}, {len(self.argumentos)} args)"

class AsignacionMiembroNode(ASTNode):
    """Nodo para asignacion a atributo
    
    Sintaxis: objeto.atributo set valor;
    """
    def __init__(self, objeto, miembro, valor):
        self.objeto = objeto
        self.miembro = miembro
        self.valor = valor
    
    def __repr__(self):
        return f"AsignacionMiembro({self.objeto}.{self.miembro} = {self.valor})"

class LlamadaMetodoNode(ASTNode):
    """Nodo para llamada a metodo
    
    Sintaxis: objeto.metodo(arg1, arg2, ...)
    """
    def __init__(self, objeto, metodo, argumentos):
        self.objeto = objeto
        self.metodo = metodo
        self.argumentos = argumentos if argumentos else []
    
    def __repr__(self):
        return f"LlamadaMetodo({self.objeto}.{self.metodo}, {len(self.argumentos)} args)"

DisplayStatementNode = DisplayNode
ReturnStatementNode = ReturnNode

class SelectCaseNode(ASTNode):
    """Caso dentro de select"""
    def __init__(self, valor, cuerpo):
        self.valor = valor
        self.cuerpo = cuerpo if cuerpo else []
    
    def __repr__(self):
        return f"Case({self.valor})"

class SelectStatementNode(ASTNode):
    """Sentencia select/case"""
    def __init__(self, expresion, casos, default):
        self.expresion = expresion
        self.casos = casos if casos else []
        self.default = default if default else []
    
    def __repr__(self):
        return f"Select({len(self.casos)} casos)"

class TryStatementNode(ASTNode):
    """Bloque attempt/rescue/ensure"""
    def __init__(self, bloque_try, rescue_identificador, bloque_rescue, bloque_ensure):
        self.bloque_try = bloque_try if bloque_try else []
        self.rescue_identificador = rescue_identificador
        self.bloque_rescue = bloque_rescue if bloque_rescue else []
        self.bloque_ensure = bloque_ensure if bloque_ensure else []
    
    def __repr__(self):
        return "TryStatement()"

class ThrowNode(ASTNode):
    """throw expresion;"""
    def __init__(self, expresion):
        self.expresion = expresion
    
    def __repr__(self):
        return f"Throw({self.expresion})"

class BreakNode(ASTNode):
    """halt;"""
    def __repr__(self):
        return "Break()"

class ContinueNode(ASTNode):
    """skip;"""
    def __repr__(self):
        return "Continue()"

class ParseError(Exception):
    def __init__(self, mensaje, token=None):
        self.mensaje = mensaje
        self.token = token
        super().__init__(self.mensaje)

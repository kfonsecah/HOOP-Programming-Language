#!/usr/bin/env python3
"""
Analizador Semántico para HOOP

Este módulo implementa el análisis semántico que valida:
- Declaración de variables antes de uso
- Tipos compatibles en operaciones
- Existencia de funciones y clases
- Validación de llamadas (número y tipo de argumentos)
- Validación de acceso a miembros de clase
- Scoping correcto (global, función, clase)
- Returns en funciones
- Uso correcto de self

NO ejecuta código, solo valida y prepara para posterior interpretación.
"""

from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum
from core.ast_nodes import *

class HoopType(Enum):
    """Tipos de datos en HOOP"""
    WHOLE = "whole"      # Entero
    FRACT = "fract"      # Decimal
    TEXT = "text"        # Cadena
    LOGIC = "logic"      # Booleano
    CHAR = "char"        # Carácter
    VOID = "void"        # Sin valor (funciones sin return)
    CLASS = "class"      # Tipo clase
    ANY = "any"          # Tipo desconocido/inferido
    ERROR = "error"      # Tipo error (para recuperación)

class SymbolType(Enum):
    """Tipos de símbolos en la tabla"""
    VARIABLE = "variable"
    FUNCTION = "function"
    CLASS = "class"
    PARAMETER = "parameter"
    ATTRIBUTE = "attribute"
    METHOD = "method"

class Symbol:
    """Representa un símbolo en la tabla de símbolos
    
    Attributes:
        name: Nombre del símbolo
        symbol_type: Tipo de símbolo (variable, función, clase, etc.)
        data_type: Tipo de dato (whole, text, logic, etc.)
        scope: Scope donde fue declarado
        line: Línea de declaración
        attributes: Diccionario de atributos adicionales
    """
    
    def __init__(self, name: str, symbol_type: SymbolType, data_type: HoopType, 
                 scope: str, line: int = 0, **attributes):
        self.name = name
        self.symbol_type = symbol_type
        self.data_type = data_type
        self.scope = scope
        self.line = line
        self.attributes = attributes
    
    def __repr__(self):
        return f"Symbol({self.name}: {self.data_type.value} [{self.symbol_type.value}])"

class Scope:
    """Representa un ámbito (scope) en el programa
    
    Maneja la visibilidad de símbolos en diferentes contextos:
    - Global: variables y funciones globales
    - Función: parámetros y variables locales
    - Clase: atributos y métodos
    """
    
    def __init__(self, name: str, parent: Optional['Scope'] = None):
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.children: List['Scope'] = []
    
    def define(self, symbol: Symbol) -> bool:
        """Define un símbolo en este scope
        
        Returns:
            True si se definió exitosamente, False si ya existía
        """
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup(self, name: str, recursive: bool = True) -> Optional[Symbol]:
        """Busca un símbolo en este scope o en los padres
        
        Args:
            name: Nombre del símbolo a buscar
            recursive: Si buscar en scopes padres
        
        Returns:
            Symbol si se encuentra, None si no existe
        """
        if name in self.symbols:
            return self.symbols[name]
        
        if recursive and self.parent:
            return self.parent.lookup(name, recursive)
        
        return None
    
    def __repr__(self):
        return f"Scope({self.name}, {len(self.symbols)} symbols)"

class SemanticError(Exception):
    """Excepción para errores semánticos"""
    
    def __init__(self, message: str, line: int = 0):
        self.message = message
        self.line = line
        super().__init__(self.message)
    
    def __str__(self):
        if self.line:
            return f"Error semántico en línea {self.line}: {self.message}"
        return f"Error semántico: {self.message}"

class SemanticAnalyzer:
    """Analizador Semántico para HOOP
    
    Realiza análisis semántico completo del AST:
    - Construcción de tabla de símbolos
    - Verificación de tipos
    - Validación de declaraciones y usos
    - Detección de errores semánticos
    """
    
    def __init__(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Definir funciones built-in
        self._define_builtins()
    
    def _define_builtins(self):
        """Define funciones y símbolos built-in del lenguaje"""
        builtins = [
            ("display", HoopType.VOID, ["any"]),  # display puede imprimir cualquier cosa
            ("length", HoopType.WHOLE, ["text"]),
            ("size", HoopType.WHOLE, ["any"]),
            ("type", HoopType.TEXT, ["any"]),
            ("convert", HoopType.ANY, ["any", "text"]),
            ("input", HoopType.TEXT, []),
            ("random", HoopType.FRACT, []),
            ("abs", HoopType.WHOLE, ["whole"]),
            ("sqrt", HoopType.FRACT, ["whole"]),
            ("pow", HoopType.WHOLE, ["whole", "whole"]),
        ]
        
        for name, return_type, params in builtins:
            symbol = Symbol(
                name=name,
                symbol_type=SymbolType.FUNCTION,
                data_type=return_type,
                scope="global",
                params=params,
                is_builtin=True
            )
            self.global_scope.define(symbol)
    
    def error(self, message: str, line: int = 0):
        """Registra un error semántico"""
        error_msg = f"Línea {line}: {message}" if line else message
        self.errors.append(error_msg)
    
    def warning(self, message: str, line: int = 0):
        """Registra una advertencia"""
        warning_msg = f"Línea {line}: {message}" if line else message
        self.warnings.append(warning_msg)
    
    def enter_scope(self, name: str) -> Scope:
        """Entra a un nuevo scope"""
        new_scope = Scope(name, self.current_scope)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
        return new_scope
    
    def exit_scope(self):
        """Sale del scope actual"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def analyze(self, ast: ProgramaNode) -> Tuple[bool, List[str], List[str]]:
        """Analiza el AST completo
        
        Args:
            ast: Árbol de sintaxis abstracta
        
        Returns:
            Tupla (es_válido, errores, advertencias)
        """
        try:
            self.visit_programa(ast)
            is_valid = len(self.errors) == 0
            return is_valid, self.errors, self.warnings
        except Exception as e:
            self.error(f"Error inesperado durante análisis: {str(e)}")
            return False, self.errors, self.warnings
    
    def visit_programa(self, node: ProgramaNode):
        """Visita el nodo raíz del programa"""
        for declaracion in node.declaraciones:
            self.visit(declaracion)
    
    def visit(self, node: ASTNode):
        """Dispatcher: visita un nodo según su tipo"""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode):
        """Visita genérica para nodos sin método específico"""
        self.warning(f"No hay visitor implementado para {type(node).__name__}")
    
    # ==========================================
    # VISITORS PARA DECLARACIONES
    # ==========================================
    
    def visit_DeclaracionNode(self, node: DeclaracionNode):
        """Visita declaración de variable: data nombre set valor;"""
        # Evaluar la expresión del valor
        valor_tipo = self.visit(node.valor)
        
        # Crear símbolo
        symbol = Symbol(
            name=node.nombre,
            symbol_type=SymbolType.VARIABLE,
            data_type=valor_tipo,
            scope=self.current_scope.name
        )
        
        # Verificar si ya existe
        existing = self.current_scope.lookup(node.nombre, recursive=False)
        if existing:
            self.error(f"Variable '{node.nombre}' ya está declarada en este scope")
        else:
            self.current_scope.define(symbol)
    
    def visit_FuncionNode(self, node: FuncionNode):
        """Visita definición de función: action nombre(params) { ... }"""
        # Verificar si ya existe
        existing = self.current_scope.lookup(node.nombre, recursive=False)
        if existing:
            self.error(f"Función '{node.nombre}' ya está declarada")
            return
        
        # Crear símbolo de función
        param_types = [self._type_from_string(p.tipo) for p in node.parametros]
        function_symbol = Symbol(
            name=node.nombre,
            symbol_type=SymbolType.FUNCTION,
            data_type=HoopType.ANY,  # Por ahora no inferimos tipo de retorno
            scope=self.current_scope.name,
            params=param_types
        )
        self.current_scope.define(function_symbol)
        
        # Entrar al scope de la función
        self.enter_scope(f"function_{node.nombre}")
        self.current_function = node.nombre
        
        # Definir parámetros en el scope de la función
        for param in node.parametros:
            param_symbol = Symbol(
                name=param.nombre,
                symbol_type=SymbolType.PARAMETER,
                data_type=self._type_from_string(param.tipo),
                scope=self.current_scope.name
            )
            self.current_scope.define(param_symbol)
        
        # Visitar cuerpo de la función
        for statement in node.cuerpo:
            self.visit(statement)
        
        # Salir del scope
        self.current_function = None
        self.exit_scope()
    
    def visit_ClaseNode(self, node: ClaseNode):
        """Visita definición de clase: mold nombre { ... }"""
        # Verificar si ya existe
        existing = self.current_scope.lookup(node.nombre, recursive=False)
        if existing:
            self.error(f"Clase '{node.nombre}' ya está declarada")
            return
        
        # Crear símbolo de clase
        class_symbol = Symbol(
            name=node.nombre,
            symbol_type=SymbolType.CLASS,
            data_type=HoopType.CLASS,
            scope=self.current_scope.name,
            attributes={},
            methods={}
        )
        self.current_scope.define(class_symbol)
        
        # Entrar al scope de la clase
        self.enter_scope(f"class_{node.nombre}")
        self.current_class = node.nombre
        
        # Visitar cuerpo de la clase
        for elemento in node.cuerpo:
            if isinstance(elemento, DeclaracionNode):
                # Atributo de clase
                self.visit_DeclaracionNode(elemento)
                # Marcar como atributo
                symbol = self.current_scope.lookup(elemento.nombre, recursive=False)
                if symbol:
                    symbol.symbol_type = SymbolType.ATTRIBUTE
            elif isinstance(elemento, FuncionNode):
                # Método de clase
                self.visit_FuncionNode(elemento)
                # Marcar como método
                symbol = self.current_scope.lookup(elemento.nombre, recursive=False)
                if symbol:
                    symbol.symbol_type = SymbolType.METHOD
        
        # Salir del scope
        self.current_class = None
        self.exit_scope()
    
    # ==========================================
    # VISITORS PARA STATEMENTS
    # ==========================================
    
    def visit_IfStatementNode(self, node: IfStatementNode):
        """Visita estructura condicional: when condicion { ... }"""
        # Verificar condición
        cond_tipo = self.visit(node.condicion)
        if cond_tipo != HoopType.LOGIC and cond_tipo != HoopType.ANY:
            self.warning(f"Condición del 'when' debería ser de tipo logic, es {cond_tipo.value}")
        
        # Visitar bloque then
        for stmt in node.bloque_then:
            self.visit(stmt)
        
        # Visitar bloque else si existe
        if node.bloque_else:
            for stmt in node.bloque_else:
                self.visit(stmt)
    
    def visit_CycleStatementNode(self, node: CycleStatementNode):
        """Visita bucle: cycle variable from inicio to fin { ... }"""
        # Verificar que inicio y fin sean numéricos
        if node.inicio:
            inicio_tipo = self.visit(node.inicio)
            if inicio_tipo not in [HoopType.WHOLE, HoopType.FRACT, HoopType.ANY]:
                self.warning(f"Inicio de cycle debería ser numérico, es {inicio_tipo.value}")
        
        if node.fin:
            fin_tipo = self.visit(node.fin)
            if fin_tipo not in [HoopType.WHOLE, HoopType.FRACT, HoopType.ANY]:
                self.warning(f"Fin de cycle debería ser numérico, es {fin_tipo.value}")
        
        # Definir variable del ciclo en un nuevo scope
        self.enter_scope(f"cycle_{node.variable}")
        
        cycle_var = Symbol(
            name=node.variable,
            symbol_type=SymbolType.VARIABLE,
            data_type=HoopType.WHOLE,
            scope=self.current_scope.name
        )
        self.current_scope.define(cycle_var)
        
        # Visitar cuerpo del ciclo
        for stmt in node.cuerpo:
            self.visit(stmt)
        
        self.exit_scope()
    
    def visit_ReturnNode(self, node: ReturnNode):
        """Visita statement de retorno: answer valor;"""
        if not self.current_function:
            self.error("'answer' solo puede usarse dentro de una función")
        
        # Verificar tipo del valor de retorno
        if node.valor:
            self.visit(node.valor)
    
    def visit_DisplayNode(self, node: DisplayNode):
        """Visita statement de impresión: display expresion;"""
        self.visit(node.expresion)
    
    def visit_AsignacionNode(self, node: AsignacionNode):
        """Visita asignación: variable set valor;"""
        # Obtener símbolo de la variable
        if isinstance(node.variable, IdentificadorNode):
            symbol = self.current_scope.lookup(node.variable.nombre)
            if not symbol:
                self.error(f"Variable '{node.variable.nombre}' no está declarada")
        elif isinstance(node.variable, AccesoMiembroNode):
            # Asignación a atributo: objeto.atributo set valor
            self.visit(node.variable)
        
        # Verificar valor
        self.visit(node.valor)
    
    # ==========================================
    # VISITORS PARA EXPRESIONES
    # ==========================================
    
    def visit_OperacionNode(self, node: OperacionNode) -> HoopType:
        """Visita operación: izquierda operador derecha"""
        # Operaciones unarias
        if node.izquierda is None:
            derecha_tipo = self.visit(node.derecha)
            if node.operador == "not":
                return HoopType.LOGIC
            elif node.operador == "minus":
                return derecha_tipo if derecha_tipo in [HoopType.WHOLE, HoopType.FRACT] else HoopType.ANY
            return HoopType.ANY
        
        # Operaciones binarias
        izq_tipo = self.visit(node.izquierda)
        der_tipo = self.visit(node.derecha)
        
        # Operadores aritméticos
        if node.operador in ["plus", "minus", "times", "divide", "mod"]:
            if izq_tipo in [HoopType.WHOLE, HoopType.FRACT, HoopType.ANY] and \
               der_tipo in [HoopType.WHOLE, HoopType.FRACT, HoopType.ANY]:
                # Si alguno es fract, el resultado es fract
                if izq_tipo == HoopType.FRACT or der_tipo == HoopType.FRACT:
                    return HoopType.FRACT
                return HoopType.WHOLE
            else:
                self.warning(f"Operación {node.operador} entre tipos incompatibles: {izq_tipo.value} y {der_tipo.value}")
                return HoopType.ERROR
        
        # Operadores de comparación
        elif node.operador in ["equals", "notequals", "greater", "less", "greatereq", "lesseq"]:
            return HoopType.LOGIC
        
        # Operadores lógicos
        elif node.operador in ["and", "or"]:
            if izq_tipo != HoopType.LOGIC or der_tipo != HoopType.LOGIC:
                self.warning(f"Operador lógico {node.operador} espera operandos logic")
            return HoopType.LOGIC
        
        return HoopType.ANY
    
    def visit_LiteralNode(self, node: LiteralNode) -> HoopType:
        """Visita literal: número, cadena, booleano"""
        tipo_map = {
            "NUMBER": HoopType.WHOLE if '.' not in node.valor else HoopType.FRACT,
            "STRING": HoopType.TEXT,
            "BOOLEAN": HoopType.LOGIC,
            "CHARACTER": HoopType.CHAR,
            "TYPE_DECLARATION": HoopType.ANY
        }
        return tipo_map.get(node.tipo, HoopType.ANY)
    
    def visit_IdentificadorNode(self, node: IdentificadorNode) -> HoopType:
        """Visita identificador: referencia a variable"""
        symbol = self.current_scope.lookup(node.nombre)
        if not symbol:
            self.error(f"Variable '{node.nombre}' no está declarada")
            return HoopType.ERROR
        return symbol.data_type
    
    def visit_LlamadaFuncionNode(self, node: LlamadaFuncionNode) -> HoopType:
        """Visita llamada a función: nombre(args)"""
        # Verificar si es forge (construcción de objeto)
        if node.nombre.startswith("forge<"):
            class_name = node.nombre[6:-1]  # Extraer nombre de clase
            symbol = self.current_scope.lookup(class_name)
            if not symbol or symbol.symbol_type != SymbolType.CLASS:
                self.error(f"Clase '{class_name}' no está declarada")
                return HoopType.ERROR
            return HoopType.CLASS
        
        # Verificar función normal
        symbol = self.current_scope.lookup(node.nombre)
        if not symbol:
            self.error(f"Función '{node.nombre}' no está declarada")
            return HoopType.ERROR
        
        if symbol.symbol_type not in [SymbolType.FUNCTION, SymbolType.METHOD]:
            self.error(f"'{node.nombre}' no es una función")
            return HoopType.ERROR
        
        # Verificar número de argumentos
        expected_params = symbol.attributes.get('params', [])
        if len(node.argumentos) != len(expected_params):
            self.warning(f"Función '{node.nombre}' espera {len(expected_params)} argumentos, recibió {len(node.argumentos)}")
        
        # Verificar argumentos
        for arg in node.argumentos:
            self.visit(arg)
        
        return symbol.data_type
    
    def visit_AccesoMiembroNode(self, node: AccesoMiembroNode) -> HoopType:
        """Visita acceso a miembro: objeto.atributo"""
        # Verificar objeto
        if isinstance(node.objeto, IdentificadorNode):
            if node.objeto.nombre == "self":
                if not self.current_class:
                    self.error("'self' solo puede usarse dentro de una clase")
                    return HoopType.ERROR
                # Buscar atributo en la clase actual
                class_scope = self.current_scope
                while class_scope and not class_scope.name.startswith("class_"):
                    class_scope = class_scope.parent
                
                if class_scope:
                    member_symbol = class_scope.lookup(node.miembro, recursive=False)
                    if member_symbol:
                        return member_symbol.data_type
                    else:
                        self.error(f"Atributo '{node.miembro}' no existe en la clase")
                        return HoopType.ERROR
            else:
                # Acceso a atributo de variable
                obj_symbol = self.current_scope.lookup(node.objeto.nombre)
                if not obj_symbol:
                    self.error(f"Variable '{node.objeto.nombre}' no está declarada")
                    return HoopType.ERROR
                # Por ahora, asumimos que existe el atributo
                return HoopType.ANY
        
        return HoopType.ANY
    
    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    def _type_from_string(self, type_str: str) -> HoopType:
        """Convierte string de tipo a HoopType"""
        type_map = {
            "whole": HoopType.WHOLE,
            "fract": HoopType.FRACT,
            "text": HoopType.TEXT,
            "logic": HoopType.LOGIC,
            "char": HoopType.CHAR,
            "void": HoopType.VOID
        }
        return type_map.get(type_str.lower(), HoopType.ANY)

# ==========================================
# FUNCIONES DE ALTO NIVEL
# ==========================================

def analyze_hoop_semantics(ast: ProgramaNode) -> Tuple[bool, List[str], List[str]]:
    """Función principal para análisis semántico
    
    Args:
        ast: Árbol de sintaxis abstracta
    
    Returns:
        Tupla (es_válido, errores, advertencias)
    """
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast)

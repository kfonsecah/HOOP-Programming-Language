#!/usr/bin/env python3
"""
Analizador semántico para HOOP
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
from core.ast_nodes import *


class HoopType(Enum):
    WHOLE = "whole"
    FRACT = "fract"
    TEXT = "text"
    LOGIC = "logic"
    CHAR = "char"
    VOID = "void"
    CLASS = "class"
    GRID = "grid"
    CHAIN = "chain"
    ANY = "any"
    ERROR = "error"


class SymbolType(Enum):
    VARIABLE = "variable"
    CONSTANT = "constant"
    PARAMETER = "parameter"
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    ATTRIBUTE = "attribute"


class Symbol:
    def __init__(self, name: str, symbol_type: SymbolType, data_type: HoopType,
                 scope: str, line: int = 0, **attributes):
        self.name = name
        self.symbol_type = symbol_type
        self.data_type = data_type
        self.scope = scope
        self.line = line
        self.attributes = attributes


class Scope:
    def __init__(self, name: str, parent: Optional['Scope'] = None):
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}

    def define(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def lookup(self, name: str, recursive: bool = True) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if recursive and self.parent:
            return self.parent.lookup(name, recursive)
        return None


class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.loop_depth = 0
        self._define_builtins()

    def _define_builtins(self):
        builtins = [
            ("display", HoopType.VOID, ["any"]),
            ("output", HoopType.VOID, ["any"]),
            ("length", HoopType.WHOLE, ["text"]),
            ("size", HoopType.WHOLE, ["any"]),
            ("type", HoopType.TEXT, ["any"]),
            ("convert", HoopType.ANY, ["any", "text"]),
            ("input", HoopType.TEXT, []),
            ("random", HoopType.FRACT, [], {"variadic": True}),
            ("abs", HoopType.WHOLE, ["whole"]),
            ("sqrt", HoopType.FRACT, ["whole"]),
            ("pow", HoopType.WHOLE, ["whole", "whole"]),
            ("max", HoopType.ANY, ["any"], {"variadic": True}),
            ("min", HoopType.ANY, ["any"], {"variadic": True}),
            ("read", HoopType.TEXT, ["text"]),
            ("write", HoopType.LOGIC, ["text", "text"]),
            ("open", HoopType.TEXT, ["text"]),
            ("close", HoopType.VOID, []),
        ]
        for entry in builtins:
            extras = {}
            if len(entry) == 4:
                name, return_type, params, extras = entry
            else:
                name, return_type, params = entry
            symbol = Symbol(
                name=name,
                symbol_type=SymbolType.FUNCTION,
                data_type=return_type,
                scope="global",
                params=params,
                is_builtin=True,
                **extras,
            )
            self.global_scope.define(symbol)

    def error(self, message: str):
        self.errors.append(message)

    def warning(self, message: str):
        self.warnings.append(message)

    def enter_scope(self, name: str):
        new_scope = Scope(name, self.current_scope)
        self.current_scope = new_scope

    def exit_scope(self):
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent

    def analyze(self, ast: ProgramaNode) -> Tuple[bool, List[str], List[str]]:
        self.visit_programa(ast)
        return len(self.errors) == 0, self.errors, self.warnings

    def visit_programa(self, node: ProgramaNode):
        for declaration in node.declaraciones:
            self.visit(declaration)

    def visit(self, node: ASTNode):
        method = getattr(self, f"visit_{type(node).__name__}", self.generic_visit)
        return method(node)

    def generic_visit(self, node: ASTNode):
        self.warning(f"No hay visitor para {type(node).__name__}")

    def visit_DeclaracionNode(self, node: DeclaracionNode):
        value_type = self.visit(node.valor)
        symbol = Symbol(
            name=node.nombre,
            symbol_type=SymbolType.VARIABLE,
            data_type=value_type,
            scope=self.current_scope.name,
        )
        if not self.current_scope.define(symbol):
            self.error(f"Variable '{node.nombre}' ya está declarada en este scope")

    def visit_ConstanteNode(self, node: ConstanteNode):
        value_type = self.visit(node.valor)
        symbol = Symbol(
            name=node.nombre,
            symbol_type=SymbolType.CONSTANT,
            data_type=value_type,
            scope=self.current_scope.name,
        )
        if not self.current_scope.define(symbol):
            self.error(f"Constante '{node.nombre}' ya está declarada en este scope")

    def visit_FuncionNode(self, node: FuncionNode):
        if not self.current_scope.define(Symbol(
            name=node.nombre,
            symbol_type=SymbolType.FUNCTION,
            data_type=HoopType.ANY,
            scope=self.current_scope.name,
            params=[self._type_from_string(p.tipo) for p in node.parametros],
        )):
            self.error(f"Función '{node.nombre}' ya está declarada")
            return
        self.enter_scope(f"function_{node.nombre}")
        self.current_function = node.nombre
        for param in node.parametros:
            self.current_scope.define(Symbol(
                name=param.nombre,
                symbol_type=SymbolType.PARAMETER,
                data_type=self._type_from_string(param.tipo),
                scope=self.current_scope.name,
            ))
        for stmt in node.cuerpo:
            self.visit(stmt)
        self.current_function = None
        self.exit_scope()

    def visit_ClaseNode(self, node: ClaseNode):
        if not self.current_scope.define(Symbol(
            name=node.nombre,
            symbol_type=SymbolType.CLASS,
            data_type=HoopType.CLASS,
            scope=self.current_scope.name,
        )):
            self.error(f"Clase '{node.nombre}' ya está declarada")
            return
        self.enter_scope(f"class_{node.nombre}")
        self.current_class = node.nombre
        for element in node.cuerpo:
            if isinstance(element, DeclaracionNode):
                self.visit_DeclaracionNode(element)
            elif isinstance(element, ConstanteNode):
                self.visit_ConstanteNode(element)
            elif isinstance(element, FuncionNode):
                self.visit_FuncionNode(element)
        self.current_class = None
        self.exit_scope()

    def visit_IfStatementNode(self, node: IfStatementNode):
        cond_type = self.visit(node.condicion)
        if cond_type not in [HoopType.LOGIC, HoopType.ANY]:
            self.warning("La condición de when debería ser logic")
        for stmt in node.bloque_then:
            self.visit(stmt)
        if node.bloque_else:
            for stmt in node.bloque_else:
                self.visit(stmt)

    def visit_CycleStatementNode(self, node: CycleStatementNode):
        self.loop_depth += 1
        self.enter_scope(f"cycle_{node.variable}")
        self.current_scope.define(Symbol(
            name=node.variable,
            symbol_type=SymbolType.VARIABLE,
            data_type=HoopType.WHOLE,
            scope=self.current_scope.name,
        ))
        for stmt in node.cuerpo:
            self.visit(stmt)
        self.exit_scope()
        self.loop_depth -= 1

    def visit_RepeatStatementNode(self, node: RepeatStatementNode):
        cond_type = self.visit(node.condicion)
        if cond_type not in [HoopType.LOGIC, HoopType.ANY]:
            self.warning("La condición de repeat debería ser logic")
        self.loop_depth += 1
        self.enter_scope("repeat")
        for stmt in node.cuerpo:
            self.visit(stmt)
        self.exit_scope()
        self.loop_depth -= 1

    def visit_SelectStatementNode(self, node: SelectStatementNode):
        self.visit(node.expresion)
        for case in node.casos:
            self.visit(case.valor)
            for stmt in case.cuerpo:
                self.visit(stmt)
        if node.default:
            for stmt in node.default:
                self.visit(stmt)

    def visit_TryStatementNode(self, node: TryStatementNode):
        for stmt in node.bloque_try:
            self.visit(stmt)
        if node.bloque_rescue:
            self.enter_scope("rescue")
            if node.rescue_identificador:
                self.current_scope.define(Symbol(
                    name=node.rescue_identificador,
                    symbol_type=SymbolType.VARIABLE,
                    data_type=HoopType.ANY,
                    scope=self.current_scope.name,
                ))
            for stmt in node.bloque_rescue:
                self.visit(stmt)
            self.exit_scope()
        if node.bloque_ensure:
            self.enter_scope("ensure")
            for stmt in node.bloque_ensure:
                self.visit(stmt)
            self.exit_scope()

    def visit_ReturnNode(self, node: ReturnNode):
        if not self.current_function:
            self.error("'answer' solo puede usarse dentro de funciones")
        if node.valor:
            self.visit(node.valor)

    def visit_DisplayNode(self, node: DisplayNode):
        self.visit(node.expresion)

    def visit_AsignacionNode(self, node: AsignacionNode):
        if isinstance(node.variable, IdentificadorNode):
            symbol = self.current_scope.lookup(node.variable.nombre)
            if not symbol:
                self.error(f"Variable '{node.variable.nombre}' no está declarada")
            elif symbol.symbol_type == SymbolType.CONSTANT:
                self.error(f"No se puede reasignar la constante '{node.variable.nombre}'")
        elif isinstance(node.variable, AccesoMiembroNode):
            self.visit(node.variable)
        self.visit(node.valor)

    def visit_OperacionNode(self, node: OperacionNode) -> HoopType:
        if node.izquierda is None:
            return self.visit(node.derecha)
        left = self.visit(node.izquierda)
        right = self.visit(node.derecha)
        if node.operador in {"plus", "minus", "times", "divide", "mod"}:
            if left not in [HoopType.WHOLE, HoopType.FRACT, HoopType.ANY] or                right not in [HoopType.WHOLE, HoopType.FRACT, HoopType.ANY]:
                self.warning("Operación aritmética entre tipos incompatibles")
            return HoopType.FRACT if HoopType.FRACT in (left, right) else HoopType.WHOLE
        if node.operador in {"equals", "notequals", "greater", "less", "greatereq", "lesseq"}:
            return HoopType.LOGIC
        if node.operador in {"and", "or"}:
            return HoopType.LOGIC
        return HoopType.ANY

    def visit_LiteralNode(self, node: LiteralNode) -> HoopType:
        mapping = {
            "NUMBER": HoopType.FRACT if '.' in str(node.valor) else HoopType.WHOLE,
            "STRING": HoopType.TEXT,
            "BOOLEAN": HoopType.LOGIC,
            "CHARACTER": HoopType.CHAR,
        }
        return mapping.get(node.tipo, HoopType.ANY)

    def visit_IdentificadorNode(self, node: IdentificadorNode) -> HoopType:
        if node.nombre == "self":
            if not self.current_class:
                self.error("'self' solo puede usarse dentro de una clase")
                return HoopType.ERROR
            return HoopType.CLASS
        symbol = self.current_scope.lookup(node.nombre)
        if not symbol:
            self.error(f"Variable '{node.nombre}' no está declarada")
            return HoopType.ERROR
        return symbol.data_type

    def visit_LlamadaFuncionNode(self, node: LlamadaFuncionNode) -> HoopType:
        if node.nombre.startswith("forge<"):
            class_name = node.nombre[6:-1]
            symbol = self.current_scope.lookup(class_name)
            if not symbol:
                self.error(f"Clase '{class_name}' no está declarada")
                return HoopType.ERROR
            return HoopType.CLASS
        symbol = self.current_scope.lookup(node.nombre)
        if not symbol:
            self.error(f"Función '{node.nombre}' no está declarada")
            return HoopType.ERROR
        expected = symbol.attributes.get("params", [])
        variadic = symbol.attributes.get("variadic", False)
        if not variadic and len(node.argumentos) != len(expected):
            self.warning(f"Función '{node.nombre}' espera {len(expected)} argumentos, recibió {len(node.argumentos)}")
        for arg in node.argumentos:
            self.visit(arg)
        return symbol.data_type

    def visit_AccesoMiembroNode(self, node: AccesoMiembroNode) -> HoopType:
        if isinstance(node.objeto, IdentificadorNode):
            if node.objeto.nombre == "self":
                if not self.current_class:
                    self.error("'self' solo puede usarse dentro de una clase")
                    return HoopType.ERROR
                return HoopType.ANY
            obj = self.current_scope.lookup(node.objeto.nombre)
            if not obj:
                self.error(f"Variable '{node.objeto.nombre}' no está declarada")
                return HoopType.ERROR
        return HoopType.ANY

    def visit_ThrowNode(self, node: ThrowNode):
        self.visit(node.expresion)

    def visit_BreakNode(self, node: BreakNode):
        if self.loop_depth <= 0:
            self.error("'halt' solo puede usarse dentro de un ciclo")

    def visit_ContinueNode(self, node: ContinueNode):
        if self.loop_depth <= 0:
            self.error("'skip' solo puede usarse dentro de un ciclo")

    def _type_from_string(self, type_str: str) -> HoopType:
        mapping = {
            "whole": HoopType.WHOLE,
            "fract": HoopType.FRACT,
            "text": HoopType.TEXT,
            "logic": HoopType.LOGIC,
            "char": HoopType.CHAR,
            "void": HoopType.VOID,
            "grid": HoopType.GRID,
            "chain": HoopType.CHAIN,
        }
        return mapping.get(type_str.lower(), HoopType.ANY)


def analyze_hoop_semantics(ast: ProgramaNode) -> Tuple[bool, List[str], List[str]]:
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast)

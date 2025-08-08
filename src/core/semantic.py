"""
Analizador Semántico para el lenguaje HOOP
==========================================

Este módulo se encarga de verificar la semántica del código HOOP.
Recibe un AST del parser y valida reglas semánticas como tipos de datos,
declaraciones de variables, uso de funciones, etc.

Proceso: AST → AST validado + Tabla de símbolos + Errores semánticos
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from core.parser import *
from core.lexer import Token

# ============================================================================
# TIPOS DE DATOS Y SÍMBOLOS
# ============================================================================

class HoopType(Enum):
    """Tipos de datos soportados por HOOP"""
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    LIST = "list"
    FUNCTION = "function"
    CLASS = "class"
    NONE = "none"
    UNKNOWN = "unknown"

@dataclass
class Symbol:
    """Representa un símbolo en la tabla de símbolos"""
    name: str
    type: HoopType
    declared_at: Token
    is_initialized: bool = False
    is_function: bool = False
    is_class: bool = False
    parameters: Optional[List[str]] = None
    return_type: Optional[HoopType] = None

@dataclass
class Scope:
    """Representa un ámbito (scope) de variables"""
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    parent: Optional['Scope'] = None
    name: str = "global"
    
    def define(self, symbol: Symbol):
        """Define un símbolo en este ámbito"""
        self.symbols[symbol.name] = symbol
    
    def get(self, name: str) -> Optional[Symbol]:
        """Busca un símbolo en este ámbito y sus padres"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.get(name)
        return None
    
    def get_local(self, name: str) -> Optional[Symbol]:
        """Busca un símbolo solo en este ámbito"""
        return self.symbols.get(name)

class SemanticError(Exception):
    """Excepción para errores semánticos"""
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"Error semántico en línea {token.line}, columna {token.column}: {message}")
        else:
            super().__init__(f"Error semántico: {message}")

# ============================================================================
# ANALIZADOR SEMÁNTICO
# ============================================================================

class HoopSemanticAnalyzer:
    """
    Analizador semántico para el lenguaje HOOP
    
    Responsabilidades:
    - Verificar que las variables estén declaradas antes de usarse
    - Validar compatibilidad de tipos en operaciones
    - Detectar redefiniciones de variables/funciones
    - Verificar que las funciones se llamen con el número correcto de argumentos
    - Validar el uso de palabras reservadas
    - Verificar el alcance (scope) de las variables
    - Detectar código inalcanzable
    """
    
    def __init__(self):
        self.global_scope = Scope(name="global")
        self.current_scope = self.global_scope
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []
        
        # Para detectar código inalcanzable
        self.in_function = False
        self.has_return = False
        
        # Funciones built-in del lenguaje
        self._define_builtin_functions()
    
    def analyze(self, program: Program) -> bool:
        """
        Analiza semánticamente un programa HOOP
        
        Args:
            program: AST del programa
            
        Returns:
            bool: True si no hay errores semánticos, False en caso contrario
        """
        self.errors.clear()
        self.warnings.clear()
        
        try:
            self._analyze_program(program)
        except Exception as e:
            self.errors.append(SemanticError(f"Error interno del analizador: {str(e)}"))
        
        return len(self.errors) == 0
    
    def _define_builtin_functions(self):
        """Define las funciones built-in del lenguaje HOOP"""
        # TODO: Implementar definición de funciones built-in
        # - show(): para mostrar output
        # - input(): para recibir input del usuario
        # - len(): para obtener longitud de listas/strings
        # - type(): para obtener el tipo de una variable
        
        builtin_functions = [
            Symbol("show", HoopType.FUNCTION, None, True, True, False, ["value"], HoopType.NONE),
            Symbol("input", HoopType.FUNCTION, None, True, True, False, ["prompt"], HoopType.STRING),
            Symbol("len", HoopType.FUNCTION, None, True, True, False, ["obj"], HoopType.INTEGER),
            Symbol("type", HoopType.FUNCTION, None, True, True, False, ["obj"], HoopType.STRING),
        ]
        
        for func in builtin_functions:
            self.global_scope.define(func)
    
    def _analyze_program(self, program: Program):
        """Analiza el programa completo"""
        for statement in program.statements:
            self._analyze_statement(statement)
    
    def _analyze_statement(self, stmt: Statement):
        """
        Analiza una declaración/sentencia
        
        TODO: Implementar análisis para cada tipo de statement:
        - FunctionDeclaration: verificar nombre único, parámetros válidos
        - ClassDeclaration: verificar nombre único, métodos válidos  
        - AssignmentStatement: verificar tipos compatibles
        - IfStatement: verificar condición booleana
        - WhileStatement: verificar condición booleana
        - ForStatement: verificar iterable válido
        - ReturnStatement: verificar tipo de retorno
        - ShowStatement: verificar expresión válida
        - ExpressionStatement: verificar expresión válida
        """
        
        if isinstance(stmt, FunctionDeclaration):
            self._analyze_function_declaration(stmt)
        elif isinstance(stmt, ClassDeclaration):
            self._analyze_class_declaration(stmt)
        elif isinstance(stmt, AssignmentStatement):
            self._analyze_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            self._analyze_if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            self._analyze_while_statement(stmt)
        elif isinstance(stmt, ForStatement):
            self._analyze_for_statement(stmt)
        elif isinstance(stmt, ReturnStatement):
            self._analyze_return_statement(stmt)
        elif isinstance(stmt, ShowStatement):
            self._analyze_show_statement(stmt)
        elif isinstance(stmt, BreakStatement):
            self._analyze_break_statement(stmt)
        elif isinstance(stmt, ContinueStatement):
            self._analyze_continue_statement(stmt)
        elif isinstance(stmt, ExpressionStatement):
            self._analyze_expression(stmt.expression)
        else:
            self._add_error(f"Tipo de declaración no reconocido: {type(stmt).__name__}")
    
    def _analyze_function_declaration(self, func: FunctionDeclaration):
        """
        Analiza una declaración de función
        
        TODO: Implementar
        - Verificar que el nombre no sea una palabra reservada
        - Verificar que no esté ya definida en el ámbito actual
        - Verificar que los parámetros no se repitan
        - Analizar el cuerpo de la función en un nuevo ámbito
        """
        # Verificar si la función ya está definida
        if self.current_scope.get_local(func.name):
            self._add_error(f"La función '{func.name}' ya está definida", func.token)
            return
        
        # Verificar que no sea palabra reservada
        if self._is_reserved_word(func.name):
            self._add_error(f"'{func.name}' es una palabra reservada", func.token)
            return
        
        # Definir la función en el ámbito actual
        func_symbol = Symbol(
            func.name, HoopType.FUNCTION, func.token, 
            True, True, False, func.parameters, HoopType.UNKNOWN
        )
        self.current_scope.define(func_symbol)
        
        # Analizar cuerpo en nuevo ámbito
        self._enter_scope(f"function_{func.name}")
        
        # Definir parámetros en el ámbito de la función
        for param in func.parameters:
            if self.current_scope.get_local(param):
                self._add_error(f"Parámetro duplicado: '{param}'", func.token)
            else:
                param_symbol = Symbol(param, HoopType.UNKNOWN, func.token, True)
                self.current_scope.define(param_symbol)
        
        # Analizar cuerpo
        old_in_function = self.in_function
        old_has_return = self.has_return
        self.in_function = True
        self.has_return = False
        
        for statement in func.body:
            self._analyze_statement(statement)
        
        self.in_function = old_in_function
        self.has_return = old_has_return
        
        self._exit_scope()
    
    def _analyze_class_declaration(self, cls: ClassDeclaration):
        """
        Analiza una declaración de clase
        
        TODO: Implementar
        - Verificar nombre único
        - Analizar métodos de la clase
        - Verificar constructor si existe
        """
        # Placeholder
        pass
    
    def _analyze_assignment(self, assign: AssignmentStatement):
        """
        Analiza una asignación
        
        TODO: Implementar
        - Verificar que el valor sea compatible con la variable
        - Definir la variable si no existe
        - Verificar tipos si la variable ya existe
        """
        # Analizar la expresión del lado derecho
        value_type = self._analyze_expression(assign.value)
        
        # Verificar si la variable ya existe
        existing_symbol = self.current_scope.get(assign.target.name)
        
        if existing_symbol:
            # Variable ya existe, verificar compatibilidad de tipos
            if not self._are_types_compatible(existing_symbol.type, value_type):
                self._add_error(
                    f"Incompatibilidad de tipos: no se puede asignar {value_type.value} a {existing_symbol.type.value}",
                    assign.token
                )
        else:
            # Variable nueva, definirla
            var_symbol = Symbol(assign.target.name, value_type, assign.token, True)
            self.current_scope.define(var_symbol)
    
    def _analyze_if_statement(self, if_stmt: IfStatement):
        """Analiza una declaración if"""
        # Verificar que la condición sea booleana
        condition_type = self._analyze_expression(if_stmt.condition)
        if condition_type != HoopType.BOOLEAN and condition_type != HoopType.UNKNOWN:
            self._add_error("La condición del if debe ser booleana", if_stmt.token)
        
        # Analizar bloques
        for stmt in if_stmt.then_branch:
            self._analyze_statement(stmt)
        
        if if_stmt.else_branch:
            for stmt in if_stmt.else_branch:
                self._analyze_statement(stmt)
    
    def _analyze_while_statement(self, while_stmt: WhileStatement):
        """Analiza una declaración while"""
        # Similar al if, verificar condición booleana
        condition_type = self._analyze_expression(while_stmt.condition)
        if condition_type != HoopType.BOOLEAN and condition_type != HoopType.UNKNOWN:
            self._add_error("La condición del while debe ser booleana", while_stmt.token)
        
        for stmt in while_stmt.body:
            self._analyze_statement(stmt)
    
    def _analyze_for_statement(self, for_stmt: ForStatement):
        """Analiza una declaración for"""
        # TODO: Implementar
        # - Verificar que el iterable sea una lista o string
        # - Definir la variable de iteración en el ámbito del for
        pass
    
    def _analyze_return_statement(self, ret_stmt: ReturnStatement):
        """Analiza una declaración return"""
        if not self.in_function:
            self._add_error("'return' solo puede usarse dentro de una función", ret_stmt.token)
        
        if ret_stmt.value:
            self._analyze_expression(ret_stmt.value)
        
        self.has_return = True
    
    def _analyze_show_statement(self, show_stmt: ShowStatement):
        """Analiza una declaración show"""
        self._analyze_expression(show_stmt.expression)
    
    def _analyze_break_statement(self, break_stmt: BreakStatement):
        """Analiza una declaración break"""
        # TODO: Verificar que esté dentro de un bucle
        pass
    
    def _analyze_continue_statement(self, continue_stmt: ContinueStatement):
        """Analiza una declaración continue"""
        # TODO: Verificar que esté dentro de un bucle
        pass
    
    def _analyze_expression(self, expr: Expression) -> HoopType:
        """
        Analiza una expresión y devuelve su tipo
        
        TODO: Implementar análisis para cada tipo de expresión:
        - LiteralExpression: devolver tipo del literal
        - IdentifierExpression: verificar que esté declarada
        - BinaryExpression: verificar compatibilidad de operandos
        - UnaryExpression: verificar operando válido
        - CallExpression: verificar función y argumentos
        """
        
        if isinstance(expr, LiteralExpression):
            return self._get_literal_type(expr.value)
        
        elif isinstance(expr, IdentifierExpression):
            symbol = self.current_scope.get(expr.name)
            if not symbol:
                self._add_error(f"Variable '{expr.name}' no está definida", expr.token)
                return HoopType.UNKNOWN
            return symbol.type
        
        elif isinstance(expr, BinaryExpression):
            left_type = self._analyze_expression(expr.left)
            right_type = self._analyze_expression(expr.right)
            return self._analyze_binary_operation(left_type, expr.operator, right_type)
        
        elif isinstance(expr, UnaryExpression):
            operand_type = self._analyze_expression(expr.operand)
            return self._analyze_unary_operation(expr.operator, operand_type)
        
        elif isinstance(expr, CallExpression):
            return self._analyze_call_expression(expr)
        
        elif isinstance(expr, ListExpression):
            # Analizar elementos de la lista
            for element in expr.elements:
                self._analyze_expression(element)
            return HoopType.LIST
        
        else:
            self._add_error(f"Tipo de expresión no reconocido: {type(expr).__name__}")
            return HoopType.UNKNOWN
    
    def _analyze_call_expression(self, call: CallExpression) -> HoopType:
        """Analiza una llamada a función"""
        # TODO: Implementar
        # - Verificar que la función existe
        # - Verificar número y tipos de argumentos
        # - Devolver tipo de retorno de la función
        
        if isinstance(call.function, IdentifierExpression):
            func_name = call.function.name
            func_symbol = self.current_scope.get(func_name)
            
            if not func_symbol:
                self._add_error(f"Función '{func_name}' no está definida", call.token)
                return HoopType.UNKNOWN
            
            if not func_symbol.is_function:
                self._add_error(f"'{func_name}' no es una función", call.token)
                return HoopType.UNKNOWN
            
            # Verificar número de argumentos
            expected_args = len(func_symbol.parameters) if func_symbol.parameters else 0
            actual_args = len(call.arguments)
            
            if expected_args != actual_args:
                self._add_error(
                    f"La función '{func_name}' espera {expected_args} argumentos, pero se proporcionaron {actual_args}",
                    call.token
                )
            
            # Analizar argumentos
            for arg in call.arguments:
                self._analyze_expression(arg)
            
            return func_symbol.return_type or HoopType.UNKNOWN
        
        return HoopType.UNKNOWN
    
    def _get_literal_type(self, value: Any) -> HoopType:
        """Determina el tipo de un literal"""
        if isinstance(value, int):
            return HoopType.INTEGER
        elif isinstance(value, float):
            return HoopType.FLOAT
        elif isinstance(value, str):
            return HoopType.STRING
        elif isinstance(value, bool):
            return HoopType.BOOLEAN
        elif value is None:
            return HoopType.NONE
        else:
            return HoopType.UNKNOWN
    
    def _analyze_binary_operation(self, left: HoopType, operator: Token, right: HoopType) -> HoopType:
        """
        Analiza una operación binaria y devuelve el tipo resultado
        
        TODO: Implementar reglas de tipos para:
        - Operaciones aritméticas (+, -, *, /, %)
        - Operaciones de comparación (==, !=, <, >, <=, >=)
        - Operaciones lógicas (and, or)
        """
        # Placeholder - implementar reglas completas
        if operator.value in ['+', '-', '*', '/', '%']:
            if left in [HoopType.INTEGER, HoopType.FLOAT] and right in [HoopType.INTEGER, HoopType.FLOAT]:
                return HoopType.FLOAT if left == HoopType.FLOAT or right == HoopType.FLOAT else HoopType.INTEGER
            elif operator.value == '+' and left == HoopType.STRING and right == HoopType.STRING:
                return HoopType.STRING
            else:
                self._add_error(f"Operación {operator.value} no válida entre {left.value} y {right.value}", operator)
                return HoopType.UNKNOWN
        
        elif operator.value in ['==', '!=', '<', '>', '<=', '>=']:
            return HoopType.BOOLEAN
        
        elif operator.value in ['and', 'or']:
            if left == HoopType.BOOLEAN and right == HoopType.BOOLEAN:
                return HoopType.BOOLEAN
            else:
                self._add_error(f"Operadores lógicos requieren operandos booleanos", operator)
                return HoopType.UNKNOWN
        
        return HoopType.UNKNOWN
    
    def _analyze_unary_operation(self, operator: Token, operand: HoopType) -> HoopType:
        """Analiza una operación unaria"""
        if operator.value == '-':
            if operand in [HoopType.INTEGER, HoopType.FLOAT]:
                return operand
            else:
                self._add_error(f"Operador - no válido para tipo {operand.value}", operator)
                return HoopType.UNKNOWN
        
        elif operator.value == 'not':
            if operand == HoopType.BOOLEAN:
                return HoopType.BOOLEAN
            else:
                self._add_error(f"Operador not requiere operando booleano", operator)
                return HoopType.UNKNOWN
        
        return HoopType.UNKNOWN
    
    def _are_types_compatible(self, type1: HoopType, type2: HoopType) -> bool:
        """Verifica si dos tipos son compatibles para asignación"""
        if type1 == type2:
            return True
        if type1 == HoopType.UNKNOWN or type2 == HoopType.UNKNOWN:
            return True
        # Permitir asignación de entero a flotante
        if type1 == HoopType.FLOAT and type2 == HoopType.INTEGER:
            return True
        return False
    
    def _is_reserved_word(self, word: str) -> bool:
        """Verifica si una palabra es reservada"""
        reserved = {
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'cycle',
            'show', 'input', 'return', 'break', 'continue', 'and', 'or', 'not',
            'in', 'True', 'False', 'None'
        }
        return word in reserved
    
    def _enter_scope(self, name: str):
        """Entra a un nuevo ámbito"""
        new_scope = Scope(parent=self.current_scope, name=name)
        self.current_scope = new_scope
    
    def _exit_scope(self):
        """Sale del ámbito actual"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def _add_error(self, message: str, token: Optional[Token] = None):
        """Agrega un error semántico"""
        self.errors.append(SemanticError(message, token))
    
    def _add_warning(self, message: str):
        """Agrega una advertencia"""
        self.warnings.append(message)
    
    def get_errors(self) -> List[SemanticError]:
        """Devuelve la lista de errores encontrados"""
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        """Devuelve la lista de advertencias"""
        return self.warnings.copy()
    
    def get_symbol_table(self) -> Dict[str, Symbol]:
        """Devuelve la tabla de símbolos global"""
        return self.global_scope.symbols.copy()

# ============================================================================
# FUNCIÓN DE UTILIDAD
# ============================================================================

def analyze_hoop_semantics(program: Program) -> tuple[bool, List[SemanticError], List[str]]:
    """
    Función de conveniencia para análisis semántico completo
    
    Args:
        program: AST del programa
        
    Returns:
        tuple: (es_válido, errores, advertencias)
    """
    analyzer = HoopSemanticAnalyzer()
    is_valid = analyzer.analyze(program)
    return is_valid, analyzer.get_errors(), analyzer.get_warnings()

if __name__ == "__main__":
    # Ejemplo de uso
    from core.parser import parse_hoop_code
    
    sample_code = """
    def calculate_area(width, height):
        return width * height
    
    x = 10
    y = 5
    area = calculate_area(x, y)
    show(area)
    """
    
    try:
        ast = parse_hoop_code(sample_code)
        is_valid, errors, warnings = analyze_hoop_semantics(ast)
        
        if is_valid:
            print("✓ Análisis semántico exitoso")
        else:
            print("✗ Errores semánticos encontrados:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("Advertencias:")
            for warning in warnings:
                print(f"  - {warning}")
                
    except Exception as e:
        print(f"Error: {e}")
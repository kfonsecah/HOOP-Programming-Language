"""
Intérprete para el lenguaje HOOP
===============================

Este módulo se encarga de ejecutar el código HOOP después de que haya pasado
por las fases de análisis léxico, sintáctico y semántico.

Proceso: AST validado → Ejecución del programa
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
import sys
from io import StringIO
from core.parser import *
from core.semantic import HoopType, Symbol, Scope
from core.lexer import Token

# ============================================================================
# ENTORNO DE EJECUCIÓN
# ============================================================================

@dataclass
class HoopValue:
    """Representa un valor en tiempo de ejecución"""
    value: Any
    type: HoopType
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return f"HoopValue({self.value}, {self.type})"

class HoopEnvironment:
    """
    Entorno de ejecución que mantiene las variables y sus valores
    Similar a un Scope pero para valores en tiempo de ejecución
    """
    
    def __init__(self, parent: Optional['HoopEnvironment'] = None):
        self.variables: Dict[str, HoopValue] = {}
        self.parent = parent
    
    def define(self, name: str, value: HoopValue):
        """Define una variable en este entorno"""
        self.variables[name] = value
    
    def get(self, name: str) -> Optional[HoopValue]:
        """Obtiene el valor de una variable"""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        return None
    
    def assign(self, name: str, value: HoopValue):
        """Asigna un valor a una variable existente"""
        if name in self.variables:
            self.variables[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        # Si no existe, la definimos en el entorno actual
        self.define(name, value)

# ============================================================================
# EXCEPCIONES DEL INTÉRPRETE
# ============================================================================

class HoopRuntimeError(Exception):
    """Excepción para errores en tiempo de ejecución"""
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"Error de ejecución en línea {token.line}: {message}")
        else:
            super().__init__(f"Error de ejecución: {message}")

class HoopReturn(Exception):
    """Excepción especial para manejar return statements"""
    def __init__(self, value: HoopValue):
        self.value = value

class HoopBreak(Exception):
    """Excepción especial para manejar break statements"""
    pass

class HoopContinue(Exception):
    """Excepción especial para manejar continue statements"""
    pass

# ============================================================================
# FUNCIÓN HOOP
# ============================================================================

@dataclass
class HoopFunction:
    """Representa una función definida por el usuario"""
    declaration: FunctionDeclaration
    closure: HoopEnvironment
    
    def call(self, interpreter: 'HoopInterpreter', arguments: List[HoopValue]) -> HoopValue:
        """Ejecuta la función con los argumentos dados"""
        # Crear nuevo entorno para la función
        environment = HoopEnvironment(self.closure)
        
        # Asignar parámetros
        for i, param in enumerate(self.declaration.parameters):
            if i < len(arguments):
                environment.define(param, arguments[i])
            else:
                # Parámetro sin valor - usar None
                environment.define(param, HoopValue(None, HoopType.NONE))
        
        try:
            # Ejecutar cuerpo de la función
            previous_env = interpreter.environment
            interpreter.environment = environment
            
            for statement in self.declaration.body:
                interpreter._execute_statement(statement)
            
            # Si no hay return explícito, devolver None
            return HoopValue(None, HoopType.NONE)
            
        except HoopReturn as ret:
            return ret.value
        finally:
            interpreter.environment = previous_env

# ============================================================================
# INTÉRPRETE PRINCIPAL
# ============================================================================

class HoopInterpreter:
    """
    Intérprete para el lenguaje HOOP
    
    Responsabilidades:
    - Ejecutar declaraciones y expresiones del AST
    - Mantener el estado de variables y funciones
    - Manejar control de flujo (if, while, for, return, break, continue)
    - Ejecutar operaciones aritméticas y lógicas
    - Gestionar llamadas a funciones
    - Proporcionar funciones built-in (show, input, etc.)
    """
    
    def __init__(self, output_stream=None):
        self.globals = HoopEnvironment()
        self.environment = self.globals
        
        # Stream para capturar output (útil para testing)
        self.output_stream = output_stream or sys.stdout
        
        # Definir funciones built-in
        self._define_builtin_functions()
    
    def interpret(self, program: Program):
        """
        Ejecuta un programa HOOP
        
        Args:
            program: AST del programa a ejecutar
            
        Raises:
            HoopRuntimeError: Si ocurre un error durante la ejecución
        """
        try:
            for statement in program.statements:
                self._execute_statement(statement)
        except HoopRuntimeError:
            raise
        except Exception as e:
            raise HoopRuntimeError(f"Error interno del intérprete: {str(e)}")
    
    def _define_builtin_functions(self):
        """Define las funciones built-in del lenguaje"""
        # TODO: Implementar funciones built-in completas
        
        def builtin_show(*args):
            """Función show() - imprime valores"""
            output = " ".join(str(arg.value) for arg in args)
            print(output, file=self.output_stream)
            return HoopValue(None, HoopType.NONE)
        
        def builtin_input(prompt=None):
            """Función input() - recibe entrada del usuario"""
            prompt_text = prompt.value if prompt else ""
            try:
                user_input = input(prompt_text)
                return HoopValue(user_input, HoopType.STRING)
            except EOFError:
                return HoopValue("", HoopType.STRING)
        
        def builtin_len(obj):
            """Función len() - devuelve longitud"""
            if obj.type == HoopType.STRING:
                return HoopValue(len(obj.value), HoopType.INTEGER)
            elif obj.type == HoopType.LIST:
                return HoopValue(len(obj.value), HoopType.INTEGER)
            else:
                raise HoopRuntimeError(f"len() no aplicable a tipo {obj.type.value}")
        
        def builtin_type(obj):
            """Función type() - devuelve tipo del objeto"""
            return HoopValue(obj.type.value, HoopType.STRING)
        
        # Registrar funciones built-in
        self.globals.define("show", HoopValue(builtin_show, HoopType.FUNCTION))
        self.globals.define("input", HoopValue(builtin_input, HoopType.FUNCTION))
        self.globals.define("len", HoopValue(builtin_len, HoopType.FUNCTION))
        self.globals.define("type", HoopValue(builtin_type, HoopType.FUNCTION))
    
    def _execute_statement(self, stmt: Statement):
        """
        Ejecuta una declaración/sentencia
        
        TODO: Implementar ejecución para cada tipo de statement:
        - FunctionDeclaration: definir función en el entorno
        - ClassDeclaration: definir clase (futuro)
        - AssignmentStatement: asignar valor a variable
        - IfStatement: evaluar condición y ejecutar rama correspondiente
        - WhileStatement: bucle while
        - ForStatement: bucle for
        - ReturnStatement: lanzar excepción HoopReturn
        - ShowStatement: ejecutar función show
        - BreakStatement/ContinueStatement: lanzar excepciones correspondientes
        - ExpressionStatement: evaluar expresión
        """
        
        if isinstance(stmt, FunctionDeclaration):
            self._execute_function_declaration(stmt)
        elif isinstance(stmt, ClassDeclaration):
            self._execute_class_declaration(stmt)
        elif isinstance(stmt, AssignmentStatement):
            self._execute_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            self._execute_if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            self._execute_while_statement(stmt)
        elif isinstance(stmt, ForStatement):
            self._execute_for_statement(stmt)
        elif isinstance(stmt, ReturnStatement):
            self._execute_return_statement(stmt)
        elif isinstance(stmt, ShowStatement):
            self._execute_show_statement(stmt)
        elif isinstance(stmt, BreakStatement):
            raise HoopBreak()
        elif isinstance(stmt, ContinueStatement):
            raise HoopContinue()
        elif isinstance(stmt, ExpressionStatement):
            self._evaluate_expression(stmt.expression)
        else:
            raise HoopRuntimeError(f"Tipo de declaración no soportado: {type(stmt).__name__}")
    
    def _execute_function_declaration(self, func_decl: FunctionDeclaration):
        """Define una función en el entorno actual"""
        function = HoopFunction(func_decl, self.environment)
        self.environment.define(func_decl.name, HoopValue(function, HoopType.FUNCTION))
    
    def _execute_class_declaration(self, class_decl: ClassDeclaration):
        """Define una clase (placeholder para futuro)"""
        # TODO: Implementar clases en versiones futuras
        pass
    
    def _execute_assignment(self, assign: AssignmentStatement):
        """Ejecuta una asignación de variable"""
        value = self._evaluate_expression(assign.value)
        self.environment.assign(assign.target.name, value)
    
    def _execute_if_statement(self, if_stmt: IfStatement):
        """Ejecuta una declaración if"""
        condition = self._evaluate_expression(if_stmt.condition)
        
        if self._is_truthy(condition):
            for statement in if_stmt.then_branch:
                self._execute_statement(statement)
        elif if_stmt.else_branch:
            for statement in if_stmt.else_branch:
                self._execute_statement(statement)
    
    def _execute_while_statement(self, while_stmt: WhileStatement):
        """Ejecuta un bucle while"""
        try:
            while True:
                condition = self._evaluate_expression(while_stmt.condition)
                if not self._is_truthy(condition):
                    break
                
                try:
                    for statement in while_stmt.body:
                        self._execute_statement(statement)
                except HoopContinue:
                    continue
                except HoopBreak:
                    break
        except HoopBreak:
            pass
    
    def _execute_for_statement(self, for_stmt: ForStatement):
        """
        Ejecuta un bucle for
        
        TODO: Implementar iteración sobre listas y strings
        """
        iterable = self._evaluate_expression(for_stmt.iterable)
        
        if iterable.type not in [HoopType.LIST, HoopType.STRING]:
            raise HoopRuntimeError(f"No se puede iterar sobre tipo {iterable.type.value}", for_stmt.token)
        
        # Crear nuevo entorno para la variable de iteración
        previous_env = self.environment
        self.environment = HoopEnvironment(previous_env)
        
        try:
            items = iterable.value
            for item in items:
                # Determinar tipo del item
                if iterable.type == HoopType.STRING:
                    item_value = HoopValue(item, HoopType.STRING)
                else:
                    # Para listas, asumir que los elementos mantienen su tipo
                    item_value = HoopValue(item, HoopType.UNKNOWN)  # TODO: mejorar tipado
                
                self.environment.define(for_stmt.variable, item_value)
                
                try:
                    for statement in for_stmt.body:
                        self._execute_statement(statement)
                except HoopContinue:
                    continue
                except HoopBreak:
                    break
        except HoopBreak:
            pass
        finally:
            self.environment = previous_env
    
    def _execute_return_statement(self, ret_stmt: ReturnStatement):
        """Ejecuta una declaración return"""
        value = HoopValue(None, HoopType.NONE)
        if ret_stmt.value:
            value = self._evaluate_expression(ret_stmt.value)
        raise HoopReturn(value)
    
    def _execute_show_statement(self, show_stmt: ShowStatement):
        """Ejecuta una declaración show"""
        value = self._evaluate_expression(show_stmt.expression)
        print(value.value, file=self.output_stream)
    
    def _evaluate_expression(self, expr: Expression) -> HoopValue:
        """
        Evalúa una expresión y devuelve su valor
        
        TODO: Implementar evaluación para cada tipo de expresión:
        - LiteralExpression: devolver el valor literal
        - IdentifierExpression: buscar variable en el entorno
        - BinaryExpression: evaluar operandos y aplicar operador
        - UnaryExpression: evaluar operando y aplicar operador
        - CallExpression: llamar función con argumentos
        - ListExpression: crear lista con elementos evaluados
        """
        
        if isinstance(expr, LiteralExpression):
            return self._evaluate_literal(expr)
        elif isinstance(expr, IdentifierExpression):
            return self._evaluate_identifier(expr)
        elif isinstance(expr, BinaryExpression):
            return self._evaluate_binary_expression(expr)
        elif isinstance(expr, UnaryExpression):
            return self._evaluate_unary_expression(expr)
        elif isinstance(expr, CallExpression):
            return self._evaluate_call_expression(expr)
        elif isinstance(expr, ListExpression):
            return self._evaluate_list_expression(expr)
        else:
            raise HoopRuntimeError(f"Tipo de expresión no soportado: {type(expr).__name__}")
    
    def _evaluate_literal(self, literal: LiteralExpression) -> HoopValue:
        """Evalúa un literal"""
        value = literal.value
        
        if isinstance(value, bool):
            return HoopValue(value, HoopType.BOOLEAN)
        elif isinstance(value, int):
            return HoopValue(value, HoopType.INTEGER)
        elif isinstance(value, float):
            return HoopValue(value, HoopType.FLOAT)
        elif isinstance(value, str):
            return HoopValue(value, HoopType.STRING)
        elif value is None:
            return HoopValue(None, HoopType.NONE)
        else:
            return HoopValue(value, HoopType.UNKNOWN)
    
    def _evaluate_identifier(self, identifier: IdentifierExpression) -> HoopValue:
        """Evalúa un identificador (variable)"""
        value = self.environment.get(identifier.name)
        if value is None:
            raise HoopRuntimeError(f"Variable '{identifier.name}' no está definida", identifier.token)
        return value
    
    def _evaluate_binary_expression(self, binary: BinaryExpression) -> HoopValue:
        """Evalúa una expresión binaria"""
        left = self._evaluate_expression(binary.left)
        right = self._evaluate_expression(binary.right)
        
        operator = binary.operator.value
        
        # Operaciones aritméticas
        if operator == '+':
            return self._add_values(left, right, binary.operator)
        elif operator == '-':
            return self._subtract_values(left, right, binary.operator)
        elif operator == '*':
            return self._multiply_values(left, right, binary.operator)
        elif operator == '/':
            return self._divide_values(left, right, binary.operator)
        elif operator == '%':
            return self._modulo_values(left, right, binary.operator)
        
        # Operaciones de comparación
        elif operator == '==':
            return HoopValue(left.value == right.value, HoopType.BOOLEAN)
        elif operator == '!=':
            return HoopValue(left.value != right.value, HoopType.BOOLEAN)
        elif operator == '<':
            return HoopValue(left.value < right.value, HoopType.BOOLEAN)
        elif operator == '>':
            return HoopValue(left.value > right.value, HoopType.BOOLEAN)
        elif operator == '<=':
            return HoopValue(left.value <= right.value, HoopType.BOOLEAN)
        elif operator == '>=':
            return HoopValue(left.value >= right.value, HoopType.BOOLEAN)
        
        # Operaciones lógicas
        elif operator == 'and':
            return HoopValue(self._is_truthy(left) and self._is_truthy(right), HoopType.BOOLEAN)
        elif operator == 'or':
            return HoopValue(self._is_truthy(left) or self._is_truthy(right), HoopType.BOOLEAN)
        
        else:
            raise HoopRuntimeError(f"Operador binario no soportado: {operator}", binary.operator)
    
    def _evaluate_unary_expression(self, unary: UnaryExpression) -> HoopValue:
        """Evalúa una expresión unaria"""
        operand = self._evaluate_expression(unary.operand)
        operator = unary.operator.value
        
        if operator == '-':
            if operand.type in [HoopType.INTEGER, HoopType.FLOAT]:
                return HoopValue(-operand.value, operand.type)
            else:
                raise HoopRuntimeError(f"Operador - no aplicable a {operand.type.value}", unary.operator)
        
        elif operator == 'not':
            return HoopValue(not self._is_truthy(operand), HoopType.BOOLEAN)
        
        else:
            raise HoopRuntimeError(f"Operador unario no soportado: {operator}", unary.operator)
    
    def _evaluate_call_expression(self, call: CallExpression) -> HoopValue:
        """Evalúa una llamada a función"""
        function = self._evaluate_expression(call.function)
        
        # Evaluar argumentos
        arguments = [self._evaluate_expression(arg) for arg in call.arguments]
        
        if function.type != HoopType.FUNCTION:
            raise HoopRuntimeError(f"'{call.function}' no es una función", call.token)
        
        # Distinguir entre funciones built-in y funciones de usuario
        if callable(function.value):
            # Función built-in
            try:
                return function.value(*arguments)
            except TypeError as e:
                raise HoopRuntimeError(f"Error en llamada a función: {str(e)}", call.token)
        elif isinstance(function.value, HoopFunction):
            # Función de usuario
            return function.value.call(self, arguments)
        else:
            raise HoopRuntimeError("Tipo de función no reconocido", call.token)
    
    def _evaluate_list_expression(self, list_expr: ListExpression) -> HoopValue:
        """Evalúa una expresión de lista"""
        elements = [self._evaluate_expression(elem) for elem in list_expr.elements]
        # Extraer valores reales para la lista
        values = [elem.value for elem in elements]
        return HoopValue(values, HoopType.LIST)
    
    # ========================================================================
    # OPERACIONES ARITMÉTICAS
    # ========================================================================
    
    def _add_values(self, left: HoopValue, right: HoopValue, token: Token) -> HoopValue:
        """Suma dos valores"""
        if left.type in [HoopType.INTEGER, HoopType.FLOAT] and right.type in [HoopType.INTEGER, HoopType.FLOAT]:
            result = left.value + right.value
            result_type = HoopType.FLOAT if left.type == HoopType.FLOAT or right.type == HoopType.FLOAT else HoopType.INTEGER
            return HoopValue(result, result_type)
        elif left.type == HoopType.STRING and right.type == HoopType.STRING:
            return HoopValue(left.value + right.value, HoopType.STRING)
        else:
            raise HoopRuntimeError(f"No se puede sumar {left.type.value} y {right.type.value}", token)
    
    def _subtract_values(self, left: HoopValue, right: HoopValue, token: Token) -> HoopValue:
        """Resta dos valores"""
        if left.type in [HoopType.INTEGER, HoopType.FLOAT] and right.type in [HoopType.INTEGER, HoopType.FLOAT]:
            result = left.value - right.value
            result_type = HoopType.FLOAT if left.type == HoopType.FLOAT or right.type == HoopType.FLOAT else HoopType.INTEGER
            return HoopValue(result, result_type)
        else:
            raise HoopRuntimeError(f"No se puede restar {left.type.value} y {right.type.value}", token)
    
    def _multiply_values(self, left: HoopValue, right: HoopValue, token: Token) -> HoopValue:
        """Multiplica dos valores"""
        if left.type in [HoopType.INTEGER, HoopType.FLOAT] and right.type in [HoopType.INTEGER, HoopType.FLOAT]:
            result = left.value * right.value
            result_type = HoopType.FLOAT if left.type == HoopType.FLOAT or right.type == HoopType.FLOAT else HoopType.INTEGER
            return HoopValue(result, result_type)
        else:
            raise HoopRuntimeError(f"No se puede multiplicar {left.type.value} y {right.type.value}", token)
    
    def _divide_values(self, left: HoopValue, right: HoopValue, token: Token) -> HoopValue:
        """Divide dos valores"""
        if left.type in [HoopType.INTEGER, HoopType.FLOAT] and right.type in [HoopType.INTEGER, HoopType.FLOAT]:
            if right.value == 0:
                raise HoopRuntimeError("División por cero", token)
            result = left.value / right.value
            return HoopValue(result, HoopType.FLOAT)
        else:
            raise HoopRuntimeError(f"No se puede dividir {left.type.value} y {right.type.value}", token)
    
    def _modulo_values(self, left: HoopValue, right: HoopValue, token: Token) -> HoopValue:
        """Calcula el módulo de dos valores"""
        if left.type in [HoopType.INTEGER, HoopType.FLOAT] and right.type in [HoopType.INTEGER, HoopType.FLOAT]:
            if right.value == 0:
                raise HoopRuntimeError("Módulo por cero", token)
            result = left.value % right.value
            result_type = HoopType.FLOAT if left.type == HoopType.FLOAT or right.type == HoopType.FLOAT else HoopType.INTEGER
            return HoopValue(result, result_type)
        else:
            raise HoopRuntimeError(f"No se puede calcular módulo de {left.type.value} y {right.type.value}", token)
    
    def _is_truthy(self, value: HoopValue) -> bool:
        """Determina si un valor es considerado verdadero"""
        if value.type == HoopType.BOOLEAN:
            return value.value
        elif value.type == HoopType.NONE:
            return False
        elif value.type == HoopType.INTEGER:
            return value.value != 0
        elif value.type == HoopType.FLOAT:
            return value.value != 0.0
        elif value.type == HoopType.STRING:
            return len(value.value) > 0
        elif value.type == HoopType.LIST:
            return len(value.value) > 0
        else:
            return True

# ============================================================================
# FUNCIÓN DE UTILIDAD
# ============================================================================

def execute_hoop_code(code: str, output_stream=None) -> str:
    """
    Función de conveniencia para ejecutar código HOOP completo
    
    Args:
        code: Código fuente en HOOP
        output_stream: Stream para capturar output (opcional)
        
    Returns:
        str: Output del programa (si se proporciona output_stream)
    """
    from core.lexer import HoopLexer
    from core.parser import HoopParser
    from core.semantic import HoopSemanticAnalyzer
    
    # Capturar output si no se proporciona stream
    capture_output = output_stream is None
    if capture_output:
        output_stream = StringIO()
    
    try:
        # Análisis léxico
        lexer = HoopLexer()
        tokens = lexer.tokenize(code)
        
        # Análisis sintáctico
        parser = HoopParser()
        ast = parser.parse(tokens)
        
        # Análisis semántico
        semantic_analyzer = HoopSemanticAnalyzer()
        is_valid = semantic_analyzer.analyze(ast)
        
        if not is_valid:
            errors = semantic_analyzer.get_errors()
            error_messages = [str(error) for error in errors]
            raise HoopRuntimeError("Errores semánticos:\n" + "\n".join(error_messages))
        
        # Ejecución
        interpreter = HoopInterpreter(output_stream)
        interpreter.interpret(ast)
        
        if capture_output:
            return output_stream.getvalue()
        return ""
        
    except Exception as e:
        if capture_output:
            return f"Error: {str(e)}"
        else:
            print(f"Error: {str(e)}", file=output_stream)
            return ""

if __name__ == "__main__":
    # Ejemplo de uso
    sample_code = """
    def greet(name):
        show("Hola, " + name + "!")
    
    def calculate_area(width, height):
        return width * height
    
    # Programa principal
    greet("Mundo")
    
    area = calculate_area(10, 5)
    show("El área es: ")
    show(area)
    
    # Bucle de ejemplo
    numbers = [1, 2, 3, 4, 5]
    for num in numbers:
        show(num * 2)
    """
    
    try:
        output = execute_hoop_code(sample_code)
        print("Salida del programa:")
        print(output)
    except Exception as e:
        print(f"Error: {e}")
#!/usr/bin/env python3
"""
Interprete de HOOP - Ejecuta el AST validado

"""

import math
import random
import sys
from typing import Any, Dict, List, Optional
from . import ast_nodes

class ReturnException(Exception):
    """Excepcion para manejar el retorno de funciones (answer)"""
    def __init__(self, value):
        self.value = value

class HoopRuntimeError(Exception):
    """Error en tiempo de ejecucion"""
    pass

class HoopObject:
    """Representa una instancia de una clase HOOP"""
    def __init__(self, class_name: str):
        self.class_name = class_name
        self.attributes = {}
    
    def get_attribute(self, name: str):
        if name in self.attributes:
            return self.attributes[name]
        raise HoopRuntimeError(f"Atributo '{name}' no existe en {self.class_name}")
    
    def set_attribute(self, name: str, value: Any):
        self.attributes[name] = value
    
    def __repr__(self):
        return f"<{self.class_name} instance>"

class ExecutionContext:
    """Contexto de ejecucion con scopes anidados"""
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}
        self.functions = {}
        self.classes = {}
    
    def define_variable(self, name: str, value: Any):
        """Define una variable en el scope actual"""
        self.variables[name] = value
    
    def get_variable(self, name: str):
        """Obtiene una variable buscando en scopes padre si es necesario"""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get_variable(name)
        raise HoopRuntimeError(f"Variable '{name}' no esta definida")
    
    def set_variable(self, name: str, value: Any):
        """Asigna valor a variable existente"""
        if name in self.variables:
            self.variables[name] = value
            return
        if self.parent:
            self.parent.set_variable(name, value)
            return
        raise HoopRuntimeError(f"Variable '{name}' no esta definida")
    
    def define_function(self, name: str, func_node):
        """Define una funcion"""
        self.functions[name] = func_node
    
    def get_function(self, name: str):
        """Obtiene una funcion"""
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.get_function(name)
        raise HoopRuntimeError(f"Funcion '{name}' no esta definida")
    
    def define_class(self, name: str, class_node):
        """Define una clase"""
        self.classes[name] = class_node
    
    def get_class(self, name: str):
        """Obtiene una clase"""
        if name in self.classes:
            return self.classes[name]
        if self.parent:
            return self.parent.get_class(name)
        raise HoopRuntimeError(f"Clase '{name}' no esta definida")

class HoopInterpreter:
    """Interprete principal de HOOP"""
    
    def __init__(self):
        self.global_context = ExecutionContext()
        self.current_context = self.global_context
        self.current_instance = None  # Para manejar 'self'
        self.output = []  # Captura salida de display
    
    def interpret(self, ast: ast_nodes.ProgramaNode):
        """Ejecuta el programa completo"""
        try:
            self.visit(ast)
            return True, None
        except HoopRuntimeError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error inesperado: {e}"
    
    def visit(self, node):
        """Visitor pattern - delega a metodo especifico segun tipo de nodo"""
        # Ignorar nodos None
        if node is None:
            return None
        
        method_name = f'visit_{node.__class__.__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        """Fallback para nodos sin visitor especifico"""
        raise HoopRuntimeError(f"No hay visitor para {node.__class__.__name__}")
    
    # ========== PROGRAMA Y DECLARACIONES ==========
    
    def visit_ProgramaNode(self, node: ast_nodes.ProgramaNode):
        """Ejecuta todas las declaraciones del programa"""
        for declaracion in node.declaraciones:
            self.visit(declaracion)
    
    def visit_DeclaracionNode(self, node: ast_nodes.DeclaracionNode):
        """Ejecuta declaracion de variable: data x set valor;"""
        valor = self.visit(node.valor)
        self.current_context.define_variable(node.nombre, valor)
    
    def visit_FuncionNode(self, node: ast_nodes.FuncionNode):
        """Registra funcion para uso posterior"""
        self.current_context.define_function(node.nombre, node)
    
    def visit_ClaseNode(self, node: ast_nodes.ClaseNode):
        """Registra clase para uso posterior"""
        self.current_context.define_class(node.nombre, node)
    
    # ========== STATEMENTS ==========
    
    def visit_DisplayNode(self, node: ast_nodes.DisplayNode):
        """Ejecuta display (print)"""
        valor = self.visit(node.expresion)
        output = self._convert_to_string(valor)
        self.output.append(output)
        print(output)
    
    def visit_AsignacionNode(self, node: ast_nodes.AsignacionNode):
        """Ejecuta asignacion: variable set valor;"""
        valor = self.visit(node.valor)
        
        # Manejar el caso donde variable puede ser un IdentificadorNode o un string
        if isinstance(node.variable, ast_nodes.IdentificadorNode):
            nombre_variable = node.variable.nombre
        else:
            nombre_variable = node.variable
        
        self.current_context.set_variable(nombre_variable, valor)
    
    def visit_AssignmentNode(self, node: ast_nodes.AssignmentNode):
        """Alias para AsignacionNode"""
        return self.visit_AsignacionNode(node)
    
    def visit_ReturnNode(self, node: ast_nodes.ReturnNode):
        """Ejecuta answer (return)"""
        valor = self.visit(node.valor) if node.valor else None
        raise ReturnException(valor)
    
    def visit_IfStatementNode(self, node: ast_nodes.IfStatementNode):
        """Ejecuta when/otherwise (if/else)"""
        condicion = self.visit(node.condicion)
        
        if self._is_truthy(condicion):
            bloque_then = node.bloque_then if isinstance(node.bloque_then, list) else [node.bloque_then]
            for stmt in bloque_then:
                self.visit(stmt)
        elif node.bloque_else:
            bloque_else = node.bloque_else if isinstance(node.bloque_else, list) else [node.bloque_else]
            for stmt in bloque_else:
                self.visit(stmt)
    
    def visit_CycleStatementNode(self, node: ast_nodes.CycleStatementNode):
        """Ejecuta cycle from to (for loop)"""
        inicio = self.visit(node.inicio)
        fin = self.visit(node.fin)
        
        if not isinstance(inicio, int) or not isinstance(fin, int):
            raise HoopRuntimeError("cycle requiere valores enteros para from y to")
        
        # Crear nuevo scope para el ciclo
        loop_context = ExecutionContext(self.current_context)
        prev_context = self.current_context
        self.current_context = loop_context
        
        try:
            for i in range(inicio, fin + 1):
                self.current_context.define_variable(node.variable, i)
                for stmt in node.cuerpo:
                    self.visit(stmt)
        finally:
            self.current_context = prev_context
    
    # ========== EXPRESIONES ==========
    
    def visit_LiteralNode(self, node: ast_nodes.LiteralNode):
        """Retorna valor literal convertido al tipo apropiado"""
        if node.tipo == "NUMBER":
            # Convertir string a numero
            valor_str = node.valor
            if '.' in valor_str:
                return float(valor_str)
            else:
                return int(valor_str)
        elif node.tipo == "BOOLEAN":
            return node.valor == 'true'
        elif node.tipo == "STRING":
            return node.valor
        elif node.tipo == "CHARACTER":
            return node.valor
        else:
            return node.valor
    
    def visit_IdentificadorNode(self, node: ast_nodes.IdentificadorNode):
        """Obtiene valor de variable o constante"""
        # Manejar 'self'
        if node.nombre == 'self':
            if self.current_instance is None:
                raise HoopRuntimeError("'self' solo puede usarse dentro de métodos")
            return self.current_instance
        
        # Manejar constantes booleanas
        if node.nombre == 'true':
            return True
        if node.nombre == 'false':
            return False
        
        # Variable normal
        return self.current_context.get_variable(node.nombre)
    
    def visit_OperacionNode(self, node: ast_nodes.OperacionNode):
        """Ejecuta operaciones aritméticas, lógicas y de comparación"""
        izq = self.visit(node.izquierda)
        der = self.visit(node.derecha)
        op = node.operador
        
        # Operaciones aritmeticas
        if op == 'plus' or op == '+':
            return izq + der
        elif op == 'minus' or op == '-':
            return izq - der
        elif op == 'times' or op == '*':
            return izq * der
        elif op == 'divide' or op == '/':
            if der == 0:
                raise HoopRuntimeError("Division por cero")
            return izq / der
        elif op == 'mod' or op == '%':
            return izq % der
        
        # Operaciones de comparacion
        elif op == 'equals' or op == '==':
            return izq == der
        elif op == 'greater' or op == '>':
            return izq > der
        elif op == 'less' or op == '<':
            return izq < der
        elif op == 'greaterequals' or op == '>=':
            return izq >= der
        elif op == 'lessequals' or op == '<=':
            return izq <= der
        elif op == 'notequals' or op == '!=':
            return izq != der
        
        # Operaciones logicas
        elif op == 'and' or op == '&&':
            return self._is_truthy(izq) and self._is_truthy(der)
        elif op == 'or' or op == '||':
            return self._is_truthy(izq) or self._is_truthy(der)
        
        else:
            raise HoopRuntimeError(f"Operador desconocido: {op}")
    
    def visit_OperacionUnaria(self, node: ast_nodes.OperacionUnaria):
        """Ejecuta operación unaria (not)"""
        valor = self.visit(node.expresion)
        
        if node.operador == 'not' or node.operador == '!':
            return not self._is_truthy(valor)
        elif node.operador == '-':
            return -valor
        else:
            raise HoopRuntimeError(f"Operador unario desconocido: {node.operador}")
    
    def visit_LlamadaFuncionNode(self, node: ast_nodes.LlamadaFuncionNode):
        """Ejecuta llamada a función"""
        nombre = node.nombre
        
        # Manejar forge especial: forge<NombreClase>
        if nombre.startswith("forge<") and nombre.endswith(">"):
            nombre_clase = nombre[6:-1]  # Extraer nombre entre < >
            return self._execute_forge(nombre_clase, node.argumentos)
        
        # Manejar llamada a método: objeto.metodo
        if "." in nombre:
            partes = nombre.split(".", 1)
            objeto_nombre = partes[0]
            metodo_nombre = partes[1]
            
            objeto = self.current_context.get_variable(objeto_nombre)
            return self._execute_method(objeto, metodo_nombre, node.argumentos)
        
        # Funciones built-in
        if nombre in BUILTIN_FUNCTIONS:
            return self._call_builtin(nombre, node.argumentos)
        
        # Función definida por usuario
        func_node = self.current_context.get_function(nombre)
        
        # Evaluar argumentos
        args = [self.visit(arg) for arg in node.argumentos]
        
        # Verificar número de argumentos
        if len(args) != len(func_node.parametros):
            raise HoopRuntimeError(
                f"Función '{nombre}' espera {len(func_node.parametros)} argumentos, "
                f"pero se pasaron {len(args)}"
            )
        
        # Crear nuevo contexto para la función
        func_context = ExecutionContext(self.global_context)
        prev_context = self.current_context
        self.current_context = func_context
        
        # Definir parámetros
        for param, arg in zip(func_node.parametros, args):
            if isinstance(param, ast_nodes.ParametroNode):
                param_name = param.nombre
            elif isinstance(param, dict):
                param_name = param['nombre']
            else:
                param_name = param
            self.current_context.define_variable(param_name, arg)
        
        try:
            # Ejecutar cuerpo de la función
            for stmt in func_node.cuerpo:
                self.visit(stmt)
            return None  # Si no hay return explícito
        except ReturnException as e:
            return e.value
        finally:
            self.current_context = prev_context
    
    def _execute_forge(self, nombre_clase: str, argumentos: List):
        """Ejecuta construcción de objeto: forge Clase()"""
        class_node = self.current_context.get_class(nombre_clase)
        
        # Crear instancia
        instance = HoopObject(nombre_clase)
        
        # Evaluar argumentos del constructor
        args = [self.visit(arg) for arg in argumentos]
        
        # Buscar método inicializar
        inicializar_method = None
        for stmt in class_node.cuerpo:
            if isinstance(stmt, ast_nodes.FuncionNode) and stmt.nombre == 'inicializar':
                inicializar_method = stmt
                break
        
        # Llamar inicializar si existe
        if inicializar_method:
            if len(args) != len(inicializar_method.parametros):
                raise HoopRuntimeError(
                    f"Constructor de '{nombre_clase}' espera {len(inicializar_method.parametros)} "
                    f"argumentos, pero se pasaron {len(args)}"
                )
            
            # Ejecutar inicializar con self
            method_context = ExecutionContext(self.global_context)
            prev_context = self.current_context
            prev_instance = self.current_instance
            
            self.current_context = method_context
            self.current_instance = instance
            
            # Definir parámetros
            for param, arg in zip(inicializar_method.parametros, args):
                if isinstance(param, ast_nodes.ParametroNode):
                    param_name = param.nombre
                elif isinstance(param, dict):
                    param_name = param['nombre']
                else:
                    param_name = param
                self.current_context.define_variable(param_name, arg)
            
            try:
                for stmt in inicializar_method.cuerpo:
                    self.visit(stmt)
            except ReturnException:
                pass  # Ignorar return en constructor
            finally:
                self.current_context = prev_context
                self.current_instance = prev_instance
        
        return instance
    
    def _execute_method(self, objeto, metodo_nombre: str, argumentos: List):
        """Ejecuta llamada a método: objeto.metodo()"""
        if not isinstance(objeto, HoopObject):
            raise HoopRuntimeError(f"Solo objetos pueden tener métodos")
        
        # Obtener clase del objeto
        class_node = self.current_context.get_class(objeto.class_name)
        
        # Buscar método en la clase
        method_node = None
        for stmt in class_node.cuerpo:
            if isinstance(stmt, ast_nodes.FuncionNode) and stmt.nombre == metodo_nombre:
                method_node = stmt
                break
        
        if not method_node:
            raise HoopRuntimeError(f"Método '{metodo_nombre}' no existe en {objeto.class_name}")
        
        # Evaluar argumentos
        args = [self.visit(arg) for arg in argumentos]
        
        # Verificar número de argumentos
        if len(args) != len(method_node.parametros):
            raise HoopRuntimeError(
                f"Método '{metodo_nombre}' espera {len(method_node.parametros)} argumentos, "
                f"pero se pasaron {len(args)}"
            )
        
        # Crear contexto para el método
        method_context = ExecutionContext(self.global_context)
        prev_context = self.current_context
        prev_instance = self.current_instance
        
        self.current_context = method_context
        self.current_instance = objeto
        
        # Definir parámetros
        for param, arg in zip(method_node.parametros, args):
            if isinstance(param, ast_nodes.ParametroNode):
                param_name = param.nombre
            elif isinstance(param, dict):
                param_name = param['nombre']
            else:
                param_name = param
            self.current_context.define_variable(param_name, arg)
        
        try:
            for stmt in method_node.cuerpo:
                self.visit(stmt)
            return None
        except ReturnException as e:
            return e.value
        finally:
            self.current_context = prev_context
            self.current_instance = prev_instance
    
    def visit_ForgeNode(self, node: ast_nodes.ForgeNode):
        """Ejecuta construcción de objeto: forge Clase()"""
        return self._execute_forge(node.clase, node.argumentos)
    
    def visit_AccesoMiembroNode(self, node: ast_nodes.AccesoMiembroNode):
        """Ejecuta acceso a atributo: objeto.atributo"""
        # node.objeto es un IdentificadorNode
        if isinstance(node.objeto, ast_nodes.IdentificadorNode):
            objeto_nombre = node.objeto.nombre
            
            # Caso especial: self
            if objeto_nombre == 'self':
                if self.current_instance is None:
                    raise HoopRuntimeError("'self' solo puede usarse dentro de métodos")
                return self.current_instance.get_attribute(node.miembro)
            
            # Caso general
            objeto = self.current_context.get_variable(objeto_nombre)
        else:
            objeto = self.visit(node.objeto)
        
        if not isinstance(objeto, HoopObject):
            raise HoopRuntimeError(f"Solo objetos pueden tener atributos")
        
        return objeto.get_attribute(node.miembro)
    
    def visit_AttributeAccessNode(self, node: ast_nodes.AttributeAccessNode):
        """Alias para AccesoMiembroNode"""
        return self.visit_AccesoMiembroNode(node)
    
    def visit_AsignacionMiembroNode(self, node: ast_nodes.AsignacionMiembroNode):
        """Ejecuta asignación a atributo: objeto.atributo set valor;"""
        # Caso especial: self.atributo
        if isinstance(node.objeto, ast_nodes.IdentificadorNode) and node.objeto.nombre == 'self':
            if self.current_instance is None:
                raise HoopRuntimeError("'self' solo puede usarse dentro de métodos")
            
            valor = self.visit(node.valor)
            self.current_instance.set_attribute(node.miembro, valor)
            return
        
        # Caso general
        objeto = self.visit(node.objeto)
        
        if not isinstance(objeto, HoopObject):
            raise HoopRuntimeError(f"Solo objetos pueden tener atributos")
        
        valor = self.visit(node.valor)
        objeto.set_attribute(node.miembro, valor)
    
    def visit_LlamadaMetodoNode(self, node: ast_nodes.LlamadaMetodoNode):
        """Ejecuta llamada a método: objeto.metodo()"""
        objeto = self.visit(node.objeto)
        
        if not isinstance(objeto, HoopObject):
            raise HoopRuntimeError(f"Solo objetos pueden tener métodos")
        
        # Obtener clase del objeto
        class_node = self.current_context.get_class(objeto.class_name)
        
        # Buscar método en la clase
        method_node = None
        for stmt in class_node.cuerpo:
            if isinstance(stmt, ast_nodes.FuncionNode) and stmt.nombre == node.metodo:
                method_node = stmt
                break
        
        if not method_node:
            raise HoopRuntimeError(f"Método '{node.metodo}' no existe en {objeto.class_name}")
        
        # Evaluar argumentos
        args = [self.visit(arg) for arg in node.argumentos]
        
        # Verificar número de argumentos
        if len(args) != len(method_node.parametros):
            raise HoopRuntimeError(
                f"Método '{node.metodo}' espera {len(method_node.parametros)} argumentos, "
                f"pero se pasaron {len(args)}"
            )
        
        # Crear contexto para el método
        method_context = ExecutionContext(self.global_context)
        prev_context = self.current_context
        prev_instance = self.current_instance
        
        self.current_context = method_context
        self.current_instance = objeto
        
        # Definir parámetros  
        for param, arg in zip(method_node.parametros, args):
            if isinstance(param, ast_nodes.ParametroNode):
                param_name = param.nombre
            elif isinstance(param, dict):
                param_name = param['nombre']
            else:
                param_name = param
            self.current_context.define_variable(param_name, arg)
        
        try:
            for stmt in method_node.cuerpo:
                self.visit(stmt)
            return None
        except ReturnException as e:
            return e.value
        finally:
            self.current_context = prev_context
            self.current_instance = prev_instance
    
    # ========== FUNCIONES BUILT-IN ==========
    
    def _call_builtin(self, name: str, argumentos: List):
        """Llama a una función built-in"""
        args = [self.visit(arg) for arg in argumentos]
        
        if name == 'display':
            # Ya manejado por DisplayStatementNode
            if args:
                output = self._convert_to_string(args[0])
                self.output.append(output)
                print(output)
            return None
        
        elif name == 'length':
            if len(args) != 1:
                raise HoopRuntimeError("length() requiere 1 argumento")
            return len(args[0])
        
        elif name == 'size':
            if len(args) != 1:
                raise HoopRuntimeError("size() requiere 1 argumento")
            return len(args[0])
        
        elif name == 'type':
            if len(args) != 1:
                raise HoopRuntimeError("type() requiere 1 argumento")
            return type(args[0]).__name__
        
        elif name == 'input':
            prompt = args[0] if args else ""
            return input(self._convert_to_string(prompt))
        
        elif name == 'random':
            if len(args) == 0:
                return random.random()
            elif len(args) == 2:
                return random.randint(args[0], args[1])
            else:
                raise HoopRuntimeError("random() requiere 0 o 2 argumentos")
        
        elif name == 'abs':
            if len(args) != 1:
                raise HoopRuntimeError("abs() requiere 1 argumento")
            return abs(args[0])
        
        elif name == 'sqrt':
            if len(args) != 1:
                raise HoopRuntimeError("sqrt() requiere 1 argumento")
            return math.sqrt(args[0])
        
        elif name == 'pow':
            if len(args) != 2:
                raise HoopRuntimeError("pow() requiere 2 argumentos")
            return pow(args[0], args[1])
        
        elif name == 'convert':
            if len(args) != 2:
                raise HoopRuntimeError("convert() requiere 2 argumentos")
            valor, tipo = args
            if tipo == 'whole':
                return int(valor)
            elif tipo == 'fract':
                return float(valor)
            elif tipo == 'text':
                return str(valor)
            elif tipo == 'logic':
                return bool(valor)
            else:
                raise HoopRuntimeError(f"Tipo desconocido: {tipo}")
        
        else:
            raise HoopRuntimeError(f"Función built-in desconocida: {name}")
    
    # ========== UTILIDADES ==========
    
    def _is_truthy(self, value: Any) -> bool:
        """Determina si un valor es verdadero en contexto booleano"""
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return True
    
    def _convert_to_string(self, value: Any) -> str:
        """Convierte valor a string para display"""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if value is None:
            return 'null'
        if isinstance(value, HoopObject):
            return f"<{value.class_name} instance>"
        return str(value)
    
    def get_output(self) -> List[str]:
        """Obtiene toda la salida capturada"""
        return self.output.copy()
    
    def clear_output(self):
        """Limpia la salida capturada"""
        self.output.clear()

# Lista de funciones built-in
BUILTIN_FUNCTIONS = {
    'display', 'length', 'size', 'type', 'convert', 
    'input', 'random', 'abs', 'sqrt', 'pow'
}

def interpret_hoop(ast: ast_nodes.ProgramaNode) -> tuple[bool, Optional[str], List[str]]:
    """
    Función de alto nivel para interpretar un programa HOOP
    
    Args:
        ast: El árbol de sintaxis abstracta validado
    
    Returns:
        (success, error_message, output)
        - success: True si la ejecución fue exitosa
        - error_message: Mensaje de error si hubo uno, None si no
        - output: Lista de strings de salida (display)
    """
    interpreter = HoopInterpreter()
    success, error = interpreter.interpret(ast)
    output = interpreter.get_output()
    return success, error, output

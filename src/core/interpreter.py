#!/usr/bin/env python3
"""
Interprete de HOOP - Ejecuta el AST validado
"""
import math
import random
import sys
from typing import Any, Dict, List, Optional, Callable
from . import ast_nodes
# Manejador opcional para redirigir las peticiones de input en la interfaz GUI
GUI_INPUT_HANDLER: Optional[Callable[[str], str]] = None
def register_input_handler(handler: Optional[Callable[[str], str]]):
    """Registra un manejador personalizado para la función built-in input"""
    global GUI_INPUT_HANDLER
    GUI_INPUT_HANDLER = handler
class ReturnException(Exception):
    """Excepcion para manejar el retorno de funciones (answer)"""
    def __init__(self, value):
        self.value = value
class LoopBreak(Exception):
    """Controla 'halt' dentro de ciclos"""
    pass
class LoopContinue(Exception):
    """Controla 'skip' dentro de ciclos"""
    pass
class HoopException(Exception):
    """Excepcion generada por throw/rescue"""
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
        self.constants = set()
    def define_variable(self, name: str, value: Any, is_constant: bool = False):
        """Define una variable en el scope actual"""
        self.variables[name] = value
        if is_constant:
            self.constants.add(name)
        elif name in self.constants:
            self.constants.remove(name)
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
            if name in self.constants:
                raise HoopRuntimeError(f"No se puede reasignar la constante '{name}'")
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
        self.loop_depth = 0
    def interpret(self, ast: ast_nodes.ProgramaNode):
        """Ejecuta el programa completo"""
        try:
            self.visit(ast)
            return True, None
        except HoopRuntimeError as e:
            return False, str(e)
        except HoopException as e:
            valor = self._convert_to_string(e.value)
            return False, f"Excepción no capturada: {valor}"
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
    def visit_ConstanteNode(self, node: ast_nodes.ConstanteNode):
        """Ejecuta declaracion de constante: fixed x set valor;"""
        valor = self.visit(node.valor)
        self.current_context.define_variable(node.nombre, valor, is_constant=True)
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
    def visit_SelectStatementNode(self, node: ast_nodes.SelectStatementNode):
        """Ejecuta select/case"""
        valor = self.visit(node.expresion)
        ejecutado = False
        for case in node.casos:
            case_valor = self.visit(case.valor)
            if valor == case_valor:
                for stmt in case.cuerpo:
                    self.visit(stmt)
                ejecutado = True
                break
        if not ejecutado and node.default:
            for stmt in node.default:
                self.visit(stmt)
    def visit_TryStatementNode(self, node: ast_nodes.TryStatementNode):
        """Ejecuta attempt/rescue/ensure"""
        try:
            self._execute_block(node.bloque_try)
        except HoopException as exc:
            handled = False
            if node.bloque_rescue:
                handled = True
                initial = {}
                if node.rescue_identificador:
                    initial[node.rescue_identificador] = exc.value
                self._execute_block_in_child_context(node.bloque_rescue, initial)
            if not handled:
                raise
        finally:
            if node.bloque_ensure:
                self._execute_block_in_child_context(node.bloque_ensure)
    def visit_ThrowNode(self, node: ast_nodes.ThrowNode):
        """Lanza una excepcion propia"""
        valor = self.visit(node.expresion)
        raise HoopException(valor)
    def visit_BreakNode(self, node: ast_nodes.BreakNode):
        if self.loop_depth <= 0:
            raise HoopRuntimeError("'halt' solo puede usarse dentro de ciclos")
        raise LoopBreak()
    def visit_ContinueNode(self, node: ast_nodes.ContinueNode):
        if self.loop_depth <= 0:
            raise HoopRuntimeError("'skip' solo puede usarse dentro de ciclos")
        raise LoopContinue()
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
        """Ejecuta cycle con limites opcionales"""
        inicio, fin = self._resolve_cycle_bounds(node)
        step = 1 if inicio <= fin else -1
        stop = fin + 1 if step > 0 else fin - 1
        loop_context = ExecutionContext(self.current_context)
        prev_context = self.current_context
        self.current_context = loop_context
        self.loop_depth += 1
        try:
            try:
                for i in range(inicio, stop, step):
                    self.current_context.define_variable(node.variable, i)
                    try:
                        for stmt in node.cuerpo:
                            self.visit(stmt)
                    except LoopContinue:
                        continue
            except LoopBreak:
                pass
        finally:
            self.loop_depth -= 1
            self.current_context = prev_context
    def visit_RepeatStatementNode(self, node: ast_nodes.RepeatStatementNode):
        """Ejecuta repeat (while)"""
        loop_context = ExecutionContext(self.current_context)
        prev_context = self.current_context
        self.current_context = loop_context
        self.loop_depth += 1
        try:
            try:
                while self._is_truthy(self.visit(node.condicion)):
                    try:
                        for stmt in node.cuerpo:
                            self.visit(stmt)
                    except LoopContinue:
                        continue
            except LoopBreak:
                pass
        finally:
            self.loop_depth -= 1
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
                raise HoopRuntimeError("'self' solo puede usarse dentro de metodos")
            return self.current_instance
        # Manejar constantes booleanas
        if node.nombre == 'true':
            return True
        if node.nombre == 'false':
            return False
        # Variable normal
        return self.current_context.get_variable(node.nombre)
    def visit_OperacionNode(self, node: ast_nodes.OperacionNode):
        """Ejecuta operaciones aritmeticas, logicas y de comparacion"""
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
        elif op in ('greatereq', 'greaterequals', '>='):
            return izq >= der
        elif op in ('lesseq', 'lessequals', '<='):
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
        """Ejecuta operacion unaria (not)"""
        valor = self.visit(node.expresion)
        if node.operador == 'not' or node.operador == '!':
            return not self._is_truthy(valor)
        elif node.operador == '-':
            return -valor
        else:
            raise HoopRuntimeError(f"Operador unario desconocido: {node.operador}")
    def visit_LlamadaFuncionNode(self, node: ast_nodes.LlamadaFuncionNode):
        """Ejecuta llamada a funcion"""
        nombre = node.nombre
        # Manejar forge especial: forge<NombreClase>
        if nombre.startswith("forge<") and nombre.endswith(">"):
            nombre_clase = nombre[6:-1]  # Extraer nombre entre < >
            return self._execute_forge(nombre_clase, node.argumentos)
        # Manejar llamada a metodo: objeto.metodo
        if "." in nombre:
            partes = nombre.split(".", 1)
            objeto_nombre = partes[0]
            metodo_nombre = partes[1]
            objeto = self.current_context.get_variable(objeto_nombre)
            return self._execute_method(objeto, metodo_nombre, node.argumentos)
        # Funciones built-in
        if nombre in BUILTIN_FUNCTIONS:
            return self._call_builtin(nombre, node.argumentos)
        # Funcion definida por usuario
        func_node = self.current_context.get_function(nombre)
        # Evaluar argumentos
        args = [self.visit(arg) for arg in node.argumentos]
        # Verificar numero de argumentos
        if len(args) != len(func_node.parametros):
            raise HoopRuntimeError(
                f"Funcion '{nombre}' espera {len(func_node.parametros)} argumentos, "
                f"pero se pasaron {len(args)}"
            )
        # Crear nuevo contexto para la funcion
        func_context = ExecutionContext(self.global_context)
        prev_context = self.current_context
        self.current_context = func_context
        # Definir paraametros
        for param, arg in zip(func_node.parametros, args):
            if isinstance(param, ast_nodes.ParametroNode):
                param_name = param.nombre
            elif isinstance(param, dict):
                param_name = param['nombre']
            else:
                param_name = param
            self.current_context.define_variable(param_name, arg)
        try:
            # Ejecutar cuerpo de la funcionoon
            for stmt in func_node.cuerpo:
                self.visit(stmt)
            return None  # si no hay return
        except ReturnException as e:
            return e.value
        finally:
            self.current_context = prev_context
    def _execute_forge(self, nombre_clase: str, argumentos: List):
        """Ejecuta construcción de objeto: forge Clase()"""
        class_node = self.current_context.get_class(nombre_clase)
        instance = HoopObject(nombre_clase)
        self._initialize_instance_attributes(instance, class_node)
        args = [self.visit(arg) for arg in argumentos]
        constructor = self._find_constructor(class_node)
        if constructor:
            if len(args) != len(constructor.parametros):
                raise HoopRuntimeError(
                    f"Constructor de '{nombre_clase}' espera {len(constructor.parametros)} "
                    f"argumentos, pero se pasaron {len(args)}"
                )
            self._run_method_node(constructor, instance, args)
        elif args:
            raise HoopRuntimeError(f"Clase '{nombre_clase}' no acepta argumentos")
        return instance
    def _execute_method(self, objeto, metodo_nombre: str, argumentos: List):
        """Ejecuta llamada a método: objeto.metodo()"""
        if not isinstance(objeto, HoopObject):
            raise HoopRuntimeError(f"Solo objetos pueden tener métodos")
        class_node = self.current_context.get_class(objeto.class_name)
        method_node = None
        for stmt in class_node.cuerpo:
            if isinstance(stmt, ast_nodes.FuncionNode) and stmt.nombre == metodo_nombre:
                method_node = stmt
                break
        if not method_node:
            raise HoopRuntimeError(f"Método '{metodo_nombre}' no existe en {objeto.class_name}")
        args = [self.visit(arg) for arg in argumentos]
        if len(args) != len(method_node.parametros):
            raise HoopRuntimeError(
                f"Método '{metodo_nombre}' espera {len(method_node.parametros)} argumentos, "
                f"pero se pasaron {len(args)}"
            )
        return self._run_method_node(method_node, objeto, args)
    def _run_method_node(self, method_node: ast_nodes.FuncionNode, instance: HoopObject, arg_values: List):
        """Ejecuta un nodo de método con un objeto dado"""
        method_context = ExecutionContext(self.global_context)
        prev_context = self.current_context
        prev_instance = self.current_instance
        self.current_context = method_context
        self.current_instance = instance
        for param, arg in zip(method_node.parametros, arg_values):
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
    def _initialize_instance_attributes(self, instance: HoopObject, class_node: ast_nodes.ClaseNode):
        """Inicializa atributos definidos en la clase"""
        prev_instance = self.current_instance
        try:
            self.current_instance = instance
            for stmt in class_node.cuerpo:
                if isinstance(stmt, (ast_nodes.DeclaracionNode, ast_nodes.ConstanteNode)):
                    valor = self._evaluate_attribute_default(stmt.valor)
                    instance.set_attribute(stmt.nombre, valor)
        finally:
            self.current_instance = prev_instance
    def _evaluate_attribute_default(self, valor_node):
        if isinstance(valor_node, ast_nodes.LiteralNode) and valor_node.tipo == "TYPE_DECLARATION":
            return None
        return self.visit(valor_node)
    def _find_constructor(self, class_node: ast_nodes.ClaseNode):
        for stmt in class_node.cuerpo:
            if isinstance(stmt, ast_nodes.FuncionNode) and stmt.nombre in ("inicializar", class_node.nombre):
                return stmt
        return None
    def visit_ForgeNode(self, node: ast_nodes.ForgeNode):
        """Ejecuta forge Clase()"""
        return self._execute_forge(node.clase, node.argumentos)
    def visit_AccesoMiembroNode(self, node: ast_nodes.AccesoMiembroNode):
        """Ejecuta acceso a atributo: objeto.atributo"""
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
        # Caso especial: self.atributo
        if isinstance(node.objeto, ast_nodes.IdentificadorNode) and node.objeto.nombre == 'self':
            if self.current_instance is None:
                raise HoopRuntimeError("'self' solo puede usarse dentro de metodos")
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
        """Ejecuta llamada a metodo: objeto.metodo()"""
        objeto = self.visit(node.objeto)
        if not isinstance(objeto, HoopObject):
            raise HoopRuntimeError(f"Solo objetos pueden tener metodos")
        # Obtener clase del objeto
        class_node = self.current_context.get_class(objeto.class_name)
        method_node = None
        for stmt in class_node.cuerpo:
            if isinstance(stmt, ast_nodes.FuncionNode) and stmt.nombre == node.metodo:
                method_node = stmt
                break
        if not method_node:
            raise HoopRuntimeError(f"Metodo '{node.metodo}' no existe en {objeto.class_name}")
        # Evaluar argumentos
        args = [self.visit(arg) for arg in node.argumentos]
        # Verificar numero de argumentos
        if len(args) != len(method_node.parametros):
            raise HoopRuntimeError(
                f"Metodo '{node.metodo}' espera {len(method_node.parametros)} argumentos, "
                f"pero se pasaron {len(args)}"
            )
        method_context = ExecutionContext(self.global_context)
        prev_context = self.current_context
        prev_instance = self.current_instance
        self.current_context = method_context
        self.current_instance = objeto
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
            if args:
                output = self._convert_to_string(args[0])
                self.output.append(output)
                print(output)
            return None
        if name == 'output':
            if args:
                output = self._convert_to_string(args[0])
                self.output.append(output)
                print(output)
            return None
        if name == 'length':
            if len(args) != 1:
                raise HoopRuntimeError("length() requiere 1 argumento")
            return len(args[0])
        if name == 'size':
            if len(args) != 1:
                raise HoopRuntimeError("size() requiere 1 argumento")
            return len(args[0])
        if name == 'type':
            if len(args) != 1:
                raise HoopRuntimeError("type() requiere 1 argumento")
            return type(args[0]).__name__
        if name == 'input':
            prompt = args[0] if args else ""
            prompt_text = self._convert_to_string(prompt)
            if GUI_INPUT_HANDLER:
                try:
                    value = GUI_INPUT_HANDLER(prompt_text)
                except Exception as exc:
                    raise HoopRuntimeError(f"Error durante input: {exc}")
                return value if value is not None else ""
            return input(prompt_text)
        if name == 'random':
            if len(args) == 0:
                return random.random()
            if len(args) == 2:
                return random.randint(int(args[0]), int(args[1]))
            raise HoopRuntimeError("random() requiere 0 o 2 argumentos")
        if name == 'abs':
            if len(args) != 1:
                raise HoopRuntimeError("abs() requiere 1 argumento")
            return abs(args[0])
        if name == 'sqrt':
            if len(args) != 1:
                raise HoopRuntimeError("sqrt() requiere 1 argumento")
            return math.sqrt(args[0])
        if name == 'pow':
            if len(args) != 2:
                raise HoopRuntimeError("pow() requiere 2 argumentos")
            return pow(args[0], args[1])
        if name == 'max':
            if not args:
                raise HoopRuntimeError("max() requiere al menos 1 argumento")
            if len(args) == 1 and hasattr(args[0], '__iter__'):
                return max(args[0])
            return max(args)
        if name == 'min':
            if not args:
                raise HoopRuntimeError("min() requiere al menos 1 argumento")
            if len(args) == 1 and hasattr(args[0], '__iter__'):
                return min(args[0])
            return min(args)
        if name == 'read':
            if len(args) != 1:
                raise HoopRuntimeError("read() requiere 1 argumento")
            path_value = str(args[0])
            try:
                with open(path_value, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                raise HoopRuntimeError(f"Archivo no encontrado: {path_value}")
        if name == 'write':
            if len(args) != 2:
                raise HoopRuntimeError("write() requiere 2 argumentos")
            path_value = str(args[0])
            data = self._convert_to_string(args[1])
            with open(path_value, 'w', encoding='utf-8') as f:
                f.write(data)
            return True
        if name == 'open':
            if len(args) != 1:
                raise HoopRuntimeError("open() requiere 1 argumento")
            path_value = str(args[0])
            try:
                with open(path_value, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                raise HoopRuntimeError(f"Archivo no encontrado: {path_value}")
        if name == 'close':
            return True
        if name == 'convert':
            if len(args) != 2:
                raise HoopRuntimeError("convert() requiere 2 argumentos")
            valor, tipo = args
            if tipo == 'whole':
                return int(valor)
            if tipo == 'fract':
                return float(valor)
            if tipo == 'text':
                return str(valor)
            if tipo == 'logic':
                return bool(valor)
            raise HoopRuntimeError(f"Tipo desconocido: {tipo}")
        raise HoopRuntimeError(f"Funcion built-in desconocida: {name}")
    def _execute_block(self, statements):
        if statements is None:
            return
        if isinstance(statements, list):
            for stmt in statements:
                self.visit(stmt)
        else:
            self.visit(statements)
    def _execute_block_in_child_context(self, statements, initial_bindings=None):
        if not statements:
            return
        child = ExecutionContext(self.current_context)
        prev_context = self.current_context
        self.current_context = child
        try:
            if initial_bindings:
                for name, value in initial_bindings.items():
                    self.current_context.define_variable(name, value)
            self._execute_block(statements)
        finally:
            self.current_context = prev_context
    def _resolve_cycle_bounds(self, node: ast_nodes.CycleStatementNode):
        if node.inicio is None and node.fin is None:
            return 0, 0
        if node.inicio is None and node.fin is not None:
            fin = self._coerce_number(self.visit(node.fin), "cycle to")
            return 0, fin
        if node.inicio is not None and node.fin is None:
            inicio = self._coerce_number(self.visit(node.inicio), "cycle from")
            return inicio, inicio
        inicio = self._coerce_number(self.visit(node.inicio), "cycle from")
        fin = self._coerce_number(self.visit(node.fin), "cycle to")
        return inicio, fin
    def _coerce_number(self, value, label):
        if isinstance(value, bool):
            raise HoopRuntimeError(f"{label} debe ser numérico")
        if isinstance(value, (int, float)):
            return int(value)
        raise HoopRuntimeError(f"{label} debe ser numérico")
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
BUILTIN_FUNCTIONS = {
    'display', 'output', 'length', 'size', 'type', 'convert',
    'input', 'random', 'abs', 'sqrt', 'pow', 'max', 'min',
    'read', 'write', 'open', 'close'
}
def interpret_hoop(ast: ast_nodes.ProgramaNode) -> tuple[bool, Optional[str], List[str]]:
    interpreter = HoopInterpreter()
    success, error = interpreter.interpret(ast)
    output = interpreter.get_output()
    return success, error, output

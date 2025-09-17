# Parser estilo YACC para HOOP

from typing import List, Any, Optional
from .core.lexer import TokenType, RESERVADAS, TIPOS, OPERADORES_PALABRAS, PALABRAS_PREGONADAS


class ParseError:
    def __init__(self, mensaje: str, linea: Optional[int] = None, columna: Optional[int] = None):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna

    def __str__(self):
        if self.linea is not None and self.columna is not None:
            return f"Error sintáctico: {self.mensaje} en {self.linea}:{self.columna}"
        return f"Error sintáctico: {self.mensaje}"


class Parser:
    """
    Parser estilo YACC para un subconjunto de HOOP.

    Gramática (resumida):
      programa     -> (declaracion | clase)* EOF
      declaracion  -> 'data' IDENTIFIER 'set' expresion ';'
      clase        -> 'mold' IDENTIFIER '{' clase_cuerpo '}'
      clase_cuerpo -> (atributo | metodo)*
      atributo     -> TYPE IDENTIFIER ';'
      metodo       -> 'action' IDENTIFIER '(' ')' '{' statements '}'   # métodos con cuerpo

    El parser recibe una lista de tokens producida por AnalizadorLexico. No usa librerías externas.
    """

    def __init__(self, tokens: List[Any]):
        self.tokens = tokens
        self.pos = 0
        self.errors: List[ParseError] = []
        self.ast: List[Any] = []

    # Utilidades
    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def advance(self):
        tok = self.current()
        if tok is not None:
            self.pos += 1
        return tok

    def add_error(self, mensaje: str, token=None):
        if token is not None:
            linea = getattr(token, 'linea', None)
            columna = getattr(token, 'columna', None)
            self.errors.append(ParseError(mensaje, linea, columna))
        else:
            self.errors.append(ParseError(mensaje))

    def match(self, token_type: TokenType, token_value: Optional[str] = None):
        """
        Consume el token actual si coincide con token_type (y opcionalmente token_value).
        Retorna el token consumido o None y registra error si no coincide.
        """
        tok = self.current()
        if tok is None:
            self.add_error(f"Se esperaba {token_type.name} pero se encontró fin de archivo")
            return None

        if tok.tipo == token_type and (token_value is None or tok.valor == token_value):
            self.advance()
            return tok
        else:
            esperado = token_value if token_value is not None else token_type.name
            encontrado = f"{tok.tipo.name}('{tok.valor}')"
            self.add_error(f"Se esperaba {esperado} pero se encontró {encontrado}", tok)
            # Intento de recuperación simple: avanzar uno para evitar bucle infinito
            self.advance()
            return None

    # Reglas
    def parse(self):
        self.ast = self.programa()
        return self.ast

    def programa(self):
        nodes = []
        while True:
            tok = self.current()
            if tok is None:
                break
            if tok.tipo == TokenType.EOF:
                break

            # Declaración global: data ...
            if tok.tipo == TokenType.KEYWORD and tok.valor == 'data':
                node = self.parse_data_declaration_unified()
                if node:
                    nodes.append(node)
                continue

            # Clase: mold ...
            if tok.tipo == TokenType.KEYWORD and tok.valor == 'mold':
                node = self.clase()
                if node:
                    nodes.append(node)
                continue
            
            # Función global: action ...
            if tok.tipo == TokenType.KEYWORD and tok.valor == 'action':
                node = self.funcion_global()
                if node:
                    nodes.append(node)
                continue

            # Statements globales (when, cycle, display, etc.)
            if tok.tipo == TokenType.KEYWORD and tok.valor in ('when', 'cycle', 'display'):
                node = self.parse_statement(max_depth=2, current_depth=1)
                if node:
                    nodes.append(node)
                continue

            # Si encontramos un NEWLINE o COMMENT o WHITESPACE, lo saltamos
            if tok.tipo in (TokenType.NEWLINE, TokenType.COMMENT, TokenType.WHITESPACE):
                self.advance()
                continue

            # Expresiones simples a nivel global
            if tok.tipo in (TokenType.IDENTIFIER, TokenType.STRING, TokenType.NUMBER, TokenType.BOOLEAN):
                node = self.parse_simple_statement()
                if node:
                    nodes.append(node)
                continue

            # Token inesperado en nivel superior
            self.add_error(f"Elemento inesperado en nivel superior: {tok.tipo.name}('{tok.valor}')", tok)
            self.advance()

        # Consumir EOF final si existe
        if self.current() and self.current().tipo == TokenType.EOF:
            self.advance()

        return nodes

    def declaracion(self):
        # 'data' IDENTIFIER 'set' expresion ';'
        inicio = self.current()
        self.match(TokenType.KEYWORD, 'data')
        id_tok = self.match(TokenType.IDENTIFIER)
        # 'set' puede ser WORD_OPERATOR
        set_tok = None
        if self.current() and self.current().tipo == TokenType.WORD_OPERATOR and self.current().valor == 'set':
            set_tok = self.match(TokenType.WORD_OPERATOR, 'set')
        else:
            # intentar aceptar como KEYWORD por si el lexer clasificó distinto
            set_tok = self.match(TokenType.KEYWORD, 'set')

        # expresión: puede ser literal simple o expresión compleja (incluyendo llamadas a función)
        expr_value = self.parse_expression()

        # punto y coma
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == ';':
            self.match(TokenType.DELIMITER, ';')
        else:
            self.add_error("Falta ';' al final de la declaración", self.current())
            # intentar sincronizar
            while self.current() and not (self.current().tipo == TokenType.DELIMITER and self.current().valor == ';') and self.current().tipo != TokenType.EOF:
                self.advance()
            if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == ';':
                self.advance()

        return {
            'tipo': 'declaracion',
            'identificador': getattr(id_tok, 'valor', None) if id_tok else None,
            'valor': expr_value,
            'inicio': getattr(inicio, 'valor', None) if inicio else None
        }

    def parse_expression(self):
        """Parsea una expresión que puede ser un literal, identificador, operación o llamada a función"""
        expr_tokens = []
        paren_depth = 0
        
       
        while self.current() and self.current().tipo != TokenType.EOF:
            tok = self.current()
            
            # Si encontramos ';' y no estamos dentro de paréntesis, parar
            if tok.tipo == TokenType.DELIMITER and tok.valor == ';' and paren_depth == 0:
                break
                
            # Contar paréntesis para manejar llamadas a función
            if tok.tipo == TokenType.DELIMITER and tok.valor == '(':
                paren_depth += 1
            elif tok.tipo == TokenType.DELIMITER and tok.valor == ')':
                paren_depth -= 1
                
            # Si encontramos delimitadores de bloque y no estamos en paréntesis, parar
            if tok.tipo == TokenType.DELIMITER and tok.valor in ('{', '}') and paren_depth == 0:
                break
                
            expr_tokens.append(tok)
            self.advance()
        
        # Construir el valor de la expresión
        if not expr_tokens:
            self.add_error("Se esperaba una expresión después de 'set'", self.current())
            return None
            
        # Si es un solo token de tipo literal, devolver su valor
        if len(expr_tokens) == 1:
            token = expr_tokens[0]
            if token.tipo in (TokenType.STRING, TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.BOOLEAN):
                return token.valor
                
        # Si es una expresión más compleja, devolver representación como string
        return ' '.join(t.valor for t in expr_tokens)

    def clase(self):
        # 'mold' IDENTIFIER '{' clase_cuerpo '}'
        inicio = self.current()
        self.match(TokenType.KEYWORD, 'mold')
        id_tok = self.match(TokenType.IDENTIFIER)
        # abrir llave
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '{':
            self.match(TokenType.DELIMITER, '{')
        else:
            self.add_error("Se esperaba '{' para iniciar el cuerpo de la clase", self.current())

        atributos = []
        metodos = []

        # cuerpo de la clase: cero o más atributos/metodos
        while self.current() and not (self.current().tipo == TokenType.DELIMITER and self.current().valor == '}') and self.current().tipo != TokenType.EOF:
            tok = self.current()
            if tok.tipo == TokenType.TYPE:
                attr = self.atributo()
                if attr:
                    atributos.append(attr)
                continue
            if tok.tipo == TokenType.KEYWORD and tok.valor == 'action':
                m = self.metodo()
                if m:
                    metodos.append(m)
                continue
            

            if tok.tipo == TokenType.KEYWORD and tok.valor == 'construct':
                self.add_error("'construct' no es una palabra válida en HOOP. Use 'action' para definir métodos.", tok)
                # Saltar hasta el siguiente ';' o '}'
                while self.current() and not (self.current().tipo == TokenType.DELIMITER and self.current().valor in (';', '}')) and self.current().tipo != TokenType.EOF:
                    self.advance()
                if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == ';':
                    self.advance()
                continue

            # saltar comentarios y newlines
            if tok.tipo in (TokenType.NEWLINE, TokenType.COMMENT, TokenType.WHITESPACE):
                self.advance()
                continue

            # elemento inesperado en cuerpo de clase
            self.add_error(f"Elemento inesperado en cuerpo de clase: {tok.tipo.name}('{tok.valor}')", tok)
            self.advance()

        # cerrar llave
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '}':
            self.match(TokenType.DELIMITER, '}')
        else:
            self.add_error("Falta '}' al final de la clase", self.current())

        return {
            'tipo': 'clase',
            'nombre': getattr(id_tok, 'valor', None) if id_tok else None,
            'atributos': atributos,
            'metodos': metodos,
            'inicio': getattr(inicio, 'valor', None) if inicio else None
        }

    def atributo(self):
        # TYPE IDENTIFIER ';'
        tipo_tok = self.match(TokenType.TYPE)
        id_tok = self.match(TokenType.IDENTIFIER)
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == ';':
            self.match(TokenType.DELIMITER, ';')
        else:
            self.add_error("Falta ';' al final de la declaración de atributo", self.current())
           
            while self.current() and not (self.current().tipo == TokenType.DELIMITER and self.current().valor == ';') and self.current().tipo != TokenType.EOF:
                self.advance()
            if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == ';':
                self.advance()

        return {
            'tipo': 'atributo',
            'data_type': getattr(tipo_tok, 'valor', None) if tipo_tok else None,
            'nombre': getattr(id_tok, 'valor', None) if id_tok else None
        }

   
    def parse_statements(self, max_depth=2, current_depth=1):
        stmts = []
        while self.current() and not (self.current().tipo == TokenType.DELIMITER and self.current().valor == '}') and self.current().tipo != TokenType.EOF:
        
            if self.current().tipo == TokenType.DELIMITER and self.current().valor == '{':
                self.add_error("Bloque inesperado '{' — se descartará hasta el correspondiente '}'", self.current())
           
                depth = 0
                while self.current() and not (self.current().tipo == TokenType.EOF):
                    if self.current().tipo == TokenType.DELIMITER and self.current().valor == '{':
                        depth += 1
                    elif self.current().tipo == TokenType.DELIMITER and self.current().valor == '}':
                        depth -= 1
                        # avanzar para salir cuando depth < 0
                        self.advance()
                        if depth <= 0:
                            break
                        continue
                    self.advance()
                continue

            # saltar comentarios/newlines
            if self.current().tipo in (TokenType.NEWLINE, TokenType.COMMENT, TokenType.WHITESPACE):
                self.advance()
                continue
            stmt = self.parse_statement(max_depth, current_depth)
            if stmt:
                stmts.append(stmt)
            else:
                # evitar bucle infinito: si parse_statement no avanzó, romper
                self.advance()
        return stmts

    def parse_statement(self, max_depth, current_depth):
        tok = self.current()
        if tok is None:
            return None

        
        if tok.tipo == TokenType.KEYWORD and tok.valor == 'data':
            return self.parse_data_declaration_unified()

        
        if tok.tipo == TokenType.KEYWORD and tok.valor == 'when':
            return self.parse_if_statement(max_depth, current_depth)

       
        if tok.tipo == TokenType.KEYWORD and tok.valor == 'cycle':
            return self.parse_cycle_statement(max_depth, current_depth)

       
        if tok.tipo == TokenType.DELIMITER and tok.valor == '{':
            self.add_error("Encontrado '{' inesperado en la posición de una sentencia; se descartará el bloque.", tok)
            
            depth = 0
            while self.current() and not (self.current().tipo == TokenType.EOF):
                if self.current().tipo == TokenType.DELIMITER and self.current().valor == '{':
                    depth += 1
                elif self.current().tipo == TokenType.DELIMITER and self.current().valor == '}':
                    depth -= 1
                    self.advance()
                    if depth <= 0:
                        break
                    continue
                self.advance()
            return None

        # Simple expression/statement: consumir hasta ';' or '{' or '}'
        expr_tokens = []
        while self.current() and not (self.current().tipo == TokenType.DELIMITER and self.current().valor in (';', '{', '}')) and self.current().tipo != TokenType.EOF:
            expr_tokens.append(self.current())
            self.advance()
        # consumir ';' si existe
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == ';':
            self.advance()
            # sugerir si algún token IDENTIFIER en la expresión parece un typo de keyword
            for tkn in expr_tokens:
                if tkn.tipo == TokenType.IDENTIFIER:
                    suggestion = self.suggest_similar_keyword(tkn.valor)
                    if suggestion and suggestion != tkn.valor:
                        self.add_error(f"Posible error tipográfico: '{tkn.valor}' — quiso '{suggestion}'?", tkn)
            return {'tipo': 'expr_stmt', 'tokens': [t.valor for t in expr_tokens]}
        else:
            # si encontramos '{', no consumirlo aquí (el llamado debe manejar el bloque)
            if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '{':
                # sugerir para identificadores en la expresión antes del bloque
                for tkn in expr_tokens:
                    if tkn.tipo == TokenType.IDENTIFIER:
                        suggestion = self.suggest_similar_keyword(tkn.valor)
                        if suggestion and suggestion != tkn.valor:
                            self.add_error(f"Posible error tipográfico: '{tkn.valor}' — quiso '{suggestion}'?", tkn)
                # devolver la expr sin consumir '{' para que el llamador lo procese o para que el bloque sea manejado
                return {'tipo': 'expr_stmt', 'tokens': [t.valor for t in expr_tokens]}
            # si no hay ';' y se encontró '}', puede ser fin del bloque; si no, marcar error
            if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '}':
                if expr_tokens:
                    # sugerir para identificadores
                    for tkn in expr_tokens:
                        if tkn.tipo == TokenType.IDENTIFIER:
                            suggestion = self.suggest_similar_keyword(tkn.valor)
                            if suggestion and suggestion != tkn.valor:
                                self.add_error(f"Posible error tipográfico: '{tkn.valor}' — quiso '{suggestion}'?", tkn)
                    return {'tipo': 'expr_stmt', 'tokens': [t.valor for t in expr_tokens]}
                return None
            self.add_error("Se esperaba ';' al final de la sentencia", self.current())
            # sugerir para identificadores
            for tkn in expr_tokens:
                if tkn.tipo == TokenType.IDENTIFIER:
                    suggestion = self.suggest_similar_keyword(tkn.valor)
                    if suggestion and suggestion != tkn.valor:
                        self.add_error(f"Posible error tipográfico: '{tkn.valor}' — quiso '{suggestion}'?", tkn)
            return {'tipo': 'expr_stmt', 'tokens': [t.valor for t in expr_tokens]}

    def parse_if_statement(self, max_depth, current_depth):
        # VERIFICAR PROFUNDIDAD ANTES DE PROCESAR
        if current_depth > max_depth:
            inicio = self.current()
            self.add_error(f"Profundidad máxima de anidamiento alcanzada ({max_depth} niveles). No se permiten más estructuras 'when' anidadas.", inicio)
            # Consumir toda la estructura 'when' sin procesarla
            self.consume_when_structure()
            return None

        inicio = self.current()
        self.match(TokenType.KEYWORD, 'when')

        # condición: tomar tokens hasta '{'
        cond_tokens = []
        while self.current() and not (self.current().tipo == TokenType.DELIMITER and self.current().valor == '{') and self.current().tipo != TokenType.EOF:
            # prevenir que condition is empty
            cond_tokens.append(self.current())
            self.advance()

        if not (self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '{'):
            self.add_error("Se esperaba '{' después de la condición de 'when'", self.current())
            return {'tipo': 'if', 'cond': [t.valor for t in cond_tokens], 'body': [], 'otherwise': None}

        # abrir bloque
        self.match(TokenType.DELIMITER, '{')

        # procesar cuerpo
        body = self.parse_statements(max_depth, current_depth + 1)

        # cerrar bloque
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '}':
            self.match(TokenType.DELIMITER, '}')
        else:
            self.add_error("Falta '}' al final del bloque de 'when'", self.current())

        # optional 'otherwise' branch
        otherwise = None
        if self.current() and self.current().tipo == TokenType.KEYWORD and self.current().valor == 'otherwise':
            self.match(TokenType.KEYWORD, 'otherwise')
            if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '{':
                self.match(TokenType.DELIMITER, '{')
                otherwise = self.parse_statements(max_depth, current_depth + 1)
                if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '}':
                    self.match(TokenType.DELIMITER, '}')
                else:
                    self.add_error("Falta '}' al final del bloque 'otherwise'", self.current())
            else:
                self.add_error("Se esperaba '{' después de 'otherwise'", self.current())

        return {
            'tipo': 'if',
            'cond': [t.valor for t in cond_tokens],
            'body': body,
            'otherwise': otherwise,
            'inicio': getattr(inicio, 'valor', None) if inicio else None
        }

    def consume_when_structure(self):
        """Consume una estructura 'when' completa sin procesarla (para manejo de profundidad máxima)"""
        # Ya estamos en 'when', avanzar
        self.advance()
        
        # Consumir condición hasta '{'
        while self.current() and not (self.current().tipo == TokenType.DELIMITER and self.current().valor == '{') and self.current().tipo != TokenType.EOF:
            self.advance()
        
        # Consumir bloque principal
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '{':
            self.consume_block()
        
        # Consumir 'otherwise' si existe
        if self.current() and self.current().tipo == TokenType.KEYWORD and self.current().valor == 'otherwise':
            self.advance()
            if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '{':
                self.consume_block()

    def consume_block(self):
        """Consume un bloque completo {...} balanceando llaves"""
        if not (self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '{'):
            return
        
        depth = 0
        while self.current() and self.current().tipo != TokenType.EOF:
            if self.current().tipo == TokenType.DELIMITER and self.current().valor == '{':
                depth += 1
            elif self.current().tipo == TokenType.DELIMITER and self.current().valor == '}':
                depth -= 1
                self.advance()
                if depth <= 0:
                    break
                continue
            self.advance()

    def parse_cycle_statement(self, max_depth, current_depth):
        inicio = self.current()
        self.match(TokenType.KEYWORD, 'cycle')

        # esperar IDENTIFIER (variable de control)
        var_tok = None
        if self.current() and self.current().tipo == TokenType.IDENTIFIER:
            var_tok = self.match(TokenType.IDENTIFIER)
        else:
            self.add_error("Se esperaba identificador en 'cycle'", self.current())

        # opcionalmente 'from' expr 'to' expr
        from_tok = None
        to_tok = None
        start_expr = None
        end_expr = None
        if self.current() and self.current().tipo == TokenType.KEYWORD and self.current().valor == 'from':
            from_tok = self.match(TokenType.KEYWORD, 'from')
            if self.current() and self.current().tipo in (TokenType.NUMBER, TokenType.IDENTIFIER):
                start_expr = self.current().valor
                self.advance()
            else:
                self.add_error("Se esperaba expresión inicial después de 'from'", self.current())
        if self.current() and self.current().tipo == TokenType.KEYWORD and self.current().valor == 'to':
            to_tok = self.match(TokenType.KEYWORD, 'to')
            if self.current() and self.current().tipo in (TokenType.NUMBER, TokenType.IDENTIFIER):
                end_expr = self.current().valor
                self.advance()
            else:
                self.add_error("Se esperaba expresión final después de 'to'", self.current())

       
        body = []
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '{':
            self.match(TokenType.DELIMITER, '{')
            body = self.parse_statements(max_depth, current_depth)
            if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '}':
                self.match(TokenType.DELIMITER, '}')
            else:
                self.add_error("Falta '}' al final del bloque de 'cycle'", self.current())
        else:
            self.add_error("Se esperaba '{' para iniciar el bloque de 'cycle'", self.current())

        return {
            'tipo': 'cycle',
            'var': getattr(var_tok, 'valor', None) if var_tok else None,
            'from': start_expr,
            'to': end_expr,
            'body': body,
            'inicio': getattr(inicio, 'valor', None) if inicio else None
        }

    def metodo(self):
        # 'action' IDENTIFIER '(' ')' '{' '}'  (metodo con cuerpo hasta profundidad 2)
        inicio = self.current()
        self.match(TokenType.KEYWORD, 'action')
        id_tok = self.match(TokenType.IDENTIFIER)
        # paréntesis vacíos (aceptamos también parámetros en el futuro)
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '(':
            self.match(TokenType.DELIMITER, '(')
            # ignorar cualquier cosa hasta ')' por simplicidad ahora
            while self.current() and not (self.current().tipo == TokenType.DELIMITER and self.current().valor == ')') and self.current().tipo != TokenType.EOF:
                self.advance()
            if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == ')':
                self.match(TokenType.DELIMITER, ')')
            else:
                self.add_error("Falta ')' en la declaración del método", self.current())
        else:
            self.add_error("Falta '(' en la declaración del método", self.current())

        # cuerpo del método: parsear sentencias con if anidados hasta 2 niveles
        body = []
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '{':
            self.match(TokenType.DELIMITER, '{')
            body = self.parse_statements(max_depth=2, current_depth=1)
            if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '}':
                self.match(TokenType.DELIMITER, '}')
            else:
                self.add_error("Falta '}' en el cuerpo del método", self.current())
        else:
            self.add_error("Falta '{' que inicia el cuerpo del método", self.current())

        return {
            'tipo': 'metodo',
            'nombre': getattr(id_tok, 'valor', None) if id_tok else None,
            'body': body,
            'inicio': getattr(inicio, 'valor', None) if inicio else None
        }

    def funcion_global(self):
        """Parsea una función a nivel global"""
        inicio = self.current()
        self.match(TokenType.KEYWORD, 'action')
        id_tok = self.match(TokenType.IDENTIFIER)
        
        # paréntesis (pueden estar vacíos o con parámetros)
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '(':
            self.match(TokenType.DELIMITER, '(')
            # ignorar parámetros por ahora
            while self.current() and not (self.current().tipo == TokenType.DELIMITER and self.current().valor == ')') and self.current().tipo != TokenType.EOF:
                self.advance()
            if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == ')':
                self.match(TokenType.DELIMITER, ')')
            else:
                self.add_error("Falta ')' en la declaración de la función", self.current())
        else:
            self.add_error("Falta '(' en la declaración de la función", self.current())

        # cuerpo de la función
        body = []
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '{':
            self.match(TokenType.DELIMITER, '{')
            body = self.parse_statements(max_depth=2, current_depth=1)
            if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '}':
                self.match(TokenType.DELIMITER, '}')
            else:
                self.add_error("Falta '}' en el cuerpo de la función", self.current())
        else:
            self.add_error("Falta '{' que inicia el cuerpo de la función", self.current())

        return {
            'tipo': 'funcion_global',
            'nombre': getattr(id_tok, 'valor', None) if id_tok else None,
            'body': body,
            'inicio': getattr(inicio, 'valor', None) if inicio else None
        }

    def parse_simple_statement(self):
        """Parsea una statement simple a nivel global"""
        expr_tokens = []
        while self.current() and not (self.current().tipo == TokenType.DELIMITER and self.current().valor == ';') and self.current().tipo not in (TokenType.EOF, TokenType.NEWLINE):
            expr_tokens.append(self.current())
            self.advance()
        
        # consumir ';' si existe
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == ';':
            self.advance()
        
        if expr_tokens:
            return {'tipo': 'expr_stmt_global', 'tokens': [t.valor for t in expr_tokens]}
        return None

    def parse_data_declaration_unified(self):
        """Función unificada para declaraciones 'data' con validación consistente en todos los contextos"""
        inicio = self.current()
        self.match(TokenType.KEYWORD, 'data')
        
       
        id_tokens = []
        
        
        id_tok = self.current()
        if not id_tok or id_tok.tipo != TokenType.IDENTIFIER:
            if id_tok and id_tok.tipo == TokenType.KEYWORD and id_tok.valor == 'self':
                # Permitir 'self' como inicio de dot notation
                id_tokens.append(id_tok)
                self.advance()
            else:
                if id_tok:
                    self.add_error(f"Se esperaba IDENTIFIER después de 'data' pero se encontró {id_tok.tipo.name}('{id_tok.valor}')", id_tok)
                else:
                    self.add_error("Se esperaba IDENTIFIER después de 'data' pero se encontró fin de archivo")
                self.recover_to_semicolon()
                return None
        else:
            id_tokens.append(id_tok)
            self.advance()
        
        # Manejar dot notation (ej: self.numero, objeto.propiedad)
        while self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == '.':
            id_tokens.append(self.current())  # agregar el '.'
            self.advance()
            
            # Debe seguir otro identificador
            next_tok = self.current()
            if next_tok and next_tok.tipo == TokenType.IDENTIFIER:
                id_tokens.append(next_tok)
                self.advance()
            else:
                self.add_error("Se esperaba IDENTIFIER después de '.' en declaración", next_tok)
                self.recover_to_semicolon()
                return None
        
        # Construir el identificador completo
        identifier = ''.join(token.valor for token in id_tokens)
        
        # Validar 'set'
        set_tok = self.current()
        if not set_tok or not (set_tok.tipo == TokenType.WORD_OPERATOR and set_tok.valor == 'set'):
            if set_tok:
                self.add_error(f"Se esperaba 'set' después del identificador '{identifier}' pero se encontró {set_tok.tipo.name}('{set_tok.valor}')", set_tok)
            else:
                self.add_error(f"Se esperaba 'set' después del identificador '{identifier}' pero se encontró fin de archivo")
            self.recover_to_semicolon()
            return None
        
        self.advance()
        
        # Parsear expresión
        expr_value = self.parse_expression()
        if expr_value is None:
            self.add_error("Se esperaba una expresión después de 'set'", self.current())
            self.recover_to_semicolon()
            return None
        
        # Validar punto y coma
        if self.current() and self.current().tipo == TokenType.DELIMITER and self.current().valor == ';':
            self.match(TokenType.DELIMITER, ';')
        else:
            self.add_error("Falta ';' al final de la declaración", self.current())
            self.recover_to_semicolon()
        
        return {
            'tipo': 'declaracion',
            'identificador': identifier,
            'valor': expr_value,
            'contexto': 'unified'
        }

    def recover_to_semicolon(self):
        """Función de recuperación mejorada para declaraciones"""
        while self.current() and self.current().tipo != TokenType.EOF:
            if self.current().tipo == TokenType.DELIMITER and self.current().valor == ';':
                self.advance()  # Consumir el ';'
                break
            # Parar en delimitadores de bloque para evitar consumir demasiado
            if self.current().tipo == TokenType.DELIMITER and self.current().valor in ('{', '}'):
                break
            self.advance()

    def levenshtein(self, a: str, b: str) -> int:
        # distancia de Levenshtein iterativa (memoria O(min(len(a), len(b))))
        if a == b:
            return 0
        if len(a) == 0:
            return len(b)
        if len(b) == 0:
            return len(a)
        # ensure a is shorter
        if len(a) > len(b):
            a, b = b, a
        previous = list(range(len(a) + 1))
        for i, cb in enumerate(b, start=1):
            current = [i]
            for j, ca in enumerate(a, start=1):
                insertions = previous[j] + 1
                deletions = current[j-1] + 1
                substitutions = previous[j-1] + (0 if ca == cb else 1)
                current.append(min(insertions, deletions, substitutions))
            previous = current
        return previous[-1]

    def suggest_similar_keyword(self, word: str) -> Optional[str]:
        # No hacer sugerencias para identificadores que claramente son variables válidas
        if not word:
            return None
            
        # Lista expandida de palabras comunes que NO deben ser sugeridas como keywords
        common_patterns = {
            # Variables de prueba y desarrollo
            "test", "temp", "aux", "tmp", "demo", "example", "sample", "mock", "stub", "dummy",
            # Variables descriptivas comunes
            "mensaje", "resultado", "nombre", "valor", "datos", "info", "item", "objeto",
            "nota1", "nota2", "nota3", "nota4", "nota5",  # Variables numéricas
            "suma", "resta", "multiplicacion", "division", "promedio",  # Variables matemáticas
            "estudiante", "persona", "cuenta", "usuario", "cliente",  # Entidades
            "nivel", "cantidad", "saldo", "titular", "numero", "activa",  # Atributos comunes
            # Variables de programación comunes
            "index", "count", "size", "length", "total", "max", "min", "avg", "first", "last",
            "start", "end", "begin", "finish", "input", "output", "buffer", "cache", "config"
        }
        
        # No sugerir si es una palabra común
        if word.lower() in common_patterns:
            return None
            
        # No sugerir para identificadores que siguen patrones comunes
        word_lower = word.lower()
        
        # Patrón: palabra + número (ej: nota1, variable2, etc.)
        if len(word) > 2 and word_lower[-1].isdigit():
            base_word = word_lower[:-1]
            if any(base_word.startswith(pattern) for pattern in ["nota", "var", "dato", "item", "elem", "test", "temp"]):
                return None
        
       
        if len(word) > 8 and any(char.isupper() for char in word[1:]):
            return None
            
        
        if len(word) > 12:
            return None
        
       
        common_suffixes = ["value", "data", "info", "item", "obj", "var", "num", "str", "bool"]
        for suffix in common_suffixes:
            if word_lower.endswith(suffix.lower()):
                return None

       
        def normalize(s: str) -> str:
            if not s:
                return s
            out = [s[0]]
            for ch in s[1:]:
                if ch == out[-1]:
                    continue
                out.append(ch)
            return ''.join(out)

        norm_word = normalize(word_lower)
        if len(norm_word) <= 2:
            return None

        candidates = set()
        candidates.update(RESERVADAS)
        candidates.update(TIPOS)
        candidates.update(OPERADORES_PALABRAS)
        
    
        candidates.discard('construct')

        best_candidate = None
        best_distance = float('inf')
        
        for candidate in candidates:
            norm_candidate = normalize(candidate.lower())
            distance = self.levenshtein(norm_word, norm_candidate)
            
          
            if len(norm_word) <= 4:
                threshold = 1  
            elif len(norm_word) <= 6:
                threshold = 2  
            else:
                threshold = min(3, len(norm_word) // 3)  
            
     
            if distance <= threshold and distance < best_distance:
     
                matching_chars = sum(1 for i, (a, b) in enumerate(zip(norm_word, norm_candidate)) if a == b)
                min_length = min(len(norm_word), len(norm_candidate))
                
                if matching_chars >= min_length * 0.4: 
                    best_distance = distance
                    best_candidate = candidate
        
        return best_candidate


    def tiene_errores(self):
        return len(self.errors) > 0

    def obtener_errores(self):
        return self.errors



def parse_tokens(tokens: List[Any]):
    p = Parser(tokens)
    ast = p.parse()
    return ast, p.obtener_errores()

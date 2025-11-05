import re
from enum import Enum

#############################
# --- Elementos Lexicos --- #
#############################

# Palabras reservadas del lenguaje HOOP
RESERVADAS = {
    # === (POO BÁSICO) ===
    "mold",     # class
    # "bond",     # interface - NO USADO EN POO BÁSICO
    # "listing",  # enum - FUTURO
    # "layout",   # struct - FUTURO
    # "unit",     # package - FUTURO
    
    # === CONTROL DE FLUJO ===
    "when",     # if
    "otherwise", # else
    "cycle",    # for
    "repeat",   # while
    "halt",     # break
    "skip",     # continue
    "answer",   # return
    "select",   # switch
    "case",     # caso específico en select
    "default",  # caso por defecto en select
    "from",     # desde (en ciclos)
    "to",       # hasta (en ciclos)
    
    # === CREACION DE OBJETOS ===
    "forge",    # new (crear objeto)
    "self",     # this
    "void",     # null
    # "parent",   # super - NO USADO (sin herencia)
    
    # === MODIFICADORES DE ACCESO - NO USADOS (todo público) ===
    # "open",     # public - NO USADO (todo es público por defecto)
    # "sealed",   # private - NO USADO (sin encapsulación avanzada)
    # "linked",   # protected - NO USADO (sin herencia)
    
    # === MANEJO DE ERRORES ===
    "attempt",  # try
    "rescue",   # catch
    "ensure",   # finally
    "throw",    # throw
    
    # === DECLARACIÓN ===
    "fixed",    # const
    "data",     # var (tipado genérico/inferido)
    "action",   # fun
    "display",  # print, printf
    
}

#########################################
# --- POO BASICO HOOP - LIMITACIONES --- #
#########################################

"""

EJEMPLO DE SINTAXIS POO BÁSICO (SIN CONSTRUCT):
mold Persona {
    text nombre;
    whole edad;
    
    # Los constructores ahora se definen como métodos action normales
    action inicializar(text n, whole e) {
        self.nombre set n;
        self.edad set e;
    }
    
    action saludar() {
        display "Hola, soy " plus self.nombre;
    }
    
    action clasificarEdad() {
        select self.edad {
            case 0: {
                display "Bebé";
            }
            case 13: {
                display "Adolescente";
            }
            case 18: {
                display "Adulto";
            }
            default: {
                display "Otra categoría";
            }
        }
    }
}

data persona set forge Persona();
persona.inicializar("Juan", 25);
persona.saludar();
persona.clasificarEdad();
"""

# Operadores en palabras (exclusivos de HOOP)
OPERADORES_PALABRAS = {
    # === ASIGNACIÓN ===
    "set",       # = (asignación)
    
    # === ARITMÉTICOS ===
    "plus",      # + (suma)
    "minus",     # - (resta)
    "times",     # * (multiplicación)
    "divide",    # / (división)
    "mod",       # % (módulo)
    
    # === COMPARACIÓN ===
    "equals",    # == (igual)
    "notequals", # != (diferente)
    "greater",   # > (mayor que)
    "less",      # < (menor que)
    "greatereq", # >= (mayor o igual)
    "lesseq",    # <= (menor o igual)
    
    # === LÓGICOS ===
    "and",       # && (y lógico)
    "or",        # || (o lógico)
    "not"        # ! (negación lógica)
}

# Tipos de datos (para tipado explícito)
TIPOS = {
    # Simples
    "logic",  # boolean - tipado explícito
    "whole",  # integer - tipado explícito
    "fract",  # decimal / float - tipado explícito
    "text",   # string - tipado explícito
    "char",   # character - tipado explícito
    # Compuestos
    "grid",   # matrix - tipado explícito
    "chain"   # linked list - tipado explícito
}




# Palabras pregonadas (built-in functions)
PALABRAS_PREGONADAS = {
    "length", "size", "type", "convert", "input", "output", 
    "read", "write", "open", "close", "max", "min", 
    "abs", "sqrt", "pow", "random"
}

# Delimitadores
DELIMITADORES = {
    '(': 'LPAREN',
    ')': 'RPAREN', 
    '{': 'LBRACE',
    '}': 'RBRACE',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    ';': 'SEMICOLON',
    ',': 'COMMA',
    '.': 'DOT',
    ':': 'COLON'
}

# Operadores
OPERADORES = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MULTIPLY',
    '/': 'DIVIDE',
    '%': 'MODULO',
    '=': 'ASSIGN',
    '==': 'EQUALS',
    '!=': 'NOT_EQUALS',
    '<': 'LESS_THAN',
    '>': 'GREATER_THAN',
    '<=': 'LESS_EQUAL',
    '>=': 'GREATER_EQUAL',
    '&&': 'AND',
    '||': 'OR',
    '!': 'NOT'
}

#############################
# --- Creador de Tokens --- #
#############################

# Tipos de tokens
class TokenType(Enum):
    # Literales
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    CHARACTER = "CHARACTER"
    BOOLEAN = "BOOLEAN"
    
    # Palabras clave
    KEYWORD = "KEYWORD"
    TYPE = "TYPE"
    BUILTIN = "BUILTIN"
    WORD_OPERATOR = "WORD_OPERATOR"  # Operadores en palabras (set, plus, etc.)
    
    # Operadores y delimitadores
    OPERATOR = "OPERATOR"
    DELIMITER = "DELIMITER"
    
    # Comentarios y espacios
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"
    NEWLINE = "NEWLINE"
    
    # Control
    EOF = "EOF"
    ERROR = "ERROR"

# Clase Token (elemento léico)
class Token:
    def __init__(self, tipo, valor, linea, columna, posicion=0):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna
        self.posicion = posicion
    
    def __str__(self):
        return f"Token({self.tipo.name}, '{self.valor}', {self.linea}:{self.columna})"
    
    def __repr__(self):
        return self.__str__()

#######################################
# --- ANALIZADOR LÉXICO PRINCIPAL --- #
#######################################

class AnalizadorLexico:
    """
    Analizador lexico para HOOP
    Lee renglones sucesivos del programa de entrada,
    los descompone en elementos lexicos individuales,
    y alimenta estos elementos a las etapas posteriores.
    """
    
    def __init__(self, codigo_fuente):
        self.codigo = codigo_fuente
        self.posicion = 0
        self.linea_actual = 1
        self.columna_actual = 1
        self.tokens = []
        self.errores = []
    
    def obtener_caracter_actual(self):
        """Obtiene el caracter en la posición actual"""
        if self.posicion >= len(self.codigo):
            return None
        return self.codigo[self.posicion]
    
    def obtener_siguiente_caracter(self):
        """Mira el siguiente carácter sin avanzar"""
        if self.posicion + 1 >= len(self.codigo):
            return None
        return self.codigo[self.posicion + 1]
    
    def avanzar(self):
        """Avanza un carácter y actualiza línea/columna"""
        if self.posicion < len(self.codigo):
            if self.codigo[self.posicion] == '\n':
                self.linea_actual += 1
                self.columna_actual = 1
            else:
                self.columna_actual += 1
            self.posicion += 1
    
    def omitir_espacios_en_blanco(self):
        """Omite espacios en blanco (excepto newlines)"""
        while (self.obtener_caracter_actual() and 
               self.obtener_caracter_actual() in ' \t\r'):
            self.avanzar()
    
    def crear_token(self, tipo, valor, linea=None, columna=None):
        """Crea un token con posición actual o especificada"""
        return Token(tipo, valor, 
                    linea or self.linea_actual, 
                    columna or self.columna_actual, 
                    self.posicion)
    
    def leer_numero(self):
        """Lee números (enteros y decimales)
        
        Formatos soportados:
        - Enteros: 42, 0, 123
        - Decimales: 3.14, 0.5, 123.456
        
        Returns:
            Token de tipo NUMBER con el valor numérico como string
        """
        linea_inicio = self.linea_actual
        columna_inicio = self.columna_actual
        valor = ""
        tiene_punto = False
        
        # Leer parte entera
        while (self.obtener_caracter_actual() and 
               self.obtener_caracter_actual().isdigit()):
            valor += self.obtener_caracter_actual()
            self.avanzar()
        
        # Verificar si es decimal
        if (self.obtener_caracter_actual() == '.' and 
            self.obtener_siguiente_caracter() and 
            self.obtener_siguiente_caracter().isdigit()):
            
            tiene_punto = True
            valor += self.obtener_caracter_actual()  # el punto
            self.avanzar()
            
            # Leer parte decimal
            while (self.obtener_caracter_actual() and 
                   self.obtener_caracter_actual().isdigit()):
                valor += self.obtener_caracter_actual()
                self.avanzar()
            
            # Verificar múltiples puntos decimales (error común)
            if self.obtener_caracter_actual() == '.':
                self.errores.append(f"Número mal formado con múltiples puntos decimales en línea {linea_inicio}:{columna_inicio}")
                # Consumir el punto extra
                self.avanzar()
        
        return Token(TokenType.NUMBER, valor, linea_inicio, columna_inicio, self.posicion)
    
    def leer_cadena(self, delimitador):
        """Lee cadenas de texto o caracteres individuales
        
        Args:
            delimitador: Comilla que delimita la cadena (' o ")
        
        Returns:
            Token de tipo STRING o CHARACTER según corresponda
        """
        linea_inicio = self.linea_actual
        columna_inicio = self.columna_actual
        self.avanzar()  # saltar comilla inicial
        valor = ""
        
        while (self.obtener_caracter_actual() and 
               self.obtener_caracter_actual() != delimitador):
            
            # Manejo de caracteres de escape
            if self.obtener_caracter_actual() == '\\':
                self.avanzar()
                if self.obtener_caracter_actual():
                    char = self.obtener_caracter_actual()
                    if char == 'n':
                        valor += '\n'
                    elif char == 't':
                        valor += '\t'
                    elif char == 'r':
                        valor += '\r'
                    elif char == '\\':
                        valor += '\\'
                    elif char == delimitador:
                        valor += delimitador
                    else:
                        valor += char
                    self.avanzar()
            else:
                valor += self.obtener_caracter_actual()
                self.avanzar()
        
        # Verificar cierre de cadena
        if self.obtener_caracter_actual() == delimitador:
            self.avanzar()  # saltar comilla final
        else:
            self.errores.append(f"Cadena sin cerrar en línea {linea_inicio}:{columna_inicio}")
            return Token(TokenType.ERROR, valor, linea_inicio, columna_inicio, self.posicion)
        
        # Determinar si es un carácter individual (solo con comillas simples y un carácter)
        if delimitador == "'" and len(valor) == 1:
            return Token(TokenType.CHARACTER, valor, linea_inicio, columna_inicio, self.posicion)
        
        return Token(TokenType.STRING, valor, linea_inicio, columna_inicio, self.posicion)
    
    def leer_identificador(self):
        """Lee identificadores, palabras clave, tipos, palabras pregonadas y operadores en palabras
        
        Returns:
            Token clasificado según el tipo de palabra reconocida
        """
        linea_inicio = self.linea_actual
        columna_inicio = self.columna_actual
        valor = ""
        
        # Leer el identificador completo
        while (self.obtener_caracter_actual() and 
               (self.obtener_caracter_actual().isalnum() or 
                self.obtener_caracter_actual() == '_')):
            valor += self.obtener_caracter_actual()
            self.avanzar()
        
        # Clasificar según las tablas definidas (orden optimizado por frecuencia de uso)
        # Primero verificar booleanos (más rápido, solo 2 valores)
        if valor in ['true', 'false']:
            tipo = TokenType.BOOLEAN
        # Luego operadores en palabras (muy comunes: set, plus, equals, etc.)
        elif valor in OPERADORES_PALABRAS:
            tipo = TokenType.WORD_OPERATOR
        # Palabras reservadas (estructuras de control, etc.)
        elif valor in RESERVADAS:
            tipo = TokenType.KEYWORD
        # Tipos de datos
        elif valor in TIPOS:
            tipo = TokenType.TYPE
        # Funciones built-in
        elif valor in PALABRAS_PREGONADAS:
            tipo = TokenType.BUILTIN
        # Si no coincide con ninguna categoría, es un identificador
        else:
            tipo = TokenType.IDENTIFIER
        
        return Token(tipo, valor, linea_inicio, columna_inicio, self.posicion)
    
    def leer_comentario(self, prefijo=""):
        """Lee comentarios de línea (# o //)
        
        Args:
            prefijo: Prefijo del comentario ya consumido (ej: '#', '//')
        """
        linea_inicio = self.linea_actual
        columna_inicio = self.columna_actual
        comentario = ""
        
        # Leer hasta el final de la línea
        while (self.obtener_caracter_actual() and 
               self.obtener_caracter_actual() != '\n'):
            comentario += self.obtener_caracter_actual()
            self.avanzar()
        
        return Token(TokenType.COMMENT, comentario.strip(), linea_inicio, columna_inicio, self.posicion)
    
    def leer_operador(self):
        """Lee operadores de uno o dos caracteres, o comentarios //"""
        linea_inicio = self.linea_actual
        columna_inicio = self.columna_actual
        
        char1 = self.obtener_caracter_actual()
        char2 = self.obtener_siguiente_caracter()
        
        # Verificar comentario // primero
        if char1 == '/' and char2 == '/':
            self.avanzar()  # primer /
            self.avanzar()  # segundo /
            return self.leer_comentario("//")
        
        # Verificar operadores de dos caracteres
        if char2 and char1 + char2 in OPERADORES:
            valor = char1 + char2
            self.avanzar()
            self.avanzar()
            return Token(TokenType.OPERATOR, valor, linea_inicio, columna_inicio, self.posicion)
        
        # Verificar operadores de un carácter
        if char1 in OPERADORES:
            valor = char1
            self.avanzar()
            return Token(TokenType.OPERATOR, valor, linea_inicio, columna_inicio, self.posicion)
        
        # Operador desconocido
        valor = char1
        self.avanzar()
        self.errores.append(f"Operador desconocido '{valor}' en línea {linea_inicio}:{columna_inicio}")
        return Token(TokenType.ERROR, valor, linea_inicio, columna_inicio, self.posicion)
    

    
    def analizar(self):
        """
        FUNCIÓN PRINCIPAL DEL ANALIZADOR LÉXICO
        
        Lee renglones sucesivos del programa de entrada,
        los descompone en elementos léxicos individuales,
        y retorna la secuencia de tokens.
        
        Esta es la fase de traducción que más tiempo requiere.
        """
        while self.posicion < len(self.codigo):
            # Omitir espacios en blanco
            self.omitir_espacios_en_blanco()
            
            char = self.obtener_caracter_actual()
            
            # Fin del código
            if char is None:
                break
            
            # === RECONOCIMIENTO DE ELEMENTOS LÉXICOS ===
            
            # Saltos de línea
            elif char == '\n':
                token = self.crear_token(TokenType.NEWLINE, char)
                self.tokens.append(token)
                self.avanzar()
            
            # Números (123, 45.67)
            elif char.isdigit():
                token = self.leer_numero()
                self.tokens.append(token)
            
            # Cadenas de texto ("texto", 'texto')
            elif char in ['"', "'"]:
                token = self.leer_cadena(char)
                self.tokens.append(token)
            
            # Identificadores, palabras clave, tipos, pregonadas
            elif char.isalpha() or char == '_':
                token = self.leer_identificador()
                self.tokens.append(token)
            
            # Comentarios (#)
            elif char == '#':
                self.avanzar()  # consumir el #
                token = self.leer_comentario("#")
                self.tokens.append(token)
            
            # Delimitadores
            elif char in DELIMITADORES:
                token = self.crear_token(TokenType.DELIMITER, char)
                self.tokens.append(token)
                self.avanzar()
            
            # Operadores
            elif char in '+-*/%=<>!&|':
                token = self.leer_operador()
                self.tokens.append(token)
            
            # Carácter desconocido
            else:
                linea_error = self.linea_actual
                columna_error = self.columna_actual
                self.errores.append(f"Carácter desconocido '{char}' (código ASCII: {ord(char)}) en línea {linea_error}:{columna_error}")
                # Crear token de error para mantener sincronización
                token = self.crear_token(TokenType.ERROR, char)
                self.tokens.append(token)
                self.avanzar()
        
        # Agregar token EOF al final
        self.tokens.append(self.crear_token(TokenType.EOF, ""))
        return self.tokens
    
    def obtener_tokens(self):
        """Retorna la lista de tokens generados"""
        return self.tokens
    
    def obtener_errores(self):
        """Retorna la lista de errores encontrados"""
        return self.errores
    
    def tiene_errores(self):
        """Verifica si hay errores léxicos"""
        return len(self.errores) > 0
    
    def imprimir_tokens(self):
        """Imprime todos los tokens de manera legible"""
        print("=== ELEMENTOS LÉXICOS GENERADOS ===")
        for i, token in enumerate(self.tokens):
            if token.tipo != TokenType.NEWLINE:  
                print(f"{i+1:3}: {token}")
        
        if self.errores:
            print("\n=== ERRORES LÉXICOS ===")
            for error in self.errores:
                print(f"ERROR: {error}")

#####################################
# --- FUNCIÓN PRINCIPAL DE USO --- #
#####################################

def analizar_codigo_hoop(codigo_fuente, mostrar_tokens=True):
    """
    Función principal para usar el analizador léxico de HOOP
    
    Args:
        codigo_fuente (str): El código HOOP a analizar
        mostrar_tokens (bool): Si mostrar los tokens generados
    
    Returns:
        (tokens, errores)
    """
    print("=== ANALIZADOR LÉXICO HOOP ===")
    print(f"Código fuente:\n{codigo_fuente}\n")
    
    # Crear y ejecutar analizador
    analizador = AnalizadorLexico(codigo_fuente)
    tokens = analizador.analizar()
    
    # Mostrar resultados si se solicita
    if mostrar_tokens:
        analizador.imprimir_tokens()
    
    # Resumen
    print(f"\nRESUMEN:")
    print(f"- Tokens generados: {len(tokens)}")
    print(f"- Errores encontrados: {len(analizador.obtener_errores())}")
    print(f"- Líneas procesadas: {analizador.linea_actual}")
    
    return tokens, analizador.obtener_errores()


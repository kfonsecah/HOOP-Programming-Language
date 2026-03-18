# src/core/constants/keywords.py

# Palabras reservadas del lenguaje HOOP
KEYWORDS = [
    # === ESTRUCTURAS BASICAS (POO BASICO) ===
    "mold",     # class
    
    # === CONTROL DE FLUJO ===
    "when",     # if
    "otherwise", # else
    "cycle",    # for
    "repeat",   # while
    "halt",     # break
    "skip",     # continue
    "answer",   # return
    "select",   # switch
    "case",     # caso especifico en select
    "default",  # caso por defecto en select
    "from",     # desde (en ciclos)
    "to",       # hasta (en ciclos)
    
    # === CREACION DE OBJETOS ===
    "forge",    # new (crear objeto)
    "self",     # this
    "void",     # null
    
    # === MANEJO DE ERRORES ===
    "attempt",  # try
    "rescue",   # catch
    "ensure",   # finally
    "throw",    # throw
    
    # === DECLARACION ===
    "fixed",    # const
    "data",     # var (tipado generico/inferido)
    "action",   # fun
    "display",  # print, printf
]

# Tipos de datos del lenguaje HOOP
TYPES = [
    "logic",  # boolean
    "whole",  # integer
    "fract",  # decimal / float
    "text",   # string
    "char",   # character
    "grid",   # matrix
    "chain"   # linked list
]

# Operadores en palabras (exclusivos de HOOP)
WORD_OPERATORS = [
    # === ASIGNACION ===
    "set",       # = (asignacion)
    
    # === ARITMETICOS ===
    "plus",      # + (suma)
    "minus",     # - (resta)
    "times",     # * (multiplicacion)
    "divide",    # / (division)
    "mod",       # % (modulo)
    
    # === COMPARACION ===
    "equals",    # == (igual)
    "notequals", # != (diferente)
    "greater",   # > (mayor que)
    "less",      # < (menor que)
    "greatereq", # >= (mayor o igual)
    "lesseq",    # <= (menor o igual)
    
    # === LOGICOS ===
    "and",       # && (y logico)
    "or",        # || (o logico)
    "not"        # ! (negacion logica)
]

# Palabras pregonadas (built-in functions)
BUILTIN_FUNCTIONS = [
    "length", "size", "type", "convert", "input", "output", 
    "read", "write", "open", "close", "max", "min", 
    "abs", "sqrt", "pow", "random"
]

# Valores booleanos
BOOLEAN_VALUES = ["true", "false"]

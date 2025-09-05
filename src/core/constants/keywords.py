# src/core/constants/keywords.py

# Palabras reservadas del lenguaje HOOP
KEYWORDS = [
    # === ESTRUCTURAS BÁSICAS (POO BÁSICO) ===
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
    "case",     # caso específico en select
    "default",  # caso por defecto en select
    "from",     # desde (en ciclos)
    "to",       # hasta (en ciclos)
    
    # === CREACIÓN DE OBJETOS ===
    "forge",    # new (crear objeto)
    "self",     # this
    "void",     # null
    
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
]

# Palabras pregonadas (built-in functions)
BUILTIN_FUNCTIONS = [
    "length", "size", "type", "convert", "input", "output", 
    "read", "write", "open", "close", "max", "min", 
    "abs", "sqrt", "pow", "random"
]

# Valores booleanos
BOOLEAN_VALUES = ["true", "false"]

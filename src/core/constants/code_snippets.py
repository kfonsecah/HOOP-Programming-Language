# src/core/constants/code_snippets.py

CODE_SNIPPETS = {
    "palabras_reservadas": {
        "title": "Palabras Reservadas",
        "code": """# --- Palabras Reservadas en HOOP ---

# Definición de funciones y clases
def  # Define una función
class  # Define una clase
return # Devuelve un valor de una función

# Control de flujo
if # Condicional
else # Alternativa a if
elif # Alternativa condicional
for # Bucle for
while # Bucle while
break # Rompe un bucle
continue # Salta a la siguiente iteración

# Operadores lógicos y de pertenencia
and # Y lógico
or # O lógico
not # Negación lógica
in # Pertenencia

# Valores nulos y booleanos
None # Representa la ausencia de valor
True # Valor booleano verdadero
False # Valor booleano falso

# Manejo de excepciones
try # Bloque para código que puede fallar
except # Captura de excepciones
finally # Se ejecuta siempre
raise # Lanza una excepción
"""
    },
    "sintaxis_control": {
        "title": "Sintaxis: Control de Flujo",
        "code": """# --- Sintaxis de Control de Flujo ---

# Estructura if-elif-else
if condicion_1:
    # Código si condicion_1 es verdadera
elif condicion_2:
    # Código si condicion_2 es verdadera
else:
    # Código si ninguna es verdadera

# Bucle while
while condicion:
    # Código a repetir mientras la condición sea verdadera
    if otra_condicion:
        break  # Salir del bucle

# Bucle for
for elemento in iterable:
    # Código a ejecutar para cada elemento
    if alguna_condicion:
        continue # Saltar al siguiente elemento
"""
    },
    "sintaxis_funciones": {
        "title": "Sintaxis: Funciones",
        "code": """# --- Sintaxis de Funciones ---

# Definición de una función simple
def mi_funcion():
    print("Hola desde una función")

# Definición con parámetros y valor de retorno
def suma(a, b):
    resultado = a + b
    return resultado

# Llamada a las funciones
mi_funcion()
valor_suma = suma(5, 3)
print(f"El resultado de la suma es {valor_suma}")
"""
    },
    "sintaxis_operaciones": {
        "title": "Sintaxis: Operaciones",
        "code": """# --- Sintaxis de Operaciones ---

# Operaciones Aritméticas
suma = 10 + 5
resta = 10 - 5
multiplicacion = 10 * 5
division = 10 / 5
modulo = 10 % 3  # Residuo

# Operaciones de Comparación
es_igual = (a == b)
no_es_igual = (a != b)
mayor_que = (a > b)
menor_o_igual = (a <= b)

# Operaciones Lógicas
y_logico = (condicion1 and condicion2)
o_logico = (condicion1 or condicion2)
negacion = not condicion1
"""
    },
    "semantica": {
        "title": "Semántica",
        "code": """# --- Semántica en HOOP ---

# La semántica se refiere al significado del código.

# Asignación de variables:
# El nombre 'edad' tiene el significado semántico de
# representar la edad de una persona.
edad = 25

# Invocación de funciones:
# Semánticamente, esto significa "ejecutar la lógica
# para calcular un área".
area = calcular_area(10, 5)

# Un código es semánticamente correcto si hace lo que
# el programador intentaba que hiciera.
# Por ejemplo, si 'calcular_area' restara en lugar de
# multiplicar, sería sintácticamente correcto pero
# semánticamente incorrecto.
"""
    },
    "tipos_de_datos": {
        "title": "Tipos de Datos",
        "code": """# --- Tipos de Datos en HOOP ---

# Tipo Entero (Integer)
numero_entero = 42

# Tipo Flotante (Float)
numero_flotante = 3.14159

# Tipo Cadena de Texto (String)
saludo = "Hola, mundo!"
otro_texto = 'También con comillas simples'

# Tipo Booleano (Boolean)
es_verdadero = True
es_falso = False

# Tipo Lista (List) - Colección ordenada y mutable
mi_lista = [1, "manzana", 3.0, True]

# Tipo Diccionario (Dictionary) - Colección clave-valor
mi_diccionario = {
    "nombre": "Alex",
    "edad": 30,
    "es_estudiante": False
}

# Tipo Nulo (NoneType)
sin_valor = None
"""
    }
}

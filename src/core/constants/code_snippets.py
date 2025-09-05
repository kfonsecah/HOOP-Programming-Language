# src/core/constants/code_snippets.py

CODE_SNIPPETS = {
    "palabras_reservadas": {
        "title": "Palabras Reservadas",
        "code": """# --- Palabras Reservadas en HOOP ---

# Definición de funciones y clases
mold  # Define una clase
action  # Define una función
answer # Devuelve un valor de una función

# Control de flujo
when # Condicional
otherwise # Alternativa a when
cycle # Bucle cycle
from # Desde (en ciclos)
to # Hasta (en ciclos)

# Declaración
data # Variable
set # Asignación
display # Imprimir

# Tipos
whole # Entero
text # Cadena
logic # Booleano
fract # Decimal

# Operadores
plus # Suma
minus # Resta
times # Multiplicación
divide # División
greater # Mayor que
less # Menor que
equals # Igual
"""
    },
    "ejemplo_basico": {
        "title": "Ejemplo Básico HOOP",
        "code": """# Ejemplo básico de código HOOP
data mensaje set "Hola mundo desde HOOP";
data numero set 42;
data activo set true;

display mensaje;
display numero;
"""
    },
    "ejemplo_clase": {
        "title": "Ejemplo de Clase",
        "code": """# Ejemplo de clase en HOOP
mold Persona {
    text nombre;
    whole edad;
    
    action saludar() {
        display "Hola, soy una persona";
    }
}

data p set "objeto creado";
"""
    },
    "ejemplo_control": {
        "title": "Ejemplo de Control de Flujo",
        "code": """# Ejemplo de estructuras de control
data x set 10;
data y set 5;

when x greater y {
    display "x es mayor que y";
} otherwise {
    display "y es mayor o igual que x";
}

cycle i from 1 to 5 {
    display i;
}
"""
    },
    "ejemplo_funcion": {
        "title": "Ejemplo de Función",
        "code": """# Ejemplo de función
action sumar() {
    data a set 5;
    data b set 3;
    data resultado set a plus b;
    display resultado;
}

data test set "función definida";
"""
    },
    "ejemplo_completo": {
        "title": "Ejemplo Completo HOOP",
        "code": """# Ejemplo completo que combina varios elementos
mold Calculadora {
    whole resultado;
    
    action sumar() {
        data a set 10;
        data b set 20;
        resultado set a plus b;
        display resultado;
    }
    
    action mostrarResultado() {
        when resultado greater 0 {
            display "El resultado es positivo";
        } otherwise {
            display "El resultado es cero o negativo";
        }
    }
}

data calc set "calculadora creada";
data contador set 0;

cycle i from 1 to 3 {
    contador set contador plus 1;
    display contador;
}
"""
    },
    "sintaxis_control": {
        "title": "Sintaxis: Control de Flujo",
        "code": """# --- Sintaxis de Control de Flujo ---

# Estructura when-otherwise
when condicion_1 {
    # Código si condicion_1 es verdadera
} otherwise {
    # Código si es falsa
}

# Bucle cycle
cycle i from 1 to 10 {
    # Código a repetir
    display i;
}
"""
    },
    "sintaxis_funciones": {
        "title": "Sintaxis: Funciones",
        "code": """# --- Sintaxis de Funciones ---

# Definición de una función simple
action mi_funcion() {
    display "Hola desde una función";
}

# Función con variables locales
action calcular() {
    data resultado set 5 plus 3;
    display resultado;
}
"""
    },
    "sintaxis_operaciones": {
        "title": "Sintaxis: Operaciones",
        "code": """# --- Sintaxis de Operaciones ---

# Operaciones Aritméticas
data suma set 10 plus 5;
data resta set 10 minus 5;
data multiplicacion set 10 times 5;
data division set 10 divide 5;

# Operaciones de Comparación
data es_mayor set 10 greater 5;
data es_menor set 5 less 10;
data es_igual set 5 equals 5;
"""
    },
    "semantica": {
        "title": "Semántica",
        "code": """# --- Semántica en HOOP ---

# La semántica se refiere al significado del código.

# Asignación de variables:
# El nombre 'edad' tiene el significado semántico de
# representar la edad de una persona.
data edad set 25;

# Un código es semánticamente correcto si hace lo que
# el programador intentaba que hiciera.
display edad;
"""
    },
    "tipos_de_datos": {
        "title": "Tipos de Datos",
        "code": """# --- Tipos de Datos en HOOP ---

# Tipo Entero (whole)
data numero_entero set 42;

# Tipo Decimal (fract)
data numero_decimal set 3.14;

# Tipo Cadena de Texto (text)
data saludo set "Hola, mundo!";

# Tipo Booleano (logic)
data es_verdadero set true;
data es_falso set false;

display numero_entero;
display saludo;
"""
    }
}

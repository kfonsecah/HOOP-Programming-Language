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

# NOTA: 'construct' ya NO es una palabra reservada válida
# Use 'action' para definir métodos, incluyendo constructores
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
        "code": """data estado set "inicio";
when estado equals "inicio" {
    display estado;
}

data nivel set 4;
when nivel greater 1 {
    when nivel less 5 {
        display "en rango";
    } otherwise {
        display "fuera de rango";
    }
} otherwise {
    display "valor invalido";
}

cycle i from 1 to 3 {
    display i;
}

data contador set 0;
repeat contador less 2 {
    display contador;
    contador set contador plus 1;
}
"""
    },

    "sintaxis_funciones": {
        "title": "Sintaxis: Funciones",
        "code": """action saludoCompleto(text nombre) {
    data saludo set "Hola ";
    saludo set saludo plus nombre;
    answer saludo;
}

action registrarVisita() {
    display "Visita registrada";
}

data mensaje set saludoCompleto("HOOP");
display mensaje;
registrarVisita();
"""
    },
    "sintaxis_operaciones": {
        "title": "Sintaxis: Operaciones",
        "code": """data suma set 8 plus 2;
data resta set 8 minus 2;
data producto set 8 times 2;
data division set 8 divide 2;

data conjuncion set true and false;
data disyuncion set true or false;
data negacion set not false;

display suma;
display resta;
display producto;
display division;
display conjuncion;
display disyuncion;
display negacion;
"""
    },
    "entrada_salida_datos": {
        "title": "Entrada y Salida de Datos",
        "code": """action pedirDatos() {
    data nombre set input("Ingresa tu nombre: ");
    data edad set input("Ingresa tu edad: ");
    data mensaje set "Hola ";
    mensaje set mensaje plus nombre;
    display mensaje;
    display "Edad: ";
    display edad;
}

pedirDatos();
"""
    },

    "semantica": {
        "title": "Semántica",
        "code": """action main() {
    data descripcion set "Programa HOOP";
    data enEjecucion set true;
    display descripcion;

    when enEjecucion {
        display "La logica vive dentro de bloques con llaves";
    } otherwise {
        display "Programa detenido";
    }
}

main();
"""
    },
    "tipos_de_datos": {
        "title": "Tipos de Datos",
        "code": """data entero set 15;
data decimal set 3.75;
data caracter set 'A';
data logicoVerdadero set true;
data logicoFalso set false;
data texto set "Cadena";

action sinValor() {
}

data valorNulo set sinValor();

mold DatosCompuestos {
    grid matrizPrincipal;
    chain listaPrincipal;
}

data matrizCompuesta set "";
data listaCompuesta set "";

data estructura set forge DatosCompuestos();

data filas set "";
cycle fila from 1 to 2 {
    data linea set "";
    cycle columna from 1 to 3 {
        data valor set fila times columna;
        linea set linea plus convert(valor, "text");
        when columna less 3 {
            linea set linea plus " ";
        }
    }
    filas set filas plus linea;
    when fila less 2 {
        filas set filas plus "\n";
    }
}

matrizCompuesta set filas;
listaCompuesta set "a,b,c";

display entero;
display decimal;
display caracter;
display logicoVerdadero;
display logicoFalso;
display texto;
display valorNulo;
display estructura;
display matrizCompuesta;
display listaCompuesta;
"""
    },


    "test_basico": {
        "title": "Test Básico - Declaraciones Simples",
        "code": """# Test básico de declaraciones
data nombre set "Juan Pérez";
data edad set 25;
data altura set 1.75;
data activo set true;
data inactivo set false;

display nombre;
display edad;
display altura;
"""
    },
    "test_operaciones": {
        "title": "Test Operaciones Aritméticas",
        "code": """# Test de operaciones aritméticas
data a set 10;
data b set 5;
data suma set a plus b;
data resta set a minus b;
data multiplicacion set a times b;
data division set a divide b;
data modulo set a mod b;

display suma;
display resta;
display multiplicacion;
display division;
display modulo;
"""
    },
    "test_comparaciones": {
        "title": "Test Operaciones de Comparación",
        "code": """# Test de operaciones de comparación
data x set 15;
data y set 10;
data es_mayor set x greater y;
data es_menor set x less y;
data son_iguales set x equals y;
data son_diferentes set x notequals y;
data mayor_igual set x greatereq y;
data menor_igual set x lesseq y;

display es_mayor;
display es_menor;
display son_iguales;
"""
    },
    "test_control_flujo": {
        "title": "Test Control de Flujo Completo",
        "code": """# Test de estructuras de control
data puntuacion set 85;
data mensaje set "Sin evaluar";

when puntuacion greater 90 {
    mensaje set "Excelente";
    display "Calificación sobresaliente";
} otherwise {
    when puntuacion greater 70 {
        mensaje set "Bueno";
        display "Calificación aceptable";
    } otherwise {
        mensaje set "Necesita mejorar";
        display "Calificación insuficiente";
    }
}

display mensaje;

cycle i from 1 to 5 {
    display "Iteración número: ";
    display i;
}
"""
    },
    "test_funciones_complejas": {
        "title": "Test Funciones y Llamadas",
        "code": """# Test de funciones complejas
action calcularPromedio(whole nota1, whole nota2, whole nota3) {
    data suma set nota1 plus nota2;
    suma set suma plus nota3;
    data promedio set suma divide 3;
    answer promedio;
}

action evaluarEstudiante(text nombre, whole promedio) {
    display "Evaluando estudiante: ";
    display nombre;
    
    when promedio greater 85 {
        display "Estudiante destacado";
    } otherwise {
        when promedio greater 70 {
            display "Estudiante regular";
        } otherwise {
            display "Estudiante necesita apoyo";
        }
    }
}

data estudiante1 set "Ana García";
data notas1 set calcularPromedio(90, 85, 88);
evaluarEstudiante(estudiante1, notas1);

data estudiante2 set "Carlos López";
data notas2 set calcularPromedio(75, 80, 70);
evaluarEstudiante(estudiante2, notas2);
"""
    },
    "test_clases_completas": {
        "title": "Test Clases y POO Completo",
        "code": """# Test completo de POO
mold Cuenta {
    text titular;
    whole numero;
    fract saldo;
    logic activa;
    
    action construct(text t, whole n, fract s) {
        self.titular set t;
        self.numero set n;
        self.saldo set s;
        self.activa set true;
        display "Cuenta creada para: ";
        display self.titular;
    }
    
    action depositar(fract cantidad) {
        when self.activa equals true {
            self.saldo set self.saldo plus cantidad;
            display "Depósito realizado. Nuevo saldo: ";
            display self.saldo;
        } otherwise {
            display "Error: Cuenta inactiva";
        }
    }
    
    action retirar(fract cantidad) {
        when self.activa equals true {
            when self.saldo greatereq cantidad {
                self.saldo set self.saldo minus cantidad;
                display "Retiro realizado. Nuevo saldo: ";
                display self.saldo;
            } otherwise {
                display "Error: Saldo insuficiente";
            }
        } otherwise {
            display "Error: Cuenta inactiva";
        }
    }
    
    action consultarSaldo() {
        when self.activa equals true {
            display "Saldo actual: ";
            display self.saldo;
        } otherwise {
            display "Cuenta inactiva";
        }
    }
}

data cuenta1 set forge Cuenta("María Rodríguez", 12345, 1000.50);
cuenta1.depositar(250.75);
cuenta1.retirar(100.25);
cuenta1.consultarSaldo();

data cuenta2 set forge Cuenta("Pedro Martínez", 67890, 500.00);
cuenta2.depositar(150.00);
cuenta2.consultarSaldo();
"""
    },
    "test_errores_lexicos": {
        "title": "Test Errores Léxicos Intencionados",
        "code": """# Test para provocar errores léxicos
data variable1 set "cadena sin cerrar;
data variable2 set 123.45.67;
data variable3 set 10 @#$;
data 123variable set "nombre inválido";
data when set 5;
data variable4 set 'otra cadena sin cerrar;
"""
    },
    "test_errores_sintacticos": {
        "title": "Test Errores Sintácticos Intencionados",
        "code": """# Test para provocar errores sintácticos
data x set 10
data y set 20;

when x greater y {
    display "x es mayor"
} otherwise
    display "y es mayor";
}

cycle i from 1 to 5
    display i;

action funcionSinCerrar() {
    display "función sin cerrar";

mold ClaseSinCerrar {
    text nombre;
"""
    },
    "test_ambiguedades": {
        "title": "Test Casos Ambiguos",
        "code": """# Test para identificar posibles ambigüedades
data set set "set";
data plus set "plus";
data when set "when";

action action() {
    display "función llamada action";
}

data data set "data";
display data;

mold mold {
    text mold;
    
    action mold() {
        display "método mold en clase mold";
    }
}

data instancia set forge mold();
instancia.mold();
"""
    },
    "test_anidamiento_profundo": {
        "title": "Test Anidamiento Máximo (Nivel 2)",
        "code": """# Test de anidamiento máximo permitido (2 niveles)
action procesarDatos(whole nivel) {
    when nivel greater 0 {
        display "Procesando nivel: ";
        display nivel;
        
        # MÁXIMO NIVEL DE ANIDAMIENTO PERMITIDO (Nivel 2)
        when nivel greater 5 {
            display "Nivel alto";
            # NO SE PERMITE MÁS ANIDAMIENTO - Esto causaría error:
            # when nivel greater 8 {
            #     display "Esto NO está permitido";
            # }
        } otherwise {
            display "Nivel bajo";
        }
    } otherwise {
        display "Nivel inválido";
    }
    
    # Los ciclos también cuentan para el anidamiento
    cycle i from 1 to 3 {
        when i mod 2 equals 0 {
            display "Número par: ";
            display i;
            # NO SE PERMITE MÁS ANIDAMIENTO AQUÍ
        } otherwise {
            display "Número impar: ";
            display i;
        }
    }
}

procesarDatos(10);
procesarDatos(3);
procesarDatos(0);
"""
    },
    "test_expresiones_complejas": {
        "title": "Test Expresiones Complejas",
        "code": """# Test de expresiones complejas
action calculadora() {
    data a set 10;
    data b set 5;
    data c set 3;
    data d set 2;
    
    # Expresiones aritméticas complejas
    data resultado1 set a plus b times c;
    data resultado2 set a times b plus c times d;
    data resultado3 set a plus b minus c divide d;
    
    display "Resultado 1: ";
    display resultado1;
    display "Resultado 2: ";
    display resultado2;
    display "Resultado 3: ";
    display resultado3;
    
    # Expresiones con comparaciones múltiples
    data condicion1 set a greater b and b greater c;
    data condicion2 set a equals 10 or b equals 3;
    data condicion3 set not a less b;
    
    when condicion1 {
        display "Condición 1 es verdadera";
    }
    
    when condicion2 {
        display "Condición 2 es verdadera";
    }
    
    when condicion3 {
        display "Condición 3 es verdadera";
    }
}

calculadora();
"""
    },
    "test_casos_limite": {
        "title": "Test Casos Límite",
        "code": """# Test de casos límite
data cadena_vacia set "";
data numero_cero set 0;
data numero_negativo set -1;
data decimal_pequeno set 0.001;
data cadena_larga set "Esta es una cadena muy larga que contiene múltiples palabras y caracteres especiales como números 123, símbolos !@#$%^&*() y texto adicional para probar el manejo de cadenas extensas en el analizador léxico";

action funcionVacia() {
}

mold ClaseVacia {
}

cycle i from 0 to 0 {
    display "Este ciclo debería ejecutarse una vez";
}

when true {
    when false {
        display "Esto nunca debería ejecutarse";
    } otherwise {
        when true {
            display "Anidamiento correcto";
        }
    }
}

# Comentarios muy largos que podrían causar problemas: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
"""
    }
}

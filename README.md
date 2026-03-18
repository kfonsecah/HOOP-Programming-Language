# HOOP — Human Object Oriented Programming

HOOP es un lenguaje de programación orientado a objetos diseñado e implementado desde cero en Python. Su sintaxis está basada en palabras en inglés en lugar de símbolos matemáticos tradicionales, haciendo el código más explícito y legible. El proyecto incluye un intérprete completo en cuatro fases y un IDE de escritorio construido con Tkinter.

---

## ¿Por qué HOOP?

La mayoría de los lenguajes usan símbolos como `+`, `-`, `==` que resultan abstractos para quienes están aprendiendo a programar. HOOP reemplaza esos símbolos por palabras: `plus`, `minus`, `equals`. El resultado es código que se lee casi como prosa en inglés, lo que hace la estructura lógica más transparente.

```
data precio set 150;
data descuento set 30;
data total set precio minus descuento;

when total greater 100 {
    display "Precio con descuento aplicado";
}
```

---

## Arquitectura del intérprete

El intérprete sigue una pipeline clásica de cuatro fases secuenciales. Cada fase consume la salida de la anterior y tiene una responsabilidad bien definida.

```
Código fuente (.hoop)
        ↓
┌─────────────────────┐
│  1. Análisis Léxico │  lexer.py → lista de Tokens
└─────────────────────┘
        ↓
┌──────────────────────────┐
│  2. Análisis Sintáctico  │  parser_oficial.py → AST
└──────────────────────────┘
        ↓
┌─────────────────────────┐
│  3. Análisis Semántico  │  semantic.py → validación + tabla de símbolos
└─────────────────────────┘
        ↓
┌──────────────────┐
│  4. Ejecución    │  interpreter.py → output del programa
└──────────────────┘
```

---

## Fase 1 — Análisis léxico (`lexer.py`)

La clase `AnalizadorLexico` recorre el código carácter por carácter y produce una lista de `Token`. Cada token tiene un tipo, un valor y su posición exacta en el archivo (línea y columna), lo que permite generar mensajes de error precisos en fases posteriores.

El lexer distingue entre cinco categorías principales de palabras: palabras reservadas del lenguaje (`mold`, `when`, `cycle`...), tipos de datos (`whole`, `fract`, `text`...), operadores en palabras (`set`, `plus`, `equals`...), funciones built-in (`display`, `length`, `input`...) y valores booleanos (`true`, `false`). Todo lo que no caiga en ninguna de esas categorías se clasifica como `IDENTIFIER`.

Algunos detalles de la implementación:

- Los números se procesan buscando el punto decimal — si el siguiente carácter después del punto es un dígito, se lee como `fract`, si no, se trata como dos tokens separados.
- Las cadenas soportan secuencias de escape (`\n`, `\t`, `\\`) y reportan error si no se cierra la comilla.
- Los comentarios se inician con `#` o `//` y consumen el resto de la línea.
- Los caracteres individuales con comillas simples (`'A'`) se tokenean como `CHARACTER`.

---

## Fase 2 — Análisis sintáctico (`parser_oficial.py`)

La clase `ParserOficial` implementa un parser recursivo descendente. Cada regla gramatical es una función de Python que llama a otras funciones recursivamente siguiendo la estructura del lenguaje.

La precedencia de operadores está codificada en la jerarquía de funciones:

```
parse_expresion
  └── parse_operacion_logica          (and, or)
        └── parse_operacion_comparacion  (equals, greater, less...)
              └── parse_operacion_aritmetica   (plus, minus)
                    └── parse_operacion_multiplicativa  (times, divide, mod)
                          └── parse_operacion_unaria    (not, - unario)
                                └── parse_primary       (literales, identificadores, llamadas)
```

Esto garantiza que `5 plus 3 times 2` se evalúe como `5 + (3 * 2)` y no como `(5 + 3) * 2`.

El resultado es un Árbol de Sintaxis Abstracta (AST) compuesto por los nodos definidos en `ast_nodes.py`. Hay nodos para cada construcción del lenguaje: `DeclaracionNode`, `FuncionNode`, `ClaseNode`, `IfStatementNode`, `CycleStatementNode`, `ForgeNode`, etc.

Una restricción de diseño importante: el parser limita el anidamiento de estructuras de control a **3 niveles**. Si se intenta un cuarto nivel de `when` o `cycle` anidado, el parser lanza un error antes de continuar. Esto se controla con la variable `nesting_depth` que se incrementa y decrementa al entrar y salir de cada bloque.

---

## Fase 3 — Análisis semántico (`semantic.py`)

El `SemanticAnalyzer` recorre el AST usando el patrón visitor y valida que el programa tenga sentido lógico. La herramienta central es la tabla de símbolos, implementada como una cadena de objetos `Scope` anidados.

Cada scope tiene acceso al scope padre, lo que permite que las variables de un contexto exterior sean visibles desde un contexto interior pero no al revés. Cuando se busca un símbolo, se recorre la cadena de scopes hacia arriba hasta encontrarlo o llegar al global.

Las validaciones más importantes que realiza:

- Variables y funciones declaradas antes de usarse
- Constantes (`fixed`) que no se reasignan
- `answer` solo dentro de funciones
- `self` solo dentro de métodos de clase
- `halt` y `skip` solo dentro de ciclos
- Número de argumentos al llamar funciones
- Compatibilidad de tipos en operaciones aritméticas (emite warnings, no errores duros, porque HOOP es dinámicamente tipado)

El analizador también registra todas las funciones built-in en el scope global al inicializarse (`_define_builtins`), incluyendo sus tipos de retorno esperados y si son variádicas, para que las llamadas a `display`, `length`, `input`, etc. pasen la validación sin tratarse como funciones indefinidas.

---

## Fase 4 — Ejecución (`interpreter.py`)

El `HoopInterpreter` es también un visitor del AST. La ejecución es directa: cada nodo sabe cómo ejecutarse a sí mismo cuando el intérprete lo visita.

El estado del programa vive en una cadena de `ExecutionContext`, análoga a los scopes del analizador semántico pero con los valores reales en lugar de solo metadatos. Cuando se llama una función, se crea un nuevo contexto hijo del contexto global (no del contexto actual, lo que previene capturas accidentales de variables locales). Cuando la función termina, el contexto se descarta.

Las funciones retornan valores usando el mecanismo de excepciones de Python: cuando el intérprete encuentra un nodo `ReturnNode` (la instrucción `answer`), lanza una `ReturnException` que sube por la pila hasta que el bloque de llamada a función la captura y extrae el valor. Lo mismo aplica para `LoopBreak` (instrucción `halt`) y `LoopContinue` (instrucción `skip`).

Los objetos se representan con la clase `HoopObject`, que internamente es un diccionario de atributos con el nombre de la clase. Cuando se ejecuta `forge Clase(args)`, el intérprete crea una instancia, inicializa sus atributos con los valores por defecto declarados en la clase, y luego busca y ejecuta el método constructor. `self` se implementa como una variable especial `current_instance` que el intérprete mantiene durante la ejecución de métodos.

---

## El lenguaje HOOP

### Tipos de datos

| HOOP     | Equivalente | Ejemplo               |
|----------|-------------|-----------------------|
| `whole`  | int         | `data x set 42;`      |
| `fract`  | float       | `data pi set 3.14;`   |
| `text`   | string      | `data s set "hola";`  |
| `logic`  | bool        | `data ok set true;`   |
| `char`   | char        | `data c set 'A';`     |
| `grid`   | matrix      | (tipo compuesto)      |
| `chain`  | linked list | (tipo compuesto)      |

### Operadores

Todos los operadores son palabras, no símbolos:

```
plus   minus   times   divide   mod
equals   notequals   greater   less   greatereq   lesseq
and   or   not
set   (asignación)
```

### Control de flujo

```
# Condicional
when puntuacion greater 90 {
    display "Excelente";
} otherwise {
    display "Sigue intentando";
}

# Bucle con rango
cycle i from 1 to 10 {
    display i;
}

# Bucle while
repeat contador less 5 {
    contador set contador plus 1;
}

# Select / case
select opcion {
    case 1 { display "Primera opción"; }
    case 2 { display "Segunda opción"; }
    default { display "Otra opción"; }
}
```

### Funciones y clases

```
action calcularArea(fract base, fract altura) {
    data area set base times altura divide 2;
    answer area;
}

mold Rectangulo {
    fract ancho;
    fract alto;

    action construct(fract a, fract b) {
        self.ancho set a;
        self.alto set b;
    }

    action area() {
        answer self.ancho times self.alto;
    }
}

data rect set forge Rectangulo(10.0, 5.0);
display rect.area();
```

### Manejo de errores

```
attempt {
    data resultado set 10 divide 0;
} rescue error {
    display "Error capturado";
} ensure {
    display "Esto siempre se ejecuta";
}
```

### Funciones built-in

`display`, `input`, `length`, `size`, `type`, `convert`, `abs`, `sqrt`, `pow`, `max`, `min`, `random`, `read`, `write`, `open`, `close`

---

## IDE (HOOP IDLE)

La interfaz gráfica está construida con Tkinter y tiene una estructura similar a VS Code: sidebar con explorador de archivos a la izquierda, editor en el centro y terminal en la parte inferior.

**Resaltado de sintaxis** — implementado en `syntax_highlighter.py` con expresiones regulares aplicadas en tiempo real mientras el usuario escribe. Las categorías tienen colores distintos basados en la paleta One Dark Pro: palabras clave en púrpura, tipos en rojo, operadores-palabra en cyan, built-ins en verde azulado, números en azul y comentarios/strings en verde. Los brackets se colorean por nivel de anidamiento.

**Terminal con pestañas** — la pestaña PROBLEMAS muestra los errores y advertencias de cada fase de compilación con sus ubicaciones. La pestaña OUTPUT muestra la salida del programa al ejecutarse.

**Flujo compilar vs ejecutar** — el botón Compilar corre solo las fases 1, 2 y 3 y reporta errores sin ejecutar. El botón Ejecutar corre las cuatro fases y muestra la salida en el terminal.

**Gestión de archivos** — el sidebar soporta crear archivos `.hoop`, crear carpetas, abrir proyectos desde disco y drag & drop para reorganizar archivos dentro del explorador.

**Snippets de código** — el menú Opciones incluye ejemplos y tests de todas las funcionalidades del lenguaje que se cargan directamente en el editor con un clic.

---

## Estructura del proyecto

```
HOOP/
├── run_gui.py                  # Entry point
├── src/
│   ├── core/
│   │   ├── lexer.py            # Fase 1: AnalizadorLexico
│   │   ├── parser_oficial.py   # Fase 2: ParserOficial (recursivo descendente)
│   │   ├── semantic.py         # Fase 3: SemanticAnalyzer + tabla de símbolos
│   │   ├── interpreter.py      # Fase 4: HoopInterpreter + ExecutionContext
│   │   ├── ast_nodes.py        # Definición de todos los nodos del AST
│   │   └── constants/
│   │       ├── keywords.py     # Palabras reservadas, tipos, operadores
│   │       └── code_snippets.py # Snippets del menú Opciones
│   └── interface/
│       ├── main_gui.py         # Ventana principal
│       ├── colors/colors.py    # Paleta de colores
│       └── components/
│           ├── content_area.py      # Editor + integración con el compilador
│           ├── sidebar.py           # Explorador de archivos
│           ├── header.py            # Barra superior + menús
│           ├── terminal.py          # Terminal con pestañas
│           ├── syntax_highlighter.py # Resaltado de sintaxis
│           ├── line_numbers.py      # Numeración de líneas
│           └── welcome_screen.py    # Pantalla de bienvenida
```

---

## Instalación y uso

```bash
# Clonar el repositorio
git clone <repo-url>
cd HOOP

# Instalar dependencias
pip install pillow

# Lanzar el IDE
python run_gui.py
```

Para ejecutar un archivo HOOP directamente sin el IDE, los módulos del core pueden usarse de forma independiente:

```python
from src.core.lexer import AnalizadorLexico
from src.core.parser_oficial import parse_tokens
from src.core.semantic import analyze_hoop_semantics
from src.core.interpreter import interpret_hoop

with open("programa.hoop") as f:
    codigo = f.read()

lexer = AnalizadorLexico(codigo)
tokens = lexer.analizar()

ast, errores = parse_tokens(tokens)
valido, errores_sem, warnings = analyze_hoop_semantics(ast)
success, error, output = interpret_hoop(ast)

for linea in output:
    print(linea)
```

---

## Limitaciones conocidas

- Herencia entre clases no implementada (cada `mold` es independiente)
- Anidamiento de estructuras de control limitado a 3 niveles por diseño
- Los tipos `grid` y `chain` están declarados pero su comportamiento compuesto no está completamente implementado en el intérprete
- Sin sistema de módulos ni imports entre archivos `.hoop`

---


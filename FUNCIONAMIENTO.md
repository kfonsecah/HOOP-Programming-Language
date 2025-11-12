# HOOP - Human Object Oriented Programming
## Funcionamiento Completo del Sistema

---

## Introducción al Lenguaje HOOP

HOOP es un lenguaje de programación orientado a objetos que hemos diseñado con una sintaxis inspirada en el inglés natural, manteniendo conceptos accesibles para hispanohablantes. El objetivo principal de HOOP es proporcionar una experiencia de programación más legible y comprensible, donde las operaciones se expresan mediante palabras completas en lugar de símbolos matemáticos tradicionales. Por ejemplo, en lugar de usar el símbolo `+` para la suma, en HOOP escribimos `plus`, haciendo el código más explícito y fácil de leer.

El lenguaje implementa características modernas de la programación orientada a objetos, incluyendo clases (que llamamos `mold`), funciones (que llamamos `action`), y un sistema completo de tipos de datos. HOOP soporta tipos primitivos como números enteros (`whole`), números decimales (`real`), cadenas de texto (`text`), valores booleanos (`logic`) y caracteres (`letter`). Además, el lenguaje incluye estructuras de control de flujo como condicionales (`when`/`otherwise`) y bucles (`cycle`), permitiendo crear programas complejos y funcionales.

---

## Arquitectura General del Sistema

Nuestro intérprete de HOOP sigue una arquitectura clásica de compilación en cuatro fases bien definidas, donde cada fase tiene una responsabilidad específica y se ejecuta de manera secuencial. Esta separación de responsabilidades no solo facilita el mantenimiento y la extensión del código, sino que también permite detectar errores de manera más precisa en cada etapa del proceso.

La primera fase es el análisis léxico, donde el código fuente se convierte en tokens. La segunda fase es el análisis sintáctico, donde esos tokens se organizan en un árbol de sintaxis abstracta. La tercera fase es el análisis semántico, donde validamos que el programa tenga sentido lógico y que respete las reglas del lenguaje. Finalmente, la cuarta fase es la ejecución, donde el intérprete recorre el árbol y ejecuta las instrucciones del programa.

El sistema completo está implementado en Python y consta de dos componentes principales: el núcleo del intérprete ubicado en `src/core/` y la interfaz gráfica ubicada en `src/interface/`. El núcleo contiene toda la lógica de compilación y ejecución, mientras que la interfaz proporciona un entorno de desarrollo integrado similar a editores modernos como Visual Studio Code.

---

## Fase 1: Análisis Léxico

El análisis léxico es la primera etapa de nuestro intérprete y su función principal es convertir el código fuente, que es simplemente una secuencia de caracteres, en una lista estructurada de tokens. Un token es la unidad mínima con significado en nuestro lenguaje, similar a las palabras en un idioma natural. Esta fase la implementamos en el archivo `lexer.py` a través de la clase `AnalizadorLexico`.

El proceso de tokenización funciona recorriendo el código carácter por carácter y agrupándolos en unidades significativas. Cuando el analizador encuentra un espacio en blanco o un tabulador, simplemente lo ignora y continúa con el siguiente carácter. Si encuentra el símbolo `#`, reconoce que todo lo que sigue hasta el final de la línea es un comentario y lo descarta. Cuando encuentra comillas dobles, comienza a leer todos los caracteres hasta encontrar las comillas de cierre, formando así un token de tipo STRING.

Para las palabras y identificadores, el lexer lee todos los caracteres alfanuméricos consecutivos y luego consulta en nuestras tablas de palabras reservadas para determinar si es una palabra clave como `mold` o `action`, un tipo de dato como `whole` o `text`, un operador en forma de palabra como `plus` o `set`, o simplemente un identificador que el programador ha definido para una variable o función. Esta clasificación es crucial porque cada tipo de token tiene un significado diferente en las fases posteriores.

Los números se procesan de manera especial para distinguir entre enteros y decimales. El lexer acumula todos los dígitos consecutivos y, si encuentra un punto decimal, continúa leyendo más dígitos para formar un número real. Los delimitadores como paréntesis, llaves y punto y coma se reconocen inmediatamente como tokens individuales porque tienen un significado sintáctico importante.

Una característica importante de nuestro analizador léxico es que mantiene un registro preciso de la posición de cada token en el código fuente, guardando el número de línea y columna. Esta información es fundamental para proporcionar mensajes de error útiles al usuario, indicándole exactamente dónde se encuentra el problema en su código.

---

## Fase 2: Análisis Sintáctico

Una vez que tenemos la lista de tokens, el análisis sintáctico se encarga de verificar que estos tokens estén organizados según las reglas gramaticales de HOOP y construir una representación estructurada del programa llamada Árbol de Sintaxis Abstracta o AST por sus siglas en inglés. Esta fase está implementada en `parser_oficial.py` utilizando la técnica de análisis sintáctico recursivo descendente.

El parser funciona como un conjunto de funciones recursivas donde cada función es responsable de reconocer una construcción específica del lenguaje. Por ejemplo, tenemos una función para reconocer declaraciones de variables, otra para reconocer funciones, otra para condicionales, y así sucesivamente. Estas funciones se llaman entre sí de manera recursiva siguiendo la estructura jerárquica de la gramática del lenguaje.

Cuando el parser comienza, lee el primer token y decide qué tipo de declaración viene a continuación. Si el token es la palabra clave `data`, sabe que debe procesar una declaración de variable y espera encontrar después un identificador, seguido de la palabra `set`, luego una expresión y finalmente un punto y coma. Si alguno de estos elementos falta o está en el orden incorrecto, el parser genera un error sintáctico detallado indicando qué se esperaba y qué se encontró.

Para las expresiones aritméticas y lógicas, el parser implementa la precedencia de operadores mediante una jerarquía de funciones. Las operaciones lógicas como `and` y `or` tienen la precedencia más baja, luego vienen las comparaciones como `equals` y `greater`, después las sumas y restas, luego las multiplicaciones y divisiones, y finalmente las operaciones unarias y los valores primarios. Esta estructura garantiza que una expresión como `5 plus 3 times 2` se evalúe correctamente como `5 + (3 * 2)` y no como `(5 + 3) * 2`.

El resultado del análisis sintáctico es un árbol donde cada nodo representa una construcción del lenguaje. Por ejemplo, un nodo `DeclaracionNode` contiene el nombre de la variable y un nodo hijo que representa su valor inicial. Un nodo `FuncionNode` contiene el nombre de la función, una lista de parámetros y una lista de nodos que representan las instrucciones del cuerpo de la función. Este árbol es mucho más fácil de procesar que la lista plana de tokens porque captura explícitamente la estructura y las relaciones entre las diferentes partes del programa.

Nuestro parser también implementa una restricción importante: limita el anidamiento de estructuras de control a un máximo de tres niveles. Esto significa que no puedes tener un `when` dentro de otro `when` dentro de otro `when` dentro de otro `when`. Esta restricción ayuda a mantener el código legible y evita programas excesivamente complejos.

---

## Fase 3: Análisis Semántico

Después de construir el árbol de sintaxis abstracta, necesitamos verificar que el programa tenga sentido desde el punto de vista lógico y semántico. Esta es la responsabilidad del analizador semántico implementado en `semantic.py`. Mientras que el parser verifica la estructura gramatical, el analizador semántico verifica las reglas de significado del lenguaje.

La herramienta principal del análisis semántico es la tabla de símbolos, una estructura de datos que mantiene un registro de todas las variables, funciones y clases declaradas en el programa, junto con información sobre sus tipos y ámbitos. Cuando el analizador encuentra una declaración de variable, agrega una entrada en la tabla de símbolos con el nombre de la variable y su tipo inferido. Cuando encuentra el uso de una variable, consulta la tabla para verificar que esa variable haya sido declarada previamente.

El sistema de ámbitos es fundamental en el análisis semántico. Cada vez que entramos en un nuevo bloque de código como el cuerpo de una función o un bucle, creamos un nuevo ámbito que puede tener sus propias variables locales. Estos ámbitos están organizados jerárquicamente, donde un ámbito hijo puede acceder a las variables de su ámbito padre, pero no al revés. Cuando buscamos una variable, primero miramos en el ámbito actual, y si no la encontramos, buscamos en el ámbito padre, y así sucesivamente hasta llegar al ámbito global.

Una de las validaciones más importantes es la verificación de tipos. Aunque HOOP es dinámicamente tipado en tiempo de ejecución, el analizador semántico intenta detectar errores de tipo obvios en tiempo de compilación. Por ejemplo, si intentas sumar un número con una cadena de texto, el analizador detectará esta incompatibilidad y generará un error antes de ejecutar el programa. También verifica que las operaciones sean apropiadas para los tipos involucrados, por ejemplo, que no intentes llamar a un método sobre un tipo primitivo que no lo soporta.

El analizador semántico también verifica reglas específicas del lenguaje, como que la palabra clave `answer` (equivalente a return) solo se use dentro de funciones, que `self` solo se use dentro de métodos de clase, que las funciones se llamen con el número correcto de argumentos, y que los atributos que se acceden en una clase realmente existan. Todas estas validaciones ayudan a detectar errores comunes antes de la ejecución.

Además de errores, el analizador semántico también puede generar advertencias para situaciones sospechosas pero no necesariamente incorrectas. Por ejemplo, si declaras una variable pero nunca la usas, o si detecta una posible división por cero con un literal, generará una advertencia para alertar al programador sin detener la compilación.

---

## Fase 4: Interpretación y Ejecución

Una vez que el programa ha pasado todas las validaciones semánticas, procedemos a la fase de ejecución implementada en `interpreter.py`. El intérprete recorre el árbol de sintaxis abstracta y ejecuta cada nodo según su tipo, manteniendo un estado de ejecución que incluye las variables definidas, las funciones disponibles y las clases registradas.

El intérprete mantiene una estructura de entornos similar a la tabla de símbolos del analizador semántico, pero en lugar de guardar solo información sobre los tipos, guarda los valores reales de las variables durante la ejecución. Cuando el intérprete encuentra un nodo de declaración, evalúa la expresión del lado derecho para obtener un valor y luego almacena ese valor en el entorno actual asociado con el nombre de la variable.

Para evaluar expresiones, el intérprete utiliza un enfoque recursivo donde cada tipo de expresión sabe cómo evaluarse a sí misma. Un literal simplemente devuelve su valor constante. Una referencia a una variable busca su valor en el entorno. Una operación binaria evalúa recursivamente sus operandos izquierdo y derecho, luego aplica el operador correspondiente. Por ejemplo, para una operación `plus`, el intérprete evalúa ambos lados y luego suma los valores resultantes.

Las funciones se ejecutan creando un nuevo entorno que es hijo del entorno global. Los parámetros de la función se definen como variables locales en este nuevo entorno con los valores de los argumentos pasados. Luego el intérprete ejecuta cada instrucción del cuerpo de la función en este entorno. Si encuentra una instrucción `answer`, captura el valor mediante una excepción especial y lo devuelve como resultado de la función. Una vez terminada la ejecución, el entorno de la función se descarta y volvemos al entorno anterior.

Los objetos y clases siguen un modelo similar. Cuando ejecutamos una instrucción `forge` para crear una nueva instancia, el intérprete busca la definición de la clase, crea un nuevo objeto con sus atributos inicializados según los argumentos proporcionados, y devuelve una referencia a ese objeto. Cuando se llama a un método sobre un objeto, el intérprete crea un entorno donde `self` está vinculado al objeto actual, permitiendo que el método acceda y modifique los atributos del objeto.

El intérprete también implementa las funciones built-in de HOOP como `display` para mostrar valores, `length` para obtener la longitud de cadenas, `type` para obtener el tipo de un valor, e `input` para leer entrada del usuario. Estas funciones están implementadas directamente en Python y se exponen al código HOOP como si fueran funciones normales del lenguaje.

Durante la ejecución, el intérprete puede encontrar errores de runtime como divisiones por cero, acceso a atributos inexistentes, o llamadas recursivas infinitas. Cuando ocurre un error de este tipo, el intérprete detiene la ejecución y genera un mensaje de error descriptivo indicando qué salió mal y dónde ocurrió el problema.

---

## Interfaz Gráfica

Para hacer más accesible el uso de HOOP, hemos desarrollado una interfaz gráfica completa utilizando Tkinter que proporciona un entorno de desarrollo integrado. La GUI está organizada en varios componentes que trabajan juntos para ofrecer una experiencia similar a editores modernos como Visual Studio Code.

El componente principal es el área de contenido donde el usuario escribe su código HOOP. Este editor incluye resaltado de sintaxis en tiempo real que colorea diferentes elementos del código según su tipo: las palabras clave aparecen en púrpura, los números en azul, las cadenas y comentarios en verde, los tipos en rojo, y los operadores en cyan. Este resaltado visual ayuda a los programadores a leer y entender el código más fácilmente.

A la izquierda del editor tenemos una barra lateral que funciona como explorador de archivos, mostrando la estructura de carpetas y archivos del proyecto en un formato de árbol. Los usuarios pueden crear nuevos archivos y carpetas, abrir archivos existentes con un doble clic, y organizar su proyecto de manera intuitiva. Los archivos HOOP se identifican con un icono especial para distinguirlos de otros tipos de archivos.

En la parte inferior de la ventana se encuentra el terminal, que tiene dos pestañas: "PROBLEMAS" y "OUTPUT". La pestaña de problemas muestra los errores y advertencias encontrados durante la compilación, con información detallada sobre la ubicación y naturaleza de cada problema. La pestaña de output muestra la salida generada por el programa durante su ejecución, incluyendo los valores impresos con la función `display`.

La barra superior contiene el menú principal con opciones para crear nuevos proyectos, cargar proyectos existentes, acceder a ejemplos de código, ejecutar los tests del sistema, y configurar opciones. También incluimos varios ejemplos de código HOOP pre-escritos que los usuarios pueden cargar con un solo clic para aprender cómo funciona el lenguaje.

Cuando el usuario hace clic en el botón "Compilar", la GUI toma el código del editor y lo pasa por las tres primeras fases: análisis léxico, sintáctico y semántico. Si se encuentran errores en cualquiera de estas fases, se detiene el proceso y se muestran los errores en la pestaña de problemas. Si todo es correcto, se muestra un mensaje de éxito. El botón "Ejecutar" hace lo mismo pero además ejecuta el programa y muestra su salida en la pestaña output.

La integración entre la GUI y el intérprete está diseñada para ser fluida y responsiva. Cuando ocurre un error, la GUI automáticamente cambia a la pestaña de problemas para que el usuario vea inmediatamente qué salió mal. Los mensajes de error incluyen números de línea, lo que permite al usuario localizar rápidamente el problema en su código.

---

## Ejemplos de Uso

Para ilustrar cómo funciona HOOP en la práctica, consideremos algunos ejemplos concretos. El ejemplo más simple es la declaración y uso de variables. Si escribimos `data x set 10;` seguido de `display x;`, el lexer generará tokens para la palabra clave `data`, el identificador `x`, el operador `set`, el número `10` y el delimitador `;`. El parser construirá un nodo de declaración con nombre "x" y valor 10, y un nodo de llamada a función para `display`. El analizador semántico verificará que no haya otra variable llamada "x" ya declarada y registrará su tipo como `whole`. Finalmente, el intérprete almacenará el valor 10 en la variable x y luego lo imprimirá en pantalla.

Un ejemplo más complejo involucra funciones. Si definimos `action suma(whole a, whole b) { answer a plus b; }` y luego llamamos `data resultado set suma(5, 3);`, el proceso es más elaborado. El parser reconocerá la definición de función y creará un nodo con el nombre "suma", dos parámetros de tipo `whole`, y un cuerpo que contiene una instrucción `answer`. El analizador semántico verificará que los tipos de los parámetros sean válidos y registrará la función en su tabla de símbolos. Cuando se ejecuta la llamada a `suma(5, 3)`, el intérprete crea un nuevo entorno, asigna 5 a "a" y 3 a "b", ejecuta el cuerpo que suma ambos valores, captura el resultado mediante la instrucción `answer`, y devuelve 8 que se almacena en la variable "resultado".

Las clases demuestran la orientación a objetos de HOOP. Si definimos una clase `mold Persona { text nombre; whole edad; }` y luego creamos una instancia con `data p set forge Persona("Juan", 25);`, el intérprete crea un objeto con dos atributos: nombre con el valor "Juan" y edad con el valor 25. Podemos acceder a estos atributos con `p.nombre` o `p.edad`, y el intérprete buscará el atributo correspondiente en el objeto y devolverá su valor.

Nuestro ejemplo estrella es la calculadora completa incluida en `calculadora_ejemplo.hoop`, que demuestra prácticamente todas las características del lenguaje: variables, funciones, condicionales, bucles, entrada de usuario, y operaciones aritméticas complejas. Este programa funciona correctamente después de pasar por todas las fases de nuestro intérprete.

---

## Testing y Validación

Para asegurar que nuestro intérprete funciona correctamente, hemos desarrollado una suite completa de tests end-to-end en `test_end_to_end.py`. Esta suite contiene 11 tests que cubren todos los aspectos del lenguaje, desde las características más básicas hasta los casos más complejos.

Los primeros tests validan funcionalidades básicas como declaración de variables, operaciones aritméticas, y estructuras de control simples. Los tests intermedios verifican características más avanzadas como funciones con múltiples parámetros, recursión, y el uso de funciones built-in. Los tests finales se enfocan en la programación orientada a objetos con clases, métodos y el uso de `self`.

Además de tests de funcionalidad correcta, también tenemos tests que verifican que el intérprete detecta y reporta errores apropiadamente. Estos tests intentan compilar programas con errores léxicos, sintácticos y semánticos deliberados, y verifican que cada fase del compilador genere los mensajes de error correctos.

El resultado de ejecutar la suite completa muestra 11 tests exitosos de 11 totales, lo que nos da una tasa de éxito del 100%. Esto nos da confianza en que nuestro intérprete maneja correctamente tanto los casos de uso normales como los casos excepcionales.

---

## Preguntas Frecuentes para la Defensa

### ¿Por qué decidieron crear un nuevo lenguaje en lugar de usar uno existente?

El objetivo de este proyecto es educativo. Crear HOOP desde cero nos permitió entender profundamente cómo funcionan los lenguajes de programación por dentro. Aprendimos sobre tokenización, parsing, análisis semántico y ejecución de código. Además, diseñar la sintaxis de HOOP con operadores en palabras completas nos permitió explorar cómo las decisiones de diseño de un lenguaje afectan su legibilidad y usabilidad.

### ¿Por qué eligieron Python para implementar el intérprete?

Python es ideal para este tipo de proyecto porque es un lenguaje de alto nivel con estructuras de datos potentes y manejo automático de memoria. Esto nos permitió concentrarnos en la lógica del intérprete sin preocuparnos por detalles de bajo nivel. Python también tiene excelentes librerías para construir interfaces gráficas como Tkinter, que usamos para nuestra GUI. Además, la sintaxis clara de Python hace que el código del intérprete sea fácil de entender y mantener.

### ¿Cómo manejan los errores en diferentes fases?

Cada fase del intérprete tiene su propio mecanismo de manejo de errores. El lexer detecta caracteres inválidos y literales malformados. El parser detecta errores de sintaxis como paréntesis sin cerrar o palabras clave en lugares incorrectos. El analizador semántico detecta errores lógicos como variables no declaradas o incompatibilidades de tipos. El intérprete detecta errores de runtime como divisiones por cero o acceso a atributos inexistentes. En cada caso, generamos mensajes de error descriptivos con información sobre la ubicación del problema.

### ¿Qué es la tabla de símbolos y por qué es importante?

La tabla de símbolos es una estructura de datos que mantiene información sobre todas las variables, funciones y clases declaradas en el programa. Durante el análisis semántico, la usamos para verificar que las variables existan antes de usarlas y para validar tipos. Durante la ejecución, una estructura similar almacena los valores reales de las variables. La tabla de símbolos soporta ámbitos anidados, lo que permite tener variables locales en funciones que no interfieren con variables globales del mismo nombre.

### ¿Cómo funciona el resaltado de sintaxis en la GUI?

El resaltado de sintaxis se implementa usando expresiones regulares que identifican patrones en el código. Tenemos patrones para palabras clave, números, cadenas, comentarios, y otros elementos del lenguaje. Cuando el usuario escribe en el editor, aplicamos estas expresiones regulares para identificar qué es cada palabra o símbolo, y luego aplicamos colores diferentes usando las capacidades de formato del widget Text de Tkinter. Este proceso se ejecuta en tiempo real mientras el usuario escribe.

### ¿Por qué limitaron el anidamiento a 3 niveles?

Esta es una decisión de diseño para mantener el código HOOP legible y simple. En nuestra experiencia, cuando tienes más de 3 niveles de if o bucles anidados, el código se vuelve difícil de entender y mantener. Esta restricción fuerza a los programadores a estructurar su código de manera más clara, posiblemente extrayendo funcionalidades a funciones separadas en lugar de agrupar todo en un bloque profundamente anidado.

### ¿Cómo implementaron la recursión?

La recursión funciona naturalmente en nuestro intérprete porque cada llamada a función crea su propio entorno con sus propias variables locales. Cuando una función se llama a sí misma recursivamente, se crea un nuevo entorno completamente independiente del entorno de la llamada anterior. La pila de llamadas de Python maneja automáticamente el seguimiento de todas estas llamadas recursivas. Cuando una llamada recursiva termina y devuelve un valor con `answer`, ese valor se propaga hacia arriba a través de la cadena de llamadas.

### ¿Qué diferencia hay entre el análisis sintáctico y semántico?

El análisis sintáctico verifica la estructura gramatical del código, es decir, que los tokens estén en el orden correcto según las reglas del lenguaje. Por ejemplo, verifica que después de `data` venga un identificador, luego `set`, luego una expresión. El análisis semántico verifica el significado lógico, como que las variables existan antes de usarlas, que los tipos sean compatibles en las operaciones, y que se respeten reglas como usar `answer` solo dentro de funciones. Un programa puede ser sintácticamente correcto pero semánticamente inválido.

### ¿Por qué usaron un parser recursivo descendente?

El parser recursivo descendente es conceptualmente simple y se alinea naturalmente con la estructura recursiva de la gramática. Cada regla gramatical se convierte en una función, y las referencias a otras reglas se convierten en llamadas a otras funciones. Esto hace que el código del parser sea fácil de entender y mantener. Además, esta técnica permite generar mensajes de error contextuales muy específicos porque en cada punto sabemos exactamente qué estábamos esperando encontrar.

### ¿Cómo se diferencian de otros lenguajes?

HOOP se diferencia principalmente en su sintaxis con operadores en palabras. Mientras que la mayoría de los lenguajes usan símbolos como `+`, `-`, `*`, `/`, HOOP usa `plus`, `minus`, `times`, `divide`. Esto hace el código más explícito y legible, aunque más verboso. También usamos palabras clave únicas como `mold` para clases, `action` para funciones, y `forge` para crear instancias. Estas elecciones hacen que HOOP sea distintivo y educativo para entender cómo las decisiones de diseño de sintaxis afectan la experiencia del programador.

### ¿Qué mejoras futuras considerarían?

Entre las mejoras futuras más importantes estaríamos la implementación de herencia y polimorfismo para hacer el sistema de objetos más completo. También sería útil agregar manejo de excepciones con algo similar a try/catch. Un sistema de módulos e imports permitiría organizar programas grandes en múltiples archivos. Optimizaciones del intérprete como compilación just-in-time podrían mejorar el rendimiento. En la GUI, características como auto-completado y depuración paso a paso serían muy útiles para los usuarios.

### ¿Cómo aseguran que el intérprete es correcto?

Nuestra principal garantía de correctitud es la suite de 11 tests end-to-end que cubren todas las características del lenguaje. Cada test ejecuta un programa HOOP completo y verifica que la salida sea la esperada. También tenemos tests específicos para la detección de errores en cada fase. Además, hemos probado el sistema con el ejemplo de la calculadora, que es un programa real y funcional. El hecho de que todos los tests pasen consistentemente nos da confianza en la correctitud del intérprete.

---

## Conclusión

HOOP representa una implementación completa de un lenguaje de programación orientado a objetos, desde el diseño de la sintaxis hasta la ejecución de programas reales. El proyecto demuestra comprensión profunda de los conceptos fundamentales de compiladores e intérpretes, incluyendo análisis léxico, sintáctico y semántico, así como la ejecución mediante interpretación de árboles de sintaxis abstracta.

La arquitectura en cuatro fases claramente separadas hace que el sistema sea mantenible y extensible. La interfaz gráfica proporciona una experiencia de usuario moderna y accesible. Los tests exhaustivos garantizan que el sistema funciona correctamente. En conjunto, HOOP es un proyecto académico robusto que cumple todos sus objetivos educativos y técnicos.

# HOOP - Human Object Oriented Programming

**HOOP** es un lenguaje de programación educativo desarrollado en Python, diseñado para enseñar conceptos fundamentales de programación y paradigmas orientados a objetos de manera accesible y comprensible.

## 🎯 Objetivos del Proyecto

- Crear un lenguaje de programación simple y educativo
- Demostrar el funcionamiento de un compilador/intérprete completo
- Enseñar conceptos de análisis léxico, sintáctico, semántico y ejecución
- Proporcionar una herramienta práctica para aprender programación

## 🏗️ Arquitectura del Proyecto

El proyecto está estructurado en cuatro componentes principales:

```
📁 src/core/
├── lexer.py        # Análisis Léxico: Código → Tokens
├── parser.py       # Análisis Sintáctico: Tokens → AST
├── semantic.py     # Análisis Semántico: Validación de reglas
└── interpreter.py  # Intérprete: Ejecución del código
```

### Flujo de Ejecución

```
Código HOOP → Lexer → Parser → Semantic → Interpreter → Resultado
     ↓           ↓        ↓         ↓          ↓
   "x = 5"   [Tokens]   [AST]   [Validado]  [Ejecutado]
```

## 🚀 Características del Lenguaje

### Palabras Reservadas
```python
def, class, if, else, elif, for, while, cycle
show, input, return, break, continue
and, or, not, in, True, False, None
```

### Tipos de Datos Soportados
- **Enteros**: `42`, `-10`
- **Flotantes**: `3.14`, `-2.5`
- **Cadenas**: `"Hola"`, `'Mundo'`
- **Booleanos**: `True`, `False`
- **Listas**: `[1, 2, 3]`, `["a", "b", "c"]`
- **Nulo**: `None`

### Sintaxis Básica

#### Variables y Asignaciones
```python
nombre = "HOOP"
edad = 25
activo = True
numeros = [1, 2, 3, 4, 5]
```

#### Funciones
```python
def saludar(nombre):
    show("Hola, " + nombre + "!")

def sumar(a, b):
    return a + b

resultado = sumar(5, 3)
saludar("Mundo")
```

#### Control de Flujo
```python
# Condicionales
if edad >= 18:
    show("Eres mayor de edad")
else:
    show("Eres menor de edad")

# Bucles
for numero in numeros:
    show(numero * 2)

contador = 0
while contador < 5:
    show(contador)
    contador = contador + 1
```

### Funciones Built-in
- `show(valor)`: Imprime un valor en la consola
- `input(prompt)`: Solicita entrada del usuario
- `len(objeto)`: Devuelve la longitud de cadenas o listas
- `type(objeto)`: Devuelve el tipo de un objeto

## 📦 Instalación y Uso

### Requisitos
- Python 3.7 o superior
- Dependencias listadas en `requirements.txt`

### Instalación
```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd HOOP

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución

#### Modo Interactivo
```bash
cd src
python main.py
```

#### Ejecutar Archivo
```bash
cd src
python main.py archivo.hoop
```

#### Ejemplo de Uso
```bash
# Crear un archivo ejemplo.hoop
echo 'show("¡Hola desde HOOP!")' > ejemplo.hoop

# Ejecutarlo
python main.py ejemplo.hoop
```

## 🧪 Ejemplos de Código

### Ejemplo 1: Hola Mundo
```python
show("¡Hola, Mundo desde HOOP!")
```

### Ejemplo 2: Calculadora Simple
```python
def calcular_area(ancho, alto):
    return ancho * alto

def main():
    ancho = 10
    alto = 5
    area = calcular_area(ancho, alto)
    show("El área es: " + str(area))

main()
```

### Ejemplo 3: Procesamiento de Listas
```python
def procesar_numeros(lista):
    suma = 0
    for num in lista:
        suma = suma + num
    return suma

numeros = [1, 2, 3, 4, 5]
total = procesar_numeros(numeros)
show("La suma total es: " + str(total))
```

## 🔧 Estructura del Código

### Lexer (Análisis Léxico)
- **Ubicación**: `src/core/lexer.py`
- **Función**: Convierte código fuente en tokens
- **Tokens soportados**: Identificadores, números, strings, operadores, palabras reservadas

### Parser (Análisis Sintáctico)
- **Ubicación**: `src/core/parser.py`
- **Función**: Convierte tokens en un Árbol de Sintaxis Abstracta (AST)
- **Técnica**: Parser recursivo descendente
- **Maneja**: Precedencia de operadores, estructura de control

### Semantic Analyzer (Análisis Semántico)
- **Ubicación**: `src/core/semantic.py`
- **Función**: Valida reglas semánticas del lenguaje
- **Verifica**: Tipos de datos, variables declaradas, ámbitos, compatibilidad

### Interpreter (Intérprete)
- **Ubicación**: `src/core/interpreter.py`
- **Función**: Ejecuta el código validado
- **Características**: Entornos de ejecución, funciones built-in, manejo de errores

## 🧩 Extensibilidad

El proyecto está diseñado para ser fácilmente extensible:

### Agregar Nuevas Palabras Reservadas
1. Actualizar `TokenType` en `lexer.py`
2. Agregar a `keywords` en `HoopLexer`
3. Implementar parsing en `parser.py`
4. Agregar análisis semántico en `semantic.py`
5. Implementar ejecución en `interpreter.py`

### Agregar Nuevos Tipos de Datos
1. Extender `HoopType` en `semantic.py`
2. Actualizar validaciones de tipos
3. Implementar operaciones en `interpreter.py`

### Agregar Funciones Built-in
1. Implementar función en `_define_builtin_functions()` del intérprete
2. Registrar en el entorno global

## 🐛 Depuración y Desarrollo

### Modo Debug
El archivo `main.py` incluye un modo de análisis paso a paso que muestra:
- Tokens generados por el lexer
- AST construido por el parser
- Resultados del análisis semántico
- Ejecución del intérprete

### Pruebas
```bash
# Ejecutar ejemplos incluidos
python main.py
# Seleccionar opción 3 para ejemplos predefinidos

# Modo interactivo para pruebas rápidas
python main.py
# Seleccionar opción 2 para modo interactivo
```

## 📚 Estado del Proyecto

### ✅ Implementado
- Estructura base del lexer con tokens principales
- Framework del parser con AST
- Análisis semántico básico con tabla de símbolos
- Intérprete con ejecución de expresiones básicas
- Sistema de archivos principal para pruebas

### 🚧 En Desarrollo
- Implementación completa del lexer (tokenización)
- Implementación completa del parser (todas las estructuras)
- Análisis semántico completo
- Ejecución completa del intérprete
- Manejo de clases y objetos
- Sistema de módulos/importaciones

### 🎯 Futuras Mejoras
- Optimizaciones de rendimiento
- Mejor manejo de errores con información de ubicación
- Herramientas de desarrollo (debugger, profiler)
- Documentación interactiva
- Extensiones del lenguaje

## 🤝 Contribución

Este es un proyecto educativo. Las contribuciones son bienvenidas:

1. Fork del repositorio
2. Crear una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit de tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia especificada en el archivo `LICENSE`.

## 👥 Autores

- Proyecto desarrollado para el curso de Paradigmas de Programación
- Universidad: [Nombre de la Universidad]
- Curso: Paradigmas de Programación

## 📞 Contacto

Para preguntas o sugerencias sobre el proyecto HOOP, puedes contactarnos a través de los issues del repositorio.

---

**HOOP** - Haciendo la programación más humana y accesible 🚀
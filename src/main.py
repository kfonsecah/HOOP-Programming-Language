"""
Archivo principal para pruebas del lenguaje HOOP
===============================================

Este archivo permite probar el compilador/intérprete completo de HOOP,
pasando código por todas las fases: lexer → parser → semantic → interpreter

Uso:
    python main.py [archivo.hoop]
    python main.py  # Modo interactivo
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Agregar el directorio core al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.lexer import AnalizadorLexico, analizar_codigo_hoop
from core.parser_oficial import parse_tokens, parse_hoop_oficial
from core.semantic import HoopSemanticAnalyzer, analyze_hoop_semantics
from core.interpreter import HoopInterpreter, execute_hoop_code, HoopRuntimeError

def print_banner():
    """Imprime el banner del intérprete HOOP"""
    print("=" * 60)
    print("  HOOP - Human Object Oriented Programming")
    print("  Intérprete de pruebas v0.1")
    print("=" * 60)
    print()

def run_file(file_path: str):
    """
    Ejecuta un archivo .hoop
    
    Args:
        file_path: Ruta al archivo HOOP
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print(f"Ejecutando archivo: {file_path}")
        print("-" * 40)
        
        # Ejecutar código completo
        output = execute_hoop_code(code)
        print(output)
        
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo '{file_path}'")
    except Exception as e:
        print(f"Error al ejecutar el archivo: {e}")

def analyze_code_step_by_step(code: str):
    """
    Analiza código paso a paso mostrando cada fase
    
    Args:
        code: Código fuente HOOP
    """
    print("📝 Analizando código paso a paso...")
    print("=" * 50)
    
    try:
        # FASE 1: Análisis Léxico
        print("🔤 FASE 1: Análisis Léxico")
        print("-" * 30)
        
        lexer = HoopLexer()
        tokens = lexer.tokenize(code)
        
        print(f"✓ Tokens generados: {len(tokens)}")
        
        # Mostrar algunos tokens (máximo 10)
        print("Primeros tokens:")
        for i, token in enumerate(tokens[:10]):
            print(f"  {i+1:2d}. {token.type.value:15} '{token.value}' (línea {token.line})")
        
        if len(tokens) > 10:
            print(f"  ... y {len(tokens) - 10} tokens más")
        
        print()
        
        # FASE 2: Análisis Sintáctico
        print("🌳 FASE 2: Análisis Sintáctico")
        print("-" * 30)
        
        parser = HoopParser()
        ast = parser.parse(tokens)
        
        print(f"✓ AST generado con {len(ast.statements)} declaraciones")
        
        # Mostrar tipos de declaraciones
        stmt_types = {}
        for stmt in ast.statements:
            stmt_type = type(stmt).__name__
            stmt_types[stmt_type] = stmt_types.get(stmt_type, 0) + 1
        
        print("Declaraciones encontradas:")
        for stmt_type, count in stmt_types.items():
            print(f"  - {stmt_type}: {count}")
        
        print()
        
        # FASE 3: Análisis Semántico
        print("🔍 FASE 3: Análisis Semántico")
        print("-" * 30)
        
        is_valid, errors, warnings = analyze_hoop_semantics(ast)
        
        if is_valid:
            print("✓ Análisis semántico exitoso")
        else:
            print("✗ Errores semánticos encontrados:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("⚠️  Advertencias:")
            for warning in warnings:
                print(f"  - {warning}")
        
        print()
        
        # FASE 4: Ejecución (solo si no hay errores)
        if is_valid:
            print("🚀 FASE 4: Ejecución")
            print("-" * 30)
            
            interpreter = HoopInterpreter()
            interpreter.interpret(ast)
            print("✓ Ejecución completada")
        else:
            print("❌ No se puede ejecutar debido a errores semánticos")
        
    except ParseError as e:
        print(f"❌ Error de sintaxis: {e}")
    except HoopRuntimeError as e:
        print(f"❌ Error de ejecución: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def interactive_mode():
    """Modo interactivo para probar código HOOP"""
    print("🔄 Modo Interactivo HOOP")
    print("Escribe código HOOP línea por línea.")
    print("Comandos especiales:")
    print("  :run    - Ejecutar código acumulado")
    print("  :clear  - Limpiar código")
    print("  :debug  - Analizar paso a paso")
    print("  :quit   - Salir")
    print("-" * 40)
    
    code_lines = []
    
    while True:
        try:
            if not code_lines:
                prompt = "hoop> "
            else:
                prompt = "...   "
            
            line = input(prompt).strip()
            
            # Comandos especiales
            if line == ":quit":
                print("¡Hasta luego!")
                break
            elif line == ":clear":
                code_lines.clear()
                print("Código limpiado.")
                continue
            elif line == ":run":
                if code_lines:
                    code = "\n".join(code_lines)
                    print("\n" + "="*40)
                    print("EJECUTANDO:")
                    print("-"*40)
                    try:
                        output = execute_hoop_code(code)
                        print(output)
                    except Exception as e:
                        print(f"Error: {e}")
                    print("="*40)
                else:
                    print("No hay código para ejecutar.")
                continue
            elif line == ":debug":
                if code_lines:
                    code = "\n".join(code_lines)
                    print("\n" + "="*50)
                    analyze_code_step_by_step(code)
                    print("="*50)
                else:
                    print("No hay código para analizar.")
                continue
            
            # Línea de código normal
            code_lines.append(line)
            
        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break
        except EOFError:
            print("\n¡Hasta luego!")
            break

def run_examples():
    """Ejecuta ejemplos de código HOOP predefinidos"""
    examples = {
        "1": {
            "name": "Hola Mundo",
            "code": '''
# Ejemplo básico de Hola Mundo
show("¡Hola, Mundo desde HOOP!")
'''
        },
        "2": {
            "name": "Funciones y Variables",
            "code": '''
# Ejemplo con funciones y variables
def greet(name):
    show("Hola, " + name + "!")

def add(a, b):
    return a + b

# Uso de las funciones
greet("Usuario")
result = add(5, 3)
show("5 + 3 = " + str(result))
'''
        },
        "3": {
            "name": "Control de Flujo",
            "code": '''
# Ejemplo con if y bucles
x = 10

if x > 5:
    show("x es mayor que 5")
else:
    show("x es menor o igual que 5")

# Bucle while
counter = 0
while counter < 3:
    show("Contador: " + str(counter))
    counter = counter + 1
'''
        },
        "4": {
            "name": "Listas y For",
            "code": '''
# Ejemplo con listas y bucle for
numbers = [1, 2, 3, 4, 5]
show("Lista de números:")

for num in numbers:
    result = num * 2
    show("  " + str(num) + " * 2 = " + str(result))
'''
        }
    }
    
    print("📚 Ejemplos de código HOOP:")
    print("-" * 30)
    
    for key, example in examples.items():
        print(f"{key}. {example['name']}")
    
    print("0. Volver al menú principal")
    print()
    
    choice = input("Selecciona un ejemplo (0-4): ").strip()
    
    if choice == "0":
        return
    elif choice in examples:
        example = examples[choice]
        print(f"\n🎯 Ejecutando: {example['name']}")
        print("=" * 50)
        print("CÓDIGO:")
        print(example['code'])
        print("=" * 50)
        print("SALIDA:")
        
        try:
            output = execute_hoop_code(example['code'])
            print(output)
        except Exception as e:
            print(f"Error: {e}")
        
        print("=" * 50)
    else:
        print("Opción no válida.")

def main():
    """Función principal"""
    print_banner()
    
    # Si se proporciona un archivo como argumento
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        run_file(file_path)
        return
    
    # Menú interactivo
    while True:
        print("Opciones:")
        print("1. Ejecutar archivo .hoop")
        print("2. Modo interactivo")
        print("3. Ejecutar ejemplos")
        print("4. Analizar código paso a paso")
        print("5. Salir")
        print()
        
        choice = input("Selecciona una opción (1-5): ").strip()
        
        if choice == "1":
            file_path = input("Ruta del archivo .hoop: ").strip()
            run_file(file_path)
            print()
            
        elif choice == "2":
            interactive_mode()
            print()
            
        elif choice == "3":
            run_examples()
            print()
            
        elif choice == "4":
            print("Ingresa el código HOOP (termina con una línea vacía):")
            code_lines = []
            while True:
                line = input()
                if line.strip() == "":
                    break
                code_lines.append(line)
            
            if code_lines:
                code = "\n".join(code_lines)
                analyze_code_step_by_step(code)
            print()
            
        elif choice == "5":
            print("¡Hasta luego!")
            break
            
        else:
            print("Opción no válida.\n")

if __name__ == "__main__":
    main()
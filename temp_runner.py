#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, r'C:\Users\Kendall Fonseca\Desktop\U\Paradigmas\HOOP\src')

from core.lexer import AnalizadorLexico
from core.parser_oficial import parse_tokens
from core.semantic import analyze_hoop_semantics
from core.interpreter import interpret_hoop

print("=" * 50)
print("  EJECUTANDO CODIGO HOOP")
print("=" * 50)
print()

# Leer código
with open(r'C:\Users\KENDAL~1\AppData\Local\Temp\tmpxvisqhi4.hoop', 'r', encoding='utf-8') as f:
    code = f.read()

try:
    # FASE 1: LÉXICO
    print("[1/4] Analisis lexico...")
    analizador = AnalizadorLexico(code)
    tokens = analizador.analizar()
    errores_lex = analizador.obtener_errores()
    
    if errores_lex:
        print("\nERRORES LEXICOS:")
        for error in errores_lex:
            print(f"  - {error}")
        sys.exit(1)
    print(f"  OK - {len(tokens)} tokens generados")
    
    # FASE 2: SINTÁCTICO
    print("[2/4] Analisis sintactico...")
    ast, errores_sin = parse_tokens(tokens)
    
    if errores_sin or not ast:
        print("\nERRORES SINTACTICOS:")
        for error in errores_sin:
            print(f"  - {error}")
        sys.exit(1)
    print(f"  OK - AST generado")
    
    # FASE 3: SEMÁNTICO
    print("[3/4] Analisis semantico...")
    valido, errores_sem, warnings = analyze_hoop_semantics(ast)
    
    if not valido:
        print("\nERRORES SEMANTICOS:")
        for error in errores_sem:
            print(f"  - {error}")
        sys.exit(1)
    print(f"  OK - Validacion exitosa")
    
    # FASE 4: EJECUCIÓN
    print("[4/4] Ejecutando...")
    print()
    print("=" * 50)
    print("  SALIDA DEL PROGRAMA")
    print("=" * 50)
    print()
    
    success, error, output = interpret_hoop(ast)
    
    if not success:
        print(f"\nERROR DE EJECUCION: {error}")
        sys.exit(1)
    
    if output:
        for line in output:
            print(line)
    else:
        print("(sin salida)")
    
    print()
    print("=" * 50)
    print("  EJECUCION COMPLETADA")
    print("=" * 50)
    
except Exception as e:
    import traceback
    print(f"\nERROR CRITICO: {e}")
    traceback.print_exc()
    sys.exit(1)
finally:
    # Limpiar archivo temporal
    try:
        os.remove(r'C:\Users\KENDAL~1\AppData\Local\Temp\tmpxvisqhi4.hoop')
    except:
        pass

input("\nPresiona ENTER para cerrar...")

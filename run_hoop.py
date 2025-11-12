#!/usr/bin/env python3
"""
Ejecuta un archivo .hoop desde la línea de comandos
Uso: python run_hoop.py calculadora_ejemplo.hoop
"""

import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))

from core.lexer import AnalizadorLexico
from core.parser_oficial import parse_tokens
from core.semantic import analyze_hoop_semantics
from core.interpreter import interpret_hoop

def run_hoop_file(filepath):
    """Ejecuta un archivo .hoop"""
    print("=" * 60)
    print(f"  EJECUTANDO: {filepath}")
    print("=" * 60)
    print()
    
    # Leer archivo
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"ERROR: Archivo '{filepath}' no encontrado")
        return 1
    except Exception as e:
        print(f"ERROR al leer archivo: {e}")
        return 1
    
    try:
        # FASE 1: LÉXICO
        print("[1/4] Análisis léxico...", end=" ")
        analizador = AnalizadorLexico(code)
        tokens = analizador.analizar()
        errores_lex = analizador.obtener_errores()
        
        if errores_lex:
            print("FALLO")
            print("\nERRORES LÉXICOS:")
            for error in errores_lex:
                print(f"  - {error}")
            return 1
        print(f"OK ({len(tokens)} tokens)")
        
        # FASE 2: SINTÁCTICO
        print("[2/4] Análisis sintáctico...", end=" ")
        ast, errores_sin = parse_tokens(tokens)
        
        if errores_sin or not ast:
            print("FALLO")
            print("\nERRORES SINTÁCTICOS:")
            for error in errores_sin:
                print(f"  - {error}")
            return 1
        print("OK")
        
        # FASE 3: SEMÁNTICO
        print("[3/4] Análisis semántico...", end=" ")
        valido, errores_sem, warnings = analyze_hoop_semantics(ast)
        
        if not valido:
            print("FALLO")
            print("\nERRORES SEMÁNTICOS:")
            for error in errores_sem:
                print(f"  - {error}")
            return 1
        print("OK")
        
        # FASE 4: EJECUCIÓN
        print("[4/4] Ejecutando...")
        print()
        print("=" * 60)
        print("  SALIDA DEL PROGRAMA")
        print("=" * 60)
        print()
        
        success, error, output = interpret_hoop(ast)
        
        if not success:
            print(f"\nERROR DE EJECUCIÓN: {error}")
            return 1
        
        if output:
            for line in output:
                print(line)
        else:
            print("(sin salida)")
        
        print()
        print("=" * 60)
        print("  EJECUCIÓN COMPLETADA")
        print("=" * 60)
        return 0
        
    except Exception as e:
        import traceback
        print(f"\nERROR CRÍTICO: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python run_hoop.py <archivo.hoop>")
        print("\nEjemplo: python run_hoop.py calculadora_ejemplo.hoop")
        sys.exit(1)
    
    filepath = sys.argv[1]
    exit_code = run_hoop_file(filepath)
    sys.exit(exit_code)

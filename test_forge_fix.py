#!/usr/bin/env python3
"""Debug específico para problema de forge"""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))

from core.lexer import AnalizadorLexico
from core.parser_oficial import parse_tokens
from core.semantic import analyze_hoop_semantics
from core.interpreter import interpret_hoop

# Código simplificado
codigo = """
mold Calculadora {
    whole resultado;
}

data calc set forge Calculadora();
display calc;
"""

print("=" * 60)
print("TEST: forge en declaración")
print("=" * 60)

print("\n1. LÉXICO...")
lexer = AnalizadorLexico(codigo)
tokens = lexer.analizar()
print(f"   ✓ {len(tokens)} tokens")

print("\n2. SINTÁCTICO...")
ast, errores = parse_tokens(tokens)
if errores:
    print("   ✗ ERRORES:")
    for err in errores:
        print(f"     - {err}")
    sys.exit(1)
print(f"   ✓ AST generado")

print("\n3. SEMÁNTICO...")
valido, errores_sem, warnings = analyze_hoop_semantics(ast)
if not valido:
    print("   ✗ ERRORES:")
    for err in errores_sem:
        print(f"     - {err}")
else:
    print(f"   ✓ Validado ({len(warnings)} warnings)")

print("\n4. EJECUCIÓN...")
success, error, output = interpret_hoop(ast)
if not success:
    print(f"   ✗ ERROR: {error}")
else:
    print(f"   ✓ Ejecutado")
    print(f"   Salida: {output}")

print("\n" + "=" * 60)
if success:
    print("✅ TODO FUNCIONAL")
else:
    print("❌ HAY PROBLEMAS")

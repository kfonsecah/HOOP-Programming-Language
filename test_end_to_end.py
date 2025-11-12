#!/usr/bin/env python3
"""
Test End-to-End Completo del Sistema HOOP
Valida el pipeline completo: Léxico → Sintáctico → Semántico → Ejecución
"""

import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))

from core.lexer import AnalizadorLexico
from core.parser_oficial import parse_tokens
from core.semantic import analyze_hoop_semantics
from core.interpreter import interpret_hoop

def run_test(nombre, codigo, expected_output=None, should_fail=False):
    """Ejecuta un test completo del pipeline"""
    print("\n" + "=" * 70)
    print(f"TEST: {nombre}")
    print("=" * 70)
    
    # FASE 1: LÉXICO
    print("\n1. ANÁLISIS LÉXICO...")
    lexer = AnalizadorLexico(codigo)
    tokens = lexer.analizar()
    errores_lex = lexer.obtener_errores()
    
    if errores_lex:
        print(f"   X {len(errores_lex)} errores lexicos")
        for err in errores_lex:
            print(f"      - {err}")
        if not should_fail:
            return False
        print("   OK Fallo como esperado")
        return True
    
    print(f"   OK {len(tokens)} tokens generados")
    
    # FASE 2: SINTÁCTICO
    print("\n2. ANÁLISIS SINTÁCTICO...")
    ast, errores_sin = parse_tokens(tokens)
    
    if errores_sin or not ast:
        print(f"   X Errores sintacticos")
        for err in errores_sin:
            print(f"      - {err}")
        if not should_fail:
            return False
        print("   OK Fallo como esperado")
        return True
    
    ast_size = len(ast.declaraciones) if hasattr(ast, 'declaraciones') else 0
    print(f"   OK AST generado ({ast_size} nodos)")
    
    # FASE 3: SEMÁNTICO
    print("\n3. ANÁLISIS SEMÁNTICO...")
    valido, errores_sem, warnings = analyze_hoop_semantics(ast)
    
    if not valido:
        print(f"   X {len(errores_sem)} errores semanticos")
        for err in errores_sem[:5]:
            print(f"      - {err}")
        if not should_fail:
            return False
        print("   OK Fallo como esperado")
        return True
    
    if warnings:
        print(f"   WARN {len(warnings)} advertencias")
    print("   OK Validacion exitosa")
    
    # FASE 4: EJECUCIÓN
    print("\n4. EJECUCIÓN...")
    success, error, output = interpret_hoop(ast)
    
    if not success:
        print(f"   X Error de ejecucion: {error}")
        if not should_fail:
            return False
        print("   OK Fallo como esperado")
        return True
    
    print(f"   OK Ejecutado exitosamente")
    
    if output:
        print("\n   SALIDA:")
        for line in output:
            print(f"      {line}")
    
    # Validar salida esperada
    if expected_output is not None:
        if output == expected_output:
            print("   OK Salida correcta")
        else:
            print(f"   X Salida incorrecta. Esperado: {expected_output}, Obtenido: {output}")
            return False
    
    print("\n>>> TEST PASADO")
    return True

def main():
    """Ejecuta batería completa de tests"""
    print("\n" + "=" * 70)
    print(" " * 15 + "TESTS END-TO-END DEL SISTEMA HOOP")
    print("=" * 70)
    
    tests_pasados = 0
    tests_totales = 0
    
    # TEST 1: Variables y operaciones básicas
    tests_totales += 1
    if run_test(
        "Variables y Operaciones Básicas",
        """
data x set 10;
data y set 20;
data suma set x plus y;
display suma;
        """,
        expected_output=["30"]
    ):
        tests_pasados += 1
    
    # TEST 2: Condicionales
    tests_totales += 1
    if run_test(
        "Condicionales (when/otherwise)",
        """
data a set 15;
data b set 10;

when a greater b {
    display "a es mayor";
} otherwise {
    display "b es mayor";
}
        """,
        expected_output=["a es mayor"]
    ):
        tests_pasados += 1
    
    # TEST 3: Ciclos
    tests_totales += 1
    if run_test(
        "Ciclos (cycle from to)",
        """
data suma set 0;

cycle i from 1 to 5 {
    suma set suma plus i;
}

display suma;
        """,
        expected_output=["15"]
    ):
        tests_pasados += 1
    
    # TEST 4: Funciones
    tests_totales += 1
    if run_test(
        "Funciones con Parámetros",
        """
action calcular(whole a, whole b) {
    data resultado set a times b;
    answer resultado;
}

data x set calcular(7, 6);
display x;
        """,
        expected_output=["42"]
    ):
        tests_pasados += 1
    
    # TEST 5: Recursión
    tests_totales += 1
    if run_test(
        "Recursión (Factorial)",
        """
action factorial(whole n) {
    when n equals 0 {
        answer 1;
    } otherwise {
        data temp set n minus 1;
        data resultado set n times factorial(temp);
        answer resultado;
    }
}

data fact set factorial(5);
display fact;
        """,
        expected_output=["120"]
    ):
        tests_pasados += 1
    
    # TEST 6: Funciones Built-in
    tests_totales += 1
    if run_test(
        "Funciones Built-in",
        """
data texto set "Hola Mundo";
data longitud set length(texto);
display longitud;

data base set 2;
data exp set 10;
data potencia set pow(base, exp);
display potencia;
        """,
        expected_output=["10", "1024"]
    ):
        tests_pasados += 1
    
    # TEST 7: Clases y Objetos
    tests_totales += 1
    if run_test(
        "Clases y Objetos",
        """
mold Calculadora {
    whole resultado;
    
    action sumar(whole a, whole b) {
        self.resultado set a plus b;
    }
}

data calc set forge Calculadora();
display calc;
        """,
        expected_output=["<Calculadora instance>"]
    ):
        tests_pasados += 1
    
    # TEST 8: Programa Complejo
    tests_totales += 1
    if run_test(
        "Programa Complejo Integrado",
        """
action esPar(whole n) {
    data residuo set n mod 2;
    when residuo equals 0 {
        answer true;
    } otherwise {
        answer false;
    }
}

data suma set 0;

cycle i from 1 to 10 {
    when esPar(i) {
        suma set suma plus i;
    }
}

display suma;
        """,
        expected_output=["30"]
    ):
        tests_pasados += 1
    
    # TEST 9: Error Léxico (debería fallar)
    tests_totales += 1
    if run_test(
        "Error Léxico (carácter inválido)",
        """
data x set 10;
data y set @20;
        """,
        should_fail=True
    ):
        tests_pasados += 1
    
    # TEST 10: Error Sintáctico (debería fallar)
    tests_totales += 1
    if run_test(
        "Error Sintáctico (sintaxis inválida)",
        """
data x set 10
data y set 20;
        """,
        should_fail=True
    ):
        tests_pasados += 1
    
    # TEST 11: Error Semántico (debería fallar)
    tests_totales += 1
    if run_test(
        "Error Semántico (variable no declarada)",
        """
data x set y plus 10;
display x;
        """,
        should_fail=True
    ):
        tests_pasados += 1
    
    # RESUMEN
    print("\n\n" + "=" * 70)
    print(" " * 25 + "RESUMEN FINAL")
    print("=" * 70)
    print(f"\n  >> Tests pasados: {tests_pasados}/{tests_totales}")
    print(f"  >> Tests fallidos: {tests_totales - tests_pasados}/{tests_totales}")
    print(f"  >> Porcentaje: {(tests_pasados/tests_totales*100):.1f}%")
    
    if tests_pasados == tests_totales:
        print("\n  *** TODOS LOS TESTS PASARON! ***")
        print("\n  El sistema HOOP esta completamente funcional:")
        print("    * Analisis lexico OK")
        print("    * Analisis sintactico OK")
        print("    * Analisis semantico OK")
        print("    * Ejecucion de codigo OK")
        print("    * Manejo de errores OK")
        return 0
    else:
        print("\n  *** Algunos tests fallaron ***")
        return 1

if __name__ == "__main__":
    sys.exit(main())

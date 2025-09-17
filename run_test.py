import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))

from core.lexer import AnalizadorLexico
from core.parser import parse_tokens


def main():
    codigo = '''mold N {
    action x() {
        when a {
            when b {
                when c {
                    display "demasiado profundo";
                    when d {
                    display "demasiado rico";
                    }
                }
            }
        }
    }
}
    '''

    print("=== Código de prueba ===")
    print(codigo)

    # Ejecutar lexer
    analizador = AnalizadorLexico(codigo)
    tokens = analizador.analizar()

    print("\n=== TOKENS GENERADOS ===")
    for i, t in enumerate(tokens, start=1):
        print(f"{i:03}: {t}")

    # Ejecutar parser
    ast, errores = parse_tokens(tokens)

    print("\n=== AST ===")
    print(ast)

    print("\n=== ERRORES LÉXICOS ===")
    print(analizador.obtener_errores())

    print("\n=== ERRORES SINTÁCTICOS ===")
    print([str(e) for e in errores])


if __name__ == '__main__':
    main()

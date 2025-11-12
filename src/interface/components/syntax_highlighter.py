# src/interface/components/syntax_highlighter.py
import re
from interface.colors.colors import (
    SYNTAX_PURPLE, SYNTAX_GREEN, SYNTAX_BLUE, SYNTAX_RED, SYNTAX_CYAN, SYNTAX_YELLOW
)
from core.constants.keywords import KEYWORDS

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text = text_widget
        self.bracket_colors = [SYNTAX_YELLOW, SYNTAX_BLUE, SYNTAX_PURPLE]
        self.setup_tags()
        self.patterns = self.create_patterns()

# src/interface/components/syntax_highlighter.py
import re
from interface.colors.colors import (
    SYNTAX_PURPLE, SYNTAX_GREEN, SYNTAX_BLUE, SYNTAX_RED, SYNTAX_CYAN, SYNTAX_YELLOW
)
from core.constants.keywords import (
    KEYWORDS, TYPES, WORD_OPERATORS, BUILTIN_FUNCTIONS, BOOLEAN_VALUES
)

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text = text_widget
        self.bracket_colors = [SYNTAX_YELLOW, SYNTAX_BLUE, SYNTAX_PURPLE]
        self.setup_tags()
        self.patterns = self.create_patterns()

    def setup_tags(self):
        """Configura los tags de color en el widget de texto."""
        self.text.tag_configure("keyword", foreground=SYNTAX_PURPLE)
        self.text.tag_configure("type", foreground="#FF6B6B")  # Rojo suave para tipos
        self.text.tag_configure("word_operator", foreground=SYNTAX_CYAN)
        self.text.tag_configure("builtin", foreground="#4ECDC4")  # Verde azulado para built-ins
        self.text.tag_configure("boolean", foreground="#45B7D1")  # Azul para booleanos
        self.text.tag_configure("comment", foreground=SYNTAX_GREEN)
        self.text.tag_configure("string", foreground=SYNTAX_GREEN)
        self.text.tag_configure("number", foreground=SYNTAX_BLUE)
        self.text.tag_configure("operator", foreground=SYNTAX_CYAN)
        self.text.tag_configure("function", foreground=SYNTAX_YELLOW)
        self.text.tag_configure("class", foreground=SYNTAX_YELLOW)
        
        # Tags para anidacion de brackets
        for i, color in enumerate(self.bracket_colors):
            self.text.tag_configure(f"bracket_{i}", foreground=color)
        self.text.tag_configure("bracket_error", foreground=SYNTAX_RED)

    def create_patterns(self):
        """Crea las expresiones regulares para el resaltado de HOOP."""
        # Crear patrones para cada categoría de palabras
        keyword_pattern = r'\b(' + '|'.join(KEYWORDS) + r')\b'
        type_pattern = r'\b(' + '|'.join(TYPES) + r')\b'
        word_operator_pattern = r'\b(' + '|'.join(WORD_OPERATORS) + r')\b'
        builtin_pattern = r'\b(' + '|'.join(BUILTIN_FUNCTIONS) + r')\b'
        boolean_pattern = r'\b(' + '|'.join(BOOLEAN_VALUES) + r')\b'
        
        patterns = {
            "keyword": re.compile(keyword_pattern),
            "type": re.compile(type_pattern),
            "word_operator": re.compile(word_operator_pattern),
            "builtin": re.compile(builtin_pattern),
            "boolean": re.compile(boolean_pattern),
            "comment": re.compile(r'#.*'),
            "string": re.compile(r'(\".*?\"|\'.*?\')'),
            "number": re.compile(r'\b\d+(\.\d+)?\b'),
            "operator": re.compile(r'[\+\-\*\/=%<>&|;]'),  # Operadores simbolicos
            "function": re.compile(r'\b\w+(?=\()'),  # Identificadores seguidos de (
            "class": re.compile(r'(?<=mold\s)\w+')  # Nombres de clase despues de 'mold'
        }
        return patterns

    def highlight(self, event=None):
        """Aplica el resaltado de sintaxis al texto segun la semantica de HOOP."""
        # Limpiar todos los tags existentes en todo el texto
        for tag in self.text.tag_names():
            if tag != "sel":
                self.text.tag_remove(tag, '1.0', 'end')

        # Aplicar tags en orden de prioridad (los mas especificos primero)
        # 1. Comentarios (tienen prioridad maxima)
        self.apply_tag(self.patterns["comment"], "comment")
        
        # 2. Strings (segunda prioridad)
        self.apply_tag(self.patterns["string"], "string")
        
        # 3. Numeros
        self.apply_tag(self.patterns["number"], "number")
        
        # 4. Palabras clave de HOOP (mold, when, etc.)
        self.apply_tag(self.patterns["keyword"], "keyword")
        
        # 5. Tipos de datos (whole, logic, etc.)
        self.apply_tag(self.patterns["type"], "type")
        
        # 6. Operadores en palabras (set, plus, greater, etc.)
        self.apply_tag(self.patterns["word_operator"], "word_operator")
        
        # 7. Funciones built-in (display, length, etc.)
        self.apply_tag(self.patterns["builtin"], "builtin")
        
        # 8. Valores booleanos (true, false)
        self.apply_tag(self.patterns["boolean"], "boolean")
        
        # 9. Nombres de clases (despues de 'mold')
        self.apply_tag(self.patterns["class"], "class")
        
        # 10. Nombres de funciones (antes de parentesis)
        self.apply_tag(self.patterns["function"], "function")
        
        # 11. Operadores simbolicos
        self.apply_tag(self.patterns["operator"], "operator")
            
        # 12. Aplicar el resaltado de brackets
        self.highlight_brackets()

    def highlight_brackets(self):
        """Resalta los pares de brackets segun su nivel de anidacion."""
        text_content = self.text.get('1.0', 'end')
        stack = []
        opening_brackets = "([{"
        closing_brackets = ")]}"
        
        for i, char in enumerate(text_content):
            start_index = self.text.index(f'1.0 + {i}c')
            end_index = self.text.index(f'1.0 + {i+1}c')

            if char in opening_brackets:
                level = len(stack) % len(self.bracket_colors)
                tag = f"bracket_{level}"
                self.text.tag_add(tag, start_index, end_index)
                stack.append((char, tag))
            elif char in closing_brackets:
                if stack:
                    last_open_bracket, last_tag = stack.pop()
                    # Verificar si el par coincide
                    if opening_brackets.index(last_open_bracket) == closing_brackets.index(char):
                        self.text.tag_add(last_tag, start_index, end_index)
                    else:
                        self.text.tag_add("bracket_error", start_index, end_index)
                else:
                    # Bracket de cierre sin apertura
                    self.text.tag_add("bracket_error", start_index, end_index)

    def apply_tag(self, pattern, tag):
        """Encuentra todas las coincidencias de un patron y aplica un tag."""
        text_content = self.text.get('1.0', 'end')
        for match in pattern.finditer(text_content):
            start, end = match.span()
            start_index = self.text.index(f'1.0 + {start}c')
            end_index = self.text.index(f'1.0 + {end}c')
            self.text.tag_add(tag, start_index, end_index)

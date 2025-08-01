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

    def setup_tags(self):
        """Configura los tags de color en el widget de texto."""
        self.text.tag_configure("keyword", foreground=SYNTAX_PURPLE)
        self.text.tag_configure("comment", foreground=SYNTAX_GREEN)
        self.text.tag_configure("string", foreground=SYNTAX_GREEN)
        self.text.tag_configure("number", foreground=SYNTAX_BLUE)
        self.text.tag_configure("operator", foreground=SYNTAX_CYAN)
        self.text.tag_configure("function", foreground=SYNTAX_YELLOW)
        self.text.tag_configure("class", foreground=SYNTAX_YELLOW)
        
        # Tags para anidación de brackets
        for i, color in enumerate(self.bracket_colors):
            self.text.tag_configure(f"bracket_{i}", foreground=color)
        self.text.tag_configure("bracket_error", foreground=SYNTAX_RED)

    def create_patterns(self):
        """Crea las expresiones regulares para el resaltado."""
        keyword_pattern = r'\b(' + '|'.join(KEYWORDS) + r')\b'
        
        patterns = {
            "keyword": re.compile(keyword_pattern),
            "comment": re.compile(r'#.*'),
            "string": re.compile(r'(\".*?\"|\'.*?\')'),
            "number": re.compile(r'\b\d+(\.\d+)?\b'),
            "operator": re.compile(r'[\+\-\*\/=%<>&|]'), # Quitado: ()[]{}
            "function": re.compile(r'\b\w+(?=\()'),
            "class": re.compile(r'(?<=class\s)\w+')
        }
        return patterns

    def highlight(self, event=None):
        """Aplica el resaltado de sintaxis al texto."""
        # Limpiar todos los tags existentes en todo el texto
        for tag in self.text.tag_names():
            if tag != "sel":
                self.text.tag_remove(tag, '1.0', 'end')

        # Iterar sobre cada patrón y aplicar el tag correspondiente
        for tag, pattern in self.patterns.items():
            self.apply_tag(pattern, tag)
            
        # Aplicar el resaltado de brackets
        self.highlight_brackets()

    def highlight_brackets(self):
        """Resalta los pares de brackets según su nivel de anidación."""
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
        """Encuentra todas las coincidencias de un patrón y aplica un tag."""
        text_content = self.text.get('1.0', 'end')
        for match in pattern.finditer(text_content):
            start, end = match.span()
            start_index = self.text.index(f'1.0 + {start}c')
            end_index = self.text.index(f'1.0 + {end}c')
            self.text.tag_add(tag, start_index, end_index)

import tkinter as tk
from interface.colors.colors import BACKGROUND_COLOR, LETTER_COLOR, SEPARATOR_COLOR

TERMINAL_BG = '#23272E'  # Fondo tipo terminal VSCode
TAB_BG = '#282C34'       # Fondo de pestañas
TAB_ACTIVE_BG = SEPARATOR_COLOR
TAB_INACTIVE_BG = TAB_BG
TAB_TEXT = LETTER_COLOR
BORDER_COLOR = SEPARATOR_COLOR

class Terminal(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg=BORDER_COLOR)
        # Frame principal con fondo tipo terminal
        main = tk.Frame(self, bg=TERMINAL_BG)
        main.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        # Barra superior tipo VSCode
        top_bar = tk.Frame(main, bg=TAB_BG, height=32)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)
        # Icono de terminal (simulado con texto)
        icon = tk.Label(top_bar, text='🖥️', bg=TAB_BG, fg=TAB_TEXT, font=('Segoe UI', 13))
        icon.pack(side=tk.LEFT, padx=(8,2), pady=2)
        # Pestañas
        self.problems_btn = tk.Label(top_bar, text='PROBLEMAS', bg=TAB_ACTIVE_BG, fg=TAB_TEXT, font=('Segoe UI', 10, 'bold'), padx=14, pady=6, cursor='hand2')
        self.problems_btn.pack(side=tk.LEFT, padx=(2,0), pady=2)
        self.problems_btn.bind('<Button-1>', lambda e: self.show_tab('problems'))
        self.output_btn = tk.Label(top_bar, text='OUTPUT', bg=TAB_INACTIVE_BG, fg=TAB_TEXT, font=('Segoe UI', 10, 'bold'), padx=14, pady=6, cursor='hand2')
        self.output_btn.pack(side=tk.LEFT, padx=(0,8), pady=2)
        self.output_btn.bind('<Button-1>', lambda e: self.show_tab('output'))
        # Frame de contenido con borde sutil
        content = tk.Frame(main, bg=TERMINAL_BG, highlightbackground=BORDER_COLOR, highlightthickness=1)
        content.pack(fill=tk.BOTH, expand=True, pady=(0,1))
        # Scroll y área de texto
        self.problems_text = tk.Text(content, bg=TERMINAL_BG, fg=TAB_TEXT, wrap=tk.WORD, font=('Consolas', 10), bd=0, highlightthickness=0, insertbackground=TAB_TEXT)
        self.output_text = tk.Text(content, bg=TERMINAL_BG, fg=TAB_TEXT, wrap=tk.WORD, font=('Consolas', 10), bd=0, highlightthickness=0, insertbackground=TAB_TEXT)
        self.scrollbar = tk.Scrollbar(content, command=self._on_scroll, bg=TAB_BG)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Mostrar pestaña inicial
        self.current_tab = 'problems'
        self.show_tab('problems')

    def _on_scroll(self, *args):
        if self.current_tab == 'problems':
            self.problems_text.yview(*args)
        else:
            self.output_text.yview(*args)

    def show_tab(self, tab_name):
        self.problems_text.pack_forget()
        self.output_text.pack_forget()
        # Actualizar colores de pestañas
        self.problems_btn.config(bg=TAB_ACTIVE_BG if tab_name=='problems' else TAB_INACTIVE_BG)
        self.output_btn.config(bg=TAB_ACTIVE_BG if tab_name=='output' else TAB_INACTIVE_BG)
        # Mostrar el área correspondiente y conectar el scrollbar
        if tab_name == 'problems':
            self.problems_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
            self.problems_text.config(yscrollcommand=self.scrollbar.set)
            self.current_tab = 'problems'
        else:
            self.output_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
            self.output_text.config(yscrollcommand=self.scrollbar.set)
            self.current_tab = 'output'

    def add_problem(self, text):
        self.problems_text.insert(tk.END, text + '\n')
        self.problems_text.see(tk.END)

    def add_output(self, text):
        self.output_text.insert(tk.END, text + '\n')
        self.output_text.see(tk.END)

    def clear_problems(self):
        self.problems_text.delete(1.0, tk.END)

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)

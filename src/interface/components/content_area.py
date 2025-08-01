# src/interface/components/content_area.py
import tkinter as tk
from tkinter import scrolledtext, filedialog, simpledialog
from interface.colors.colors import BACKGROUND_COLOR, LETTER_COLOR, SEPARATOR_COLOR
from .syntax_highlighter import SyntaxHighlighter
from .line_numbers import LineNumbers
from PIL import Image, ImageTk
import os

class ContentArea(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        self.current_file_path = None

        # --- Barra de Herramientas ---
        toolbar = tk.Frame(self, bg=BACKGROUND_COLOR)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(0, 2))
        
        # Placeholder para iconos (usando los existentes temporalmente)
        try:
            assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
            
            save_icon_path = os.path.join(assets_path, 'save.png')
            save_image = Image.open(save_icon_path).resize((18, 18), Image.Resampling.LANCZOS)
            self.save_icon = ImageTk.PhotoImage(save_image)

            compile_icon_path = os.path.join(assets_path, 'compile.png') # Placeholder
            compile_image = Image.open(compile_icon_path).resize((18, 18), Image.Resampling.LANCZOS)
            self.compile_icon = ImageTk.PhotoImage(compile_image)

            run_icon_path = os.path.join(assets_path, 'play.png') # Placeholder
            run_image = Image.open(run_icon_path).resize((18, 18), Image.Resampling.LANCZOS)
            self.run_icon = ImageTk.PhotoImage(run_image)

        except Exception as e:
            print(f"Error al cargar iconos de la barra de herramientas: {e}")
            self.save_icon = None
            self.compile_icon = None
            self.run_icon = None

        # Botones de la barra de herramientas (empaquetados de derecha a izquierda)
        run_label = tk.Label(toolbar, image=self.run_icon, bg=BACKGROUND_COLOR)
        run_label.pack(side=tk.RIGHT, padx=5)
        run_label.bind("<Button-1>", self.run_code)

        compile_label = tk.Label(toolbar, image=self.compile_icon, bg=BACKGROUND_COLOR)
        compile_label.pack(side=tk.RIGHT, padx=5)
        compile_label.bind("<Button-1>", self.compile_code)

        save_label = tk.Label(toolbar, image=self.save_icon, bg=BACKGROUND_COLOR)
        save_label.pack(side=tk.RIGHT, padx=5)
        save_label.bind("<Button-1>", self.save_file)

        # --- Área de Texto con Números de Línea ---
        text_frame = tk.Frame(self, bg=SEPARATOR_COLOR)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Widget de texto principal
        self.text_area = tk.Text(
            text_frame, 
            wrap=tk.WORD,
            bg=SEPARATOR_COLOR,
            fg=LETTER_COLOR,
            insertbackground=LETTER_COLOR,
            selectbackground="#3E4451",
            font=("Courier New", 12),
            bd=0,
            highlightthickness=0,
            undo=True # Habilitar undo/redo
        )
        
        # Barra de scroll vertical
        scrollbar = tk.Scrollbar(text_frame, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        # Widget de números de línea
        self.line_numbers = LineNumbers(text_frame, self.text_area)
        
        # Empaquetar los componentes
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configurar el resaltador de sintaxis
        self.highlighter = SyntaxHighlighter(self.text_area)
        
        # Vincular eventos para redibujar los números de línea
        self.text_area.bind('<KeyRelease>', self.on_key_release)
        self.text_area.bind('<MouseWheel>', self.on_scroll) # Para macOS/Windows
        self.text_area.bind('<Button-4>', self.on_scroll) # Para Linux (scroll up)
        self.text_area.bind('<Button-5>', self.on_scroll) # Para Linux (scroll down)
        self.text_area.bind('<Configure>', self.on_scroll) # Cuando cambia el tamaño

    def on_scroll(self, event=None):
        """Maneja cualquier evento de scroll o cambio de vista."""
        self.line_numbers.redraw()

    def on_key_release(self, event=None):
        """Llama al resaltador y a los números de línea cada vez que se suelta una tecla."""
        self.highlighter.highlight()
        self.line_numbers.redraw()

    def insert_code(self, code_snippet):
        """Inserta un bloque de código en el área de texto y lo resalta."""
        self.current_file_path = None # Es un snippet, no un archivo
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert(tk.END, code_snippet)
        self.highlighter.highlight()
        self.line_numbers.redraw()

    def load_file(self, file_path):
        """Lee el contenido de un archivo, lo muestra y lo resalta."""
        self.current_file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert(tk.END, content)
            self.highlighter.highlight()
            self.line_numbers.redraw()
        except Exception as e:
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert(tk.END, f"Error al abrir el archivo: {e}")

    def save_file(self, event=None):
        """Guarda el contenido actual en el archivo."""
        if self.current_file_path:
            try:
                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_area.get('1.0', 'end-1c'))
                print(f"Archivo guardado: {self.current_file_path}")
            except Exception as e:
                print(f"Error al guardar el archivo: {e}")
        else:
            self.save_file_as()

    def save_file_as(self, event=None):
        """Abre un diálogo para guardar el archivo con un nuevo nombre."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".hoop",
            filetypes=[("HOOP Files", "*.hoop"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_file_path = file_path
            self.save_file()

    def compile_code(self, event=None):
        """Placeholder para la acción de compilar."""
        print("--- Compilando código ---")
        # Aquí iría la lógica de compilación
        # 1. Guardar el archivo actual
        self.save_file()
        # 2. Llamar al compilador
        print("Compilación completada (simulado).")

    def run_code(self, event=None):
        """Placeholder para la acción de ejecutar."""
        print("--- Ejecutando código ---")
        # Aquí iría la lógica de ejecución
        print("Ejecución completada (simulado).")

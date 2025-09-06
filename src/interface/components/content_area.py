# src/interface/components/content_area.py
import tkinter as tk
from tkinter import scrolledtext, filedialog, simpledialog, messagebox
from interface.colors.colors import BACKGROUND_COLOR, LETTER_COLOR, SEPARATOR_COLOR
from .syntax_highlighter import SyntaxHighlighter
from .line_numbers import LineNumbers
from PIL import Image, ImageTk
import os
import sys

# Importar los módulos del core de HOOP
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
from core.lexer import AnalizadorLexico
from core.parser_oficial import parse_tokens

class ContentArea(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        self.current_file_path = None
        self.terminal = None  # Referencia al terminal para mostrar salida

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
        run_label = tk.Label(toolbar, image=self.run_icon, bg=BACKGROUND_COLOR, cursor='hand2')
        run_label.pack(side=tk.RIGHT, padx=5)
        run_label.bind("<Button-1>", self.run_code)
        run_label.bind("<Enter>", lambda e: e.widget.config(bg='#3E4451'))
        run_label.bind("<Leave>", lambda e: e.widget.config(bg=BACKGROUND_COLOR))

        compile_label = tk.Label(toolbar, image=self.compile_icon, bg=BACKGROUND_COLOR, cursor='hand2')
        compile_label.pack(side=tk.RIGHT, padx=5)
        compile_label.bind("<Button-1>", self.compile_code)
        compile_label.bind("<Enter>", lambda e: e.widget.config(bg='#3E4451'))
        compile_label.bind("<Leave>", lambda e: e.widget.config(bg=BACKGROUND_COLOR))

        save_label = tk.Label(toolbar, image=self.save_icon, bg=BACKGROUND_COLOR, cursor='hand2')
        save_label.pack(side=tk.RIGHT, padx=5)
        save_label.bind("<Button-1>", self.save_file)
        save_label.bind("<Enter>", lambda e: e.widget.config(bg='#3E4451'))
        save_label.bind("<Leave>", lambda e: e.widget.config(bg=BACKGROUND_COLOR))

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

    def set_terminal(self, terminal):
        """Establece la referencia al terminal para mostrar la salida"""
        self.terminal = terminal

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

    def get_code(self):
        """Obtiene el código actual del área de texto"""
        return self.text_area.get('1.0', 'end-1c')

    def compile_code(self, event=None):
        """Ejecuta el análisis léxico del código HOOP"""
        code = self.get_code()
        if not code.strip():
            self.show_message("No hay código para analizar", "warning")
            return

        # Mostrar el terminal automáticamente si no está visible
        self._ensure_terminal_visible()

        try:
            # Limpiar terminal
            if self.terminal:
                self.terminal.clear_problems()
                self.terminal.show_tab('problems')

            # Ejecutar análisis léxico
            analizador = AnalizadorLexico(code)
            tokens = analizador.analizar()

            # Mostrar resultados en terminal
            if self.terminal:
                self.terminal.add_problem("=== ANÁLISIS LÉXICO ===")
                self.terminal.add_problem(f"Código analizado: {len(code)} caracteres")
                self.terminal.add_problem(f"Tokens generados: {len(tokens)}")
                
                # Mostrar errores léxicos si existen
                errores_lexicos = analizador.obtener_errores()
                if errores_lexicos:
                    self.terminal.add_problem("\n--- ERRORES LÉXICOS ---")
                    for error in errores_lexicos:
                        self.terminal.add_problem(f"❌ {error}")
                else:
                    self.terminal.add_problem("✅ Sin errores léxicos")

                # Mostrar algunos tokens
                self.terminal.add_problem("\n--- TOKENS GENERADOS ---")
                tokens_to_show = min(20, len(tokens))
                for i, token in enumerate(tokens[:tokens_to_show]):
                    if token.tipo.name != 'NEWLINE':
                        self.terminal.add_problem(f"{i+1:3d}: {token.tipo.name:15} '{token.valor}' (línea {token.linea})")
                
                if len(tokens) > tokens_to_show:
                    self.terminal.add_problem(f"... y {len(tokens) - tokens_to_show} tokens más")

            print("✅ Análisis léxico completado")

        except Exception as e:
            error_msg = f"Error en análisis léxico: {str(e)}"
            if self.terminal:
                self.terminal.add_problem(f"❌ {error_msg}")
            print(f"❌ {error_msg}")

    def run_code(self, event=None):
        """Ejecuta el análisis completo (léxico + sintáctico) del código HOOP"""
        code = self.get_code()
        if not code.strip():
            self.show_message("No hay código para ejecutar", "warning")
            return

        # Mostrar el terminal automáticamente si no está visible
        self._ensure_terminal_visible()

        try:
            # Limpiar terminal
            if self.terminal:
                self.terminal.clear_output()
                self.terminal.clear_problems()
                self.terminal.show_tab('output')

            # === FASE 1: ANÁLISIS LÉXICO ===
            if self.terminal:
                self.terminal.add_output("🔤 EJECUTANDO ANÁLISIS LÉXICO...")
                self.terminal.add_output("=" * 50)

            analizador = AnalizadorLexico(code)
            tokens = analizador.analizar()

            if self.terminal:
                self.terminal.add_output(f"✓ Tokens generados: {len(tokens)}")

            # Verificar errores léxicos
            errores_lexicos = analizador.obtener_errores()
            if errores_lexicos:
                if self.terminal:
                    self.terminal.add_output("\n❌ ERRORES LÉXICOS ENCONTRADOS:")
                    for error in errores_lexicos:
                        self.terminal.add_output(f"  - {error}")
                    self.terminal.add_output("\n❌ No se puede continuar debido a errores léxicos.")
                return

            if self.terminal:
                self.terminal.add_output("✅ Análisis léxico exitoso\n")

            # === FASE 2: ANÁLISIS SINTÁCTICO ===
            if self.terminal:
                self.terminal.add_output("🌳 EJECUTANDO ANÁLISIS SINTÁCTICO...")
                self.terminal.add_output("=" * 50)

            ast, errores_sintacticos = parse_tokens(tokens)

            if self.terminal:
                ast_size = len(ast.declaraciones) if hasattr(ast, 'declaraciones') else len(ast) if ast else 0
                self.terminal.add_output(f"✓ AST generado con {ast_size} nodos principales")

            # Verificar errores sintácticos
            if errores_sintacticos:
                if self.terminal:
                    self.terminal.add_output("\n❌ ERRORES SINTÁCTICOS ENCONTRADOS:")
                    for error in errores_sintacticos:
                        self.terminal.add_output(f"  - {str(error)}")
                
                # También mostrar en la pestaña de problemas
                if self.terminal:
                    self.terminal.clear_problems()
                    self.terminal.add_problem("=== ERRORES SINTÁCTICOS ===")
                    for error in errores_sintacticos:
                        self.terminal.add_problem(f"❌ {str(error)}")
                return

            if self.terminal:
                self.terminal.add_output("✅ Análisis sintáctico exitoso\n")

            # === MOSTRAR RESULTADO DEL AST ===
            if self.terminal:
                self.terminal.add_output("📊 ESTRUCTURA DEL AST:")
                self.terminal.add_output("=" * 50)
                self.show_ast_summary(ast)

            print("✅ Análisis completo exitoso")

        except Exception as e:
            error_msg = f"Error durante la ejecución: {str(e)}"
            if self.terminal:
                self.terminal.add_output(f"❌ {error_msg}")
                self.terminal.add_problem(f"❌ {error_msg}")
            print(f"❌ {error_msg}")

    def show_ast_summary(self, ast):
        """Muestra un resumen del AST en el terminal"""
        if not self.terminal:
            return

        if not ast:
            self.terminal.add_output("AST vacío")
            return

        # Verificar si es el nuevo formato (ProgramaNode)
        if hasattr(ast, 'declaraciones'):
            declaraciones = ast.declaraciones
            self.terminal.add_output(f"Programa con {len(declaraciones)} declaraciones:")
            
            # Contar tipos de nodos
            node_types = {}
            for node in declaraciones:
                node_type = type(node).__name__
                node_types[node_type] = node_types.get(node_type, 0) + 1

            # Mostrar resumen
            self.terminal.add_output("Elementos encontrados:")
            for node_type, count in node_types.items():
                self.terminal.add_output(f"  - {node_type}: {count}")

            # Mostrar detalles de algunos nodos
            self.terminal.add_output("\nDetalles:")
            for i, node in enumerate(declaraciones[:5]):  # Mostrar máximo 5 nodos
                self.terminal.add_output(f"  {i+1}. {type(node).__name__}")
                if hasattr(node, 'nombre'):
                    self.terminal.add_output(f"     Nombre: {node.nombre}")
                elif hasattr(node, 'identificador'):
                    self.terminal.add_output(f"     Identificador: {node.identificador}")
        else:
            # Formato anterior (compatibilidad)
            # Contar tipos de nodos
            node_types = {}
            for node in ast:
                if isinstance(node, dict) and 'tipo' in node:
                    node_type = node['tipo']
                    node_types[node_type] = node_types.get(node_type, 0) + 1

            # Mostrar resumen
            self.terminal.add_output("Elementos encontrados:")
            for node_type, count in node_types.items():
                self.terminal.add_output(f"  - {node_type}: {count}")

            # Mostrar detalles de algunos nodos
            self.terminal.add_output("\nDetalles:")
            for i, node in enumerate(ast[:5]):  # Mostrar máximo 5 nodos
                if isinstance(node, dict):
                    self.terminal.add_output(f"  {i+1}. {node.get('tipo', 'desconocido')}")
                    if 'identificador' in node:
                        self.terminal.add_output(f"     Identificador: {node['identificador']}")
                    if 'nombre' in node:
                        self.terminal.add_output(f"     Nombre: {node['nombre']}")
                if 'valor' in node:
                    self.terminal.add_output(f"     Valor: {node['valor']}")

        # Calcular tamaño para mostrar elementos restantes
        ast_size = len(ast.declaraciones) if hasattr(ast, 'declaraciones') else len(ast) if ast else 0
        if ast_size > 5:
            self.terminal.add_output(f"  ... y {ast_size - 5} elementos más")

    def show_message(self, message, msg_type="info"):
        """Muestra un mensaje en una ventana emergente"""
        if msg_type == "error":
            messagebox.showerror("Error", message)
        elif msg_type == "warning":
            messagebox.showwarning("Advertencia", message)
        else:
            messagebox.showinfo("Información", message)

    def _ensure_terminal_visible(self):
        """Asegura que el terminal sea visible"""
        try:
            # Navegar hasta la ventana principal para acceder al toggle_terminal
            current = self.master
            while current and not hasattr(current, 'terminal_visible'):
                current = getattr(current, 'master', None)
            
            if current and hasattr(current, 'toggle_terminal') and not current.terminal_visible:
                current.toggle_terminal()
        except Exception as e:
            print(f"No se pudo mostrar el terminal automáticamente: {e}")

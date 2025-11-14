import tkinter as tk
from tkinter import scrolledtext, filedialog, simpledialog, messagebox
from interface.colors.colors import BACKGROUND_COLOR, LETTER_COLOR, SEPARATOR_COLOR
from .syntax_highlighter import SyntaxHighlighter
from .line_numbers import LineNumbers
from PIL import Image, ImageTk
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
from core.lexer import AnalizadorLexico
from core.parser_oficial import parse_tokens
from core.semantic import analyze_hoop_semantics
from core.interpreter import interpret_hoop, register_input_handler

class ContentArea(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        self.current_file_path = None
        self.terminal = None

        toolbar = tk.Frame(self, bg=BACKGROUND_COLOR)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(0, 2))
        
        try:
            assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
            
            save_icon_path = os.path.join(assets_path, 'save.png')
            save_image = Image.open(save_icon_path).resize((18, 18), Image.Resampling.LANCZOS)
            self.save_icon = ImageTk.PhotoImage(save_image)

            compile_icon_path = os.path.join(assets_path, 'compile.png')
            compile_image = Image.open(compile_icon_path).resize((18, 18), Image.Resampling.LANCZOS)
            self.compile_icon = ImageTk.PhotoImage(compile_image)

            run_icon_path = os.path.join(assets_path, 'play.png')
            run_image = Image.open(run_icon_path).resize((18, 18), Image.Resampling.LANCZOS)
            self.run_icon = ImageTk.PhotoImage(run_image)

        except Exception as e:
            print(f"Error al cargar iconos de la barra de herramientas: {e}")
            self.save_icon = None
            self.compile_icon = None
            self.run_icon = None

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

        text_frame = tk.Frame(self, bg=SEPARATOR_COLOR)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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
            undo=True
        )
        
        scrollbar = tk.Scrollbar(text_frame, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        self.line_numbers = LineNumbers(text_frame, self.text_area)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.highlighter = SyntaxHighlighter(self.text_area)
        
        self.text_area.bind('<KeyRelease>', self.on_key_release)
        self.text_area.bind('<MouseWheel>', self.on_scroll)
        self.text_area.bind('<Button-4>', self.on_scroll)
        self.text_area.bind('<Button-5>', self.on_scroll)
        self.text_area.bind('<Configure>', self.on_scroll)

        # Registrar manejador personalizado para input() dentro de la GUI
        register_input_handler(self._gui_input_handler)

    def set_terminal(self, terminal):
        self.terminal = terminal

    def on_scroll(self, event=None):
        self.line_numbers.redraw()

    def on_key_release(self, event=None):
        self.highlighter.highlight()
        self.line_numbers.redraw()

    def insert_code(self, code_snippet):
        self.current_file_path = None
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert(tk.END, code_snippet)
        self.highlighter.highlight()
        self.line_numbers.redraw()

    def load_file(self, file_path):
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
        file_path = filedialog.asksaveasfilename(
            defaultextension=".hoop",
            filetypes=[("HOOP Files", "*.hoop"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_file_path = file_path
            self.save_file()

    def get_code(self):
        return self.text_area.get('1.0', 'end-1c')

    def compile_code(self, event=None):
        code = self.get_code()
        if not code.strip():
            self.show_message("No hay código para analizar", "warning")
            return

        self._ensure_terminal_visible()

        try:
            if self.terminal:
                self.terminal.clear_problems()
                self.terminal.show_tab('problems')

            if self.terminal:
                self.terminal.add_problem("╔═══════════════════════════════════════════╗")
                self.terminal.add_problem("║   ANÁLISIS LÉXICO                         ║")
                self.terminal.add_problem("╚═══════════════════════════════════════════╝")

            analizador = AnalizadorLexico(code)
            tokens = analizador.analizar()

            if self.terminal:
                self.terminal.add_problem(f"Tokens generados: {len(tokens)}")
                
            errores_lexicos = analizador.obtener_errores()
            if errores_lexicos:
                if self.terminal:
                    self.terminal.add_problem("\nERRORES LÉXICOS:")
                    for error in errores_lexicos:
                        self.terminal.add_problem(f"  {error}")
                self.show_message(
                    "Se encontraron errores léxicos:\n" + "\n".join(errores_lexicos),
                    "error"
                )
                return
            else:
                if self.terminal:
                    self.terminal.add_problem("Sin errores léxicos\n")

            if self.terminal:
                self.terminal.add_problem("Primeros tokens:")
                tokens_to_show = min(10, len(tokens))
                for i, token in enumerate(tokens[:tokens_to_show]):
                    if token.tipo.name != 'NEWLINE':
                        self.terminal.add_problem(f"  {i+1:2d}. {token.tipo.name:15} '{token.valor}' (línea {token.linea})")
                
                if len(tokens) > tokens_to_show:
                    self.terminal.add_problem(f"  ... y {len(tokens) - tokens_to_show} tokens más")
                self.terminal.add_problem("")

            if self.terminal:
                self.terminal.add_problem("╔═══════════════════════════════════════════╗")
                self.terminal.add_problem("║   ANÁLISIS SINTÁCTICO                     ║")
                self.terminal.add_problem("╚═══════════════════════════════════════════╝")

            ast, errores_sintacticos = parse_tokens(tokens)

            if errores_sintacticos:
                if self.terminal:
                    self.terminal.add_problem("\nERRORES SINTÁCTICOS:")
                    for error in errores_sintacticos:
                        self.terminal.add_problem(f"  {str(error)}")
                self.show_message(
                    "Se encontraron errores sintácticos:\n" + "\n".join(map(str, errores_sintacticos)),
                    "error"
                )
                return

            if not ast:
                if self.terminal:
                    self.terminal.add_problem("\nERROR: No se pudo generar el AST")
                self.show_message("No se pudo generar el AST. Revise su código.", "error")
                return

            if self.terminal:
                ast_size = len(ast.declaraciones) if hasattr(ast, 'declaraciones') else 0
                self.terminal.add_problem(f"AST generado: {ast_size} nodos principales")
                self.terminal.add_problem("Sin errores sintácticos\n")

            if self.terminal and hasattr(ast, 'declaraciones'):
                node_types = {}
                for node in ast.declaraciones:
                    node_type = type(node).__name__
                    node_types[node_type] = node_types.get(node_type, 0) + 1

                self.terminal.add_problem("Estructura del programa:")
                for node_type, count in sorted(node_types.items()):
                    self.terminal.add_problem(f"  {node_type}: {count}")
                self.terminal.add_problem("")

            if self.terminal:
                self.terminal.add_problem("╔═══════════════════════════════════════════╗")
                self.terminal.add_problem("║   ANÁLISIS SEMÁNTICO                      ║")
                self.terminal.add_problem("╚═══════════════════════════════════════════╝")

            valido, errores_semanticos, warnings = analyze_hoop_semantics(ast)

            if warnings:
                if self.terminal:
                    self.terminal.add_problem(f"\n{len(warnings)} ADVERTENCIAS:")
                    for warning in warnings[:10]:
                        self.terminal.add_problem(f"  {warning}")
                    if len(warnings) > 10:
                        self.terminal.add_problem(f"  ... y {len(warnings) - 10} advertencias más")

            if not valido:
                if self.terminal:
                    self.terminal.add_problem(f"\n{len(errores_semanticos)} ERRORES SEMÁNTICOS:")
                    for error in errores_semanticos:
                        self.terminal.add_problem(f"  {error}")
                self.show_message(
                    "Se encontraron errores semánticos:\n" + "\n".join(errores_semanticos),
                    "error"
                )
                return

            if self.terminal:
                self.terminal.add_problem("Sin errores semánticos\n")

            if self.terminal:
                self.terminal.add_problem("═" * 43)
                self.terminal.add_problem("COMPILACIÓN EXITOSA")
                self.terminal.add_problem("═" * 43)
                self.terminal.add_problem(f"  Tokens: {len(tokens)}")
                self.terminal.add_problem(f"  Nodos AST: {ast_size}")
                self.terminal.add_problem(f"  Errores: 0")
                self.terminal.add_problem(f"  Advertencias: {len(warnings)}")
                self.terminal.add_problem("")
                self.terminal.add_problem("El código está listo para ejecutarse.")

        except Exception as e:
            import traceback
            error_msg = f"Error inesperado durante la compilación: {str(e)}"
            if self.terminal:
                self.terminal.add_problem(f"\n❌ {error_msg}")
                self.terminal.add_problem("\nTraceback:")
                for line in traceback.format_exc().split('\n'):
                    if line.strip():
                        self.terminal.add_problem(line)
            print(f"ERROR: {error_msg}")
            traceback.print_exc()

    def run_code(self, event=None):
        code = self.get_code()
        if not code.strip():
            self.show_message("No hay código para ejecutar", "warning")
            return

        self._ensure_terminal_visible()

        try:
            if self.terminal:
                self.terminal.clear_output()
                self.terminal.clear_problems()
                self.terminal.show_tab('output')

            if self.terminal:
                self.terminal.add_output("╔═══════════════════════════════════════════╗")
                self.terminal.add_output("║   FASE 1: ANÁLISIS LÉXICO                ║")
                self.terminal.add_output("╚═══════════════════════════════════════════╝")

            analizador = AnalizadorLexico(code)
            tokens = analizador.analizar()

            if self.terminal:
                self.terminal.add_output(f"Tokens generados: {len(tokens)}")

            errores_lexicos = analizador.obtener_errores()
            if errores_lexicos:
                if self.terminal:
                    self.terminal.add_output("\nERRORES LÉXICOS ENCONTRADOS:")
                    for error in errores_lexicos:
                        self.terminal.add_output(f"  {error}")
                        self.terminal.add_problem(f"LÉXICO: {error}")
                    self.terminal.show_tab('problems')
                self.show_message(
                    "Se encontraron errores léxicos:\n" + "\n".join(errores_lexicos),
                    "error"
                )
                return

            if self.terminal:
                self.terminal.add_output("Análisis léxico exitoso\n")

            if self.terminal:
                self.terminal.add_output("╔═══════════════════════════════════════════╗")
                self.terminal.add_output("║   FASE 2: ANÁLISIS SINTÁCTICO            ║")
                self.terminal.add_output("╚═══════════════════════════════════════════╝")

            ast, errores_sintacticos = parse_tokens(tokens)

            if self.terminal:
                ast_size = len(ast.declaraciones) if hasattr(ast, 'declaraciones') else len(ast) if ast else 0
                self.terminal.add_output(f"AST generado con {ast_size} nodos principales")

            if errores_sintacticos:
                if self.terminal:
                    self.terminal.add_output("\nERRORES SINTÁCTICOS ENCONTRADOS:")
                    for error in errores_sintacticos:
                        self.terminal.add_output(f"  {str(error)}")
                        self.terminal.add_problem(f"SINTÁCTICO: {str(error)}")
                    self.terminal.show_tab('problems')
                self.show_message(
                    "Se encontraron errores sintácticos:\n" + "\n".join(map(str, errores_sintacticos)),
                    "error"
                )
                return

            if not ast:
                if self.terminal:
                    self.terminal.add_output("\nERROR: No se pudo generar el AST")
                    self.terminal.add_problem("SINTÁCTICO: No se pudo generar el AST")
                    self.terminal.show_tab('problems')
                self.show_message("No se pudo generar el AST. Revise su código.", "error")
                return

            if self.terminal:
                self.terminal.add_output("Análisis sintáctico exitoso\n")

            if self.terminal:
                self.terminal.add_output("╔═══════════════════════════════════════════╗")
                self.terminal.add_output("║   FASE 3: ANÁLISIS SEMÁNTICO             ║")
                self.terminal.add_output("╚═══════════════════════════════════════════╝")

            valido, errores_semanticos, warnings = analyze_hoop_semantics(ast)

            if warnings and self.terminal:
                self.terminal.add_output(f"{len(warnings)} advertencias semánticas")
                for warning in warnings[:5]:
                    self.terminal.add_output(f"  {warning}")
                    self.terminal.add_problem(f"WARNING: {warning}")

            if not valido:
                if self.terminal:
                    self.terminal.add_output("\nERRORES SEMÁNTICOS ENCONTRADOS:")
                    for error in errores_semanticos:
                        self.terminal.add_output(f"  {error}")
                        self.terminal.add_problem(f"SEMÁNTICO: {error}")
                    self.terminal.show_tab('problems')
                self.show_message(
                    "Se encontraron errores semánticos:\n" + "\n".join(errores_semanticos),
                    "error"
                )
                return

            if self.terminal:
                self.terminal.add_output("Análisis semántico exitoso\n")

            if self.terminal:
                self.terminal.add_output("╔═══════════════════════════════════════════╗")
                self.terminal.add_output("║   FASE 4: EJECUCIÓN DEL PROGRAMA         ║")
                self.terminal.add_output("╚═══════════════════════════════════════════╝")
                self.terminal.add_output("")

            success, error_ejecucion, output = interpret_hoop(ast)

            if not success:
                if self.terminal:
                    self.terminal.add_output(f"\nERROR DE EJECUCIÓN:")
                    self.terminal.add_output(f"  {error_ejecucion}")
                    self.terminal.add_problem(f"EJECUCIÓN: {error_ejecucion}")
                    self.terminal.show_tab('problems')
                if error_ejecucion:
                    self.show_message(f"Error en la ejecución:\n{error_ejecucion}", "error")
                return

            if output:
                if self.terminal:
                    for line in output:
                        self.terminal.add_output(line)
            else:
                if self.terminal:
                    self.terminal.add_output("(sin salida)")

            if self.terminal:
                self.terminal.add_output("")
                self.terminal.add_output("═" * 43)
                self.terminal.add_output("EJECUCIÓN COMPLETADA EXITOSAMENTE")
                self.terminal.add_output("═" * 43)

        except Exception as e:
            import traceback
            error_msg = f"Error inesperado: {str(e)}"
            if self.terminal:
                self.terminal.add_output(f"\n❌ {error_msg}")
                self.terminal.add_output("\nTraceback:")
                self.terminal.add_output(traceback.format_exc())
                self.terminal.add_problem(f"CRÍTICO: {error_msg}")
                self.terminal.show_tab('problems')
            print(f"ERROR: {error_msg}")
            traceback.print_exc()

    def show_ast_summary(self, ast):
        if not self.terminal:
            return

        if not ast:
            self.terminal.add_output("AST vacío")
            return

        if hasattr(ast, 'declaraciones'):
            declaraciones = ast.declaraciones
            self.terminal.add_output(f"Programa con {len(declaraciones)} declaraciones:")
            
            node_types = {}
            for node in declaraciones:
                node_type = type(node).__name__
                node_types[node_type] = node_types.get(node_type, 0) + 1

            self.terminal.add_output("Elementos encontrados:")
            for node_type, count in node_types.items():
                self.terminal.add_output(f"  - {node_type}: {count}")

            self.terminal.add_output("\nDetalles:")
            for i, node in enumerate(declaraciones[:5]):
                self.terminal.add_output(f"  {i+1}. {type(node).__name__}")
                if hasattr(node, 'nombre'):
                    self.terminal.add_output(f"     Nombre: {node.nombre}")
                elif hasattr(node, 'identificador'):
                    self.terminal.add_output(f"     Identificador: {node.identificador}")
        else:
            node_types = {}
            for node in ast:
                if isinstance(node, dict) and 'tipo' in node:
                    node_type = node['tipo']
                    node_types[node_type] = node_types.get(node_type, 0) + 1

            self.terminal.add_output("Elementos encontrados:")
            for node_type, count in node_types.items():
                self.terminal.add_output(f"  - {node_type}: {count}")

            self.terminal.add_output("\nDetalles:")
            for i, node in enumerate(ast[:5]):
                if isinstance(node, dict):
                    self.terminal.add_output(f"  {i+1}. {node.get('tipo', 'desconocido')}")
                    if 'identificador' in node:
                        self.terminal.add_output(f"     Identificador: {node['identificador']}")
                    if 'nombre' in node:
                        self.terminal.add_output(f"     Nombre: {node['nombre']}")
                if 'valor' in node:
                    self.terminal.add_output(f"     Valor: {node['valor']}")

        ast_size = len(ast.declaraciones) if hasattr(ast, 'declaraciones') else len(ast) if ast else 0
        if ast_size > 5:
            self.terminal.add_output(f"  ... y {ast_size - 5} elementos mas")

    def show_message(self, message, msg_type="info"):
        if msg_type == "error":
            messagebox.showerror("Error", message)
        elif msg_type == "warning":
            messagebox.showwarning("Advertencia", message)
        else:
            messagebox.showinfo("Información", message)

    def _ensure_terminal_visible(self):
        try:
            current = self.master
            while current and not hasattr(current, 'terminal_visible'):
                current = getattr(current, 'master', None)
            
            if current and hasattr(current, 'toggle_terminal') and not current.terminal_visible:
                current.toggle_terminal()
        except Exception as e:
            print(f"No se pudo mostrar el terminal automaticamente: {e}")

    def _gui_input_handler(self, prompt: str) -> str:
        """Solicita datos al usuario mediante un diálogo cuando se usa input() desde la GUI."""
        try:
            self.master.show_content_area()
        except Exception:
            pass
        self._ensure_terminal_visible()
        mensaje = prompt if prompt else "Ingrese un valor:"
        respuesta = simpledialog.askstring("Entrada HOOP", mensaje, parent=self)
        return respuesta if respuesta is not None else ""

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, Menu
from interface.colors.colors import BACKGROUND_COLOR, LETTER_COLOR
from PIL import Image, ImageTk
import os
from core.constants.code_snippets import CODE_SNIPPETS

class Header(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.configure(bg=BACKGROUND_COLOR)

        # Guardar referencias a otros componentes
        self.sidebar = None
        self.content_area = None
        self.toggle_terminal_command = None

        # --- Botones como Labels ---
        new_label = tk.Label(self, text="Nuevo", 
                             bg=BACKGROUND_COLOR, fg=LETTER_COLOR,
                             bd=0, highlightthickness=0,
                             font=("Arial", 10), padx=10, pady=5)
        new_label.bind("<Button-1>", self.create_new_project)
        new_label.bind("<Enter>", lambda e: e.widget.config(bg='#3E4451'))
        new_label.bind("<Leave>", lambda e: e.widget.config(bg=BACKGROUND_COLOR))

        # Botón de Cargar Proyecto
        load_project_label = tk.Label(self, text="Cargar Proyecto",
                                      bg=BACKGROUND_COLOR, fg=LETTER_COLOR,
                                      bd=0, highlightthickness=0,
                                      font=("Arial", 10), padx=10, pady=5)
        load_project_label.bind("<Button-1>", self.load_project)
        load_project_label.bind("<Enter>", lambda e: e.widget.config(bg='#3E4451'))
        load_project_label.bind("<Leave>", lambda e: e.widget.config(bg=BACKGROUND_COLOR))

        # Botón de Opciones con Menú
        options_label = tk.Label(self, text="Opciones",
                                 bg=BACKGROUND_COLOR, fg=LETTER_COLOR,
                                 bd=0, highlightthickness=0,
                                 font=("Arial", 10), padx=10, pady=5)
        options_label.bind("<Button-1>", self.show_options_menu)
        options_label.bind("<Enter>", lambda e: e.widget.config(bg='#3E4451'))
        options_label.bind("<Leave>", lambda e: e.widget.config(bg=BACKGROUND_COLOR))

        exit_label = tk.Label(self, text="Salir",
                              bg=BACKGROUND_COLOR, fg=LETTER_COLOR,
                              bd=0, highlightthickness=0,
                              font=("Arial", 10), padx=10, pady=5)
        exit_label.bind("<Button-1>", lambda e: self.master.destroy())
        exit_label.bind("<Enter>", lambda e: e.widget.config(bg='#3E4451'))
        exit_label.bind("<Leave>", lambda e: e.widget.config(bg=BACKGROUND_COLOR))

        # Cargar el logo
        try:
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'HOOP icon.png')
            logo = Image.open(logo_path)
            logo = logo.resize((40, 40), Image.Resampling.LANCZOS)
            self.logo_icon = ImageTk.PhotoImage(logo)
            
            # Crear label para el logo
            logo_label = tk.Label(self, image=self.logo_icon, bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
            logo_label.image = self.logo_icon  # mantener una referencia

            # Usar tk.Label en lugar de ttk.Label para mejor control del fondo
            title_label = tk.Label(self, text="HOOP IDLE", font=("Arial", 24), 
                                  bg=BACKGROUND_COLOR, fg=LETTER_COLOR, bd=0, highlightthickness=0)

            # Empaquetar logo y título juntos
            logo_label.pack(side=tk.LEFT, padx=(5, 2))
            title_label.pack(side=tk.LEFT, padx=10)
            
            # Empaquetar botones a la derecha
            exit_label.pack(side=tk.RIGHT, padx=10, pady=10)
            options_label.pack(side=tk.RIGHT, padx=10, pady=10)
            load_project_label.pack(side=tk.RIGHT, padx=10, pady=10)
            new_label.pack(side=tk.RIGHT, padx=10, pady=10)
        except Exception as e:
            print(f"Error al cargar el logo: {e}")

    def set_sidebar(self, sidebar):
        """Guarda una referencia al sidebar."""
        self.sidebar = sidebar

    def set_content_area(self, content_area):
        """Guarda una referencia al área de contenido."""
        self.content_area = content_area

    def set_toggle_terminal_command(self, command):
        """Guarda el comando para mostrar/ocultar el terminal."""
        self.toggle_terminal_command = command

    def create_new_project(self, event=None):
        """Abre un diálogo para seleccionar una carpeta y la carga en el sidebar."""
        # Pedir al usuario que seleccione una carpeta contenedora
        parent_dir = filedialog.askdirectory(title="Seleccione la ubicación para el nuevo proyecto")
        
        # Pedir el nombre del proyecto
        project_name = simpledialog.askstring("Nuevo Proyecto", "Ingrese el nombre del nuevo proyecto:")
        
        if parent_dir and project_name:
            project_path = os.path.join(parent_dir, project_name)
            try:
                os.makedirs(project_path)
                if self.sidebar:
                    self.sidebar.load_directory(project_path)
            except Exception as e:
                print(f"Error al crear el proyecto: {e}")

    def load_project(self, event=None):
        """Abre un diálogo para seleccionar y cargar una carpeta de proyecto."""
        project_path = filedialog.askdirectory(title="Seleccione una carpeta de proyecto para cargar")
        if project_path:
            if self.sidebar:
                self.sidebar.load_directory(project_path)

    def show_options_menu(self, event):
        """Muestra el menú de opciones debajo del label."""
        menu = Menu(self, tearoff=0, bg=BACKGROUND_COLOR, fg=LETTER_COLOR,
                    activebackground='#3E4451', activeforeground=LETTER_COLOR,
                    bd=0)

        # Palabras Reservadas
        menu.add_command(label="Palabras Reservadas", 
                         command=lambda: self.insert_snippet("palabras_reservadas"))

        # Submenú de Sintaxis
        sintaxis_menu = Menu(menu, tearoff=0, bg=BACKGROUND_COLOR, fg=LETTER_COLOR,
                             activebackground='#3E4451', activeforeground=LETTER_COLOR,
                             bd=0)
        sintaxis_menu.add_command(label="Control", 
                                  command=lambda: self.insert_snippet("sintaxis_control"))
        sintaxis_menu.add_command(label="Funciones", 
                                  command=lambda: self.insert_snippet("sintaxis_funciones"))
        sintaxis_menu.add_command(label="Operaciones", 
                                  command=lambda: self.insert_snippet("sintaxis_operaciones"))
        menu.add_cascade(label="Sintaxis", menu=sintaxis_menu)

        # Semántica
        menu.add_command(label="Semántica", 
                         command=lambda: self.insert_snippet("semantica"))

        # Tipos de Datos
        menu.add_command(label="Tipos de Datos", 
                         command=lambda: self.insert_snippet("tipos_de_datos"))

        menu.add_separator()
        menu.add_command(label="Abrir/Cerrar Terminal",
                         command=self.toggle_terminal_command)

        # Mostrar el menú en la posición del cursor
        menu.post(event.x_root, event.y_root)

    def insert_snippet(self, key):
        """Inserta un fragmento de código en el área de contenido."""
        if self.content_area and key in CODE_SNIPPETS:
            # Asegurarse de que el content_area sea visible antes de insertar
            self.master.show_content_area()
            snippet = CODE_SNIPPETS[key]["code"]
            self.content_area.insert_code(snippet)

    def placeholder_command(self, event=None):
        """Placeholder command for buttons without functionality yet."""
        print("Botón presionado (sin acción)")

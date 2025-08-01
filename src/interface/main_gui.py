import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from interface.components.sidebar import Sidebar
from interface.components.header import Header
from interface.components.content_area import ContentArea
from interface.components.welcome_screen import WelcomeScreen
from interface.components.terminal import Terminal
from interface.colors.colors import BACKGROUND_COLOR, LETTER_COLOR, SEPARATOR_COLOR

class Main (tk.Tk) :
    def __init__(self):
        super().__init__()
        self.title("HOOP IDLE")
        self.geometry("1200x800")
        self.configure(bg=BACKGROUND_COLOR)

        # --- Set the application-wide theme ---
        style = ttk.Style()
        style.theme_use('default') # Use default theme to avoid sidebar border issues

        # Header en la parte superior
        self.header = Header(self)
        self.header.pack(fill=tk.X)

        # Frame principal para contener sidebar y área de contenido
        self.main_frame = tk.Frame(self, bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0)) # Añadir padding vertical superior

        # Sidebar a la izquierda, sin padding que pueda causar un borde
        self.sidebar = Sidebar(self.main_frame)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        
        separator = tk.Frame(self.main_frame, bg=SEPARATOR_COLOR, width=2)
        separator.pack(side=tk.LEFT, fill=tk.Y)

        # Pasar la referencia del sidebar al header
        self.header.set_sidebar(self.sidebar)

        # --- Área de Contenido y Pantalla de Bienvenida ---

        # Crear un frame contenedor para el área derecha
        self.right_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Terminal ---
        # PanedWindow para área principal y terminal
        self.paned_window = tk.PanedWindow(self.right_frame, orient=tk.VERTICAL, bg=BACKGROUND_COLOR, sashwidth=3, sashrelief=tk.FLAT, bd=0)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Frame para el área principal
        self.top_frame = tk.Frame(self.paned_window, bg=BACKGROUND_COLOR)
        self.paned_window.add(self.top_frame)

        # Frame para la terminal (solo se agrega cuando se abre)
        self.terminal_frame = tk.Frame(self.paned_window, bg=BACKGROUND_COLOR)
        self.terminal_frame.pack_propagate(False)
        self.terminal = Terminal(self.terminal_frame)
        self.terminal.pack(fill=tk.BOTH, expand=True)
        self.terminal_visible = False
        self.terminal_min_height = 220

        # Pantalla de Bienvenida (visible al inicio)
        self.welcome_screen = WelcomeScreen(self.top_frame)
        self.welcome_screen.pack(fill=tk.BOTH, expand=True)

        # Área de contenido (inicialmente oculta)
        self.content_area = ContentArea(self.top_frame)
        # No se empaqueta aquí, se gestionará su visibilidad

        # Pasar la referencia del content_area y el toggle_terminal al header
        self.header.set_content_area(self.content_area)
        self.header.set_toggle_terminal_command(self.toggle_terminal)

    def show_content_area(self):
        """Muestra el área de contenido y oculta la pantalla de bienvenida."""
        if not self.content_area.winfo_viewable():
            # Ocultar la pantalla de bienvenida
            self.welcome_screen.pack_forget()
            # Mostrar el área de contenido
            self.content_area.pack(fill=tk.BOTH, expand=True)

    def toggle_terminal(self):
        """Muestra u oculta el terminal."""
        if self.terminal_visible:
            self.paned_window.forget(self.terminal_frame)
            self.terminal_visible = False
        else:
            self.paned_window.add(self.terminal_frame)
            self.terminal_visible = True
            self.update_idletasks()
            total_height = self.paned_window.winfo_height()
            if total_height > self.terminal_min_height + 50:
                self.paned_window.sash_place(0, 0, total_height - self.terminal_min_height)
            else:
                self.paned_window.sash_place(0, 0, total_height // 2)

import tkinter as tk
from interface.colors.colors import BACKGROUND_COLOR, LETTER_COLOR
from PIL import Image, ImageTk
import os

class WelcomeScreen(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)

        # Frame para centrar el contenido
        center_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Logo de la aplicación
        try:
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'HOOP icon.png')
            logo_image = Image.open(logo_path).resize((100, 100), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            
            logo_label = tk.Label(center_frame, image=self.logo_photo, bg=BACKGROUND_COLOR)
            logo_label.pack(pady=10)
        except Exception as e:
            print(f"Error al cargar el logo de bienvenida: {e}")

        # Mensaje de Bienvenida
        welcome_label = tk.Label(
            center_frame,
            text="Bienvenido a HOOP IDLE",
            font=("Arial", 24, "bold"),
            bg=BACKGROUND_COLOR,
            fg=LETTER_COLOR
        )
        welcome_label.pack(pady=(10, 5))

        # Subtítulo con instrucciones
        subtitle_label = tk.Label(
            center_frame,
            text="Seleccione un archivo para empezar a editar\no use el menú de Opciones para explorar el lenguaje.",
            font=("Arial", 12),
            bg=BACKGROUND_COLOR,
            fg=LETTER_COLOR
        )
        subtitle_label.pack(pady=(5, 10))

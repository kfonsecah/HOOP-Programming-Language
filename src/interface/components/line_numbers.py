# src/interface/components/line_numbers.py
import tkinter as tk
from interface.colors.colors import BACKGROUND_COLOR, LETTER_COLOR, SEPARATOR_COLOR

class LineNumbers(tk.Canvas):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.configure(
            bg=SEPARATOR_COLOR, # Mismo fondo que el area de texto
            highlightthickness=0,
            width=40 # Ancho inicial
        )

    def redraw(self, *args):
        """Redibuja los numeros de linea."""
        self.delete("all")

        # Obtener la primera linea visible en el widget de texto
        first_line_index = self.text_widget.index("@0,0")
        
        # Iterar mientras la linea sea visible
        line_no = int(first_line_index.split('.')[0])
        while True:
            # Obtener las coordenadas del bounding box de la linea
            dline = self.text_widget.dlineinfo(f"{line_no}.0")
            if dline is None:
                break # La linea no es visible, salir del bucle
            
            # Coordenadas y para dibujar el numero
            y = dline[1]
            
            # Dibujar el numero de linea en el canvas
            self.create_text(
                38, # Posición x (alineado a la derecha)
                y,
                anchor="ne",
                text=str(line_no),
                fill=LETTER_COLOR,
                font=("Arial", 10)
            )
            
            line_no += 1
            # Si la coordenada y está más allá de la altura del widget, parar
            if y > self.winfo_height():
                break

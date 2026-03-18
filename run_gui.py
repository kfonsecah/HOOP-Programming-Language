#!/usr/bin/env python3
"""
Launcher para la GUI de HOOP
"""
import sys
import os

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar y ejecutar la GUI
from interface.main_gui import Main

if __name__ == "__main__":
    app = Main()
    app.mainloop()

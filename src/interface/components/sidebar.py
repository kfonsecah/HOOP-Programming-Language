import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from interface.colors.colors import BACKGROUND_COLOR, LETTER_COLOR
from PIL import Image, ImageTk
import os
import shutil

class Sidebar(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        # Forzar sin borde en el frame principal del sidebar
        self.configure(bg=BACKGROUND_COLOR, width=250, bd=0, highlightthickness=0)
        
        # Cargar el icono HOOP
        self.load_icons()
        
        # Crear estilo para el treeview
        style = ttk.Style()
        
        # NOTE: The theme is now set globally in main_gui.py
        style.theme_use('default')

        style.configure("Treeview",
                       background=BACKGROUND_COLOR,
                       foreground=LETTER_COLOR,
                       fieldbackground=BACKGROUND_COLOR,
                       borderwidth=0,
                       relief='flat',
                       highlightthickness=0)
        style.map("Treeview",
                 background=[('selected', '#3E4451')],
                 foreground=[('selected', LETTER_COLOR)])

        style.configure("Treeview.Heading",
                       background=BACKGROUND_COLOR,
                       foreground=LETTER_COLOR,
                       relief='flat')
        
        # Frame para la barra de título que contendrá el título y los botones
        title_bar_frame = tk.Frame(self, bg=BACKGROUND_COLOR)
        title_bar_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Título "EXPLORADOR" a la izquierda
        title_label = tk.Label(title_bar_frame, text="EXPLORADOR", 
                              bg=BACKGROUND_COLOR, fg=LETTER_COLOR,
                              font=("Arial", 12, "bold"),
                              bd=0, highlightthickness=0)
        title_label.pack(side=tk.LEFT)

        # Frame para los botones de acción a la derecha
        action_buttons_frame = tk.Frame(title_bar_frame, bg=BACKGROUND_COLOR)
        action_buttons_frame.pack(side=tk.RIGHT)

        # Usar Labels en lugar de Buttons para control visual completo
        new_folder_label = tk.Label(action_buttons_frame, image=self.new_folder_icon, 
                                     bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        new_folder_label.pack(side=tk.LEFT, padx=(0, 5))
        new_folder_label.bind("<Button-1>", self.create_new_folder)
        new_folder_label.bind("<Enter>", lambda e: e.widget.config(bg='#3E4451'))
        new_folder_label.bind("<Leave>", lambda e: e.widget.config(bg=BACKGROUND_COLOR))

        new_file_label = tk.Label(action_buttons_frame, image=self.new_file_icon,
                                    bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        new_file_label.pack(side=tk.LEFT)
        new_file_label.bind("<Button-1>", self.create_new_file)
        new_file_label.bind("<Enter>", lambda e: e.widget.config(bg='#3E4451'))
        new_file_label.bind("<Leave>", lambda e: e.widget.config(bg=BACKGROUND_COLOR))

        # Frame contenedor para el Treeview, sin bordes
        tree_container = tk.Frame(self, bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Crear el treeview
        self.tree = ttk.Treeview(tree_container, style="Treeview", show="tree")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configurar eventos
        self.tree.bind('<<TreeviewOpen>>', self.on_folder_open)
        self.tree.bind('<Double-1>', self.on_file_double_click)

        # --- Lógica de Drag and Drop ---
        self.tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.tree.bind("<B1-Motion>", self.on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self.on_drop)
        self.drag_data = {"item": None, "path": None}
        self.last_highlighted = None

        # NO cargar el directorio inicial, esperar a que el usuario elija
        # self.load_directory()
        
        # Mantener el ancho fijo
        self.pack_propagate(False)
    
    def load_icons(self):
        """Cargar los iconos para el treeview"""
        try:
            # Ruta a los iconos
            assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets')
            
            # Cargar iconos para creación (más grandes)
            new_file_path = os.path.join(assets_path, 'new document.png')
            new_file_image = Image.open(new_file_path).resize((20, 20), Image.Resampling.LANCZOS)
            self.new_file_icon = ImageTk.PhotoImage(new_file_image)

            new_folder_path = os.path.join(assets_path, 'new folder.png')
            new_folder_image = Image.open(new_folder_path).resize((20, 20), Image.Resampling.LANCZOS)
            self.new_folder_icon = ImageTk.PhotoImage(new_folder_image)

            # Cargar icono HOOP para archivos
            hoop_icon_path = os.path.join(assets_path, 'HOOP.ico')
            hoop_image = Image.open(hoop_icon_path)
            hoop_image = hoop_image.resize((16, 16), Image.Resampling.LANCZOS)
            self.file_icon = ImageTk.PhotoImage(hoop_image)
            
            # Cargar icono de carpeta cerrada (PNG)
            folder_closed_path = os.path.join(assets_path, 'folder.png')
            folder_closed_image = Image.open(folder_closed_path)
            folder_closed_image = folder_closed_image.resize((16, 16), Image.Resampling.LANCZOS)
            self.folder_closed_icon = ImageTk.PhotoImage(folder_closed_image)
            
            # Cargar icono de carpeta abierta (PNG)
            folder_open_path = os.path.join(assets_path, 'open folder.png')
            folder_open_image = Image.open(folder_open_path)
            folder_open_image = folder_open_image.resize((16, 16), Image.Resampling.LANCZOS)
            self.folder_open_icon = ImageTk.PhotoImage(folder_open_image)
            
        except Exception as e:
            print(f"Error cargando icono HOOP: {e}")
            # Fallback final a iconos de texto
            self.file_icon = None
            self.folder_closed_icon = None
            self.folder_open_icon = None
    
    def load_directory(self, path=None):
        """Cargar el directorio en el treeview"""
        if path is None:
            # Obtener el directorio del proyecto (subir desde src)
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.dirname(current_dir)  # Directorio raíz del proyecto
            self.project_root = path # Guardar la raíz del proyecto
        else:
            self.project_root = path # Guardar la raíz del proyecto
        
        # Limpiar el tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insertar el directorio raíz
        project_name = os.path.basename(path)
        root_node = self.tree.insert('', 'end', text=f"{project_name}", 
                                    values=[path], open=True, image=self.folder_open_icon, tags=('folder',))
        
        # Cargar contenido del directorio raíz
        self.load_folder_contents(root_node, path)
    
    def load_folder_contents(self, parent_node, folder_path):
        """Cargar el contenido de una carpeta"""
        try:
            items = os.listdir(folder_path)
            items.sort()
            
            # Separar carpetas y archivos
            folders = []
            files = []
            
            for item in items:
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    folders.append((item, item_path))
                else:
                    files.append((item, item_path))
            
            # Insertar carpetas primero
            for folder_name, folder_path in folders:
                if not folder_name.startswith('.'):  # Ignorar carpetas ocultas
                    if hasattr(self, 'folder_closed_icon') and self.folder_closed_icon:
                        folder_node = self.tree.insert(parent_node, 'end', 
                                                     text=f"{folder_name}",
                                                     values=[folder_path], image=self.folder_closed_icon, tags=('folder',))
                    else:
                        folder_node = self.tree.insert(parent_node, 'end', 
                                                     text=f"{folder_name}",
                                                     values=[folder_path], image=self.folder_open_icon, tags=('folder',))
                    # Insertar un item dummy para mostrar la flecha de expansión
                    self.tree.insert(folder_node, 'end', text="", values=["dummy"], tags=('folder',))
            
            # Insertar archivos después
            for file_name, file_path in files:
                if not file_name.startswith('.'):  # Ignorar archivos ocultas
                    if hasattr(self, 'file_icon') and self.file_icon:
                        self.tree.insert(parent_node, 'end', 
                                       text=f"{file_name}",
                                       values=[file_path], image=self.file_icon, tags=('file',))
                    else:
                        icon = self.get_file_icon(file_name)
                        self.tree.insert(parent_node, 'end', 
                                       text=f"{icon} {file_name}",
                                       values=[file_path], tags=('file',))
        
        except PermissionError:
            pass  # Ignorar carpetas sin permisos

    def get_selected_path(self):
        """Obtiene la ruta del directorio seleccionado o la raíz del proyecto."""
        selected_item = self.tree.focus()
        if not selected_item:
            # Si no hay nada seleccionado, usar la raíz del proyecto
            return getattr(self, 'project_root', None)
        
        # Obtener la ruta del item seleccionado
        item_values = self.tree.item(selected_item, 'values')
        if not item_values:
            return getattr(self, 'project_root', None)
            
        path = item_values[0]
        
        # Si es un archivo, devolver la carpeta que lo contiene
        if os.path.isfile(path):
            return os.path.dirname(path)
        # Si es una carpeta, devolver su ruta
        else:
            return path

    def refresh_node(self, node):
        """Refresca el contenido de un nodo en el treeview."""
        path = self.tree.item(node, 'values')[0]
        if os.path.isdir(path):
            # Eliminar hijos existentes (excepto el dummy)
            for child in self.tree.get_children(node):
                self.tree.delete(child)
            # Recargar contenido
            self.load_folder_contents(node, path)

    def create_new_folder(self, event=None):
        """Crea una nueva carpeta en la ubicación seleccionada."""
        target_path = self.get_selected_path()
        if not target_path:
            print("No se pudo determinar la ruta de destino.")
            return

        folder_name = simpledialog.askstring("Nueva Carpeta", "Ingrese el nombre de la nueva carpeta:")
        if folder_name:
            try:
                new_folder_path = os.path.join(target_path, folder_name)
                os.makedirs(new_folder_path)
                print(f"Carpeta creada: {new_folder_path}")
                # Refrescar el explorador para mostrar la nueva carpeta
                self.load_directory(self.project_root) # Solución simple: recargar todo
            except Exception as e:
                print(f"Error al crear la carpeta: {e}")

    def create_new_file(self, event=None):
        """Crea un nuevo archivo .hoop en la ubicación seleccionada."""
        target_path = self.get_selected_path()
        if not target_path:
            print("No se pudo determinar la ruta de destino.")
            return

        file_name = simpledialog.askstring("Nuevo Archivo", "Ingrese el nombre del nuevo archivo (sin extensión):")
        if file_name:
            try:
                # Añadir la extensión .hoop
                full_file_name = f"{file_name}.hoop"
                new_file_path = os.path.join(target_path, full_file_name)
                
                # Crear el archivo vacío
                with open(new_file_path, 'w') as f:
                    pass
                print(f"Archivo creado: {new_file_path}")
                # Refrescar el explorador para mostrar el nuevo archivo
                self.load_directory(self.project_root) # Solución simple: recargar todo
            except Exception as e:
                print(f"Error al crear el archivo: {e}")
    
    def on_drag_start(self, event):
        """Captura el elemento que se empieza a arrastrar."""
        item_id = self.tree.identify_row(event.y)
        if item_id:
            path = self.tree.item(item_id, "values")[0]
            self.drag_data["item"] = item_id
            self.drag_data["path"] = path

    def on_drag_motion(self, event):
        """Resalta el elemento de destino mientras se arrastra."""
        if not self.drag_data["item"]:
            return

        target_id = self.tree.identify_row(event.y)
        
        # Limpiar el resaltado anterior si es diferente al actual
        if self.last_highlighted and self.last_highlighted != target_id:
            self.tree.item(self.last_highlighted, tags=self.tree.item(self.last_highlighted, 'tags'))
            self.last_highlighted = None

        if target_id and target_id != self.drag_data["item"]:
            # Resaltar el destino
            self.tree.selection_set(target_id)
            self.last_highlighted = target_id

    def on_drop(self, event):
        """Maneja la lógica de soltar el elemento."""
        # Limpiar resaltado
        if self.last_highlighted:
            self.tree.item(self.last_highlighted, tags=self.tree.item(self.last_highlighted, 'tags'))
            self.last_highlighted = None

        # Elemento de destino (donde se suelta el ratón)
        target_id = self.tree.identify_row(event.y)
        
        # Si no hay un origen, no hacer nada
        if not self.drag_data["path"]:
            self.reset_drag_data()
            return

        source_path = self.drag_data["path"]
        
        # Si no hay un destino claro, usar la raíz del proyecto
        if not target_id:
            # Verificar si la raíz del proyecto está definida
            if not hasattr(self, 'project_root') or not self.project_root:
                print("Error: La raíz del proyecto no está definida.")
                self.reset_drag_data()
                return
            
            dest_dir = self.project_root
            # Obtener el ID del nodo raíz
            root_nodes = self.tree.get_children('')
            if not root_nodes:
                self.reset_drag_data()
                return
            dest_parent_id = root_nodes[0]

        else:
            # Si el origen y el destino son el mismo, no hacer nada
            if target_id == self.drag_data["item"]:
                self.reset_drag_data()
                return

            target_item_values = self.tree.item(target_id, "values")
            if not target_item_values:
                self.reset_drag_data()
                return
            target_item_path = target_item_values[0]

            # Determinar el directorio de destino
            if os.path.isdir(target_item_path):
                dest_dir = target_item_path
                dest_parent_id = target_id
            else:
                dest_dir = os.path.dirname(target_item_path)
                dest_parent_id = self.tree.parent(target_id)

        # --- Validaciones ---
        # No mover una carpeta dentro de sí misma o de sus hijos
        if os.path.isdir(source_path) and dest_dir.startswith(source_path):
            print("Error: No se puede mover una carpeta a su interior.")
            self.reset_drag_data()
            return
        
        # No mover al mismo lugar
        if dest_dir == os.path.dirname(source_path):
            self.reset_drag_data()
            return

        # --- Mover y Actualizar UI ---
        try:
            # 1. Mover el archivo/carpeta en el sistema de archivos
            shutil.move(source_path, dest_dir)
            
            # 2. Actualizar la ruta interna del item en el Treeview (CRUCIAL)
            new_path = os.path.join(dest_dir, os.path.basename(source_path))
            self.tree.item(self.drag_data["item"], values=[new_path])

            # 3. Mover el elemento visualmente en el Treeview
            source_id = self.drag_data["item"]
            self.tree.move(source_id, dest_parent_id, 'end')

        except Exception as e:
            print(f"Error al mover el elemento: {e}")
        finally:
            self.reset_drag_data()

    def reset_drag_data(self):
        """Limpia los datos del elemento arrastrado."""
        self.drag_data["item"] = None
        self.drag_data["path"] = None
        self.last_highlighted = None

    def on_file_double_click(self, event):
        """Manejar el doble clic en un archivo"""
        selected_item = self.tree.focus()
        if selected_item:
            item_values = self.tree.item(selected_item, 'values')
            if item_values:
                file_path = item_values[0]
                if os.path.isfile(file_path):
                    # Notificar a la ventana principal que muestre el content_area
                    # y cargue el archivo
                    self.master.master.show_content_area()
                    self.master.master.content_area.load_file(file_path)
    
    def on_folder_open(self, event):
        """Manejar la apertura de carpetas"""
        item = self.tree.focus()
        if item:
            # Obtener la ruta de la carpeta
            values = self.tree.item(item, 'values')
            if values and len(values) > 0:
                folder_path = values[0]
                
                # Verificar si es una carpeta real (no dummy)
                if folder_path != "dummy" and os.path.isdir(folder_path):
                    # Verificar si la carpeta ya tiene contenido cargado (no dummy)
                    children = self.tree.get_children(item)
                    has_dummy = False
                    has_real_content = False
                    
                    for child in children:
                        child_values = self.tree.item(child, 'values')
                        if child_values and child_values[0] == "dummy":
                            has_dummy = True
                        else:
                            has_real_content = True
                    
                    # Solo cargar contenido si no ha sido cargado antes
                    if has_dummy and not has_real_content:
                        # Eliminar items dummy
                        for child in children:
                            child_values = self.tree.item(child, 'values')
                            if child_values and child_values[0] == "dummy":
                                self.tree.delete(child)
                        
                        # Cargar contenido de la carpeta
                        self.load_folder_contents(item, folder_path)
                    
                    # Cambiar icono a carpeta abierta
                    if hasattr(self, 'folder_open_icon') and self.folder_open_icon:
                        self.tree.item(item, image=self.folder_open_icon)

    def on_folder_close(self, event):
        """Manejar el cierre de carpetas"""
        item = self.tree.focus()
        if item:
            # Cambiar icono a carpeta cerrada
            if hasattr(self, 'folder_closed_icon') and self.folder_closed_icon:
                self.tree.item(item, image=self.folder_closed_icon)

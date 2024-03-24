from tkinter import *
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import math
import random

class App:
    def __init__(self, master):
        # Crear la ventana principal
        self.master = master

        # Crear el menú
        self.menu = Menu(self.master)
        self.master.config(menu=self.menu)

        # Crear el submenú "Archivo"
        self.file_menu = Menu(self.menu)
        self.menu.add_cascade(label="Archivo", menu=self.file_menu)
        self.file_menu.add_command(label="Abrir imagen (Ctrl+A)", command=self.open_image, accelerator="Ctrl+A")
        self.file_menu.add_command(label="Salir", command=self.master.quit)

        # Crear el lienzo para la imagen
        self.canvas = Canvas(self.master, width=640, height=480)
        self.canvas.pack(side=LEFT)

        # Crear el marco para la tabla
        self.table_frame = Frame(self.master)
        self.table_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # Crear la tabla
        self.tree = ttk.Treeview(self.table_frame, columns=("Elemento", "Medida"), show="headings")
        self.tree.heading("Elemento", text="Elemento")
        self.tree.heading("Medida", text="Medida")
        self.tree.pack(fill=BOTH, expand=True)

        # Crear el cuadro de texto para la distancia real
        self.entry = Entry(self.master)
        self.entry.insert(0, "1")
        self.entry.pack()

        # Crear el botón para establecer la escala
        self.scale_button = Button(self.master, text="Establecer escala", command=self.set_scale)
        self.scale_button.pack()

        # Crear la etiqueta para el factor de escala
        self.scale_label = Label(self.master, text="")
        self.scale_label.pack()

        # Crear el menú desplegable para las unidades
        self.unit_var = StringVar(self.master)
        self.unit_var.set("um")  # valor por defecto
        self.unit_menu = OptionMenu(self.master, self.unit_var, "um", "nm", "mm", "cm", "m")
        self.unit_menu.pack()

        # Inicializar las variables
        self.dist_real = None
        self.dist_img = None
        self.scale_factor = None
        self.points = []
        self.measurements = 0

        # Vincular el evento de clic del ratón al lienzo
        self.canvas.bind("<Button-1>", self.get_mouse_pos)

        # Vincular la combinación de teclas Ctrl+A a la acción de abrir un archivo
        self.master.bind("<Control-a>", lambda event: self.open_image())

    def get_mouse_pos(self, event):
        # Almacenar la posición del ratón y dibujar un círculo en esa posición
        self.points.append((event.x, event.y))
        if len(self.points) == 1:
            self.color = "#%06x" % random.randint(0, 0xFFFFFF)
            self.canvas.create_oval(event.x-5, event.y-5, event.x+5, event.y+5, fill=self.color)
        elif len(self.points) == 2:
            # Calcular la distancia entre los dos puntos y dibujar una línea entre ellos
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]
            self.dist_img = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            self.canvas.create_oval(event.x-5, event.y-5, event.x+5, event.y+5, fill=self.color)
            self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=3)
            self.points = []
            if self.scale_factor is not None:
                # Calcular la distancia real y añadirla a la tabla
                real_dist = self.dist_img * self.scale_factor
                self.measurements += 1
                self.tree.insert("", "end", values=(f"Elemento {self.measurements}", f"{real_dist} {self.unit_var.get()}"))

    def set_scale(self):
        # Establecer el factor de escala y actualizar la etiqueta y el botón correspondientes
        self.dist_real = float(self.entry.get())
        if self.dist_img is not None and self.dist_real is not None:
            self.scale_factor = self.dist_real / self.dist_img
            self.scale_label.config(text=f"Factor de escala: {self.scale_factor}")
            if self.scale_button.cget("text") == "Establecer escala":
                self.scale_button.config(text="Reestablecer escala")
            else:
                self.scale_button.config(text="Establecer escala")
                self.entry.delete(0, END)
                self.entry.insert(0, "1")
                self.scale_factor = None
                self.canvas.delete("all")
                self.tree.delete(*self.tree.get_children())
                self.canvas.create_image(0, 0, image=self.photo, anchor=NW)

    def open_image(self):
        # Abrir una imagen y mostrarla en el lienzo
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            # Redimensionar la imagen manteniendo la proporción
            self.image.thumbnail((640, 480), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)

root = Tk()
app = App(root)
root.mainloop()

from tkinter import *
from tkinter import filedialog, ttk, simpledialog
from PIL import Image, ImageTk
import math
import random
import os
import itertools

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
        self.tree = ttk.Treeview(self.table_frame, columns=("Item", "Elemento", "Perímetro", "Área", "Longitud"), show="headings")
        self.tree.column("Item",anchor=CENTER,stretch=NO,width=70)
        self.tree.heading("Item", text="Item")
        self.tree.column("Elemento",anchor=CENTER,stretch=NO,width=70)
        self.tree.heading("Elemento", text="Elemento")
        self.tree.column("Perímetro",anchor=CENTER,stretch=NO,width=70)
        self.tree.heading("Perímetro", text="Perímetro")
        self.tree.column("Área",anchor=CENTER,stretch=NO,width=70)
        self.tree.heading("Área", text="Área")
        self.tree.column("Longitud",anchor=CENTER,stretch=NO,width=70)
        self.tree.heading("Longitud", text="Longitud")
        self.tree.pack(fill=BOTH, expand=True)

        # Crear el botón para establecer la escala
        self.scale_button = Button(self.master, text="Establecer escala", command=self.open_scale_dialog)
        self.scale_button.pack()

        # Crear el botón para trazar con nodos
        self.trace_button = Button(self.master, text="Trazar con nodos", command=self.toggle_trace_mode)
        self.trace_button.pack()

        # Crear la etiqueta para el factor de escala
        self.scale_label = Label(self.master, text="")
        self.scale_label.pack()

        # Crear la etiqueta para el perímetro
        self.perimeter_label = Label(self.master, text="")
        self.perimeter_label.pack()

        # Inicializar las variables
        self.dist_real = None
        self.dist_img = None
        self.scale_factor = None
        self.points = []
        self.measurements = 0
        self.trace_mode = False
        self.color = "#000000"  # Inicializar el color a negro
        self.file_name = None
        self.longest_line = None

        # Vincular el evento de clic del ratón al lienzo
        self.canvas.bind("<Button-1>", self.get_mouse_pos)

        # Vincular la combinación de teclas Ctrl+A a la acción de abrir un archivo
        self.master.bind("<Control-a>", lambda event: self.open_image())

    def get_mouse_pos(self, event):
        # Almacenar la posición del ratón y dibujar un círculo en esa posición
        self.points.append((event.x, event.y))
        self.canvas.create_oval(event.x-5, event.y-5, event.x+5, event.y+5, fill=self.color)
        if len(self.points) >= 2:
            # Calcular la distancia entre los dos puntos y dibujar una línea entre ellos
            x1, y1 = self.points[-2]
            x2, y2 = self.points[-1]
            dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=3)
            if not self.trace_mode:
                self.dist_img = dist
                self.points = []

    def open_scale_dialog(self):
        # Abrir un cuadro de diálogo para establecer la escala
        dialog = Toplevel(self.master)
        dialog.title("Establecer escala")

        # Crear el cuadro de texto para la medida conocida
        known_measure_label = Label(dialog, text="Medida conocida:")
        known_measure_label.pack()
        self.known_measure_entry = Entry(dialog)
        self.known_measure_entry.pack()

        # Crear el menú desplegable para las unidades
        self.unit_var = StringVar(dialog)
        self.unit_var.set("um")  # valor por defecto
        unit_menu = OptionMenu(dialog, self.unit_var, "um", "nm", "mm", "cm", "m")
        unit_menu.pack()

        # Crear el botón para medir la distancia
        measure_button = Button(dialog, text="Medir distancia conocida", command=self.measure_known_distance)
        measure_button.pack()

        # Crear el botón para establecer la escala
        set_scale_button = Button(dialog, text="Establecer", command=self.set_scale)
        set_scale_button.pack()

    def measure_known_distance(self):
        # Medir la distancia conocida
        self.dist_real = float(self.known_measure_entry.get())

    def set_scale(self):
        # Establecer el factor de escala y actualizar la etiqueta correspondiente
        if self.dist_img is not None and self.dist_real is not None:
            self.scale_factor = self.dist_real / self.dist_img
            self.scale_label.config(text=f"Factor de escala: {self.scale_factor}")

    def toggle_trace_mode(self):
        # Activar o desactivar el modo de trazado
        self.trace_mode = not self.trace_mode
        if self.trace_mode:
            self.trace_button.config(text="Finalizar trazo")
            self.color = "#%06x" % random.randint(0, 0xFFFFFF)  # Generar un nuevo color aleatorio
        else:
            self.trace_button.config(text="Trazar con nodos")
            if len(self.points) > 2:
                # Unir el último punto con el primero y calcular el perímetro
                x1, y1 = self.points[0]
                x2, y2 = self.points[-1]
                dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=3)
                # Calcular el perímetro
                perimeter = sum(math.sqrt((x2 - x1)**2 + (y2 - y1)**2) for (x1, y1), (x2, y2) in zip(self.points, self.points[1:] + [self.points[0]]))
                # Calcular el área
                area = 0.5 * abs(sum(x1*y2 - x2*y1 for (x1, y1), (x2, y2) in zip(self.points, self.points[1:] + [self.points[0]])))
                if self.scale_factor is not None:
                    # Calcular el perímetro real y mostrarlo en la etiqueta
                    real_perimeter = perimeter * self.scale_factor
                    self.perimeter_label.config(text=f"Perímetro: {real_perimeter} {self.unit_var.get()}")
                    # Calcular el área real
                    real_area = area * (self.scale_factor ** 2)
                    # Calcular la longitud real
                    longest_distance = max(math.sqrt((x2 - x1)**2 + (y2 - y1)**2) for (x1, y1), (x2, y2) in itertools.combinations(self.points, 2))
                    real_longest_distance = longest_distance * self.scale_factor
                    # Añadir el número de elemento, el perímetro real, el área y la longitud a la tabla
                    self.measurements += 1
                    self.tree.insert("", "end", values=(self.measurements, f"{self.file_name}_{str(self.measurements).zfill(4)}", f"{real_perimeter} {self.unit_var.get()}", f"{real_area} {self.unit_var.get()}^2", f"{real_longest_distance} {self.unit_var.get()}"))
                    # Añadir el número de elemento al lienzo
                    self.canvas.create_text(sum(x for x, y in self.points) / len(self.points), sum(y for x, y in self.points) / len(self.points), text=str(self.measurements), fill=self.color, font=("Arial", 16))
                    # Dibujar la línea más larga
                    longest_pair = max(itertools.combinations(self.points, 2), key=lambda pair: math.sqrt((pair[1][0] - pair[0][0])**2 + (pair[1][1] - pair[0][1])**2))
                    self.longest_line = self.canvas
                                        # Dibujar la línea más larga
                    longest_pair = max(itertools.combinations(self.points, 2), key=lambda pair: math.sqrt((pair[1][0] - pair[0][0])**2 + (pair[1][1] - pair[0][1])**2))
                    self.longest_line = self.canvas.create_line(longest_pair[0][0], longest_pair[0][1], longest_pair[1][0], longest_pair[1][1], fill=self.color, width=1, arrow=BOTH)
            self.points = []

    def open_image(self):
        # Abrir una imagen y mostrarla en el lienzo
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            # Redimensionar la imagen manteniendo la proporción
            self.image.thumbnail((640, 480), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
            # Obtener el nombre del archivo sin la extensión
            self.file_name = os.path.splitext(os.path.basename(file_path))[0]

root = Tk()
app = App(root)
root.mainloop()

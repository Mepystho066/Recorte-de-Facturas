import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from PIL import Image, ImageTk

from config.pdf_config import (
    obtener_info_pdf,
    crear_vista_previa,
    table_order_list_word
)


class AppFacturacion(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Organizador de Facturas")
        self.geometry("1100x750")
        self.minsize(900, 650)
        self.configure(bg="#1e1e2e")

        self.bg = "#1e1e2e"
        self.bg_dark = "#181825"
        self.bg_panel = "#313244"
        self.bg_hover = "#45475a"
        self.bg_selected = "#585b70"
        self.fg = "#ffffff"
        self.fg_secondary = "#a6adc8"
        self.accent = "#89b4fa"

        self.archivos = []
        self.drag_index = None
        self.preview_image = None

        self.crear_interfaz()

    # =========================================================
    # INTERFAZ PRINCIPAL
    # =========================================================

    def crear_interfaz(self):
        self.crear_header()
        self.crear_contenido()
        self.crear_footer()

    # =========================================================
    # HEADER
    # =========================================================

    def crear_header(self):
        header = tk.Frame(self, bg=self.bg)
        header.pack(fill="x", padx=25, pady=(20, 15))

        tk.Label(
            header,
            text="Organizador de Facturas",
            bg=self.bg,
            fg=self.fg,
            font=("Arial", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Selecciona, revisa y organiza tus documentos PDF",
            bg=self.bg,
            fg=self.fg_secondary,
            font=("Arial", 10)
        ).pack(anchor="w", pady=(4, 0))

    # =========================================================
    # CONTENIDO
    # =========================================================

    def crear_contenido(self):
        content = tk.Frame(self, bg=self.bg)
        content.pack(fill="both",expand=True,padx=25,pady=(0, 15))

        self.crear_panel_archivos(content)
        self.crear_panel_previsualizacion(content)

    # =========================================================
    # PANEL DE ARCHIVOS
    # =========================================================

    def crear_panel_archivos(self, parent):
        panel = tk.Frame(parent,bg=self.bg_dark,highlightthickness=1,highlightbackground=self.bg_panel)

        panel.pack(side="left",fill="both",expand=True,padx=(0, 8))

        # Encabezado
        header = tk.Frame(panel, bg=self.bg_dark)
        header.pack(fill="x", padx=15, pady=15)

        tk.Label(header,text="Archivos",bg=self.bg_dark,fg=self.fg,font=("Arial", 13, "bold")).pack(side="left")

        self.file_count = tk.Label(header,text="0 archivos",bg=self.bg_dark,fg=self.fg_secondary,font=("Arial", 9) )

        self.file_count.pack(side="right")

        # Lista
        list_container = tk.Frame(panel,bg=self.bg_dark)

        list_container.pack(fill="both",expand=True,padx=15)

        scrollbar = tk.Scrollbar(
            list_container
        )

        scrollbar.pack(side="right",fill="y")

        self.file_list = tk.Listbox(
            list_container,
            bg=self.bg,
            fg=self.fg,
            selectbackground=self.bg_selected,
            selectforeground=self.fg,
            activestyle="none",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Arial", 10),
            yscrollcommand=scrollbar.set
        )

        self.file_list.pack(side="left",fill="both",expand=True)

        scrollbar.config(
            command=self.file_list.yview
        )

        self.file_list.bind("<<ListboxSelect>>",self.seleccionar_archivo)

        self.file_list.bind("<Button-1>",self.start_drag)

        self.file_list.bind("<B1-Motion>",self.drag_motion)

        self.file_list.bind("<ButtonRelease-1>",self.end_drag)

        buttons = tk.Frame(panel,bg=self.bg_dark)

        buttons.pack(fill="x",padx=15,pady=15)

        self.crear_boton(buttons,"Seleccionar carpeta",self.select_file
        ).pack(side="left",fill="x",expand=True)

        self.crear_boton(buttons,"Eliminar",self.delete_selected
        ).pack(side="left",padx=(8, 0))

    def crear_panel_previsualizacion(self, parent):
        panel = tk.Frame(parent,bg=self.bg_dark,highlightthickness=1,highlightbackground=self.bg_panel)

        panel.pack(side="right",fill="both",expand=True,padx=(8, 0))

        # Título
        tk.Label(panel,text="Vista previa",bg=self.bg_dark,fg=self.fg,font=("Arial", 13, "bold")
        ).pack(anchor="w",padx=15,pady=(15, 10))

        # Información
        info_frame = tk.Frame(panel,bg=self.bg_panel)

        info_frame.pack(fill="x",padx=15
        )

        self.info_label = tk.Label(
            info_frame,
            text="Selecciona un archivo para ver su información",
            bg=self.bg_panel,
            fg=self.fg_secondary,
            justify="left",
            anchor="w",
            font=("Arial", 9),
            padx=12,
            pady=12
        )

        self.info_label.pack(fill="x")

        # Imagen
        preview_container = tk.Frame(panel,bg=self.bg)

        preview_container.pack(fill="both",expand=True,padx=15,pady=15)

        self.preview_label = tk.Label(preview_container,text="No hay documento seleccionado",bg=self.bg,fg=self.fg_secondary,font=("Arial", 10))

        self.preview_label.pack(fill="both",expand=True)

    def crear_footer(self):
        footer = tk.Frame(self,bg=self.bg)

        footer.pack(fill="x",padx=25,pady=(0, 20))

        # Consola
        console_frame = tk.Frame(footer,bg=self.bg_dark,highlightthickness=1,highlightbackground=self.bg_panel)

        console_frame.pack(fill="x")

        tk.Label(console_frame,text="Actividad",bg=self.bg_dark,fg=self.fg,font=("Arial", 10, "bold")
        ).pack(anchor="w",padx=12,pady=(8, 3))

        self.console = tk.Text(
            console_frame,
            height=5,
            bg=self.bg,
            fg=self.fg_secondary,
            insertbackground=self.fg,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Consolas", 9),
            state="disabled"
        )

        self.console.pack(fill="x",padx=12,pady=(0, 10))

        # Botones inferiores
        actions = tk.Frame(footer,bg=self.bg)

        actions.pack(fill="x",pady=(10, 0))

        self.crear_boton(actions,"Guardar",self.save
        ).pack(side="right",padx=(0, 8))

    def crear_boton(self, parent, texto, comando):
        return tk.Button(
            parent,
            text=texto,
            command=comando,
            bg=self.bg_panel,
            fg=self.fg,
            activebackground=self.bg_hover,
            activeforeground=self.fg,
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            cursor="hand2"
        )

    def select_file(self):
        carpeta = filedialog.askdirectory(
            title="Seleccionar carpeta"
        )

        if not carpeta:
            return

        self.file_list.delete(
            0,
            tk.END
        )

        self.archivos.clear()

        try:
            archivos = sorted(
                archivo
                for archivo in os.listdir(carpeta)
                if archivo.lower().endswith(".pdf")
            )

            for archivo in archivos:
                ruta = os.path.join(
                    carpeta,
                    archivo
                )

                self.archivos.append(ruta)

                self.file_list.insert(
                    tk.END,
                    archivo
                )

            self.actualizar_contador()

            self.write_console(
                f"Carpeta seleccionada: {carpeta}"
            )

            self.write_console(
                f"PDF encontrados: {len(archivos)}"
            )

        except Exception as e:
            self.write_console(
                f"ERROR: {e}"
            )

            messagebox.showerror(
                "Error",
                str(e)
            )

    def seleccionar_archivo(self, event=None):
        seleccion = self.file_list.curselection()

        if not seleccion:
            return

        index = seleccion[0]
        ruta = self.archivos[index]

        self.mostrar_informacion(ruta)
        self.mostrar_preview(ruta)

    def mostrar_informacion(self, ruta):
        try:
            info = obtener_info_pdf(ruta)

            texto = info["texto"].strip()

            if len(texto) > 500:
                texto = texto[:500] + "..."

            informacion = (
                f"Archivo: {info['nombre']}\n"
                f"Páginas: {info['paginas']}\n"
                f"Tamaño: {info['tamaño']}\n"
                f"Dimensiones: {info['ancho']} × {info['alto']}\n\n"
                f"Texto:\n{texto}"
            )

            self.info_label.config(
                text=informacion,
                fg=self.fg
            )

        except Exception as e:
            self.info_label.config(
                text=f"No se pudo leer el documento:\n{e}",
                fg="#f38ba8"
            )



    def mostrar_preview(self, ruta):
        try:
            nombre = os.path.basename(ruta)

            salida = os.path.join(
                tempfile.gettempdir(),
                f"preview_{os.getpid()}.png"
            )

            resultado = crear_vista_previa(
                ruta,
                salida
            )

            if not resultado or not os.path.exists(salida):
                self.preview_label.config(
                    image="",
                    text="No se pudo detectar la zona del documento",
                    fg="#f38ba8"
                )
                return

            image = Image.open(salida)

            image.thumbnail(
                (500, 400),
                Image.Resampling.LANCZOS
            )

            self.preview_image = ImageTk.PhotoImage(
                image
            )

            self.preview_label.config(
                image=self.preview_image,
                text=""
            )

            self.write_console(
                f"Vista previa generada: {nombre}"
            )

        except Exception as e:
            self.preview_label.config(image="",text=f"Error generando vista previa:\n{e}",fg="#f38ba8")

    def start_drag(self, event):
        self.drag_index = self.file_list.nearest(
            event.y
        )

    def drag_motion(self, event):
        if self.drag_index is None:
            return

        new_index = self.file_list.nearest(
            event.y
        )

        total = self.file_list.size()

        if total == 0:
            return

        new_index = max(
            0,
            min(new_index, total - 1)
        )

        if new_index == self.drag_index:
            return

        texto = self.file_list.get(
            self.drag_index
        )

        archivo = self.archivos.pop(
            self.drag_index
        )

        self.file_list.delete(
            self.drag_index
        )

        self.file_list.insert(
            new_index,
            texto
        )

        self.archivos.insert(
            new_index,
            archivo
        )

        self.drag_index = new_index

        self.file_list.selection_clear(
            0,
            tk.END
        )

        self.file_list.selection_set(
            new_index
        )

    def end_drag(self, event):
        self.drag_index = None

    def delete_selected(self):
        seleccion = self.file_list.curselection()

        if not seleccion:
            self.write_console(
                "No hay ningún archivo seleccionado."
            )
            return

        index = seleccion[0]
        nombre = self.file_list.get(index)

        self.file_list.delete(index)
        self.archivos.pop(index)

        self.actualizar_contador()

        self.preview_label.config(
            image="",
            text="No hay documento seleccionado"
        )

        self.info_label.config(
            text="Selecciona un archivo para ver su información"
        )

        self.write_console(
            f"Archivo eliminado: {nombre}"
        )


    def actualizar_contador(self):
        cantidad = len(self.archivos)

        texto = (
            "1 archivo"
            if cantidad == 1
            else f"{cantidad} archivos"
        )

        self.file_count.config(
            text=texto
        )

    def write_console(self, texto):
        self.console.config(
            state="normal"
        )

        self.console.insert(
            tk.END,
            texto + "\n"
        )

        self.console.see(
            tk.END
        )

        self.console.config(
            state="disabled"
        )

    def save(self):
        if not self.archivos:
            messagebox.showwarning(
                "Sin archivos",
                "No hay archivos para guardar."
            )
            return

        ruta = filedialog.asksaveasfilename(
            title="Guardar documento",
            defaultextension=".docx",
            filetypes=[
                ("Documento Word", "*.docx")
            ]
        )

        if not ruta:
            return

        try:
            resultado = table_order_list_word(
                self.archivos,
                ruta
            )

            self.write_console(
                resultado
            )

            messagebox.showinfo(
                "Proceso completado",
                resultado
            )

        except Exception as e:
            self.write_console(
                f"ERROR: {e}"
            )

            messagebox.showerror(
                "Error",
                str(e)
            )


if __name__ == "__main__":
    app = AppFacturacion()
    app.mainloop()

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, 
                             QLabel, QFileDialog, QAbstractItemView,QLineEdit)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon,QColor

from datetime import datetime
from config.pdf_config import table_order_list_word

from pathlib import Path
from src.style import style
ruta_descargas = Path.home() 

def fecha_actual():
    date_time = datetime.now()
    fecha_formateada = date_time.strftime("%d-%m-%Y")
    return fecha_formateada

class OrganizadorDocumentos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organizador de Documentos")
        self.setMinimumSize(500, 600)
        
        # Estilo visual moderno (Dark mode elegante)
        self.setStyleSheet(style)

        # Widget central y Layout principal
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout = QVBoxLayout(widget_central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 1. Zona de selección de carpeta
        layout_superior = QHBoxLayout()
        self.lbl_carpeta = QLabel("Ninguna carpeta seleccionada")
        btn_seleccionar = QPushButton("Seleccionar Carpeta")
        btn_seleccionar.setObjectName("btn_buscar")
        btn_seleccionar.clicked.connect(self.seleccionar_carpeta)
        
        layout_superior.addWidget(self.lbl_carpeta, stretch=1)
        layout_superior.addWidget(btn_seleccionar)
        layout.addLayout(layout_superior)

        # Etiqueta informativa
        info_label = QLabel("Haz clic y arrastra los elementos para cambiar el orden:")
        info_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(info_label)

        # 2. Lista interactiva (Soporta arrastrar y soltar interno)
        self.lista_archivos = QListWidget()
        self.lista_archivos.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove) # Permite reordenar
        self.lista_archivos.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(self.lista_archivos)

        # 3. Botón de acción final
        self.btn_procesar = QPushButton("Procesar Documentos en este Orden")
        self.btn_procesar.clicked.connect(self.procesar_orden)
        layout.addWidget(self.btn_procesar)
        
        # 4. Barra para agregar el nombre para el documento final (opcional)
        info_label = QLabel("nombre del documento final (opcional):")
        layout.addWidget(info_label)
        
        self.input_nombre_doc = QLineEdit(f"Factura_{fecha_actual()}.docx")
        layout.addWidget(self.input_nombre_doc)

        # 5.Ventana de consola para mostrar el orden final de los documentos
        self.consola = QLabel()
        self.consola.setText("Consola de salida:")
        self.consola.setFont(QFont("Arial", 10))
        self.consola.setStyleSheet("background-color: #1e1e2e; color: #ffffff; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.consola)

    def seleccionar_carpeta(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta con Documentos")
        if carpeta:
            self.lbl_carpeta.setText(os.path.basename(carpeta))
            self.lista_archivos.clear()
            
            # Filtrar y cargar archivos de la carpeta
            for archivo in os.listdir(carpeta):
                ruta_completa = os.path.join(carpeta, archivo)
                if os.path.isfile(ruta_completa):
                    item = QListWidgetItem(f"📄 {archivo}")
                    # Guardamos la ruta real oculta dentro del item para usarla después
                    #item.setBackground(QColor("#1e1e2e"))
                    item.setData(Qt.ItemDataRole.UserRole, ruta_completa)
                    self.lista_archivos.addItem(item)

    def procesar_orden(self):
        conteo = self.lista_archivos.count()
        ruta_archivo = []
        if conteo == 0:
            print("No hay archivos en la lista.")
            return
            
        print("\n--- PROCESANDO EN EL ORDEN ELEGIDO ---")
        for i in range(conteo):
            item = self.lista_archivos.item(i)
            ruta_archivo.append(item.data(Qt.ItemDataRole.UserRole))
            print(f"Posición {i+1}: {ruta_archivo[i]}")
        table_order_list_word(ruta_archivo, f"{ruta_descargas}/{self.input_nombre_doc.text()}")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = OrganizadorDocumentos()
    ventana.show()
    sys.exit(app.exec())
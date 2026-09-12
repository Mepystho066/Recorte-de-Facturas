import os
import pymupdf  # PyMuPDF
from docx import Document
from docx.shared import Inches
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from pathlib import Path

ruta_descargas = Path.home() 
def encontrar_zona_por_lineas(pagina, ancho_minimo, tolerancia=2):
   
    lineas_horizontales = []  # (x0, x1, y, ancho)
    lineas_verticales = []    # (x, y0, y1, alto)

    for dibujo in pagina.get_drawings():
        for item in dibujo["items"]:
            tipo = item[0]

            if tipo == "l":
                p1, p2 = item[1], item[2]
                x0, x1 = sorted([p1.x, p2.x])
                y0, y1 = sorted([p1.y, p2.y])
            elif tipo == "re":
                r = item[1]
                x0, x1, y0, y1 = r.x0, r.x1, r.y0, r.y1
            else:
                continue

            ancho = x1 - x0
            alto = y1 - y0

            if ancho > ancho_minimo and alto <= tolerancia:
                lineas_horizontales.append((x0, x1, y0, ancho))
            elif alto > tolerancia and ancho <= tolerancia:
                lineas_verticales.append((x0, y0, y1, alto))

    if not lineas_horizontales:
        return None  
    x0, x1, y_inicio, _ = max(lineas_horizontales, key=lambda l: l[3])

    if lineas_verticales:
        
        _, _, _, altura = max(lineas_verticales, key=lambda l: l[3])
        y_fin = y_inicio + altura
    else:
        y_fin = pagina.rect.y1

    return pymupdf.Rect(x0, y_inicio, x1, y_fin)


def recorte2(pdf_origen):
    doc = pymupdf.open(pdf_origen)

    UMBRAL_RELATIVO = 0.89  
    MIN_ALTURA_RECTANGULO = 5  
    MARGEN_INFERIOR = 70   

    imagen_temporal = None
    os.makedirs(f"{ruta_descargas}", exist_ok=True)

    numero_pagina = 0
    pagina = doc[numero_pagina]  

    ancho_minimo = pagina.rect.width * UMBRAL_RELATIVO
    rectangulos = []

    for dibujo in pagina.get_drawings():
        rect = dibujo["rect"]
        if rect.width > ancho_minimo and rect.height > MIN_ALTURA_RECTANGULO:
            rectangulos.append(rect)

    zona = None

    if rectangulos:
        rectangulo_mayor = max(rectangulos, key=lambda r: r.width * r.height)
        print(f"Rectángulo mayor encontrado en la página {numero_pagina}: {rectangulo_mayor}")

        zona = pymupdf.Rect(rectangulo_mayor)
        zona.y1 -= MARGEN_INFERIOR

    else:
        zona = encontrar_zona_por_lineas(pagina, ancho_minimo=ancho_minimo)
        if zona is not None:
            zona.y1 -= MARGEN_INFERIOR
            print(f"Zona por líneas detectada en la página {numero_pagina}: {zona}")

    if zona is not None:

        if zona.x1 <= zona.x0 or zona.y1 <= zona.y0:
            print(f"⚠️ Zona con coordenadas inválidas en la página {numero_pagina} de '{pdf_origen}': {zona}")
        else:
            zona &= pagina.rect  # recorta para no salirse de los límites de la página

            if zona.is_empty or zona.width <= 0 or zona.height <= 0:
                print(f"⚠️ Zona vacía tras ajustar a los límites de la página {numero_pagina} de '{pdf_origen}': {zona}")
            else:
                pix = pagina.get_pixmap(
                    clip=zona,
                    matrix=pymupdf.Matrix(2, 2)
                )
                imagen_temporal = f"{ruta_descargas}/recorte_temp.png"
                pix.save(imagen_temporal)

    return imagen_temporal


def table_order_list_word(lista, docx_path):

    if os.path.exists(docx_path):
        doc_word = Document(docx_path)
    else:
        doc_word = Document()

    filas = (len(lista)) // 2 if len(lista) % 2 == 0 else (len(lista) // 2) + 1
    table = doc_word.add_table(rows=filas, cols=2)
    for i, archivo in enumerate(lista):
        imagen_temporal = recorte2(archivo)

        if imagen_temporal is None or not os.path.exists(imagen_temporal):
            raise ValueError(f"⚠️ No se encontró rectángulo ni línea válida en '{archivo}', se omite.")
            continue

        fila = i // 2
        columna = i % 2
        cell = table.cell(fila, columna)
        cell.add_paragraph().add_run().add_picture(imagen_temporal, width=Inches(3))

        os.remove(imagen_temporal)

    doc_word.save(docx_path)

    return f"¡Proceso completado con éxito! Recortes añadidos a '{docx_path}'."


def read_directory(directory):
    try:
        archivos = os.listdir(directory)
        archivos = [f"{directory}/{archivo}" for archivo in archivos]
        return archivos
    except FileNotFoundError:
        print(f"El directorio '{directory}' no existe.")
        return []

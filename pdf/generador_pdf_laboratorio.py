from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import *

import os


def generar_pdf_laboratorio(lab):

    os.makedirs(
        "pdfs_laboratorio",
        exist_ok=True
    )

    ruta = f"pdfs_laboratorio/{lab.codigo}.pdf"

    documento = SimpleDocTemplate(
        ruta,
        pagesize=landscape(letter)
    )

    elementos = []

    elementos.append(

        Paragraph(
            "REGISTRO DE PRACTICA DE LABORATORIO",
            getSampleStyleSheet()["Title"]
        )

    )

    elementos.append(
        Spacer(1, 20)
    )

    tabla = Table([

        ["Laboratorio", lab.laboratorio],

        ["Asignatura", lab.asignatura],

        ["Carrera", lab.carrera],

        ["Semestre", lab.semestre],

        ["Docente", lab.docente_responsable]

    ])

    tabla.setStyle(

        TableStyle([

            ('GRID',(0,0),(-1,-1),1,colors.black),

            ('BACKGROUND',(0,0),(0,-1),colors.lightgrey)

        ])

    )

    elementos.append(tabla)

    elementos.append(
        Spacer(1,20)
    )

    elementos.append(
        Paragraph(
            "<b>Tema</b>",
            getSampleStyleSheet()['Heading2']
        )
    )

    elementos.append(
        Paragraph(
            lab.tema_practica,
            getSampleStyleSheet()['BodyText']
        )
    )

    elementos.append(
        Spacer(1,10)
    )

    elementos.append(
        Paragraph(
            "<b>Objetivo</b>",
            getSampleStyleSheet()['Heading2']
        )
    )

    elementos.append(
        Paragraph(
            lab.objetivo_practica,
            getSampleStyleSheet()['BodyText']
        )
    )

    documento.build(
        elementos
    )

    return ruta
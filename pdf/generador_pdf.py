from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
SimpleDocTemplate,
Table,
TableStyle,
Spacer,
Paragraph
)
from reportlab.lib.styles import getSampleStyleSheet

def texto_seguro(valor):

    if valor is None:
        return ""

    return str(valor)

def generar_pdf(practica, ruta_pdf):

    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    estilos = getSampleStyleSheet()

    elementos = []

    # ==================================================
    # ENCABEZADO
    # ==================================================

    encabezado = Table(
        [
            [
                "UNIVERSIDAD LAICA ELOY ALFARO DE MANABÍ\nFacultad de ciencias de la vida"

            ],
            [
                "PLANIFICACIÓN DE PRÁCTICAS DE CAMPO O LABORATORIO "
            ],
            [
                "Este formato tiene como finalidad planificar y registrar las prácticas de campo,\n"
                " laboratorio, planta piloto, vinculación o simulación, articuladas con el currículo,\n"
                " los resultados de aprendizaje, las competencias profesionales y los núcleos problémicos de cada carrera"
            ]
        ],
        colWidths=[550]
    )

    encabezado.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ])
    )

    elementos.append(encabezado)
    elementos.append(Spacer(1, 10))

    # ==================================================
    # DATOS INFORMATIVOS
    # ==================================================

    elementos.append(
        Table(
            [["1. DATOS INFORMATIVOS"]],
            colWidths=[550],
            style=[
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold")
            ]
        )
    )

    datos = [

        ["Código", texto_seguro(practica.codigo)],

        ["Carrera", texto_seguro(practica.carrera)],

        ["Semestre", texto_seguro(practica.semestre)],

        ["Asignatura", texto_seguro(practica.asignatura)],

        ["Unidad del Sílabo",
        texto_seguro(practica.unidad_silabo)],

        ["Tipo de Práctica",
        texto_seguro(practica.tipo_practica)],

        ["Docente Responsable",
        texto_seguro(practica.ingeniero_revisor)],

        ["Lugar de ejecución",
        texto_seguro(practica.lugar_ejecucion)],

        ["Semana planificada",
        texto_seguro(practica.semana_planificada)]
    ]

    tabla = Table(
        datos,
        colWidths=[180, 370]
    )

    tabla.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFEFEF")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ])
    )

    elementos.append(tabla)
    elementos.append(Spacer(1, 10))

    # ==================================================
    # DATOS ACADÉMICOS
    # ==================================================

    elementos.append(
        Table(
            [["2. DATOS ACADÉMICOS"]],
            colWidths=[550],
            style=[
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold")
            ]
        )
    )

    tema = Table(
        [
            ["Tema de la práctica"],
            [texto_seguro(practica.tema_practica)]
        ],
        colWidths=[550]
    )

    tema.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFEFEF")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("MINROWHEIGHT", (0, 1), (-1, 1), 60)
        ])
    )

    elementos.append(tema)
    elementos.append(Spacer(1, 5))

    resultado = Table(
        [
            ["Resultado de aprendizaje"],
            [texto_seguro(practica.resultado_aprendizaje)]
        ],
        colWidths=[550]
    )

    resultado.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFEFEF")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("MINROWHEIGHT", (0, 1), (-1, 1), 60)
        ])
    )

    elementos.append(resultado)
    elementos.append(Spacer(1, 5))

    articulacion = Table(
        [
            ["Articulación Curricular"],
            [texto_seguro(practica.articulacion_curricular)]
        ],
        colWidths=[550]
    )

    articulacion.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFEFEF")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
        ])
    )

    elementos.append(articulacion)
    elementos.append(Spacer(1, 10))

    # ==================================================
    # OBJETIVO GENERAL
    # ==================================================

    objetivo = Table(
        [
            ["2.1. OBJETIVO GENERAL"],
            [texto_seguro(practica.objetivo_general)]
        ],
        colWidths=[550]
    )

    objetivo.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("MINROWHEIGHT", (0, 1), (-1, 1), 70)
        ])
    )

    elementos.append(objetivo)
    elementos.append(Spacer(1, 10))

    # ==================================================
    # MATERIALES
    # ==================================================

    materiales = Table(
        [
            ["2.2. MATERIALES Y EQUIPOS"],
            [texto_seguro(practica.materiales_equipos)]
        ],
        colWidths=[550]
    )

    materiales.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("MINROWHEIGHT", (0, 1), (-1, 1), 70)
        ])
    )

    elementos.append(materiales)
    elementos.append(Spacer(1, 10))

    # ==================================================
    # DESCRIPCIÓN
    # ==================================================

    descripcion = Table(
        [
            ["2.4. DESCRIPCIÓN DE ACTIVIDADES"],
            [texto_seguro(practica.descripcion_actividad)]
        ],
        colWidths=[550]
    )

    descripcion.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("MINROWHEIGHT", (0, 1), (-1, 1), 120)
        ])
    )

    elementos.append(descripcion)
    elementos.append(Spacer(1, 10))

    # ==================================================
    # EVIDENCIAS
    # ==================================================

    evidencias = Table(
        [
            ["2.4. EVIDENCIA DE LA PRÁCTICA"],
            [texto_seguro(practica.evidencias)]
        ],
        colWidths=[550]
    )

    evidencias.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("MINROWHEIGHT", (0, 1), (-1, 1), 60)
        ])
    )

    elementos.append(evidencias)
    elementos.append(Spacer(1, 25))

    # ==================================================
    # FIRMAS
    # ==================================================

    firmas = Table(
        [
            ["", ""],
            ["____________________", "____________________"],
            [
                texto_seguro(f"Docente Responsable:\n {practica.ingeniero_revisor}"),
                "Comisión Académica"
            ]
        ],
        colWidths=[275, 275]
    )

    firmas.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ])
    )

    elementos.append(firmas)

    doc.build(elementos)

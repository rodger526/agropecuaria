import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer,
    Paragraph,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

RUTA_LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo_uleam.png")


def texto_seguro(valor):
    if valor is None:
        return ""
    return str(valor)


def _imagen_firma(ruta, width=120, height=50):
    """Devuelve un Image de reportlab si la ruta existe, o un string vacío."""
    if ruta and os.path.exists(ruta):
        return Image(ruta, width=width, height=height)
    return Paragraph("", ParagraphStyle("vacio"))


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

    estilo_celda = ParagraphStyle(
        "celda",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        alignment=TA_LEFT
    )

    estilo_celda_bold = ParagraphStyle(
        "celda_bold",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_LEFT
    )

    estilo_titulo_seccion = ParagraphStyle(
        "titulo_seccion",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        alignment=TA_LEFT
    )

    estilo_subtitulo = ParagraphStyle(
        "subtitulo",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_LEFT
    )

    estilo_institucional = ParagraphStyle(
        "institucional",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#3B3B3B")
    )

    estilo_intro = ParagraphStyle(
        "intro",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=8.3,
        leading=10.5,
        alignment=TA_JUSTIFY
    )

    estilo_firma_nombre = ParagraphStyle(
        "firma_nombre",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER
    )

    estilo_firma_cargo = ParagraphStyle(
        "firma_cargo",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555")
    )

    GRIS_CLARO  = colors.HexColor("#E7E7E7")
    GRIS_TITULO = colors.HexColor("#D9D9D9")

    elementos = []

    # ── ENCABEZADO ────────────────────────────────────────────────────
    if os.path.exists(RUTA_LOGO):
        logo = Image(RUTA_LOGO, width=130, height=46)
    else:
        logo = Paragraph("ULEAM", estilo_institucional)

    texto_facultad = Paragraph(
        "Facultad de Ciencias de la Vida<br/>y Tecnologías",
        estilo_institucional
    )

    encabezado_logo = Table(
        [[logo, texto_facultad]],
        colWidths=[275, 275]
    )
    encabezado_logo.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1, colors.black),
        ("LINEAFTER",     (0, 0), (0,  0),  1, colors.HexColor("#7FBF7F")),
        ("ALIGN",         (0, 0), (0,  0),  "LEFT"),
        ("ALIGN",         (1, 0), (1,  0),  "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (0,  0),  8),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elementos.append(encabezado_logo)

    # ── TÍTULO ────────────────────────────────────────────────────────
    titulo_formato = Table(
        [[
            Paragraph("PLANIFICACIÓN DE PRÁCTICAS DE CAMPO O LABORATORIO", estilo_titulo_seccion),
            Paragraph("Versión 1", estilo_subtitulo)
        ]],
        colWidths=[440, 110]
    )
    titulo_formato.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID",     (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elementos.append(titulo_formato)

    # ── INTRO ─────────────────────────────────────────────────────────
    intro = Table(
        [[Paragraph(
            "Este formato tiene como finalidad planificar y registrar las prácticas de campo, laboratorio, planta "
            "piloto, vinculación o simulación, articuladas con el currículo, los resultados de aprendizaje, las "
            "competencias profesionales y los núcleos problémicos de cada carrera.",
            estilo_intro
        )]],
        colWidths=[550]
    )
    intro.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1, colors.black),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elementos.append(intro)

    # ── 1. DATOS INFORMATIVOS ─────────────────────────────────────────
    elementos.append(Table(
        [[Paragraph("1.&nbsp;&nbsp;&nbsp;DATOS INFORMATIVOS", estilo_titulo_seccion)]],
        colWidths=[550],
        style=[
            ("BOX",           (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND",    (0, 0), (-1, -1), GRIS_TITULO),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    ))

    fecha_str = (
        practica.fecha_creacion.strftime("%d/%m/%Y  %H:%M")
        if practica.fecha_creacion else ""
    )

    datos = [
        ["Fecha de registro:",    fecha_str],
        ["Carrera:",              texto_seguro(practica.carrera)],
        ["Semestre:",             texto_seguro(practica.semestre)],
        ["Asignatura:",           texto_seguro(practica.asignatura)],
        ["Unidad del Sílabo:",    texto_seguro(practica.unidad_silabo)],
        ["Tipo de Práctica:",     texto_seguro(practica.tipo_practica)],
        ["Docente Responsable:",  texto_seguro(practica.ingeniero_revisor)],
        ["Lugar de ejecución:",   texto_seguro(practica.lugar_ejecucion)],
        ["Semana planificada:",   texto_seguro(practica.semana_planificada)],
    ]

    tabla = Table(
        [[Paragraph(f[0], estilo_celda_bold), Paragraph(f[1], estilo_celda)] for f in datos],
        colWidths=[180, 370]
    )
    tabla.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID",     (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elementos.append(tabla)

    # ── 2. DATOS ACADÉMICOS ───────────────────────────────────────────
    elementos.append(Table(
        [[Paragraph("2.&nbsp;&nbsp;&nbsp;DATOS ACADÉMICOS", estilo_titulo_seccion)]],
        colWidths=[550],
        style=[
            ("BOX",           (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND",    (0, 0), (-1, -1), GRIS_TITULO),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    ))

    academicos = [
        ["Tema de la Practica/Visita:",               texto_seguro(practica.tema_practica)],
        ["Resultado de aprendizaje de\nla asignatura:", texto_seguro(practica.resultado_aprendizaje)],
        ["Articulación curricular:",                   texto_seguro(practica.articulacion_curricular)],
    ]
    tabla_academicos = Table(
        [[Paragraph(f[0].replace("\n", "<br/>"), estilo_celda_bold), Paragraph(f[1], estilo_celda)] for f in academicos],
        colWidths=[180, 370]
    )
    tabla_academicos.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID",     (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("MINROWHEIGHT",  (0, 2), (-1, 2),  60),
    ]))
    elementos.append(tabla_academicos)

    # ── 2.1 OBJETIVO ──────────────────────────────────────────────────
    def _seccion_texto(titulo, contenido, min_height=70):
        t = Table(
            [
                [Paragraph(titulo, estilo_titulo_seccion)],
                [Paragraph(texto_seguro(contenido), estilo_celda)]
            ],
            colWidths=[550]
        )
        t.setStyle(TableStyle([
            ("BOX",           (0, 0), (-1, -1), 1, colors.black),
            ("LINEBELOW",     (0, 0), (-1,  0), 1, colors.black),
            ("BACKGROUND",    (0, 0), (-1,  0), GRIS_CLARO),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("MINROWHEIGHT",  (0, 1), (-1,  1), min_height),
            ("VALIGN",        (0, 1), (-1,  1), "TOP"),
        ]))
        return t

    elementos.append(_seccion_texto("2.1.&nbsp;&nbsp;&nbsp;OBJETIVO GENERAL DE LA PRÁCTICA",   practica.objetivo_general,     70))
    elementos.append(_seccion_texto("2.2.&nbsp;&nbsp;&nbsp;MATERIALES/RECURSOS Y EQUIPOS",      practica.materiales_equipos,   70))
    elementos.append(_seccion_texto("2.3.&nbsp;&nbsp;&nbsp;DESCRIPCIÓN DE LA ACTIVIDAD",        practica.descripcion_actividad, 120))
    elementos.append(_seccion_texto("2.4.&nbsp;&nbsp;&nbsp;EVIDENCIA DE LA PRÁCTICA",           practica.evidencias,           60))

    elementos.append(Spacer(1, 18))

    # ── FIRMAS ────────────────────────────────────────────────────────
    # Construir cada celda de firma de forma segura
    img_doc = _imagen_firma(practica.firma_docente, width=120, height=50)
    img_com = _imagen_firma(practica.firma_comision, width=120, height=50)

    nombre_docente  = texto_seguro(practica.ingeniero_revisor) or "Docente Responsable"
    nombre_comision = "Comisión Académica"

    firmas = Table(
        [
            # Fila 1: imágenes de firma
            [img_doc, img_com],
            # Fila 2: línea separadora visual (borde superior en estilo)
            [Paragraph(nombre_docente,  estilo_firma_nombre),
             Paragraph(nombre_comision, estilo_firma_nombre)],
            # Fila 3: cargo
            [Paragraph("Docente Responsable", estilo_firma_cargo),
             Paragraph("Comisión Académica",  estilo_firma_cargo)],
        ],
        colWidths=[275, 275]
    )
    firmas.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID",     (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        # Línea superior en fila de nombres (simula línea de firma)
        ("LINEABOVE",     (0, 1), (-1,  1), 0.8, colors.black),
        ("MINROWHEIGHT",  (0, 0), (-1,  0), 60),
    ]))
    elementos.append(firmas)

    doc.build(elementos)
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer,
    Paragraph,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ─── Colores institucionales (igual a la imagen de referencia) ───────
AZUL_CLARO   = colors.HexColor("#BDD7EE")   # encabezados de sección
AZUL_TABLA   = colors.HexColor("#9DC3E6")   # encabezado nómina estudiantes
VERDE_CLARO  = colors.HexColor("#C6E0B4")   # encabezado materiales/reactivos
GRIS_LINEA   = colors.black


def _texto(valor):
    if valor is None:
        return ""
    return str(valor)


def generar_pdf_laboratorio(lab):

    os.makedirs("pdfs_laboratorio", exist_ok=True)
    ruta = f"pdfs_laboratorio/{lab.codigo}.pdf"

    documento = SimpleDocTemplate(
        ruta,
        pagesize=letter,
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    estilos = getSampleStyleSheet()

    estilo_celda = ParagraphStyle(
        "celda", parent=estilos["Normal"],
        fontName="Helvetica", fontSize=8.5, leading=10.5, alignment=TA_LEFT,
    )
    estilo_celda_bold = ParagraphStyle(
        "celda_bold", parent=estilos["Normal"],
        fontName="Helvetica-Bold", fontSize=8.5, leading=10.5, alignment=TA_LEFT,
    )
    estilo_seccion_header = ParagraphStyle(
        "seccion_header", parent=estilos["Normal"],
        fontName="Helvetica-Bold", fontSize=9, leading=11, alignment=TA_LEFT,
    )
    estilo_titulo = ParagraphStyle(
        "titulo", parent=estilos["Normal"],
        fontName="Helvetica-Bold", fontSize=12, leading=14, alignment=TA_CENTER,
    )
    estilo_cuerpo = ParagraphStyle(
        "cuerpo", parent=estilos["Normal"],
        fontName="Helvetica", fontSize=8.5, leading=11, alignment=TA_LEFT,
    )
    estilo_tabla_celda = ParagraphStyle(
        "tabla_celda", parent=estilos["Normal"],
        fontName="Helvetica", fontSize=8, leading=10, alignment=TA_LEFT,
    )

    elementos = []
    ANCHO_TOTAL = 560

    # ── TÍTULO ────────────────────────────────────────────────────────
    titulo_tbl = Table(
        [[Paragraph("REGISTRO DE PRACTICA DE LABORATORIO", estilo_titulo)]],
        colWidths=[ANCHO_TOTAL],
    )
    titulo_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, GRIS_LINEA),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elementos.append(titulo_tbl)

    # ── 1. DATOS INFORMATIVOS ────────────────────────────────────────
    elementos.append(Table(
        [[Paragraph("1.&nbsp;&nbsp;&nbsp;DATOS INFORMATIVOS", estilo_seccion_header)]],
        colWidths=[ANCHO_TOTAL],
        style=[
            ("BOX", (0, 0), (-1, -1), 1, GRIS_LINEA),
            ("BACKGROUND", (0, 0), (-1, -1), AZUL_CLARO),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]
    ))

    datos_info = [
        [Paragraph("LABORATORIO:", estilo_celda_bold), Paragraph(_texto(lab.laboratorio), estilo_celda),
         Paragraph("N° de Estudiantes:", estilo_celda_bold), Paragraph(_texto(lab.numero_estudiantes), estilo_celda)],

        [Paragraph("Asignatura:", estilo_celda_bold), Paragraph(_texto(lab.asignatura), estilo_celda),
         Paragraph("Unidad Académica:", estilo_celda_bold), Paragraph(_texto(lab.unidad_academica), estilo_celda)],

        [Paragraph("Semestre:", estilo_celda_bold), Paragraph(_texto(lab.semestre), estilo_celda),
         Paragraph("Carrera:", estilo_celda_bold), Paragraph(_texto(lab.carrera), estilo_celda)],

        [Paragraph("Institución:", estilo_celda_bold), Paragraph(_texto(lab.institucion), estilo_celda),
         Paragraph("Ciudad:", estilo_celda_bold), Paragraph(_texto(lab.ciudad), estilo_celda)],

        [Paragraph("Hora Entrada:", estilo_celda_bold), Paragraph(_texto(lab.hora_entrada), estilo_celda),
         Paragraph("Hora Salida:", estilo_celda_bold), Paragraph(_texto(lab.hora_salida), estilo_celda)],

        [Paragraph("Docente Responsable:", estilo_celda_bold), Paragraph(_texto(lab.docente_responsable), estilo_celda),
         Paragraph("Fecha:", estilo_celda_bold), Paragraph(_texto(lab.fecha_practica), estilo_celda)],
    ]

    tabla_info = Table(datos_info, colWidths=[110, 170, 110, 170])
    tabla_info.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, GRIS_LINEA),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elementos.append(tabla_info)

    # ── 2. DATOS ACADÉMICOS ──────────────────────────────────────────
    elementos.append(Table(
        [[Paragraph("2.&nbsp;&nbsp;&nbsp;DATOS ACADÉMICOS", estilo_seccion_header)]],
        colWidths=[ANCHO_TOTAL],
        style=[
            ("BOX", (0, 0), (-1, -1), 1, GRIS_LINEA),
            ("BACKGROUND", (0, 0), (-1, -1), AZUL_CLARO),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]
    ))

    # Encabezados de la sub-tabla (Tema / Subtema / Logro)
    encabezados_academicos = Table(
        [[
            Paragraph("Tema de la Practica/Visita:", estilo_celda_bold),
            Paragraph("Subtema(s):", estilo_celda_bold),
            Paragraph("Logro de aprendizaje:", estilo_celda_bold),
        ]],
        colWidths=[ANCHO_TOTAL / 3] * 3,
    )
    encabezados_academicos.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, GRIS_LINEA),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elementos.append(encabezados_academicos)

    contenido_academico = Table(
        [[
            Paragraph(_texto(lab.tema_practica), estilo_celda),
            Paragraph(_texto(lab.subtema), estilo_celda),
            Paragraph(_texto(lab.logro_aprendizaje), estilo_celda),
        ]],
        colWidths=[ANCHO_TOTAL / 3] * 3,
    )
    contenido_academico.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, GRIS_LINEA),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("MINROWHEIGHT", (0, 0), (-1, 0), 50),
    ]))
    elementos.append(contenido_academico)

    # ── Bloques 2.1 a 2.5 (igual estilo que tu imagen) ────────────────
    def _bloque_seccion(numero, titulo, contenido, alto_min=50):
        elementos.append(Table(
            [[Paragraph(f"{numero}. {titulo}", estilo_celda_bold)]],
            colWidths=[ANCHO_TOTAL],
            style=[
                ("BOX", (0, 0), (-1, -1), 1, GRIS_LINEA),
                ("BACKGROUND", (0, 0), (-1, -1), AZUL_CLARO),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        ))
        cuerpo = Table(
            [[Paragraph(_texto(contenido).replace("\n", "<br/>"), estilo_cuerpo)]],
            colWidths=[ANCHO_TOTAL],
        )
        cuerpo.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, GRIS_LINEA),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("MINROWHEIGHT", (0, 0), (-1, 0), alto_min),
        ]))
        elementos.append(cuerpo)

    _bloque_seccion("2.1", "Objetivos de la Practica",          lab.objetivos,     45)
    _bloque_seccion("2.2", "Metodología de la Práctica:",        lab.metodologia,   60)
    _bloque_seccion("2.3", "Resultados a obtenerse",             lab.resultados,    60)
    _bloque_seccion("2.4", "Conclusiones y Recomendaciones",     lab.conclusiones,  50)
    _bloque_seccion("2.5", "Observaciones",                      lab.observaciones, 40)

    # ── PÁGINA 2: Materiales/Reactivos + Nómina de Estudiantes ──────
    from reportlab.platypus import PageBreak
    elementos.append(PageBreak())

    ANCHO_IZQ = 190
    ANCHO_DER = ANCHO_TOTAL - ANCHO_IZQ

    # --- Columna izquierda: encabezado Materiales ---
    encabezado_izq = Table(
        [[
            Paragraph("1.&nbsp;&nbsp;Equipos y Materiales", estilo_celda_bold),
            Paragraph("Cantidad", estilo_celda_bold),
        ]],
        colWidths=[ANCHO_IZQ * 0.72, ANCHO_IZQ * 0.28],
    )
    encabezado_izq.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, GRIS_LINEA),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ("BACKGROUND", (0, 0), (-1, -1), VERDE_CLARO),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    # --- Columna derecha: encabezado Nómina de Estudiantes ----------
    encabezado_der_titulo = Table(
        [[Paragraph("5.&nbsp;&nbsp;Nómina de Estudiantes", estilo_celda_bold)]],
        colWidths=[ANCHO_DER],
    )
    encabezado_der_titulo.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, GRIS_LINEA),
        ("BACKGROUND", (0, 0), (-1, -1), VERDE_CLARO),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    encabezado_der_cols = Table(
        [[
            Paragraph("Nombres y Apellidos", estilo_celda_bold),
            Paragraph("N° de Cédula", estilo_celda_bold),
            Paragraph("Firma", estilo_celda_bold),
        ]],
        colWidths=[ANCHO_DER * 0.45, ANCHO_DER * 0.25, ANCHO_DER * 0.30],
    )
    encabezado_der_cols.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, GRIS_LINEA),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ("BACKGROUND", (0, 0), (-1, -1), AZUL_TABLA),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    # Encabezados lado a lado en una sola fila
    fila_encabezados = Table(
        [[encabezado_izq, Table([[encabezado_der_titulo]], colWidths=[ANCHO_DER])]],
        colWidths=[ANCHO_IZQ, ANCHO_DER],
    )
    fila_encabezados.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elementos.append(fila_encabezados)

    fila_subencabezados = Table(
        [["", encabezado_der_cols]],
        colWidths=[ANCHO_IZQ, ANCHO_DER],
    )
    fila_subencabezados.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elementos.append(fila_subencabezados)

    # ── Construir filas: materiales+reactivos a la izq, estudiantes a la der ──
    filas_izq = []
    for m in (lab.materiales or []):
        filas_izq.append((_texto(m.get("nombre")), _texto(m.get("cantidad"))))

    # Encabezado intermedio "Reactivos e Insumos" dentro de la misma columna
    idx_reactivos_header = len(filas_izq)
    for r in (lab.reactivos or []):
        filas_izq.append((_texto(r.get("nombre")), _texto(r.get("cantidad"))))

    filas_der = []
    for e in (lab.estudiantes or []):
        firma_ruta = e.get("firma_ruta")
        if firma_ruta and os.path.exists(firma_ruta):
            celda_firma = Image(firma_ruta, width=70, height=28)
        else:
            celda_firma = Paragraph("", estilo_tabla_celda)

        filas_der.append((
            Paragraph(_texto(e.get("nombre")), estilo_tabla_celda),
            Paragraph(_texto(e.get("cedula")), estilo_tabla_celda),
            celda_firma,
        ))

    n_filas = max(len(filas_izq) + 1, len(filas_der))  # +1 por el header de reactivos

    # Construir la tabla combinada fila por fila
    data_combinada = []
    for i in range(n_filas):
        # --- columna izquierda (materiales/reactivos) ---
        if i < idx_reactivos_header:
            nombre_izq, cant_izq = filas_izq[i]
            celda_izq_nombre = Paragraph(nombre_izq, estilo_tabla_celda)
            celda_izq_cant   = Paragraph(cant_izq, estilo_tabla_celda)
        elif i == idx_reactivos_header and lab.reactivos:
            celda_izq_nombre = Paragraph("<b>2.&nbsp;&nbsp;Reactivos e Insumos</b>", estilo_tabla_celda)
            celda_izq_cant   = Paragraph("<b>Cantidad</b>", estilo_tabla_celda)
        else:
            idx_r = i - idx_reactivos_header - 1
            if 0 <= idx_r < len(lab.reactivos or []):
                nombre_izq, cant_izq = filas_izq[idx_reactivos_header + idx_r]
                celda_izq_nombre = Paragraph(nombre_izq, estilo_tabla_celda)
                celda_izq_cant   = Paragraph(cant_izq, estilo_tabla_celda)
            else:
                celda_izq_nombre, celda_izq_cant = "", ""

        # --- columna derecha (estudiantes) ---
        if i < len(filas_der):
            nombre_der, cedula_der, firma_der = filas_der[i]
        else:
            nombre_der, cedula_der, firma_der = "", "", ""

        data_combinada.append([celda_izq_nombre, celda_izq_cant, nombre_der, cedula_der, firma_der])

    if not data_combinada:
        data_combinada = [["", "", "", "", ""]]

    tabla_combinada = Table(
        data_combinada,
        colWidths=[
            ANCHO_IZQ * 0.72, ANCHO_IZQ * 0.28,
            ANCHO_DER * 0.45, ANCHO_DER * 0.25, ANCHO_DER * 0.30,
        ],
    )
    tabla_combinada.setStyle(TableStyle([
        ("BOX", (0, 0), (1, -1), 1, GRIS_LINEA),
        ("BOX", (2, 0), (4, -1), 1, GRIS_LINEA),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("MINROWHEIGHT", (0, 0), (-1, -1), 18),
    ]))
    elementos.append(tabla_combinada)

    documento.build(elementos)
    return ruta
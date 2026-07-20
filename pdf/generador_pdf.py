import os

from xml.sax.saxutils import escape

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
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.enums import (
    TA_LEFT,
    TA_CENTER,
    TA_JUSTIFY,
)


RUTA_LOGO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "assets",
    "logo_uleam.png",
)


def texto_seguro(valor):
    """
    Convierte cualquier valor a texto seguro para ReportLab.

    - None se convierte en cadena vacía.
    - Escapa caracteres especiales como &, < y >.
    - Convierte saltos de línea en <br/>.
    """

    if valor is None:
        return ""

    return escape(str(valor)).replace("\n", "<br/>")


def _imagen_firma(ruta, width=120, height=50):
    """
    Devuelve una imagen de ReportLab si la ruta existe.

    Si no existe la firma, devuelve un párrafo vacío para evitar
    errores al generar la tabla.
    """

    if ruta and os.path.exists(ruta):
        return Image(
            ruta,
            width=width,
            height=height,
        )

    return Paragraph(
        "",
        ParagraphStyle("vacio"),
    )


def _formatear_fecha(fecha):
    """
    Convierte la fecha de creación a un formato legible.

    Acepta objetos datetime/date o texto.
    """

    if not fecha:
        return ""

    if hasattr(fecha, "strftime"):
        return fecha.strftime("%d/%m/%Y  %H:%M")

    return texto_seguro(fecha)


def generar_pdf(practica, ruta_pdf):
    """
    Genera el PDF de planificación de prácticas.

    Parámetros:
        practica:
            Objeto Practica con todos los datos necesarios.

        ruta_pdf:
            Ruta local donde se generará el archivo PDF.

    Devuelve:
        La misma ruta donde fue creado el PDF.
    """

    if practica is None:
        raise ValueError(
            "El objeto práctica no puede ser None."
        )

    if not ruta_pdf:
        raise ValueError(
            "La ruta del PDF no puede estar vacía."
        )

    ruta_pdf = os.path.abspath(
        str(ruta_pdf)
    )

    carpeta_destino = os.path.dirname(
        ruta_pdf
    )

    if carpeta_destino:
        os.makedirs(
            carpeta_destino,
            exist_ok=True,
        )

    documento = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    estilos = getSampleStyleSheet()

    estilo_celda = ParagraphStyle(
        "celda",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
    )

    estilo_celda_bold = ParagraphStyle(
        "celda_bold",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
    )

    estilo_titulo_seccion = ParagraphStyle(
        "titulo_seccion",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
    )

    estilo_subtitulo = ParagraphStyle(
        "subtitulo",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
    )

    estilo_institucional = ParagraphStyle(
        "institucional",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#3B3B3B"),
    )

    estilo_intro = ParagraphStyle(
        "intro",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=8.3,
        leading=10.5,
        alignment=TA_JUSTIFY,
    )

    estilo_firma_nombre = ParagraphStyle(
        "firma_nombre",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
    )

    estilo_firma_cargo = ParagraphStyle(
        "firma_cargo",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
    )

    estilo_vacio = ParagraphStyle(
        "vacio",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
    )

    GRIS_CLARO = colors.HexColor("#E7E7E7")
    GRIS_TITULO = colors.HexColor("#D9D9D9")

    elementos = []

    # ============================================================
    # ENCABEZADO
    # ============================================================

    if os.path.exists(RUTA_LOGO):
        logo = Image(
            RUTA_LOGO,
            width=130,
            height=46,
        )
    else:
        logo = Paragraph(
            "ULEAM",
            estilo_institucional,
        )

    texto_facultad = Paragraph(
        "Facultad de Ciencias de la Vida<br/>y Tecnologías",
        estilo_institucional,
    )

    encabezado_logo = Table(
        [
            [
                logo,
                texto_facultad,
            ]
        ],
        colWidths=[
            275,
            275,
        ],
    )

    encabezado_logo.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "LINEAFTER",
                    (0, 0),
                    (0, 0),
                    1,
                    colors.HexColor("#7FBF7F"),
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (0, 0),
                    "LEFT",
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, 0),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (0, 0),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elementos.append(
        encabezado_logo
    )

    # ============================================================
    # TÍTULO
    # ============================================================

    titulo_formato = Table(
        [
            [
                Paragraph(
                    "PLANIFICACIÓN DE PRÁCTICAS DE CAMPO O LABORATORIO",
                    estilo_titulo_seccion,
                ),
                Paragraph(
                    "Versión 1",
                    estilo_subtitulo,
                ),
            ]
        ],
        colWidths=[
            440,
            110,
        ],
    )

    titulo_formato.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    elementos.append(
        titulo_formato
    )

    # ============================================================
    # INTRODUCCIÓN
    # ============================================================

    intro = Table(
        [
            [
                Paragraph(
                    "Este formato tiene como finalidad planificar y registrar "
                    "las prácticas de campo, laboratorio, planta piloto, "
                    "vinculación o simulación, articuladas con el currículo, "
                    "los resultados de aprendizaje, las competencias "
                    "profesionales y los núcleos problémicos de cada carrera.",
                    estilo_intro,
                )
            ]
        ],
        colWidths=[
            550,
        ],
    )

    intro.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    elementos.append(
        intro
    )

    # ============================================================
    # 1. DATOS INFORMATIVOS
    # ============================================================

    tabla_titulo_informativos = Table(
        [
            [
                Paragraph(
                    "1.&nbsp;&nbsp;&nbsp;DATOS INFORMATIVOS",
                    estilo_titulo_seccion,
                )
            ]
        ],
        colWidths=[
            550,
        ],
    )

    tabla_titulo_informativos.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    GRIS_TITULO,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    elementos.append(
        tabla_titulo_informativos
    )

    fecha_str = _formatear_fecha(
        getattr(
            practica,
            "fecha_creacion",
            None,
        )
    )

    datos = [
        [
            "Fecha de registro:",
            fecha_str,
        ],
        [
            "Carrera:",
            texto_seguro(
                getattr(
                    practica,
                    "carrera",
                    "",
                )
            ),
        ],
        [
            "Semestre:",
            texto_seguro(
                getattr(
                    practica,
                    "semestre",
                    "",
                )
            ),
        ],
        [
            "Asignatura:",
            texto_seguro(
                getattr(
                    practica,
                    "asignatura",
                    "",
                )
            ),
        ],
        [
            "Unidad del Sílabo:",
            texto_seguro(
                getattr(
                    practica,
                    "unidad_silabo",
                    "",
                )
            ),
        ],
        [
            "Tipo de Práctica:",
            texto_seguro(
                getattr(
                    practica,
                    "tipo_practica",
                    "",
                )
            ),
        ],
        [
            "Docente Responsable:",
            texto_seguro(
                getattr(
                    practica,
                    "ingeniero_revisor",
                    "",
                )
            ),
        ],
        [
            "Lugar de ejecución:",
            texto_seguro(
                getattr(
                    practica,
                    "lugar_ejecucion",
                    "",
                )
            ),
        ],
        [
            "Semana planificada:",
            texto_seguro(
                getattr(
                    practica,
                    "semana_planificada",
                    "",
                )
            ),
        ],
    ]

    tabla_datos = Table(
        [
            [
                Paragraph(
                    fila[0],
                    estilo_celda_bold,
                ),
                Paragraph(
                    fila[1],
                    estilo_celda,
                ),
            ]
            for fila in datos
        ],
        colWidths=[
            180,
            370,
        ],
    )

    tabla_datos.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    elementos.append(
        tabla_datos
    )

    # ============================================================
    # 2. DATOS ACADÉMICOS
    # ============================================================

    tabla_titulo_academicos = Table(
        [
            [
                Paragraph(
                    "2.&nbsp;&nbsp;&nbsp;DATOS ACADÉMICOS",
                    estilo_titulo_seccion,
                )
            ]
        ],
        colWidths=[
            550,
        ],
    )

    tabla_titulo_academicos.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    GRIS_TITULO,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    elementos.append(
        tabla_titulo_academicos
    )

    academicos = [
        [
            "Tema de la Práctica/Visita:",
            texto_seguro(
                getattr(
                    practica,
                    "tema_practica",
                    "",
                )
            ),
        ],
        [
            "Resultado de aprendizaje de<br/>la asignatura:",
            texto_seguro(
                getattr(
                    practica,
                    "resultado_aprendizaje",
                    "",
                )
            ),
        ],
        [
            "Articulación curricular:",
            texto_seguro(
                getattr(
                    practica,
                    "articulacion_curricular",
                    "",
                )
            ),
        ],
    ]

    tabla_academicos = Table(
        [
            [
                Paragraph(
                    fila[0],
                    estilo_celda_bold,
                ),
                Paragraph(
                    fila[1],
                    estilo_celda,
                ),
            ]
            for fila in academicos
        ],
        colWidths=[
            180,
            370,
        ],
    )

    tabla_academicos.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "MINROWHEIGHT",
                    (0, 2),
                    (-1, 2),
                    60,
                ),
            ]
        )
    )

    elementos.append(
        tabla_academicos
    )

    # ============================================================
    # BLOQUES 2.1 A 2.4
    # ============================================================

    def _seccion_texto(
        titulo,
        contenido,
        min_height=70,
    ):
        tabla_seccion = Table(
            [
                [
                    Paragraph(
                        titulo,
                        estilo_titulo_seccion,
                    )
                ],
                [
                    Paragraph(
                        texto_seguro(contenido),
                        estilo_celda,
                    )
                ],
            ],
            colWidths=[
                550,
            ],
        )

        tabla_seccion.setStyle(
            TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.black,
                    ),
                    (
                        "LINEBELOW",
                        (0, 0),
                        (-1, 0),
                        1,
                        colors.black,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        GRIS_CLARO,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "MINROWHEIGHT",
                        (0, 1),
                        (-1, 1),
                        min_height,
                    ),
                    (
                        "VALIGN",
                        (0, 1),
                        (-1, 1),
                        "TOP",
                    ),
                ]
            )
        )

        return tabla_seccion

    elementos.append(
        _seccion_texto(
            "2.1.&nbsp;&nbsp;&nbsp;OBJETIVO GENERAL DE LA PRÁCTICA",
            getattr(
                practica,
                "objetivo_general",
                "",
            ),
            70,
        )
    )

    elementos.append(
        _seccion_texto(
            "2.2.&nbsp;&nbsp;&nbsp;MATERIALES/RECURSOS Y EQUIPOS",
            getattr(
                practica,
                "materiales_equipos",
                "",
            ),
            70,
        )
    )

    elementos.append(
        _seccion_texto(
            "2.3.&nbsp;&nbsp;&nbsp;DESCRIPCIÓN DE LA ACTIVIDAD",
            getattr(
                practica,
                "descripcion_actividad",
                "",
            ),
            120,
        )
    )

    elementos.append(
        _seccion_texto(
            "2.4.&nbsp;&nbsp;&nbsp;EVIDENCIA DE LA PRÁCTICA",
            getattr(
                practica,
                "evidencias",
                "",
            ),
            60,
        )
    )

    elementos.append(
        Spacer(
            1,
            18,
        )
    )

    # ============================================================
    # FIRMAS
    # ============================================================

    firma_docente = getattr(
        practica,
        "firma_docente",
        None,
    )

    firma_comision = getattr(
        practica,
        "firma_comision",
        None,
    )

    imagen_docente = _imagen_firma(
        firma_docente,
        width=120,
        height=50,
    )

    imagen_comision = _imagen_firma(
        firma_comision,
        width=120,
        height=50,
    )

    nombre_docente = texto_seguro(
        getattr(
            practica,
            "ingeniero_revisor",
            "",
        )
    )

    if not nombre_docente:
        nombre_docente = "Docente Responsable"

    nombre_comision = "Comisión Académica"

    firmas = Table(
        [
            [
                imagen_docente,
                imagen_comision,
            ],
            [
                Paragraph(
                    nombre_docente,
                    estilo_firma_nombre,
                ),
                Paragraph(
                    nombre_comision,
                    estilo_firma_nombre,
                ),
            ],
            [
                Paragraph(
                    "Docente Responsable",
                    estilo_firma_cargo,
                ),
                Paragraph(
                    "Comisión Académica",
                    estilo_firma_cargo,
                ),
            ],
        ],
        colWidths=[
            275,
            275,
        ],
    )

    firmas.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "LINEABOVE",
                    (0, 1),
                    (-1, 1),
                    0.8,
                    colors.black,
                ),
                (
                    "MINROWHEIGHT",
                    (0, 0),
                    (-1, 0),
                    60,
                ),
            ]
        )
    )

    elementos.append(
        firmas
    )

    # ============================================================
    # GENERAR ARCHIVO
    # ============================================================

    documento.build(
        elementos
    )

    if not os.path.isfile(ruta_pdf):
        raise FileNotFoundError(
            "ReportLab terminó sin crear el archivo PDF:\n"
            f"{ruta_pdf}"
        )

    return ruta_pdf
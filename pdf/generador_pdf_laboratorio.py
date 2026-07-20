import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)


# ============================================================
# Colores institucionales
# ============================================================

AZUL_CLARO = colors.HexColor("#BDD7EE")
AZUL_TABLA = colors.HexColor("#9DC3E6")
VERDE_CLARO = colors.HexColor("#C6E0B4")
GRIS_CLARO = colors.HexColor("#E7E7E7")
GRIS_TEXTO = colors.HexColor("#555555")
NEGRO = colors.black


# ============================================================
# Funciones auxiliares
# ============================================================

def _texto(valor):
    """
    Convierte cualquier valor en texto seguro.
    """

    if valor is None:
        return ""

    return str(valor)


def _ruta_valida(ruta):
    """
    Comprueba si una ruta local existe.
    """

    if not ruta:
        return False

    try:
        return os.path.isfile(
            str(ruta)
        )

    except Exception:
        return False


def _imagen_firma(
    ruta,
    ancho=120,
    alto=50,
):
    """
    Devuelve una imagen de firma para ReportLab.

    Si el archivo no existe, devuelve un espacio vacío.
    """

    if _ruta_valida(ruta):
        try:
            return Image(
                str(ruta),
                width=ancho,
                height=alto,
            )

        except Exception as error:
            print(
                "No se pudo cargar la firma:",
                error,
            )

    return ""


def _imagen_estudiante(
    ruta,
    ancho=70,
    alto=28,
):
    """
    Carga una firma de estudiante.
    """

    if _ruta_valida(ruta):
        try:
            return Image(
                str(ruta),
                width=ancho,
                height=alto,
            )

        except Exception as error:
            print(
                "No se pudo cargar la firma del estudiante:",
                error,
            )

    return ""


# ============================================================
# Generador principal
# ============================================================

def generar_pdf_laboratorio(lab):
    """
    Genera el PDF de un registro de práctica de laboratorio.

    Incluye:

        - Datos informativos.
        - Datos académicos.
        - Objetivos.
        - Metodología.
        - Resultados.
        - Conclusiones.
        - Observaciones.
        - Materiales.
        - Reactivos.
        - Nómina de estudiantes.
        - Firma de cada estudiante.
        - Firma del docente responsable.
        - Firma del encargado del laboratorio.
        - Nombre y cargo del encargado.

    Devuelve:
        Ruta local del PDF generado.
    """

    if lab is None:
        raise ValueError(
            "El objeto laboratorio no puede ser None."
        )

    codigo = str(
        getattr(
            lab,
            "codigo",
            "",
        )
        or ""
    ).strip()

    if not codigo:
        raise ValueError(
            "El laboratorio no tiene un código válido."
        )

    # ============================================================
    # Ruta del PDF
    # ============================================================

    carpeta_salida = "pdfs_laboratorio"

    os.makedirs(
        carpeta_salida,
        exist_ok=True,
    )

    ruta = os.path.join(
        carpeta_salida,
        f"{codigo}.pdf",
    )

    documento = SimpleDocTemplate(
        ruta,
        pagesize=letter,
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
        title=(
            "Registro de práctica de laboratorio"
        ),
        author=_texto(
            getattr(
                lab,
                "docente_responsable",
                "",
            )
        ),
    )

    estilos = getSampleStyleSheet()

    # ============================================================
    # Estilos
    # ============================================================

    estilo_celda = ParagraphStyle(
        "celda",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=10.5,
        alignment=TA_LEFT,
    )

    estilo_celda_bold = ParagraphStyle(
        "celda_bold",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=10.5,
        alignment=TA_LEFT,
    )

    estilo_seccion_header = ParagraphStyle(
        "seccion_header",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
    )

    estilo_titulo = ParagraphStyle(
        "titulo",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        alignment=TA_CENTER,
    )

    estilo_cuerpo = ParagraphStyle(
        "cuerpo",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        alignment=TA_LEFT,
    )

    estilo_tabla_celda = ParagraphStyle(
        "tabla_celda",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        alignment=TA_LEFT,
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
        textColor=GRIS_TEXTO,
    )

    estilo_firma_estado = ParagraphStyle(
        "firma_estado",
        parent=estilos["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=9,
        alignment=TA_CENTER,
        textColor=GRIS_TEXTO,
    )

    elementos = []

    ancho_total = 560

    # ============================================================
    # Título
    # ============================================================

    titulo_tbl = Table(
        [
            [
                Paragraph(
                    "REGISTRO DE PRÁCTICA DE LABORATORIO",
                    estilo_titulo,
                )
            ]
        ],
        colWidths=[
            ancho_total,
        ],
    )

    titulo_tbl.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    NEGRO,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    elementos.append(
        titulo_tbl
    )

    # ============================================================
    # 1. Datos informativos
    # ============================================================

    elementos.append(
        Table(
            [
                [
                    Paragraph(
                        "1.&nbsp;&nbsp;&nbsp;DATOS INFORMATIVOS",
                        estilo_seccion_header,
                    )
                ]
            ],
            colWidths=[
                ancho_total,
            ],
            style=[
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    NEGRO,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    AZUL_CLARO,
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
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ],
        )
    )

    datos_info = [
        [
            Paragraph(
                "LABORATORIO:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "laboratorio",
                        "",
                    )
                ),
                estilo_celda,
            ),
            Paragraph(
                "N° de estudiantes:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "numero_estudiantes",
                        "",
                    )
                ),
                estilo_celda,
            ),
        ],
        [
            Paragraph(
                "Asignatura:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "asignatura",
                        "",
                    )
                ),
                estilo_celda,
            ),
            Paragraph(
                "Unidad académica:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "unidad_academica",
                        "",
                    )
                ),
                estilo_celda,
            ),
        ],
        [
            Paragraph(
                "Semestre:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "semestre",
                        "",
                    )
                ),
                estilo_celda,
            ),
            Paragraph(
                "Carrera:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "carrera",
                        "",
                    )
                ),
                estilo_celda,
            ),
        ],
        [
            Paragraph(
                "Institución:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "institucion",
                        "",
                    )
                ),
                estilo_celda,
            ),
            Paragraph(
                "Ciudad:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "ciudad",
                        "",
                    )
                ),
                estilo_celda,
            ),
        ],
        [
            Paragraph(
                "Hora entrada:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "hora_entrada",
                        "",
                    )
                ),
                estilo_celda,
            ),
            Paragraph(
                "Hora salida:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "hora_salida",
                        "",
                    )
                ),
                estilo_celda,
            ),
        ],
        [
            Paragraph(
                "Docente responsable:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "docente_responsable",
                        "",
                    )
                ),
                estilo_celda,
            ),
            Paragraph(
                "Fecha:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "fecha_practica",
                        "",
                    )
                ),
                estilo_celda,
            ),
        ],
        [
            Paragraph(
                "Encargado:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "encargado_laboratorio",
                        "",
                    )
                ),
                estilo_celda,
            ),
            Paragraph(
                "Cargo:",
                estilo_celda_bold,
            ),
            Paragraph(
                _texto(
                    getattr(
                        lab,
                        "cargo_encargado",
                        "",
                    )
                ),
                estilo_celda,
            ),
        ],
    ]

    tabla_info = Table(
        datos_info,
        colWidths=[
            110,
            170,
            110,
            170,
        ],
    )

    tabla_info.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    NEGRO,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    NEGRO,
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
        tabla_info
    )

    # ============================================================
    # 2. Datos académicos
    # ============================================================

    elementos.append(
        Table(
            [
                [
                    Paragraph(
                        "2.&nbsp;&nbsp;&nbsp;DATOS ACADÉMICOS",
                        estilo_seccion_header,
                    )
                ]
            ],
            colWidths=[
                ancho_total,
            ],
            style=[
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    NEGRO,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    AZUL_CLARO,
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
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ],
        )
    )

    encabezados_academicos = Table(
        [
            [
                Paragraph(
                    "Tema de la práctica/visita:",
                    estilo_celda_bold,
                ),
                Paragraph(
                    "Subtema(s):",
                    estilo_celda_bold,
                ),
                Paragraph(
                    "Logro de aprendizaje:",
                    estilo_celda_bold,
                ),
            ]
        ],
        colWidths=[
            ancho_total / 3,
            ancho_total / 3,
            ancho_total / 3,
        ],
    )

    encabezados_academicos.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    NEGRO,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    NEGRO,
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
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    elementos.append(
        encabezados_academicos
    )

    contenido_academico = Table(
        [
            [
                Paragraph(
                    _texto(
                        getattr(
                            lab,
                            "tema_practica",
                            "",
                        )
                    ),
                    estilo_celda,
                ),
                Paragraph(
                    _texto(
                        getattr(
                            lab,
                            "subtema",
                            "",
                        )
                    ),
                    estilo_celda,
                ),
                Paragraph(
                    _texto(
                        getattr(
                            lab,
                            "logro_aprendizaje",
                            "",
                        )
                    ),
                    estilo_celda,
                ),
            ]
        ],
        colWidths=[
            ancho_total / 3,
            ancho_total / 3,
            ancho_total / 3,
        ],
    )

    contenido_academico.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    NEGRO,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    NEGRO,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
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
                    (0, 0),
                    (-1, 0),
                    50,
                ),
            ]
        )
    )

    elementos.append(
        contenido_academico
    )

    # ============================================================
    # Bloques de planificación
    # ============================================================

    def _bloque_seccion(
        numero,
        titulo,
        contenido,
        alto_minimo=50,
    ):
        elementos.append(
            Table(
                [
                    [
                        Paragraph(
                            f"{numero}. {titulo}",
                            estilo_celda_bold,
                        )
                    ]
                ],
                colWidths=[
                    ancho_total,
                ],
                style=[
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        1,
                        NEGRO,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        AZUL_CLARO,
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
                        3,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        3,
                    ),
                ],
            )
        )

        cuerpo = Table(
            [
                [
                    Paragraph(
                        _texto(
                            contenido
                        ).replace(
                            "\n",
                            "<br/>",
                        ),
                        estilo_cuerpo,
                    )
                ]
            ],
            colWidths=[
                ancho_total,
            ],
        )

        cuerpo.setStyle(
            TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        1,
                        NEGRO,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
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
                        (0, 0),
                        (-1, 0),
                        alto_minimo,
                    ),
                ]
            )
        )

        elementos.append(
            cuerpo
        )

    _bloque_seccion(
        "2.1",
        "Objetivos de la práctica",
        getattr(
            lab,
            "objetivos",
            "",
        ),
        45,
    )

    _bloque_seccion(
        "2.2",
        "Metodología de la práctica",
        getattr(
            lab,
            "metodologia",
            "",
        ),
        60,
    )

    _bloque_seccion(
        "2.3",
        "Resultados a obtenerse",
        getattr(
            lab,
            "resultados",
            "",
        ),
        60,
    )

    _bloque_seccion(
        "2.4",
        "Conclusiones y recomendaciones",
        getattr(
            lab,
            "conclusiones",
            "",
        ),
        50,
    )

    _bloque_seccion(
        "2.5",
        "Observaciones",
        getattr(
            lab,
            "observaciones",
            "",
        ),
        40,
    )

    # ============================================================
    # Página 2
    # ============================================================

    elementos.append(
        PageBreak()
    )

    ancho_izquierdo = 190
    ancho_derecho = (
        ancho_total
        - ancho_izquierdo
    )

    # ============================================================
    # Encabezado materiales
    # ============================================================

    encabezado_izquierdo = Table(
        [
            [
                Paragraph(
                    "1.&nbsp;&nbsp;Equipos y materiales",
                    estilo_celda_bold,
                ),
                Paragraph(
                    "Cantidad",
                    estilo_celda_bold,
                ),
            ]
        ],
        colWidths=[
            ancho_izquierdo * 0.72,
            ancho_izquierdo * 0.28,
        ],
    )

    encabezado_izquierdo.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    NEGRO,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    NEGRO,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    VERDE_CLARO,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    # ============================================================
    # Encabezado estudiantes
    # ============================================================

    encabezado_derecho_titulo = Table(
        [
            [
                Paragraph(
                    "5.&nbsp;&nbsp;Nómina de estudiantes",
                    estilo_celda_bold,
                )
            ]
        ],
        colWidths=[
            ancho_derecho,
        ],
    )

    encabezado_derecho_titulo.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    NEGRO,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    VERDE_CLARO,
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    encabezado_derecho_columnas = Table(
        [
            [
                Paragraph(
                    "Nombres y apellidos",
                    estilo_celda_bold,
                ),
                Paragraph(
                    "N° de cédula",
                    estilo_celda_bold,
                ),
                Paragraph(
                    "Firma",
                    estilo_celda_bold,
                ),
            ]
        ],
        colWidths=[
            ancho_derecho * 0.45,
            ancho_derecho * 0.25,
            ancho_derecho * 0.30,
        ],
    )

    encabezado_derecho_columnas.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    NEGRO,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    NEGRO,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    AZUL_TABLA,
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    fila_encabezados = Table(
        [
            [
                encabezado_izquierdo,
                Table(
                    [
                        [
                            encabezado_derecho_titulo
                        ]
                    ],
                    colWidths=[
                        ancho_derecho,
                    ],
                ),
            ]
        ],
        colWidths=[
            ancho_izquierdo,
            ancho_derecho,
        ],
    )

    fila_encabezados.setStyle(
        TableStyle(
            [
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
            ]
        )
    )

    elementos.append(
        fila_encabezados
    )

    fila_subencabezados = Table(
        [
            [
                "",
                encabezado_derecho_columnas,
            ]
        ],
        colWidths=[
            ancho_izquierdo,
            ancho_derecho,
        ],
    )

    fila_subencabezados.setStyle(
        TableStyle(
            [
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    elementos.append(
        fila_subencabezados
    )

    # ============================================================
    # Materiales
    # ============================================================

    materiales = getattr(
        lab,
        "materiales",
        [],
    ) or []

    reactivos = getattr(
        lab,
        "reactivos",
        [],
    ) or []

    estudiantes = getattr(
        lab,
        "estudiantes",
        [],
    ) or []

    filas_izquierdas = []

    for material in materiales:
        if not isinstance(
            material,
            dict,
        ):
            continue

        filas_izquierdas.append(
            (
                _texto(
                    material.get(
                        "nombre"
                    )
                ),
                _texto(
                    material.get(
                        "cantidad"
                    )
                ),
            )
        )

    indice_encabezado_reactivos = len(
        filas_izquierdas
    )

    for reactivo in reactivos:
        if not isinstance(
            reactivo,
            dict,
        ):
            continue

        filas_izquierdas.append(
            (
                _texto(
                    reactivo.get(
                        "nombre"
                    )
                ),
                _texto(
                    reactivo.get(
                        "cantidad"
                    )
                ),
            )
        )

    # ============================================================
    # Estudiantes
    # ============================================================

    filas_derechas = []

    for estudiante in estudiantes:
        if not isinstance(
            estudiante,
            dict,
        ):
            continue

        firma_estudiante = _imagen_estudiante(
            estudiante.get(
                "firma_ruta"
            )
        )

        filas_derechas.append(
            (
                Paragraph(
                    _texto(
                        estudiante.get(
                            "nombre"
                        )
                    ),
                    estilo_tabla_celda,
                ),
                Paragraph(
                    _texto(
                        estudiante.get(
                            "cedula"
                        )
                    ),
                    estilo_tabla_celda,
                ),
                firma_estudiante,
            )
        )

    cantidad_filas_izquierda = (
        len(materiales)
        + len(reactivos)
        + (
            1
            if reactivos
            else 0
        )
    )

    numero_filas = max(
        cantidad_filas_izquierda,
        len(
            filas_derechas
        ),
        1,
    )

    data_combinada = []

    for indice in range(
        numero_filas
    ):
        # Materiales
        if indice < indice_encabezado_reactivos:
            nombre_izquierdo, cantidad_izquierda = (
                filas_izquierdas[
                    indice
                ]
            )

            celda_nombre_izquierda = Paragraph(
                nombre_izquierdo,
                estilo_tabla_celda,
            )

            celda_cantidad_izquierda = Paragraph(
                cantidad_izquierda,
                estilo_tabla_celda,
            )

        # Encabezado de reactivos
        elif (
            indice == indice_encabezado_reactivos
            and reactivos
        ):
            celda_nombre_izquierda = Paragraph(
                "<b>2.&nbsp;&nbsp;Reactivos e insumos</b>",
                estilo_tabla_celda,
            )

            celda_cantidad_izquierda = Paragraph(
                "<b>Cantidad</b>",
                estilo_tabla_celda,
            )

        # Reactivos
        else:
            indice_reactivo = (
                indice
                - indice_encabezado_reactivos
                - (
                    1
                    if reactivos
                    else 0
                )
            )

            if (
                0 <= indice_reactivo
                < len(reactivos)
            ):
                reactivo = reactivos[
                    indice_reactivo
                ]

                celda_nombre_izquierda = Paragraph(
                    _texto(
                        reactivo.get(
                            "nombre"
                        )
                    ),
                    estilo_tabla_celda,
                )

                celda_cantidad_izquierda = Paragraph(
                    _texto(
                        reactivo.get(
                            "cantidad"
                        )
                    ),
                    estilo_tabla_celda,
                )

            else:
                celda_nombre_izquierda = ""
                celda_cantidad_izquierda = ""

        # Estudiantes
        if indice < len(
            filas_derechas
        ):
            nombre_estudiante, cedula_estudiante, firma_estudiante = (
                filas_derechas[
                    indice
                ]
            )

        else:
            nombre_estudiante = ""
            cedula_estudiante = ""
            firma_estudiante = ""

        data_combinada.append(
            [
                celda_nombre_izquierda,
                celda_cantidad_izquierda,
                nombre_estudiante,
                cedula_estudiante,
                firma_estudiante,
            ]
        )

    tabla_combinada = Table(
        data_combinada,
        colWidths=[
            ancho_izquierdo * 0.72,
            ancho_izquierdo * 0.28,
            ancho_derecho * 0.45,
            ancho_derecho * 0.25,
            ancho_derecho * 0.30,
        ],
        repeatRows=0,
    )

    tabla_combinada.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (1, -1),
                    1,
                    NEGRO,
                ),
                (
                    "BOX",
                    (2, 0),
                    (4, -1),
                    1,
                    NEGRO,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    NEGRO,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (4, 0),
                    (4, -1),
                    "CENTER",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
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
                    (0, 0),
                    (-1, -1),
                    22,
                ),
            ]
        )
    )

    elementos.append(
        tabla_combinada
    )

    # ============================================================
    # Firmas responsables
    # ============================================================

    elementos.append(
        Spacer(
            1,
            24,
        )
    )

    elementos.append(
        Table(
            [
                [
                    Paragraph(
                        "6.&nbsp;&nbsp;&nbsp;FIRMAS DE RESPONSABLES",
                        estilo_seccion_header,
                    )
                ]
            ],
            colWidths=[
                ancho_total,
            ],
            style=[
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    NEGRO,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    AZUL_CLARO,
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
            ],
        )
    )

    firma_docente_ruta = getattr(
        lab,
        "firma_docente_ruta",
        None,
    )

    firma_encargado_ruta = getattr(
        lab,
        "firma_encargado_ruta",
        None,
    )

    imagen_firma_docente = _imagen_firma(
        firma_docente_ruta,
        ancho=125,
        alto=52,
    )

    imagen_firma_encargado = _imagen_firma(
        firma_encargado_ruta,
        ancho=125,
        alto=52,
    )

    nombre_docente = _texto(
        getattr(
            lab,
            "docente_responsable",
            "",
        )
    ).strip()

    nombre_encargado = _texto(
        getattr(
            lab,
            "encargado_laboratorio",
            "",
        )
    ).strip()

    cargo_encargado = _texto(
        getattr(
            lab,
            "cargo_encargado",
            "",
        )
    ).strip()

    if not nombre_docente:
        nombre_docente = "Docente responsable"

    if not nombre_encargado:
        nombre_encargado = "Encargado del laboratorio"

    if not cargo_encargado:
        cargo_encargado = "Encargado del laboratorio"

    estado_docente = (
        "Firma digital registrada"
        if _ruta_valida(
            firma_docente_ruta
        )
        else "Firma pendiente"
    )

    estado_encargado = (
        "Firma digital registrada"
        if _ruta_valida(
            firma_encargado_ruta
        )
        else "Firma pendiente"
    )

    tabla_firmas = Table(
        [
            [
                imagen_firma_docente,
                imagen_firma_encargado,
            ],
            [
                Paragraph(
                    nombre_docente,
                    estilo_firma_nombre,
                ),
                Paragraph(
                    nombre_encargado,
                    estilo_firma_nombre,
                ),
            ],
            [
                Paragraph(
                    "Docente responsable",
                    estilo_firma_cargo,
                ),
                Paragraph(
                    cargo_encargado,
                    estilo_firma_cargo,
                ),
            ],
            [
                Paragraph(
                    estado_docente,
                    estilo_firma_estado,
                ),
                Paragraph(
                    estado_encargado,
                    estilo_firma_estado,
                ),
            ],
        ],
        colWidths=[
            ancho_total / 2,
            ancho_total / 2,
        ],
    )

    tabla_firmas.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    NEGRO,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    NEGRO,
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
                    "MINROWHEIGHT",
                    (0, 0),
                    (-1, 0),
                    65,
                ),
                (
                    "LINEABOVE",
                    (0, 1),
                    (-1, 1),
                    0.8,
                    NEGRO,
                ),
                (
                    "BACKGROUND",
                    (0, 2),
                    (-1, 2),
                    GRIS_CLARO,
                ),
            ]
        )
    )

    elementos.append(
        tabla_firmas
    )

    # ============================================================
    # Construir PDF
    # ============================================================

    documento.build(
        elementos
    )

    if not os.path.isfile(
        ruta
    ):
        raise FileNotFoundError(
            "El PDF del laboratorio no fue generado."
        )

    print(
        f"PDF de laboratorio generado: {ruta}"
    )

    return ruta
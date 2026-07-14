import os
import tempfile

from pathlib import Path
from urllib.request import urlopen
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import (
    TA_CENTER,
    TA_JUSTIFY,
    TA_LEFT,
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ============================================================
# Colores
# ============================================================

AZUL_TITULO = colors.HexColor("#D9EAF7")
AZUL_SECCION = colors.HexColor("#BDD7EE")
GRIS_CLARO = colors.HexColor("#F2F2F2")
GRIS_TEXTO = colors.HexColor("#444444")
NEGRO = colors.black


def _texto_seguro(valor):
    """
    Convierte cualquier valor en texto seguro para ReportLab.

    También convierte saltos de línea en <br/>.
    """

    if valor is None:
        return ""

    return escape(
        str(valor)
    ).replace(
        "\n",
        "<br/>",
    )


def _formatear_fecha(fecha):
    """
    Convierte datetime, date o texto a formato legible.
    """

    if not fecha:
        return ""

    if hasattr(
        fecha,
        "strftime",
    ):
        return fecha.strftime(
            "%d/%m/%Y %H:%M"
        )

    return _texto_seguro(
        fecha
    )


def _descargar_imagen_temporal(url):
    """
    Descarga temporalmente una imagen desde una URL.

    Devuelve:
        Ruta temporal del archivo descargado.
        None si no fue posible descargarlo.
    """

    try:
        datos = urlopen(
            url,
            timeout=15,
        ).read()

        extension = Path(
            str(url).split("?")[0]
        ).suffix.lower()

        if extension not in {
            ".png",
            ".jpg",
            ".jpeg",
        }:
            extension = ".jpg"

        archivo_temporal = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        )

        archivo_temporal.write(
            datos
        )

        archivo_temporal.close()

        return archivo_temporal.name

    except Exception as error:
        print(
            "[generador_pdf_informe] "
            f"No fue posible descargar la imagen: {error}"
        )
        return None


def _obtener_ruta_imagen(valor):
    """
    Recibe una ruta local o una URL.

    Si es URL, descarga la imagen temporalmente.
    Si es ruta local, comprueba que exista.
    """

    if not valor:
        return None

    valor = str(
        valor
    ).strip()

    if valor.lower().startswith(
        ("http://", "https://")
    ):
        return _descargar_imagen_temporal(
            valor
        )

    ruta = Path(
        valor
    )

    if ruta.is_file():
        return str(
            ruta.resolve()
        )

    return None


def _crear_titulo_seccion(
    texto,
    estilo,
    ancho=530,
):
    """
    Crea una tabla de encabezado para cada sección.
    """

    tabla = Table(
        [
            [
                Paragraph(
                    texto,
                    estilo,
                )
            ]
        ],
        colWidths=[
            ancho,
        ],
    )

    tabla.setStyle(
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
                    AZUL_SECCION,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
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

    return tabla


def _crear_bloque_texto(
    contenido,
    estilo,
    ancho=530,
    alto_minimo=45,
):
    """
    Crea una tabla con el contenido de una sección.
    """

    tabla = Table(
        [
            [
                Paragraph(
                    _texto_seguro(
                        contenido
                    ),
                    estilo,
                )
            ]
        ],
        colWidths=[
            ancho,
        ],
    )

    tabla.setStyle(
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
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "MINROWHEIGHT",
                    (0, 0),
                    (-1, -1),
                    alto_minimo,
                ),
            ]
        )
    )

    return tabla


def generar_pdf_informe(
    informe,
    ruta_pdf,
):
    """
    Genera el PDF completo de un informe de laboratorio.

    Incluye:
        - portada y datos generales;
        - resumen;
        - palabras clave;
        - introducción;
        - objetivos;
        - materiales y reactivos;
        - procedimiento experimental;
        - resultados;
        - discusión;
        - conclusiones;
        - recomendaciones;
        - bibliografía;
        - hoja de datos;
        - cuestionario;
        - anexos;
        - fotografías.

    Devuelve:
        Ruta absoluta del PDF generado.
    """

    if informe is None:
        raise ValueError(
            "El objeto informe no puede ser None."
        )

    if not ruta_pdf:
        raise ValueError(
            "La ruta del PDF no puede estar vacía."
        )

    ruta_pdf = Path(
        ruta_pdf
    ).resolve()

    ruta_pdf.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    documento = SimpleDocTemplate(
        str(ruta_pdf),
        pagesize=letter,
        leftMargin=32,
        rightMargin=32,
        topMargin=30,
        bottomMargin=30,
        title=str(
            informe.titulo
            or "Informe de laboratorio"
        ),
        author=str(
            informe.autores
            or ""
        ),
    )

    estilos = getSampleStyleSheet()

    estilo_titulo_principal = ParagraphStyle(
        "TituloPrincipalInforme",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#1F1F1F"
        ),
        spaceAfter=7,
    )

    estilo_subtitulo = ParagraphStyle(
        "SubtituloInforme",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        textColor=GRIS_TEXTO,
    )

    estilo_datos = ParagraphStyle(
        "DatosInforme",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
    )

    estilo_seccion = ParagraphStyle(
        "SeccionInforme",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        alignment=TA_LEFT,
    )

    estilo_cuerpo = ParagraphStyle(
        "CuerpoInforme",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12.5,
        alignment=TA_JUSTIFY,
    )

    estilo_centrado = ParagraphStyle(
        "CentradoInforme",
        parent=estilo_cuerpo,
        alignment=TA_CENTER,
    )

    estilo_foto = ParagraphStyle(
        "DescripcionFoto",
        parent=estilos["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=GRIS_TEXTO,
    )

    elementos = []
    archivos_temporales = []

    # ============================================================
    # Encabezado principal
    # ============================================================

    cabecera = Table(
        [
            [
                Paragraph(
                    "INFORME DE PRÁCTICA DE LABORATORIO",
                    estilo_titulo_principal,
                )
            ]
        ],
        colWidths=[
            530,
        ],
    )

    cabecera.setStyle(
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
                    AZUL_TITULO,
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
                    9,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
            ]
        )
    )

    elementos.append(
        cabecera
    )

    # ============================================================
    # Título de la práctica
    # ============================================================

    titulo_practica = Table(
        [
            [
                Paragraph(
                    _texto_seguro(
                        informe.titulo
                    ),
                    estilo_titulo_principal,
                )
            ]
        ],
        colWidths=[
            530,
        ],
    )

    titulo_practica.setStyle(
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
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    elementos.append(
        titulo_practica
    )

    # ============================================================
    # Datos informativos
    # ============================================================

    fecha_texto = _formatear_fecha(
        informe.fecha_creacion
    )

    datos_generales = [
        [
            Paragraph(
                "<b>Código:</b>",
                estilo_datos,
            ),
            Paragraph(
                _texto_seguro(
                    informe.codigo
                ),
                estilo_datos,
            ),
            Paragraph(
                "<b>Fecha:</b>",
                estilo_datos,
            ),
            Paragraph(
                fecha_texto,
                estilo_datos,
            ),
        ],
        [
            Paragraph(
                "<b>Autores:</b>",
                estilo_datos,
            ),
            Paragraph(
                _texto_seguro(
                    informe.autores
                ),
                estilo_datos,
            ),
            Paragraph(
                "<b>Docente:</b>",
                estilo_datos,
            ),
            Paragraph(
                _texto_seguro(
                    informe.docente
                ),
                estilo_datos,
            ),
        ],
        [
            Paragraph(
                "<b>Asignatura:</b>",
                estilo_datos,
            ),
            Paragraph(
                _texto_seguro(
                    informe.asignatura
                ),
                estilo_datos,
            ),
            Paragraph(
                "<b>Carrera:</b>",
                estilo_datos,
            ),
            Paragraph(
                _texto_seguro(
                    informe.carrera
                ),
                estilo_datos,
            ),
        ],
        [
            Paragraph(
                "<b>Semestre:</b>",
                estilo_datos,
            ),
            Paragraph(
                _texto_seguro(
                    informe.semestre
                ),
                estilo_datos,
            ),
            Paragraph(
                "",
                estilo_datos,
            ),
            Paragraph(
                "",
                estilo_datos,
            ),
        ],
    ]

    tabla_datos = Table(
        datos_generales,
        colWidths=[
            80,
            190,
            80,
            180,
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
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
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
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    GRIS_CLARO,
                ),
                (
                    "BACKGROUND",
                    (2, 0),
                    (2, -1),
                    GRIS_CLARO,
                ),
            ]
        )
    )

    elementos.append(
        tabla_datos
    )

    elementos.append(
        Spacer(
            1,
            12,
        )
    )

    # ============================================================
    # Resumen
    # ============================================================

    elementos.append(
        _crear_titulo_seccion(
            "RESUMEN",
            estilo_seccion,
        )
    )

    elementos.append(
        _crear_bloque_texto(
            informe.resumen,
            estilo_cuerpo,
            alto_minimo=80,
        )
    )

    tabla_palabras = Table(
        [
            [
                Paragraph(
                    "<b>Palabras clave:</b>",
                    estilo_datos,
                ),
                Paragraph(
                    _texto_seguro(
                        informe.palabras_clave
                    ),
                    estilo_datos,
                ),
            ]
        ],
        colWidths=[
            105,
            425,
        ],
    )

    tabla_palabras.setStyle(
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
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
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
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, 0),
                    GRIS_CLARO,
                ),
            ]
        )
    )

    elementos.append(
        tabla_palabras
    )

    # ============================================================
    # Secciones principales
    # ============================================================

    secciones = [
        (
            "1. INTRODUCCIÓN",
            informe.introduccion,
            100,
        ),
        (
            "2.1 OBJETIVO GENERAL",
            informe.objetivo_general,
            65,
        ),
        (
            "2.2 OBJETIVOS ESPECÍFICOS",
            informe.objetivos_especificos,
            85,
        ),
        (
            "3.1 MATERIALES Y REACTIVOS",
            informe.materiales_reactivos,
            100,
        ),
        (
            "3.2 PROCEDIMIENTO EXPERIMENTAL",
            informe.procedimiento_experimental,
            140,
        ),
        (
            "4. RESULTADOS",
            informe.resultados,
            140,
        ),
        (
            "5. DISCUSIÓN",
            informe.discusion,
            140,
        ),
        (
            "6. CONCLUSIONES",
            informe.conclusiones,
            100,
        ),
        (
            "7. RECOMENDACIONES",
            informe.recomendaciones,
            85,
        ),
        (
            "8. BIBLIOGRAFÍA",
            informe.bibliografia,
            110,
        ),
    ]

    for titulo_seccion, contenido, alto in secciones:
        elementos.append(
            Spacer(
                1,
                8,
            )
        )

        elementos.append(
            _crear_titulo_seccion(
                titulo_seccion,
                estilo_seccion,
            )
        )

        elementos.append(
            _crear_bloque_texto(
                contenido,
                estilo_cuerpo,
                alto_minimo=alto,
            )
        )

    # ============================================================
    # Hoja de datos
    # ============================================================

    elementos.append(
        Spacer(
            1,
            8,
        )
    )

    elementos.append(
        _crear_titulo_seccion(
            "9. HOJA DE DATOS",
            estilo_seccion,
        )
    )

    if informe.hoja_datos_url:
        contenido_hoja = (
            "La hoja de datos escaneada fue almacenada "
            "digitalmente en Supabase Storage."
        )
    else:
        contenido_hoja = (
            "No se adjuntó una hoja de datos escaneada."
        )

    elementos.append(
        _crear_bloque_texto(
            contenido_hoja,
            estilo_cuerpo,
            alto_minimo=45,
        )
    )

    # ============================================================
    # Cuestionario opcional
    # ============================================================

    if str(
        informe.cuestionario or ""
    ).strip():
        elementos.append(
            Spacer(
                1,
                8,
            )
        )

        elementos.append(
            _crear_titulo_seccion(
                "10. CUESTIONARIO",
                estilo_seccion,
            )
        )

        elementos.append(
            _crear_bloque_texto(
                informe.cuestionario,
                estilo_cuerpo,
                alto_minimo=100,
            )
        )

    # ============================================================
    # Anexos opcionales
    # ============================================================

    if str(
        informe.anexos or ""
    ).strip():
        elementos.append(
            Spacer(
                1,
                8,
            )
        )

        elementos.append(
            _crear_titulo_seccion(
                "11. ANEXOS",
                estilo_seccion,
            )
        )

        elementos.append(
            _crear_bloque_texto(
                informe.anexos,
                estilo_cuerpo,
                alto_minimo=100,
            )
        )

    # ============================================================
    # Fotografías
    # ============================================================

    if informe.fotos:
        elementos.append(
            PageBreak()
        )

        elementos.append(
            _crear_titulo_seccion(
                "REGISTRO FOTOGRÁFICO",
                estilo_seccion,
            )
        )

        elementos.append(
            Spacer(
                1,
                12,
            )
        )

        for indice, fotografia in enumerate(
            informe.fotos,
            start=1,
        ):
            if not isinstance(
                fotografia,
                dict,
            ):
                continue

            origen = (
                fotografia.get(
                    "ruta_local"
                )
                or fotografia.get(
                    "foto_url"
                )
            )

            ruta_imagen = _obtener_ruta_imagen(
                origen
            )

            if not ruta_imagen:
                continue

            if str(
                origen
            ).lower().startswith(
                ("http://", "https://")
            ):
                archivos_temporales.append(
                    ruta_imagen
                )

            try:
                imagen = Image(
                    ruta_imagen,
                )

                ancho_original = float(
                    imagen.imageWidth
                )

                alto_original = float(
                    imagen.imageHeight
                )

                ancho_maximo = 420
                alto_maximo = 300

                escala = min(
                    ancho_maximo / ancho_original,
                    alto_maximo / alto_original,
                    1,
                )

                imagen.drawWidth = (
                    ancho_original
                    * escala
                )

                imagen.drawHeight = (
                    alto_original
                    * escala
                )

                tabla_imagen = Table(
                    [
                        [
                            imagen
                        ]
                    ],
                    colWidths=[
                        530,
                    ],
                )

                tabla_imagen.setStyle(
                    TableStyle(
                        [
                            (
                                "ALIGN",
                                (0, 0),
                                (-1, -1),
                                "CENTER",
                            ),
                            (
                                "BOX",
                                (0, 0),
                                (-1, -1),
                                0.5,
                                colors.HexColor(
                                    "#777777"
                                ),
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                8,
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                8,
                            ),
                        ]
                    )
                )

                elementos.append(
                    tabla_imagen
                )

                descripcion = str(
                    fotografia.get(
                        "descripcion"
                    )
                    or ""
                ).strip()

                elementos.append(
                    Paragraph(
                        (
                            f"Figura {indice}. "
                            f"{_texto_seguro(descripcion)}"
                        ),
                        estilo_foto,
                    )
                )

                elementos.append(
                    Spacer(
                        1,
                        14,
                    )
                )

            except Exception as error:
                print(
                    "[generador_pdf_informe] "
                    f"No se pudo agregar una fotografía: {error}"
                )

    # ============================================================
    # Generar PDF
    # ============================================================

    try:
        documento.build(
            elementos
        )

    finally:
        # Eliminar imágenes descargadas temporalmente.
        for archivo_temporal in archivos_temporales:
            try:
                if os.path.isfile(
                    archivo_temporal
                ):
                    os.remove(
                        archivo_temporal
                    )
            except Exception:
                pass

    if not ruta_pdf.is_file():
        raise FileNotFoundError(
            "ReportLab terminó sin crear el PDF del informe."
        )

    return str(
        ruta_pdf
    )
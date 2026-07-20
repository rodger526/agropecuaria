from pathlib import Path

import fitz


def agregar_firma_comision(
    pdf_entrada,
    ruta_firma,
    pdf_salida,
):
    """
    Inserta la firma de comisión sobre el PDF anterior.

    Conserva intacta la firma del docente porque trabaja
    directamente sobre el PDF ya generado.

    Parámetros:
        pdf_entrada:
            Ruta del PDF anterior.

        ruta_firma:
            Ruta local de la imagen de firma de comisión.

        pdf_salida:
            Ruta donde se guardará el PDF actualizado.

    Devuelve:
        La ruta del PDF nuevo.
    """

    pdf_entrada = Path(pdf_entrada).resolve()
    ruta_firma = Path(ruta_firma).resolve()
    pdf_salida = Path(pdf_salida).resolve()

    if not pdf_entrada.is_file():
        raise FileNotFoundError(
            f"No se encontró el PDF anterior:\n{pdf_entrada}"
        )

    if not ruta_firma.is_file():
        raise FileNotFoundError(
            f"No se encontró la firma de comisión:\n{ruta_firma}"
        )

    pdf_salida.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    documento = fitz.open(
        str(pdf_entrada)
    )

    try:
        pagina_firma = None
        rectangulo_texto = None

        textos_busqueda = (
            "Comisión Académica",
            "COMISIÓN ACADÉMICA",
            "Comision Academica",
            "COMISION ACADEMICA",
        )

        # Buscar desde la última página hacia atrás.
        for numero_pagina in range(
            documento.page_count - 1,
            -1,
            -1,
        ):
            pagina = documento[
                numero_pagina
            ]

            for texto in textos_busqueda:
                coincidencias = pagina.search_for(
                    texto
                )

                if coincidencias:
                    pagina_firma = pagina
                    rectangulo_texto = coincidencias[-1]
                    break

            if pagina_firma is not None:
                break

        # Si no encuentra el texto, usa la última página.
        if pagina_firma is None:
            pagina_firma = documento[
                documento.page_count - 1
            ]

            ancho = pagina_firma.rect.width
            alto = pagina_firma.rect.height

            rectangulo_firma = fitz.Rect(
                ancho * 0.62,
                alto * 0.70,
                ancho * 0.86,
                alto * 0.79,
            )

        else:
            centro_x = (
                rectangulo_texto.x0
                + rectangulo_texto.x1
            ) / 2

            ancho_firma = 120
            alto_firma = 50

            y_inferior = max(
                55,
                rectangulo_texto.y0 - 8,
            )

            y_superior = max(
                5,
                y_inferior - alto_firma,
            )

            rectangulo_firma = fitz.Rect(
                centro_x - ancho_firma / 2,
                y_superior,
                centro_x + ancho_firma / 2,
                y_inferior,
            )

        pagina_firma.insert_image(
            rectangulo_firma,
            filename=str(ruta_firma),
            keep_proportion=True,
            overlay=True,
        )

        documento.save(
            str(pdf_salida),
            garbage=4,
            deflate=True,
            clean=True,
        )

    finally:
        documento.close()

    if not pdf_salida.is_file():
        raise RuntimeError(
            "No se creó el PDF actualizado."
        )

    return str(pdf_salida)
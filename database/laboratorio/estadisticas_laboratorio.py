from database.conexion import obtener_conexion


def obtener_resumen_general():
    """
    Devuelve los indicadores principales del dashboard.

    Retorna un diccionario con:
        - total_laboratorios
        - total_pdfs
        - creados_este_mes
        - cantidad_total_reactivos
        - porcentaje_con_pdf
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_laboratorios,

                COUNT(*) FILTER (
                    WHERE pdf_url IS NOT NULL
                    AND TRIM(pdf_url) <> ''
                ) AS total_pdfs,

                COUNT(*) FILTER (
                    WHERE DATE_TRUNC('month', fecha_creacion)
                          = DATE_TRUNC('month', CURRENT_DATE)
                ) AS creados_este_mes

            FROM laboratorios
            """
        )

        resultado = cursor.fetchone()

        total_laboratorios = resultado[0] or 0
        total_pdfs = resultado[1] or 0
        creados_este_mes = resultado[2] or 0

        cursor.execute(
            """
            SELECT COALESCE(
                SUM(
                    CASE
                        WHEN cantidad::text ~ '^[0-9]+([.,][0-9]+)?$'
                        THEN REPLACE(cantidad::text, ',', '.')::numeric
                        ELSE 0
                    END
                ),
                0
            )
            FROM laboratorio_reactivos
            """
        )

        cantidad_total_reactivos = cursor.fetchone()[0] or 0

        porcentaje_con_pdf = 0

        if total_laboratorios > 0:
            porcentaje_con_pdf = round(
                total_pdfs * 100 / total_laboratorios,
                2,
            )

        return {
            "total_laboratorios": int(total_laboratorios),
            "total_pdfs": int(total_pdfs),
            "creados_este_mes": int(creados_este_mes),
            "cantidad_total_reactivos": float(
                cantidad_total_reactivos
            ),
            "porcentaje_con_pdf": float(
                porcentaje_con_pdf
            ),
        }

    except Exception as error:
        print(
            "\n========== ERROR EN RESUMEN GENERAL =========="
        )
        print(error)
        print(
            "==============================================\n"
        )

        return {
            "total_laboratorios": 0,
            "total_pdfs": 0,
            "creados_este_mes": 0,
            "cantidad_total_reactivos": 0,
            "porcentaje_con_pdf": 0,
        }

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def obtener_pdfs_por_mes(
    anio=None,
):
    """
    Devuelve cuántos PDFs fueron creados por mes.

    Retorna una lista de tuplas:
        [
            (1, "Enero", 10),
            (2, "Febrero", 15),
            ...
        ]
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        if anio is None:
            cursor.execute(
                """
                SELECT EXTRACT(
                    YEAR FROM CURRENT_DATE
                )::INTEGER
                """
            )

            anio = cursor.fetchone()[0]

        cursor.execute(
            """
            WITH meses AS (
                SELECT GENERATE_SERIES(
                    1,
                    12
                ) AS numero_mes
            ),
            datos AS (
                SELECT
                    EXTRACT(
                        MONTH FROM fecha_creacion
                    )::INTEGER AS numero_mes,
                    COUNT(*) AS total

                FROM laboratorios

                WHERE EXTRACT(
                    YEAR FROM fecha_creacion
                )::INTEGER = %s

                AND pdf_url IS NOT NULL
                AND TRIM(pdf_url) <> ''

                GROUP BY
                    EXTRACT(
                        MONTH FROM fecha_creacion
                    )
            )

            SELECT
                meses.numero_mes,

                CASE meses.numero_mes
                    WHEN 1 THEN 'Enero'
                    WHEN 2 THEN 'Febrero'
                    WHEN 3 THEN 'Marzo'
                    WHEN 4 THEN 'Abril'
                    WHEN 5 THEN 'Mayo'
                    WHEN 6 THEN 'Junio'
                    WHEN 7 THEN 'Julio'
                    WHEN 8 THEN 'Agosto'
                    WHEN 9 THEN 'Septiembre'
                    WHEN 10 THEN 'Octubre'
                    WHEN 11 THEN 'Noviembre'
                    WHEN 12 THEN 'Diciembre'
                END AS nombre_mes,

                COALESCE(
                    datos.total,
                    0
                ) AS total

            FROM meses

            LEFT JOIN datos
                ON datos.numero_mes = meses.numero_mes

            ORDER BY meses.numero_mes
            """,
            (
                anio,
            ),
        )

        return cursor.fetchall()

    except Exception as error:
        print(
            "\n========== ERROR EN PDFS POR MES =========="
        )
        print(error)
        print(
            "===========================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def obtener_uso_por_laboratorio():
    """
    Devuelve los laboratorios más utilizados.

    Retorna:
        [
            ("Laboratorio de Aguas", 20),
            ("Laboratorio de Análisis", 15)
        ]
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                COALESCE(
                    NULLIF(
                        TRIM(laboratorio),
                        ''
                    ),
                    'Sin especificar'
                ) AS nombre_laboratorio,

                COUNT(*) AS total

            FROM laboratorios

            GROUP BY
                COALESCE(
                    NULLIF(
                        TRIM(laboratorio),
                        ''
                    ),
                    'Sin especificar'
                )

            ORDER BY total DESC
            """
        )

        return cursor.fetchall()

    except Exception as error:
        print(
            "\n========== ERROR EN USO POR LABORATORIO =========="
        )
        print(error)
        print(
            "==================================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def obtener_practicas_por_carrera():
    """
    Devuelve cuántas prácticas tiene cada carrera.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                COALESCE(
                    NULLIF(
                        TRIM(carrera),
                        ''
                    ),
                    'Sin especificar'
                ) AS carrera,

                COUNT(*) AS total

            FROM laboratorios

            GROUP BY
                COALESCE(
                    NULLIF(
                        TRIM(carrera),
                        ''
                    ),
                    'Sin especificar'
                )

            ORDER BY total DESC
            """
        )

        return cursor.fetchall()

    except Exception as error:
        print(
            "\n========== ERROR EN PRÁCTICAS POR CARRERA =========="
        )
        print(error)
        print(
            "====================================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def obtener_practicas_por_asignatura(
    limite=10,
):
    """
    Devuelve las asignaturas con más prácticas.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                COALESCE(
                    NULLIF(
                        TRIM(asignatura),
                        ''
                    ),
                    'Sin especificar'
                ) AS asignatura,

                COUNT(*) AS total

            FROM laboratorios

            GROUP BY
                COALESCE(
                    NULLIF(
                        TRIM(asignatura),
                        ''
                    ),
                    'Sin especificar'
                )

            ORDER BY total DESC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        return cursor.fetchall()

    except Exception as error:
        print(
            "\n========== ERROR EN PRÁCTICAS POR ASIGNATURA =========="
        )
        print(error)
        print(
            "=======================================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def obtener_docentes_mas_activos(
    limite=10,
):
    """
    Devuelve los docentes con mayor cantidad de prácticas.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                COALESCE(
                    NULLIF(
                        TRIM(docente_responsable),
                        ''
                    ),
                    'Sin especificar'
                ) AS docente,

                COUNT(*) AS total

            FROM laboratorios

            GROUP BY
                COALESCE(
                    NULLIF(
                        TRIM(docente_responsable),
                        ''
                    ),
                    'Sin especificar'
                )

            ORDER BY total DESC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        return cursor.fetchall()

    except Exception as error:
        print(
            "\n========== ERROR EN DOCENTES MÁS ACTIVOS =========="
        )
        print(error)
        print(
            "==================================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def obtener_reactivos_mas_utilizados(
    limite=10,
):
    """
    Devuelve los reactivos con mayor cantidad acumulada.

    La consulta intenta convertir el campo cantidad a número.
    Solo suma valores que sean numéricos, por ejemplo:
        10
        10.5
        10,5

    Retorna:
        [
            ("Alcohol", 150.0),
            ("Ácido clorhídrico", 90.0)
        ]
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                COALESCE(
                    NULLIF(
                        TRIM(nombre),
                        ''
                    ),
                    'Sin especificar'
                ) AS nombre_reactivo,

                COALESCE(
                    SUM(
                        CASE
                            WHEN cantidad::text
                                 ~ '^[0-9]+([.,][0-9]+)?$'
                            THEN REPLACE(
                                cantidad::text,
                                ',',
                                '.'
                            )::numeric
                            ELSE 0
                        END
                    ),
                    0
                ) AS cantidad_total

            FROM laboratorio_reactivos

            GROUP BY
                COALESCE(
                    NULLIF(
                        TRIM(nombre),
                        ''
                    ),
                    'Sin especificar'
                )

            ORDER BY cantidad_total DESC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        return cursor.fetchall()

    except Exception as error:
        print(
            "\n========== ERROR EN REACTIVOS MÁS UTILIZADOS =========="
        )
        print(error)
        print(
            "=======================================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def obtener_consumo_reactivos_por_mes(
    anio=None,
):
    """
    Suma las cantidades de reactivos utilizadas por mes.

    La relación se realiza por laboratorio_id.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        if anio is None:
            cursor.execute(
                """
                SELECT EXTRACT(
                    YEAR FROM CURRENT_DATE
                )::INTEGER
                """
            )

            anio = cursor.fetchone()[0]

        cursor.execute(
            """
            WITH meses AS (
                SELECT GENERATE_SERIES(
                    1,
                    12
                ) AS numero_mes
            ),
            datos AS (
                SELECT
                    EXTRACT(
                        MONTH FROM l.fecha_creacion
                    )::INTEGER AS numero_mes,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN r.cantidad::text
                                     ~ '^[0-9]+([.,][0-9]+)?$'
                                THEN REPLACE(
                                    r.cantidad::text,
                                    ',',
                                    '.'
                                )::numeric
                                ELSE 0
                            END
                        ),
                        0
                    ) AS total

                FROM laboratorios l

                INNER JOIN laboratorio_reactivos r
                    ON r.laboratorio_id = l.id

                WHERE EXTRACT(
                    YEAR FROM l.fecha_creacion
                )::INTEGER = %s

                GROUP BY
                    EXTRACT(
                        MONTH FROM l.fecha_creacion
                    )
            )

            SELECT
                meses.numero_mes,

                CASE meses.numero_mes
                    WHEN 1 THEN 'Enero'
                    WHEN 2 THEN 'Febrero'
                    WHEN 3 THEN 'Marzo'
                    WHEN 4 THEN 'Abril'
                    WHEN 5 THEN 'Mayo'
                    WHEN 6 THEN 'Junio'
                    WHEN 7 THEN 'Julio'
                    WHEN 8 THEN 'Agosto'
                    WHEN 9 THEN 'Septiembre'
                    WHEN 10 THEN 'Octubre'
                    WHEN 11 THEN 'Noviembre'
                    WHEN 12 THEN 'Diciembre'
                END AS nombre_mes,

                COALESCE(
                    datos.total,
                    0
                ) AS total

            FROM meses

            LEFT JOIN datos
                ON datos.numero_mes = meses.numero_mes

            ORDER BY meses.numero_mes
            """,
            (
                anio,
            ),
        )

        return cursor.fetchall()

    except Exception as error:
        print(
            "\n========== ERROR EN CONSUMO POR MES =========="
        )
        print(error)
        print(
            "==============================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def obtener_consumo_por_laboratorio(
    limite=10,
):
    """
    Devuelve los laboratorios con mayor consumo acumulado
    de reactivos.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                COALESCE(
                    NULLIF(
                        TRIM(l.laboratorio),
                        ''
                    ),
                    'Sin especificar'
                ) AS laboratorio,

                COALESCE(
                    SUM(
                        CASE
                            WHEN r.cantidad::text
                                 ~ '^[0-9]+([.,][0-9]+)?$'
                            THEN REPLACE(
                                r.cantidad::text,
                                ',',
                                '.'
                            )::numeric
                            ELSE 0
                        END
                    ),
                    0
                ) AS cantidad_total

            FROM laboratorios l

            INNER JOIN laboratorio_reactivos r
                ON r.laboratorio_id = l.id

            GROUP BY
                COALESCE(
                    NULLIF(
                        TRIM(l.laboratorio),
                        ''
                    ),
                    'Sin especificar'
                )

            ORDER BY cantidad_total DESC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        return cursor.fetchall()

    except Exception as error:
        print(
            "\n========== ERROR EN CONSUMO POR LABORATORIO =========="
        )
        print(error)
        print(
            "======================================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def obtener_anios_disponibles():
    """
    Devuelve los años disponibles para el filtro del dashboard.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT DISTINCT
                EXTRACT(
                    YEAR FROM fecha_creacion
                )::INTEGER AS anio

            FROM laboratorios

            WHERE fecha_creacion IS NOT NULL

            ORDER BY anio DESC
            """
        )

        return [
            fila[0]
            for fila in cursor.fetchall()
        ]

    except Exception as error:
        print(
            "\n========== ERROR OBTENIENDO AÑOS =========="
        )
        print(error)
        print(
            "===========================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


def obtener_ultimos_laboratorios(
    limite=10,
):
    """
    Devuelve los últimos laboratorios registrados.
    """

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                id,
                codigo,
                fecha_creacion,
                fecha_practica,
                laboratorio,
                carrera,
                asignatura,
                docente_responsable,
                pdf_url

            FROM laboratorios

            ORDER BY fecha_creacion DESC, id DESC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        return cursor.fetchall()

    except Exception as error:
        print(
            "\n========== ERROR EN ÚLTIMOS LABORATORIOS =========="
        )
        print(error)
        print(
            "===================================================\n"
        )

        return []

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()
from database.conexion import obtener_conexion


# ============================================================
# Utilidades internas
# ============================================================

def _cerrar_recursos(cursor, conexion):
    """
    Cierra de forma segura el cursor y la conexión.
    """

    if cursor:
        try:
            cursor.close()
        except Exception:
            pass

    if conexion:
        try:
            conexion.close()
        except Exception:
            pass


def _normalizar_texto(valor, predeterminado="Sin información"):
    """
    Limpia valores de texto recibidos desde PostgreSQL.
    """

    if valor is None:
        return predeterminado

    texto = str(valor).strip()

    return texto if texto else predeterminado


# ============================================================
# Resumen general
# ============================================================

def obtener_resumen_pdfs():
    """
    Obtiene indicadores generales relacionados con archivos PDF
    registrados en prácticas y laboratorios.

    Devuelve:

        total_documentos
        pdfs_laboratorios
        pdfs_practicas
        registros_sin_pdf
        enlaces_web
        archivos_locales
        porcentaje_con_pdf
    """

    conexion = None
    cursor = None

    resultado = {
        "total_documentos": 0,
        "pdfs_laboratorios": 0,
        "pdfs_practicas": 0,
        "registros_sin_pdf": 0,
        "enlaces_web": 0,
        "archivos_locales": 0,
        "porcentaje_con_pdf": 0.0,
    }

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            WITH documentos AS (
                SELECT
                    'Laboratorio'::TEXT AS tipo,
                    pdf_url

                FROM laboratorios

                UNION ALL

                SELECT
                    'Práctica'::TEXT AS tipo,
                    pdf_url

                FROM practicas
            )

            SELECT
                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(pdf_url, '')
                    ) <> ''
                ) AS total_documentos,

                COUNT(*) FILTER (
                    WHERE tipo = 'Laboratorio'
                    AND TRIM(
                        COALESCE(pdf_url, '')
                    ) <> ''
                ) AS pdfs_laboratorios,

                COUNT(*) FILTER (
                    WHERE tipo = 'Práctica'
                    AND TRIM(
                        COALESCE(pdf_url, '')
                    ) <> ''
                ) AS pdfs_practicas,

                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(pdf_url, '')
                    ) = ''
                ) AS registros_sin_pdf,

                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(pdf_url, '')
                    ) <> ''

                    AND (
                        LOWER(TRIM(pdf_url)) LIKE 'http://%'
                        OR LOWER(TRIM(pdf_url)) LIKE 'https://%'
                    )
                ) AS enlaces_web,

                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(pdf_url, '')
                    ) <> ''

                    AND LOWER(TRIM(pdf_url)) NOT LIKE 'http://%'
                    AND LOWER(TRIM(pdf_url)) NOT LIKE 'https://%'
                ) AS archivos_locales,

                CASE
                    WHEN COUNT(*) = 0
                    THEN 0

                    ELSE ROUND(
                        (
                            COUNT(*) FILTER (
                                WHERE TRIM(
                                    COALESCE(pdf_url, '')
                                ) <> ''
                            )::NUMERIC
                            /
                            COUNT(*)::NUMERIC
                        ) * 100,
                        2
                    )
                END AS porcentaje_con_pdf

            FROM documentos
            """
        )

        fila = cursor.fetchone()

        if fila:
            resultado["total_documentos"] = int(
                fila[0] or 0
            )

            resultado["pdfs_laboratorios"] = int(
                fila[1] or 0
            )

            resultado["pdfs_practicas"] = int(
                fila[2] or 0
            )

            resultado["registros_sin_pdf"] = int(
                fila[3] or 0
            )

            resultado["enlaces_web"] = int(
                fila[4] or 0
            )

            resultado["archivos_locales"] = int(
                fila[5] or 0
            )

            resultado["porcentaje_con_pdf"] = float(
                fila[6] or 0
            )

        return resultado

    except Exception as error:
        print(
            "\n========== ERROR EN RESUMEN DE PDF =========="
        )
        print(error)
        print(
            "=============================================\n"
        )

        return resultado

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# PDF por tipo de registro
# ============================================================

def obtener_pdfs_por_tipo():
    """
    Compara los documentos PDF registrados en laboratorios
    y prácticas.
    """

    conexion = None
    cursor = None
    resultados = []

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            WITH documentos AS (
                SELECT
                    'Laboratorios'::TEXT AS tipo,
                    pdf_url

                FROM laboratorios

                UNION ALL

                SELECT
                    'Prácticas'::TEXT AS tipo,
                    pdf_url

                FROM practicas
            )

            SELECT
                tipo,

                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(pdf_url, '')
                    ) <> ''
                ) AS con_pdf,

                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(pdf_url, '')
                    ) = ''
                ) AS sin_pdf,

                COUNT(*) AS total,

                CASE
                    WHEN COUNT(*) = 0
                    THEN 0

                    ELSE ROUND(
                        (
                            COUNT(*) FILTER (
                                WHERE TRIM(
                                    COALESCE(pdf_url, '')
                                ) <> ''
                            )::NUMERIC
                            /
                            COUNT(*)::NUMERIC
                        ) * 100,
                        2
                    )
                END AS porcentaje

            FROM documentos

            GROUP BY tipo

            ORDER BY tipo ASC
            """
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "tipo": fila[0],
                    "con_pdf": int(
                        fila[1] or 0
                    ),
                    "sin_pdf": int(
                        fila[2] or 0
                    ),
                    "total": int(
                        fila[3] or 0
                    ),
                    "porcentaje": float(
                        fila[4] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n======= ERROR AL OBTENER PDFS POR TIPO ======="
        )
        print(error)
        print(
            "==============================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# PDF por carrera
# ============================================================

def obtener_pdfs_por_carrera(limite=10):
    """
    Obtiene documentos asociados a cada carrera.
    """

    conexion = None
    cursor = None
    resultados = []

    try:
        limite = max(
            1,
            int(limite),
        )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            WITH documentos AS (
                SELECT
                    carrera,
                    pdf_url

                FROM laboratorios

                UNION ALL

                SELECT
                    carrera,
                    pdf_url

                FROM practicas
            )

            SELECT
                COALESCE(
                    NULLIF(
                        INITCAP(
                            LOWER(
                                TRIM(carrera)
                            )
                        ),
                        ''
                    ),
                    'Sin carrera'
                ) AS carrera,

                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(pdf_url, '')
                    ) <> ''
                ) AS con_pdf,

                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(pdf_url, '')
                    ) = ''
                ) AS sin_pdf,

                COUNT(*) AS total

            FROM documentos

            GROUP BY
                COALESCE(
                    NULLIF(
                        INITCAP(
                            LOWER(
                                TRIM(carrera)
                            )
                        ),
                        ''
                    ),
                    'Sin carrera'
                )

            ORDER BY
                con_pdf DESC,
                total DESC,
                carrera ASC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "carrera": _normalizar_texto(
                        fila[0],
                        "Sin carrera",
                    ),
                    "con_pdf": int(
                        fila[1] or 0
                    ),
                    "sin_pdf": int(
                        fila[2] or 0
                    ),
                    "total": int(
                        fila[3] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n====== ERROR AL OBTENER PDFS POR CARRERA ======"
        )
        print(error)
        print(
            "================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# PDF por asignatura
# ============================================================

def obtener_pdfs_por_asignatura(limite=10):
    """
    Obtiene las asignaturas con mayor cantidad de documentos PDF.
    """

    conexion = None
    cursor = None
    resultados = []

    try:
        limite = max(
            1,
            int(limite),
        )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            WITH documentos AS (
                SELECT
                    asignatura,
                    pdf_url

                FROM laboratorios

                UNION ALL

                SELECT
                    asignatura,
                    pdf_url

                FROM practicas
            )

            SELECT
                COALESCE(
                    NULLIF(
                        TRIM(asignatura),
                        ''
                    ),
                    'Sin asignatura'
                ) AS asignatura,

                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(pdf_url, '')
                    ) <> ''
                ) AS con_pdf,

                COUNT(*) AS total

            FROM documentos

            GROUP BY
                COALESCE(
                    NULLIF(
                        TRIM(asignatura),
                        ''
                    ),
                    'Sin asignatura'
                )

            ORDER BY
                con_pdf DESC,
                total DESC,
                asignatura ASC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "asignatura": _normalizar_texto(
                        fila[0],
                        "Sin asignatura",
                    ),
                    "con_pdf": int(
                        fila[1] or 0
                    ),
                    "total": int(
                        fila[2] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n===== ERROR AL OBTENER PDFS POR ASIGNATURA ====="
        )
        print(error)
        print(
            "=================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Ubicación de archivos
# ============================================================

def obtener_distribucion_ubicacion_pdfs():
    """
    Clasifica los PDF como enlaces web o archivos locales.
    """

    conexion = None
    cursor = None
    resultados = []

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            WITH documentos AS (
                SELECT pdf_url
                FROM laboratorios

                UNION ALL

                SELECT pdf_url
                FROM practicas
            ),

            clasificados AS (
                SELECT
                    CASE
                        WHEN LOWER(
                            TRIM(pdf_url)
                        ) LIKE 'http://%'
                        OR LOWER(
                            TRIM(pdf_url)
                        ) LIKE 'https://%'
                        THEN 'Enlace web'

                        ELSE 'Archivo local'
                    END AS ubicacion

                FROM documentos

                WHERE TRIM(
                    COALESCE(pdf_url, '')
                ) <> ''
            )

            SELECT
                ubicacion,
                COUNT(*) AS cantidad

            FROM clasificados

            GROUP BY ubicacion

            ORDER BY cantidad DESC
            """
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "ubicacion": fila[0],
                    "cantidad": int(
                        fila[1] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n===== ERROR AL OBTENER UBICACIÓN DE PDFS ====="
        )
        print(error)
        print(
            "==============================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Actividad mensual
# ============================================================

def obtener_pdfs_por_mes(meses=12):
    """
    Obtiene documentos PDF registrados por mes.

    Para laboratorios utiliza fecha_practica.
    Para prácticas utiliza fecha_registro.
    """

    conexion = None
    cursor = None
    resultados = []

    try:
        meses = max(
            1,
            int(meses),
        )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            WITH meses AS (
                SELECT
                    GENERATE_SERIES(
                        DATE_TRUNC(
                            'month',
                            CURRENT_DATE
                        ) - (
                            (%s - 1) * INTERVAL '1 month'
                        ),

                        DATE_TRUNC(
                            'month',
                            CURRENT_DATE
                        ),

                        INTERVAL '1 month'
                    )::DATE AS mes
            ),

            documentos AS (
                SELECT
                    DATE_TRUNC(
                        'month',
                        fecha_practica
                    )::DATE AS mes,

                    'Laboratorio'::TEXT AS tipo

                FROM laboratorios

                WHERE fecha_practica IS NOT NULL
                AND TRIM(
                    COALESCE(pdf_url, '')
                ) <> ''

                UNION ALL

                SELECT
                    DATE_TRUNC(
                        'month',
                        fecha_registro
                    )::DATE AS mes,

                    'Práctica'::TEXT AS tipo

                FROM practicas

                WHERE fecha_registro IS NOT NULL
                AND TRIM(
                    COALESCE(pdf_url, '')
                ) <> ''
            ),

            documentos_mes AS (
                SELECT
                    mes,

                    COUNT(*) AS total,

                    COUNT(*) FILTER (
                        WHERE tipo = 'Laboratorio'
                    ) AS laboratorios,

                    COUNT(*) FILTER (
                        WHERE tipo = 'Práctica'
                    ) AS practicas

                FROM documentos

                GROUP BY mes
            )

            SELECT
                m.mes,

                TO_CHAR(
                    m.mes,
                    'Mon YYYY'
                ) AS nombre_mes,

                COALESCE(
                    d.total,
                    0
                ) AS total,

                COALESCE(
                    d.laboratorios,
                    0
                ) AS laboratorios,

                COALESCE(
                    d.practicas,
                    0
                ) AS practicas

            FROM meses m

            LEFT JOIN documentos_mes d
                ON d.mes = m.mes

            ORDER BY m.mes ASC
            """,
            (
                meses,
            ),
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "fecha": fila[0],
                    "mes": fila[1],
                    "total": int(
                        fila[2] or 0
                    ),
                    "laboratorios": int(
                        fila[3] or 0
                    ),
                    "practicas": int(
                        fila[4] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n========= ERROR AL OBTENER PDFS POR MES ========="
        )
        print(error)
        print(
            "=================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Últimos documentos
# ============================================================

def obtener_ultimos_pdfs(limite=15):
    """
    Obtiene los PDF más recientes de prácticas y laboratorios.
    """

    conexion = None
    cursor = None
    resultados = []

    try:
        limite = max(
            1,
            int(limite),
        )

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            WITH documentos AS (
                SELECT
                    id,
                    'Laboratorio'::TEXT AS tipo,

                    COALESCE(
                        NULLIF(
                            TRIM(codigo),
                            ''
                        ),
                        'Sin código'
                    ) AS codigo,

                    COALESCE(
                        NULLIF(
                            TRIM(carrera),
                            ''
                        ),
                        'Sin carrera'
                    ) AS carrera,

                    COALESCE(
                        NULLIF(
                            TRIM(asignatura),
                            ''
                        ),
                        'Sin asignatura'
                    ) AS asignatura,

                    COALESCE(
                        NULLIF(
                            TRIM(tema_practica),
                            ''
                        ),
                        'Sin tema'
                    ) AS tema,

                    COALESCE(
                        NULLIF(
                            TRIM(docente_responsable),
                            ''
                        ),
                        'Sin docente'
                    ) AS responsable,

                    pdf_url,

                    fecha_practica::TIMESTAMP AS fecha

                FROM laboratorios

                WHERE TRIM(
                    COALESCE(pdf_url, '')
                ) <> ''

                UNION ALL

                SELECT
                    id,
                    'Práctica'::TEXT AS tipo,

                    COALESCE(
                        NULLIF(
                            TRIM(codigo),
                            ''
                        ),
                        'Sin código'
                    ) AS codigo,

                    COALESCE(
                        NULLIF(
                            TRIM(carrera),
                            ''
                        ),
                        'Sin carrera'
                    ) AS carrera,

                    COALESCE(
                        NULLIF(
                            TRIM(asignatura),
                            ''
                        ),
                        'Sin asignatura'
                    ) AS asignatura,

                    COALESCE(
                        NULLIF(
                            TRIM(tema_practica),
                            ''
                        ),
                        'Sin tema'
                    ) AS tema,

                    COALESCE(
                        NULLIF(
                            TRIM(ingeniero_revisor),
                            ''
                        ),
                        'Sin revisor'
                    ) AS responsable,

                    pdf_url,

                    fecha_registro::TIMESTAMP AS fecha

                FROM practicas

                WHERE TRIM(
                    COALESCE(pdf_url, '')
                ) <> ''
            )

            SELECT
                id,
                tipo,
                codigo,
                carrera,
                asignatura,
                tema,
                responsable,
                pdf_url,
                fecha,

                CASE
                    WHEN LOWER(
                        TRIM(pdf_url)
                    ) LIKE 'http://%'
                    OR LOWER(
                        TRIM(pdf_url)
                    ) LIKE 'https://%'
                    THEN 'Web'

                    ELSE 'Local'
                END AS ubicacion

            FROM documentos

            ORDER BY
                fecha DESC NULLS LAST,
                id DESC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "id": fila[0],
                    "tipo": fila[1],
                    "codigo": _normalizar_texto(
                        fila[2],
                        "Sin código",
                    ),
                    "carrera": _normalizar_texto(
                        fila[3],
                        "Sin carrera",
                    ),
                    "asignatura": _normalizar_texto(
                        fila[4],
                        "Sin asignatura",
                    ),
                    "tema": _normalizar_texto(
                        fila[5],
                        "Sin tema",
                    ),
                    "responsable": _normalizar_texto(
                        fila[6],
                        "Sin responsable",
                    ),
                    "pdf_url": _normalizar_texto(
                        fila[7],
                        "",
                    ),
                    "fecha": fila[8],
                    "ubicacion": fila[9],
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n========= ERROR AL OBTENER ÚLTIMOS PDF ========="
        )
        print(error)
        print(
            "================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Dashboard completo
# ============================================================

def obtener_dashboard_pdfs():
    """
    Centraliza todas las consultas necesarias para el dashboard
    de documentos PDF.
    """

    return {
        "resumen": obtener_resumen_pdfs(),

        "por_tipo": obtener_pdfs_por_tipo(),

        "por_carrera": obtener_pdfs_por_carrera(
            limite=10
        ),

        "por_asignatura": obtener_pdfs_por_asignatura(
            limite=10
        ),

        "por_ubicacion": obtener_distribucion_ubicacion_pdfs(),

        "por_mes": obtener_pdfs_por_mes(
            meses=12
        ),

        "ultimos": obtener_ultimos_pdfs(
            limite=15
        ),
    }


# ============================================================
# Prueba individual
# ============================================================

if __name__ == "__main__":
    datos = obtener_dashboard_pdfs()

    print(
        "\n========== DASHBOARD DE PDF ==========\n"
    )

    print("RESUMEN:")
    print(datos["resumen"])

    print("\nPDF POR TIPO:")

    for registro in datos["por_tipo"]:
        print(registro)

    print("\nPDF POR CARRERA:")

    for registro in datos["por_carrera"]:
        print(registro)

    print("\nPDF POR ASIGNATURA:")

    for registro in datos["por_asignatura"]:
        print(registro)

    print("\nUBICACIÓN DE PDF:")

    for registro in datos["por_ubicacion"]:
        print(registro)

    print("\nPDF POR MES:")

    for registro in datos["por_mes"]:
        print(registro)

    print("\nÚLTIMOS PDF:")

    for registro in datos["ultimos"]:
        print(registro)
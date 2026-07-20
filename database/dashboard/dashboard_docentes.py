from database.conexion import obtener_conexion


# ============================================================
# Utilidades internas
# ============================================================

def _cerrar_recursos(cursor, conexion):
    """
    Cierra el cursor y la conexión de forma segura.
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
    Limpia valores de texto obtenidos desde PostgreSQL.
    """

    if valor is None:
        return predeterminado

    texto = str(valor).strip()

    return texto if texto else predeterminado


# ============================================================
# Resumen principal
# ============================================================

def obtener_resumen_docentes():
    """
    Obtiene los indicadores generales relacionados con docentes.

    Utiliza el campo:

        laboratorios.docente_responsable

    Devuelve:

        total_docentes
        total_participaciones
        docentes_con_pdf
        carreras_atendidas
        docente_mas_activo
        participaciones_docente_mas_activo
    """

    conexion = None
    cursor = None

    resultado = {
        "total_docentes": 0,
        "total_participaciones": 0,
        "docentes_con_pdf": 0,
        "carreras_atendidas": 0,
        "docente_mas_activo": "Sin registros",
        "participaciones_docente_mas_activo": 0,
    }

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(
                    DISTINCT LOWER(
                        TRIM(
                            COALESCE(
                                docente_responsable,
                                ''
                            )
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            docente_responsable,
                            ''
                        )
                    ) <> ''
                ) AS total_docentes,

                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            docente_responsable,
                            ''
                        )
                    ) <> ''
                ) AS total_participaciones,

                COUNT(
                    DISTINCT LOWER(
                        TRIM(
                            docente_responsable
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            docente_responsable,
                            ''
                        )
                    ) <> ''

                    AND TRIM(
                        COALESCE(
                            pdf_url,
                            ''
                        )
                    ) <> ''
                ) AS docentes_con_pdf,

                COUNT(
                    DISTINCT LOWER(
                        TRIM(
                            COALESCE(
                                carrera,
                                ''
                            )
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            carrera,
                            ''
                        )
                    ) <> ''
                ) AS carreras_atendidas

            FROM laboratorios
            """
        )

        fila = cursor.fetchone()

        if fila:
            resultado["total_docentes"] = int(
                fila[0] or 0
            )

            resultado["total_participaciones"] = int(
                fila[1] or 0
            )

            resultado["docentes_con_pdf"] = int(
                fila[2] or 0
            )

            resultado["carreras_atendidas"] = int(
                fila[3] or 0
            )

        cursor.execute(
            """
            SELECT
                INITCAP(
                    LOWER(
                        TRIM(
                            docente_responsable
                        )
                    )
                ) AS docente,

                COUNT(*) AS participaciones

            FROM laboratorios

            WHERE TRIM(
                COALESCE(
                    docente_responsable,
                    ''
                )
            ) <> ''

            GROUP BY
                LOWER(
                    TRIM(
                        docente_responsable
                    )
                )

            ORDER BY
                participaciones DESC,
                docente ASC

            LIMIT 1
            """
        )

        fila_docente = cursor.fetchone()

        if fila_docente:
            resultado["docente_mas_activo"] = _normalizar_texto(
                fila_docente[0],
                "Sin registros",
            )

            resultado["participaciones_docente_mas_activo"] = int(
                fila_docente[1] or 0
            )

        return resultado

    except Exception as error:
        print(
            "\n========== ERROR EN RESUMEN DE DOCENTES =========="
        )
        print(error)
        print(
            "==================================================\n"
        )

        return resultado

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Docentes con más registros
# ============================================================

def obtener_docentes_mas_activos(limite=10):
    """
    Devuelve los docentes ordenados por cantidad de registros
    de laboratorio.
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
            SELECT
                INITCAP(
                    LOWER(
                        TRIM(
                            docente_responsable
                        )
                    )
                ) AS docente,

                COUNT(*) AS participaciones,

                COUNT(
                    DISTINCT LOWER(
                        TRIM(
                            COALESCE(
                                carrera,
                                ''
                            )
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            carrera,
                            ''
                        )
                    ) <> ''
                ) AS carreras,

                COUNT(
                    DISTINCT LOWER(
                        TRIM(
                            COALESCE(
                                laboratorio,
                                ''
                            )
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            laboratorio,
                            ''
                        )
                    ) <> ''
                ) AS laboratorios,

                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            pdf_url,
                            ''
                        )
                    ) <> ''
                ) AS documentos_pdf

            FROM laboratorios

            WHERE TRIM(
                COALESCE(
                    docente_responsable,
                    ''
                )
            ) <> ''

            GROUP BY
                LOWER(
                    TRIM(
                        docente_responsable
                    )
                )

            ORDER BY
                participaciones DESC,
                documentos_pdf DESC,
                docente ASC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "docente": _normalizar_texto(
                        fila[0],
                        "Sin nombre",
                    ),
                    "participaciones": int(
                        fila[1] or 0
                    ),
                    "carreras": int(
                        fila[2] or 0
                    ),
                    "laboratorios": int(
                        fila[3] or 0
                    ),
                    "pdfs": int(
                        fila[4] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n===== ERROR AL OBTENER DOCENTES MÁS ACTIVOS ====="
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
# PDFs por docente
# ============================================================

def obtener_pdfs_por_docente(limite=10):
    """
    Obtiene la cantidad de registros con PDF por docente.
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
            SELECT
                INITCAP(
                    LOWER(
                        TRIM(
                            docente_responsable
                        )
                    )
                ) AS docente,

                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            pdf_url,
                            ''
                        )
                    ) <> ''
                ) AS con_pdf,

                COUNT(*) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            pdf_url,
                            ''
                        )
                    ) = ''
                ) AS sin_pdf,

                COUNT(*) AS total

            FROM laboratorios

            WHERE TRIM(
                COALESCE(
                    docente_responsable,
                    ''
                )
            ) <> ''

            GROUP BY
                LOWER(
                    TRIM(
                        docente_responsable
                    )
                )

            ORDER BY
                con_pdf DESC,
                total DESC,
                docente ASC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "docente": _normalizar_texto(
                        fila[0],
                        "Sin nombre",
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
            "\n========= ERROR AL OBTENER PDFS POR DOCENTE ========="
        )
        print(error)
        print(
            "=====================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Carreras atendidas por docente
# ============================================================

def obtener_carreras_por_docente(limite=10):
    """
    Obtiene el número de carreras diferentes atendidas por cada
    docente.
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
            SELECT
                INITCAP(
                    LOWER(
                        TRIM(
                            docente_responsable
                        )
                    )
                ) AS docente,

                COUNT(
                    DISTINCT LOWER(
                        TRIM(
                            carrera
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            carrera,
                            ''
                        )
                    ) <> ''
                ) AS carreras_diferentes,

                STRING_AGG(
                    DISTINCT INITCAP(
                        LOWER(
                            TRIM(
                                carrera
                            )
                        )
                    ),
                    ', '
                    ORDER BY INITCAP(
                        LOWER(
                            TRIM(
                                carrera
                            )
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            carrera,
                            ''
                        )
                    ) <> ''
                ) AS carreras,

                COUNT(*) AS participaciones

            FROM laboratorios

            WHERE TRIM(
                COALESCE(
                    docente_responsable,
                    ''
                )
            ) <> ''

            GROUP BY
                LOWER(
                    TRIM(
                        docente_responsable
                    )
                )

            ORDER BY
                carreras_diferentes DESC,
                participaciones DESC,
                docente ASC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "docente": _normalizar_texto(
                        fila[0],
                        "Sin nombre",
                    ),
                    "cantidad_carreras": int(
                        fila[1] or 0
                    ),
                    "carreras": _normalizar_texto(
                        fila[2],
                        "Sin carreras",
                    ),
                    "participaciones": int(
                        fila[3] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n====== ERROR AL OBTENER CARRERAS POR DOCENTE ======"
        )
        print(error)
        print(
            "===================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Laboratorios utilizados por docente
# ============================================================

def obtener_laboratorios_por_docente(limite=10):
    """
    Obtiene el número de laboratorios diferentes utilizados por
    cada docente.
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
            SELECT
                INITCAP(
                    LOWER(
                        TRIM(
                            docente_responsable
                        )
                    )
                ) AS docente,

                COUNT(
                    DISTINCT LOWER(
                        TRIM(
                            laboratorio
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            laboratorio,
                            ''
                        )
                    ) <> ''
                ) AS laboratorios_diferentes,

                STRING_AGG(
                    DISTINCT INITCAP(
                        LOWER(
                            TRIM(
                                laboratorio
                            )
                        )
                    ),
                    ', '
                    ORDER BY INITCAP(
                        LOWER(
                            TRIM(
                                laboratorio
                            )
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(
                            laboratorio,
                            ''
                        )
                    ) <> ''
                ) AS laboratorios,

                COUNT(*) AS participaciones

            FROM laboratorios

            WHERE TRIM(
                COALESCE(
                    docente_responsable,
                    ''
                )
            ) <> ''

            GROUP BY
                LOWER(
                    TRIM(
                        docente_responsable
                    )
                )

            ORDER BY
                laboratorios_diferentes DESC,
                participaciones DESC,
                docente ASC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "docente": _normalizar_texto(
                        fila[0],
                        "Sin nombre",
                    ),
                    "cantidad_laboratorios": int(
                        fila[1] or 0
                    ),
                    "laboratorios": _normalizar_texto(
                        fila[2],
                        "Sin laboratorios",
                    ),
                    "participaciones": int(
                        fila[3] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n==== ERROR AL OBTENER LABORATORIOS POR DOCENTE ===="
        )
        print(error)
        print(
            "===================================================\n"
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

def obtener_actividad_docentes_por_mes(meses=12):
    """
    Obtiene la actividad de docentes en los últimos meses usando
    la columna laboratorios.fecha_practica.
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

            actividad AS (
                SELECT
                    DATE_TRUNC(
                        'month',
                        fecha_practica
                    )::DATE AS mes,

                    COUNT(*) FILTER (
                        WHERE TRIM(
                            COALESCE(
                                docente_responsable,
                                ''
                            )
                        ) <> ''
                    ) AS participaciones,

                    COUNT(
                        DISTINCT LOWER(
                            TRIM(
                                docente_responsable
                            )
                        )
                    ) FILTER (
                        WHERE TRIM(
                            COALESCE(
                                docente_responsable,
                                ''
                            )
                        ) <> ''
                    ) AS docentes_diferentes

                FROM laboratorios

                WHERE fecha_practica IS NOT NULL

                GROUP BY
                    DATE_TRUNC(
                        'month',
                        fecha_practica
                    )::DATE
            )

            SELECT
                m.mes,

                TO_CHAR(
                    m.mes,
                    'Mon YYYY'
                ) AS nombre_mes,

                COALESCE(
                    a.participaciones,
                    0
                ) AS participaciones,

                COALESCE(
                    a.docentes_diferentes,
                    0
                ) AS docentes_diferentes

            FROM meses m

            LEFT JOIN actividad a
                ON a.mes = m.mes

            ORDER BY
                m.mes ASC
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
                    "participaciones": int(
                        fila[2] or 0
                    ),
                    "docentes": int(
                        fila[3] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n====== ERROR EN ACTIVIDAD MENSUAL DE DOCENTES ======"
        )
        print(error)
        print(
            "===================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Últimos registros
# ============================================================

def obtener_ultimas_participaciones_docentes(limite=10):
    """
    Obtiene los registros recientes con docente responsable.
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
            SELECT
                id,

                COALESCE(
                    NULLIF(
                        TRIM(
                            docente_responsable
                        ),
                        ''
                    ),
                    'Sin docente'
                ) AS docente,

                COALESCE(
                    NULLIF(
                        TRIM(
                            laboratorio
                        ),
                        ''
                    ),
                    'Sin laboratorio'
                ) AS laboratorio,

                COALESCE(
                    NULLIF(
                        TRIM(
                            carrera
                        ),
                        ''
                    ),
                    'Sin carrera'
                ) AS carrera,

                COALESCE(
                    NULLIF(
                        TRIM(
                            asignatura
                        ),
                        ''
                    ),
                    'Sin asignatura'
                ) AS asignatura,

                COALESCE(
                    NULLIF(
                        TRIM(
                            tema_practica
                        ),
                        ''
                    ),
                    'Sin tema'
                ) AS tema,

                fecha_practica,

                CASE
                    WHEN TRIM(
                        COALESCE(
                            pdf_url,
                            ''
                        )
                    ) <> ''
                    THEN TRUE
                    ELSE FALSE
                END AS tiene_pdf

            FROM laboratorios

            WHERE TRIM(
                COALESCE(
                    docente_responsable,
                    ''
                )
            ) <> ''

            ORDER BY
                fecha_practica DESC NULLS LAST,
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
                    "docente": _normalizar_texto(
                        fila[1],
                        "Sin docente",
                    ),
                    "laboratorio": _normalizar_texto(
                        fila[2],
                        "Sin laboratorio",
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
                    "fecha": fila[6],
                    "tiene_pdf": bool(
                        fila[7]
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n==== ERROR AL OBTENER PARTICIPACIONES RECIENTES ===="
        )
        print(error)
        print(
            "===================================================\n"
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

def obtener_dashboard_docentes():
    """
    Centraliza todas las consultas necesarias para construir el
    panel de docentes.
    """

    return {
        "resumen": obtener_resumen_docentes(),

        "mas_activos": obtener_docentes_mas_activos(
            limite=10
        ),

        "pdfs_por_docente": obtener_pdfs_por_docente(
            limite=10
        ),

        "carreras_por_docente": obtener_carreras_por_docente(
            limite=10
        ),

        "laboratorios_por_docente": (
            obtener_laboratorios_por_docente(
                limite=10
            )
        ),

        "actividad_mensual": obtener_actividad_docentes_por_mes(
            meses=12
        ),

        "ultimos": obtener_ultimas_participaciones_docentes(
            limite=10
        ),
    }


# ============================================================
# Prueba individual
# ============================================================

if __name__ == "__main__":
    datos = obtener_dashboard_docentes()

    print(
        "\n========== DASHBOARD DE DOCENTES ==========\n"
    )

    print("RESUMEN:")
    print(datos["resumen"])

    print("\nDOCENTES MÁS ACTIVOS:")

    for docente in datos["mas_activos"]:
        print(docente)

    print("\nPDFS POR DOCENTE:")

    for docente in datos["pdfs_por_docente"]:
        print(docente)

    print("\nCARRERAS POR DOCENTE:")

    for docente in datos["carreras_por_docente"]:
        print(docente)

    print("\nLABORATORIOS POR DOCENTE:")

    for docente in datos["laboratorios_por_docente"]:
        print(docente)

    print("\nACTIVIDAD MENSUAL:")

    for mes in datos["actividad_mensual"]:
        print(mes)

    print("\nÚLTIMAS PARTICIPACIONES:")

    for registro in datos["ultimos"]:
        print(registro)
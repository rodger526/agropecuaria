from database.conexion import obtener_conexion


# ============================================================
# Utilidades internas
# ============================================================

def _convertir_cantidad_sql(alias="lr"):
    """
    Convierte la columna cantidad a un valor numérico.

    Permite interpretar cantidades almacenadas como:

        2
        2.5
        2,5
        10 ml
        3 litros

    Extrae únicamente la parte numérica del contenido.
    """

    return f"""
        CASE
            WHEN NULLIF(
                REGEXP_REPLACE(
                    REPLACE(
                        COALESCE({alias}.cantidad::TEXT, ''),
                        ',',
                        '.'
                    ),
                    '[^0-9.]',
                    '',
                    'g'
                ),
                ''
            ) IS NULL
            THEN 0

            ELSE NULLIF(
                REGEXP_REPLACE(
                    REPLACE(
                        COALESCE({alias}.cantidad::TEXT, ''),
                        ',',
                        '.'
                    ),
                    '[^0-9.]',
                    '',
                    'g'
                ),
                ''
            )::NUMERIC
        END
    """


def _normalizar_numero(valor):
    """
    Convierte Decimal, int, float o None en float.
    """

    try:
        return float(valor or 0)

    except (TypeError, ValueError):
        return 0.0


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


# ============================================================
# Resumen principal
# ============================================================

def obtener_resumen_reactivos():
    """
    Obtiene los indicadores principales de reactivos.

    Devuelve:

        total_registros
        reactivos_diferentes
        cantidad_acumulada
        laboratorios_con_reactivos
        reactivo_mas_utilizado
        cantidad_reactivo_mas_utilizado
    """

    conexion = None
    cursor = None

    resultado = {
        "total_registros": 0,
        "reactivos_diferentes": 0,
        "cantidad_acumulada": 0.0,
        "laboratorios_con_reactivos": 0,
        "reactivo_mas_utilizado": "Sin registros",
        "cantidad_reactivo_mas_utilizado": 0.0,
    }

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cantidad_sql = _convertir_cantidad_sql("lr")

        cursor.execute(
            f"""
            SELECT
                COUNT(*) AS total_registros,

                COUNT(
                    DISTINCT LOWER(
                        TRIM(
                            COALESCE(lr.nombre, '')
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(lr.nombre, '')
                    ) <> ''
                ) AS reactivos_diferentes,

                COALESCE(
                    SUM(
                        {cantidad_sql}
                    ),
                    0
                ) AS cantidad_acumulada,

                COUNT(
                    DISTINCT lr.laboratorio_id
                ) AS laboratorios_con_reactivos

            FROM laboratorio_reactivos lr
            """
        )

        fila = cursor.fetchone()

        if fila:
            resultado["total_registros"] = int(
                fila[0] or 0
            )

            resultado["reactivos_diferentes"] = int(
                fila[1] or 0
            )

            resultado["cantidad_acumulada"] = _normalizar_numero(
                fila[2]
            )

            resultado["laboratorios_con_reactivos"] = int(
                fila[3] or 0
            )

        cursor.execute(
            f"""
            SELECT
                INITCAP(
                    LOWER(
                        TRIM(lr.nombre)
                    )
                ) AS reactivo,

                COALESCE(
                    SUM(
                        {cantidad_sql}
                    ),
                    0
                ) AS cantidad_total

            FROM laboratorio_reactivos lr

            WHERE TRIM(
                COALESCE(lr.nombre, '')
            ) <> ''

            GROUP BY
                LOWER(
                    TRIM(lr.nombre)
                )

            ORDER BY
                cantidad_total DESC,
                reactivo ASC

            LIMIT 1
            """
        )

        fila_reactivo = cursor.fetchone()

        if fila_reactivo:
            resultado["reactivo_mas_utilizado"] = (
                fila_reactivo[0]
                or "Sin registros"
            )

            resultado["cantidad_reactivo_mas_utilizado"] = (
                _normalizar_numero(
                    fila_reactivo[1]
                )
            )

        return resultado

    except Exception as error:
        print(
            "\n========== ERROR EN RESUMEN DE REACTIVOS =========="
        )
        print(error)
        print(
            "===================================================\n"
        )

        return resultado

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Reactivos más utilizados
# ============================================================

def obtener_reactivos_mas_utilizados(limite=10):
    """
    Obtiene los reactivos con mayor cantidad acumulada.
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

        cantidad_sql = _convertir_cantidad_sql("lr")

        cursor.execute(
            f"""
            SELECT
                INITCAP(
                    LOWER(
                        TRIM(lr.nombre)
                    )
                ) AS reactivo,

                COALESCE(
                    SUM(
                        {cantidad_sql}
                    ),
                    0
                ) AS cantidad_total,

                COUNT(*) AS numero_registros

            FROM laboratorio_reactivos lr

            WHERE TRIM(
                COALESCE(lr.nombre, '')
            ) <> ''

            GROUP BY
                LOWER(
                    TRIM(lr.nombre)
                )

            ORDER BY
                cantidad_total DESC,
                numero_registros DESC,
                reactivo ASC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "reactivo": fila[0] or "Sin nombre",
                    "cantidad": _normalizar_numero(
                        fila[1]
                    ),
                    "registros": int(
                        fila[2] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n===== ERROR AL OBTENER REACTIVOS MÁS UTILIZADOS ====="
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
# Reactivos por laboratorio
# ============================================================

def obtener_reactivos_por_laboratorio(limite=10):
    """
    Obtiene la cantidad acumulada de reactivos por laboratorio.
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

        cantidad_sql = _convertir_cantidad_sql("lr")

        cursor.execute(
            f"""
            SELECT
                COALESCE(
                    NULLIF(
                        TRIM(l.laboratorio),
                        ''
                    ),
                    'Sin laboratorio'
                ) AS laboratorio,

                COALESCE(
                    SUM(
                        {cantidad_sql}
                    ),
                    0
                ) AS cantidad_total,

                COUNT(
                    DISTINCT LOWER(
                        TRIM(
                            COALESCE(lr.nombre, '')
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(lr.nombre, '')
                    ) <> ''
                ) AS reactivos_diferentes,

                COUNT(lr.*) AS numero_registros

            FROM laboratorio_reactivos lr

            INNER JOIN laboratorios l
                ON l.id = lr.laboratorio_id

            GROUP BY
                COALESCE(
                    NULLIF(
                        TRIM(l.laboratorio),
                        ''
                    ),
                    'Sin laboratorio'
                )

            ORDER BY
                cantidad_total DESC,
                numero_registros DESC,
                laboratorio ASC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "laboratorio": fila[0],
                    "cantidad": _normalizar_numero(
                        fila[1]
                    ),
                    "reactivos_diferentes": int(
                        fila[2] or 0
                    ),
                    "registros": int(
                        fila[3] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n===== ERROR AL OBTENER REACTIVOS POR LABORATORIO ====="
        )
        print(error)
        print(
            "======================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Reactivos por carrera
# ============================================================

def obtener_reactivos_por_carrera(limite=10):
    """
    Obtiene las cantidades acumuladas de reactivos por carrera.
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

        cantidad_sql = _convertir_cantidad_sql("lr")

        cursor.execute(
            f"""
            SELECT
                COALESCE(
                    NULLIF(
                        TRIM(l.carrera),
                        ''
                    ),
                    'Sin carrera'
                ) AS carrera,

                COALESCE(
                    SUM(
                        {cantidad_sql}
                    ),
                    0
                ) AS cantidad_total,

                COUNT(
                    DISTINCT LOWER(
                        TRIM(
                            COALESCE(lr.nombre, '')
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(lr.nombre, '')
                    ) <> ''
                ) AS reactivos_diferentes,

                COUNT(
                    DISTINCT lr.laboratorio_id
                ) AS practicas_laboratorio

            FROM laboratorio_reactivos lr

            INNER JOIN laboratorios l
                ON l.id = lr.laboratorio_id

            GROUP BY
                COALESCE(
                    NULLIF(
                        TRIM(l.carrera),
                        ''
                    ),
                    'Sin carrera'
                )

            ORDER BY
                cantidad_total DESC,
                reactivos_diferentes DESC,
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
                    "carrera": fila[0],
                    "cantidad": _normalizar_numero(
                        fila[1]
                    ),
                    "reactivos_diferentes": int(
                        fila[2] or 0
                    ),
                    "laboratorios": int(
                        fila[3] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n======= ERROR AL OBTENER REACTIVOS POR CARRERA ======="
        )
        print(error)
        print(
            "======================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Reactivos por mes
# ============================================================

def obtener_reactivos_por_mes(meses=12):
    """
    Obtiene la actividad mensual de reactivos utilizando
    laboratorios.fecha_practica.
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

        cantidad_sql = _convertir_cantidad_sql("lr")

        cursor.execute(
            f"""
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

            reactivos_mes AS (
                SELECT
                    DATE_TRUNC(
                        'month',
                        l.fecha_practica
                    )::DATE AS mes,

                    COALESCE(
                        SUM(
                            {cantidad_sql}
                        ),
                        0
                    ) AS cantidad_total,

                    COUNT(lr.*) AS numero_registros,

                    COUNT(
                        DISTINCT LOWER(
                            TRIM(
                                COALESCE(lr.nombre, '')
                            )
                        )
                    ) FILTER (
                        WHERE TRIM(
                            COALESCE(lr.nombre, '')
                        ) <> ''
                    ) AS reactivos_diferentes

                FROM laboratorio_reactivos lr

                INNER JOIN laboratorios l
                    ON l.id = lr.laboratorio_id

                WHERE l.fecha_practica IS NOT NULL

                GROUP BY
                    DATE_TRUNC(
                        'month',
                        l.fecha_practica
                    )::DATE
            )

            SELECT
                m.mes,

                TO_CHAR(
                    m.mes,
                    'Mon YYYY'
                ) AS nombre_mes,

                COALESCE(
                    rm.cantidad_total,
                    0
                ) AS cantidad_total,

                COALESCE(
                    rm.numero_registros,
                    0
                ) AS numero_registros,

                COALESCE(
                    rm.reactivos_diferentes,
                    0
                ) AS reactivos_diferentes

            FROM meses m

            LEFT JOIN reactivos_mes rm
                ON rm.mes = m.mes

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
                    "cantidad": _normalizar_numero(
                        fila[2]
                    ),
                    "registros": int(
                        fila[3] or 0
                    ),
                    "reactivos_diferentes": int(
                        fila[4] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n========= ERROR AL OBTENER REACTIVOS POR MES ========="
        )
        print(error)
        print(
            "======================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Reactivo más frecuente
# ============================================================

def obtener_reactivo_mas_frecuente():
    """
    Obtiene el reactivo que aparece en más registros.
    """

    conexion = None
    cursor = None

    resultado = {
        "reactivo": "Sin registros",
        "registros": 0,
        "cantidad": 0.0,
    }

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cantidad_sql = _convertir_cantidad_sql("lr")

        cursor.execute(
            f"""
            SELECT
                INITCAP(
                    LOWER(
                        TRIM(lr.nombre)
                    )
                ) AS reactivo,

                COUNT(*) AS numero_registros,

                COALESCE(
                    SUM(
                        {cantidad_sql}
                    ),
                    0
                ) AS cantidad_total

            FROM laboratorio_reactivos lr

            WHERE TRIM(
                COALESCE(lr.nombre, '')
            ) <> ''

            GROUP BY
                LOWER(
                    TRIM(lr.nombre)
                )

            ORDER BY
                numero_registros DESC,
                cantidad_total DESC,
                reactivo ASC

            LIMIT 1
            """
        )

        fila = cursor.fetchone()

        if fila:
            resultado["reactivo"] = (
                fila[0]
                or "Sin registros"
            )

            resultado["registros"] = int(
                fila[1] or 0
            )

            resultado["cantidad"] = _normalizar_numero(
                fila[2]
            )

        return resultado

    except Exception as error:
        print(
            "\n======= ERROR AL OBTENER REACTIVO MÁS FRECUENTE ======="
        )
        print(error)
        print(
            "=======================================================\n"
        )

        return resultado

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Últimos reactivos registrados
# ============================================================

def obtener_ultimos_reactivos(limite=10):
    """
    Obtiene los reactivos registrados recientemente.
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

        cantidad_sql = _convertir_cantidad_sql("lr")

        cursor.execute(
            f"""
            SELECT
                lr.id,

                COALESCE(
                    NULLIF(
                        TRIM(lr.nombre),
                        ''
                    ),
                    'Sin nombre'
                ) AS reactivo,

                COALESCE(
                    {cantidad_sql},
                    0
                ) AS cantidad,

                COALESCE(
                    NULLIF(
                        TRIM(l.laboratorio),
                        ''
                    ),
                    'Sin laboratorio'
                ) AS laboratorio,

                COALESCE(
                    NULLIF(
                        TRIM(l.carrera),
                        ''
                    ),
                    'Sin carrera'
                ) AS carrera,

                COALESCE(
                    NULLIF(
                        TRIM(l.asignatura),
                        ''
                    ),
                    'Sin asignatura'
                ) AS asignatura,

                l.fecha_practica

            FROM laboratorio_reactivos lr

            INNER JOIN laboratorios l
                ON l.id = lr.laboratorio_id

            ORDER BY
                l.fecha_practica DESC NULLS LAST,
                lr.id DESC

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
                    "reactivo": fila[1],
                    "cantidad": _normalizar_numero(
                        fila[2]
                    ),
                    "laboratorio": fila[3],
                    "carrera": fila[4],
                    "asignatura": fila[5],
                    "fecha": fila[6],
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n======== ERROR AL OBTENER ÚLTIMOS REACTIVOS ========="
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
# Dashboard completo
# ============================================================

def obtener_dashboard_reactivos():
    """
    Centraliza todas las consultas necesarias para la vista.
    """

    return {
        "resumen": obtener_resumen_reactivos(),

        "mas_utilizados": obtener_reactivos_mas_utilizados(
            limite=10
        ),

        "por_laboratorio": obtener_reactivos_por_laboratorio(
            limite=10
        ),

        "por_carrera": obtener_reactivos_por_carrera(
            limite=10
        ),

        "por_mes": obtener_reactivos_por_mes(
            meses=12
        ),

        "ultimos": obtener_ultimos_reactivos(
            limite=10
        ),

        "mas_frecuente": obtener_reactivo_mas_frecuente(),
    }


# ============================================================
# Prueba individual
# ============================================================

if __name__ == "__main__":
    datos = obtener_dashboard_reactivos()

    print(
        "\n========== DASHBOARD DE REACTIVOS ==========\n"
    )

    print(
        "RESUMEN:"
    )
    print(
        datos["resumen"]
    )

    print(
        "\nREACTIVOS MÁS UTILIZADOS:"
    )

    for reactivo in datos["mas_utilizados"]:
        print(
            reactivo
        )

    print(
        "\nREACTIVOS POR LABORATORIO:"
    )

    for laboratorio in datos["por_laboratorio"]:
        print(
            laboratorio
        )

    print(
        "\nREACTIVOS POR CARRERA:"
    )

    for carrera in datos["por_carrera"]:
        print(
            carrera
        )

    print(
        "\nREACTIVOS POR MES:"
    )

    for mes in datos["por_mes"]:
        print(
            mes
        )

    print(
        "\nÚLTIMOS REACTIVOS:"
    )

    for reactivo in datos["ultimos"]:
        print(
            reactivo
        )

    print(
        "\nREACTIVO MÁS FRECUENTE:"
    )
    print(
        datos["mas_frecuente"]
    )
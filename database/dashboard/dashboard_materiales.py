from database.conexion import obtener_conexion


# ============================================================
# Utilidades internas
# ============================================================

def _convertir_cantidad_sql(alias="lm"):
    """
    Convierte la columna cantidad a número.

    La tabla laboratorio_materiales puede guardar cantidades
    como texto, por ejemplo:

        "2"
        "2.5"
        "10 unidades"
        "3 cajas"

    Esta expresión extrae únicamente la parte numérica.
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
    Convierte valores Decimal, int, float o None a float.
    """

    try:
        return float(valor or 0)
    except (TypeError, ValueError):
        return 0.0


def _cerrar_recursos(cursor, conexion):
    """
    Cierra cursor y conexión de forma segura.
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

def obtener_resumen_materiales():
    """
    Obtiene los indicadores principales de materiales.

    Devuelve un diccionario con:

        total_registros:
            Cantidad de filas registradas.

        materiales_diferentes:
            Cantidad de nombres diferentes.

        cantidad_acumulada:
            Suma de las cantidades registradas.

        laboratorios_con_materiales:
            Número de registros de laboratorio que tienen materiales.

        material_mas_utilizado:
            Nombre del material con mayor cantidad acumulada.

        cantidad_material_mas_utilizado:
            Cantidad acumulada del material más utilizado.
    """

    conexion = None
    cursor = None

    resultado = {
        "total_registros": 0,
        "materiales_diferentes": 0,
        "cantidad_acumulada": 0.0,
        "laboratorios_con_materiales": 0,
        "material_mas_utilizado": "Sin registros",
        "cantidad_material_mas_utilizado": 0.0,
    }

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cantidad_sql = _convertir_cantidad_sql("lm")

        cursor.execute(
            f"""
            SELECT
                COUNT(*) AS total_registros,

                COUNT(
                    DISTINCT LOWER(
                        TRIM(
                            COALESCE(lm.nombre, '')
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(lm.nombre, '')
                    ) <> ''
                ) AS materiales_diferentes,

                COALESCE(
                    SUM(
                        {cantidad_sql}
                    ),
                    0
                ) AS cantidad_acumulada,

                COUNT(
                    DISTINCT lm.laboratorio_id
                ) AS laboratorios_con_materiales

            FROM laboratorio_materiales lm
            """
        )

        fila = cursor.fetchone()

        if fila:
            resultado["total_registros"] = int(
                fila[0] or 0
            )

            resultado["materiales_diferentes"] = int(
                fila[1] or 0
            )

            resultado["cantidad_acumulada"] = _normalizar_numero(
                fila[2]
            )

            resultado["laboratorios_con_materiales"] = int(
                fila[3] or 0
            )

        cursor.execute(
            f"""
            SELECT
                INITCAP(
                    LOWER(
                        TRIM(lm.nombre)
                    )
                ) AS material,

                COALESCE(
                    SUM(
                        {cantidad_sql}
                    ),
                    0
                ) AS cantidad_total

            FROM laboratorio_materiales lm

            WHERE TRIM(
                COALESCE(lm.nombre, '')
            ) <> ''

            GROUP BY
                LOWER(
                    TRIM(lm.nombre)
                )

            ORDER BY
                cantidad_total DESC,
                material ASC

            LIMIT 1
            """
        )

        fila_material = cursor.fetchone()

        if fila_material:
            resultado["material_mas_utilizado"] = (
                fila_material[0]
                or "Sin registros"
            )

            resultado["cantidad_material_mas_utilizado"] = (
                _normalizar_numero(
                    fila_material[1]
                )
            )

        return resultado

    except Exception as error:
        print(
            "\n========== ERROR EN RESUMEN DE MATERIALES =========="
        )
        print(error)
        print(
            "====================================================\n"
        )

        return resultado

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Materiales más utilizados
# ============================================================

def obtener_materiales_mas_utilizados(limite=10):
    """
    Devuelve los materiales ordenados por cantidad acumulada.

    Resultado:

        [
            {
                "material": "Microscopio",
                "cantidad": 25.0,
                "registros": 4
            }
        ]
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

        cantidad_sql = _convertir_cantidad_sql("lm")

        cursor.execute(
            f"""
            SELECT
                INITCAP(
                    LOWER(
                        TRIM(lm.nombre)
                    )
                ) AS material,

                COALESCE(
                    SUM(
                        {cantidad_sql}
                    ),
                    0
                ) AS cantidad_total,

                COUNT(*) AS numero_registros

            FROM laboratorio_materiales lm

            WHERE TRIM(
                COALESCE(lm.nombre, '')
            ) <> ''

            GROUP BY
                LOWER(
                    TRIM(lm.nombre)
                )

            ORDER BY
                cantidad_total DESC,
                numero_registros DESC,
                material ASC

            LIMIT %s
            """,
            (
                limite,
            ),
        )

        for fila in cursor.fetchall():
            resultados.append(
                {
                    "material": fila[0] or "Sin nombre",
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
            "\n===== ERROR AL OBTENER MATERIALES MÁS UTILIZADOS ====="
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
# Materiales por laboratorio
# ============================================================

def obtener_materiales_por_laboratorio(limite=10):
    """
    Obtiene la cantidad acumulada de materiales agrupada por
    laboratorio.

    Resultado:

        [
            {
                "laboratorio": "Laboratorio de Química",
                "cantidad": 40.0,
                "materiales_diferentes": 8,
                "registros": 15
            }
        ]
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

        cantidad_sql = _convertir_cantidad_sql("lm")

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
                            COALESCE(lm.nombre, '')
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(lm.nombre, '')
                    ) <> ''
                ) AS materiales_diferentes,

                COUNT(lm.*) AS numero_registros

            FROM laboratorio_materiales lm

            INNER JOIN laboratorios l
                ON l.id = lm.laboratorio_id

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
                    "materiales_diferentes": int(
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
            "\n===== ERROR AL OBTENER MATERIALES POR LABORATORIO ====="
        )
        print(error)
        print(
            "=======================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Materiales por carrera
# ============================================================

def obtener_materiales_por_carrera(limite=10):
    """
    Obtiene las cantidades de materiales agrupadas por carrera.
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

        cantidad_sql = _convertir_cantidad_sql("lm")

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
                            COALESCE(lm.nombre, '')
                        )
                    )
                ) FILTER (
                    WHERE TRIM(
                        COALESCE(lm.nombre, '')
                    ) <> ''
                ) AS materiales_diferentes,

                COUNT(
                    DISTINCT lm.laboratorio_id
                ) AS practicas_laboratorio

            FROM laboratorio_materiales lm

            INNER JOIN laboratorios l
                ON l.id = lm.laboratorio_id

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
                materiales_diferentes DESC,
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
                    "materiales_diferentes": int(
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
            "\n======= ERROR AL OBTENER MATERIALES POR CARRERA ======="
        )
        print(error)
        print(
            "=======================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Materiales registrados por mes
# ============================================================

def obtener_materiales_por_mes(meses=12):
    """
    Obtiene las cantidades registradas durante los últimos meses.

    Utiliza laboratorios.fecha_practica.

    Resultado:

        [
            {
                "fecha": date,
                "mes": "Jul 2026",
                "cantidad": 20.0,
                "registros": 5,
                "materiales_diferentes": 3
            }
        ]
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

        cantidad_sql = _convertir_cantidad_sql("lm")

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

            materiales_mes AS (
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

                    COUNT(lm.*) AS numero_registros,

                    COUNT(
                        DISTINCT LOWER(
                            TRIM(
                                COALESCE(lm.nombre, '')
                            )
                        )
                    ) FILTER (
                        WHERE TRIM(
                            COALESCE(lm.nombre, '')
                        ) <> ''
                    ) AS materiales_diferentes

                FROM laboratorio_materiales lm

                INNER JOIN laboratorios l
                    ON l.id = lm.laboratorio_id

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
                    mm.cantidad_total,
                    0
                ) AS cantidad_total,

                COALESCE(
                    mm.numero_registros,
                    0
                ) AS numero_registros,

                COALESCE(
                    mm.materiales_diferentes,
                    0
                ) AS materiales_diferentes

            FROM meses m

            LEFT JOIN materiales_mes mm
                ON mm.mes = m.mes

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
                    "materiales_diferentes": int(
                        fila[4] or 0
                    ),
                }
            )

        return resultados

    except Exception as error:
        print(
            "\n========= ERROR AL OBTENER MATERIALES POR MES ========="
        )
        print(error)
        print(
            "=======================================================\n"
        )

        return resultados

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Últimos materiales registrados
# ============================================================

def obtener_ultimos_materiales(limite=10):
    """
    Obtiene los últimos materiales registrados junto con los
    datos del laboratorio al que pertenecen.
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

        cantidad_sql = _convertir_cantidad_sql("lm")

        cursor.execute(
            f"""
            SELECT
                lm.id,

                COALESCE(
                    NULLIF(
                        TRIM(lm.nombre),
                        ''
                    ),
                    'Sin nombre'
                ) AS material,

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

            FROM laboratorio_materiales lm

            INNER JOIN laboratorios l
                ON l.id = lm.laboratorio_id

            ORDER BY
                l.fecha_practica DESC NULLS LAST,
                lm.id DESC

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
                    "material": fila[1],
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
            "\n======== ERROR AL OBTENER ÚLTIMOS MATERIALES ========="
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
# Material por mayor frecuencia
# ============================================================

def obtener_material_mas_frecuente():
    """
    Obtiene el material que aparece en más registros,
    independientemente de su cantidad acumulada.
    """

    conexion = None
    cursor = None

    resultado = {
        "material": "Sin registros",
        "registros": 0,
        "cantidad": 0.0,
    }

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cantidad_sql = _convertir_cantidad_sql("lm")

        cursor.execute(
            f"""
            SELECT
                INITCAP(
                    LOWER(
                        TRIM(lm.nombre)
                    )
                ) AS material,

                COUNT(*) AS numero_registros,

                COALESCE(
                    SUM(
                        {cantidad_sql}
                    ),
                    0
                ) AS cantidad_total

            FROM laboratorio_materiales lm

            WHERE TRIM(
                COALESCE(lm.nombre, '')
            ) <> ''

            GROUP BY
                LOWER(
                    TRIM(lm.nombre)
                )

            ORDER BY
                numero_registros DESC,
                cantidad_total DESC,
                material ASC

            LIMIT 1
            """
        )

        fila = cursor.fetchone()

        if fila:
            resultado["material"] = (
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
            "\n======= ERROR AL OBTENER MATERIAL MÁS FRECUENTE ======="
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
# Función general para el dashboard
# ============================================================

def obtener_dashboard_materiales():
    """
    Obtiene todos los datos necesarios para construir el panel
    gráfico de materiales.

    Esta función centraliza todas las consultas para que la vista
    pueda actualizarse con una sola llamada.
    """

    return {
        "resumen": obtener_resumen_materiales(),

        "mas_utilizados": obtener_materiales_mas_utilizados(
            limite=10
        ),

        "por_laboratorio": obtener_materiales_por_laboratorio(
            limite=10
        ),

        "por_carrera": obtener_materiales_por_carrera(
            limite=10
        ),

        "por_mes": obtener_materiales_por_mes(
            meses=12
        ),

        "ultimos": obtener_ultimos_materiales(
            limite=10
        ),

        "mas_frecuente": obtener_material_mas_frecuente(),
    }


# ============================================================
# Prueba individual
# ============================================================

if __name__ == "__main__":
    datos = obtener_dashboard_materiales()

    print(
        "\n========== DASHBOARD DE MATERIALES ==========\n"
    )

    print(
        "RESUMEN:"
    )
    print(
        datos["resumen"]
    )

    print(
        "\nMATERIALES MÁS UTILIZADOS:"
    )

    for material in datos["mas_utilizados"]:
        print(
            material
        )

    print(
        "\nMATERIALES POR LABORATORIO:"
    )

    for laboratorio in datos["por_laboratorio"]:
        print(
            laboratorio
        )

    print(
        "\nMATERIALES POR CARRERA:"
    )

    for carrera in datos["por_carrera"]:
        print(
            carrera
        )

    print(
        "\nMATERIALES POR MES:"
    )

    for mes in datos["por_mes"]:
        print(
            mes
        )

    print(
        "\nÚLTIMOS MATERIALES:"
    )

    for material in datos["ultimos"]:
        print(
            material
        )

    print(
        "\nMATERIAL MÁS FRECUENTE:"
    )
    print(
        datos["mas_frecuente"]
    )
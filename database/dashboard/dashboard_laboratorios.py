from datetime import date
from decimal import Decimal, InvalidOperation
import re

from database.conexion import obtener_conexion


TABLA_LABORATORIOS = "laboratorios"
TABLA_REACTIVOS = "laboratorio_reactivos"
TABLA_MATERIALES = "laboratorio_materiales"


# ============================================================
# Funciones internas
# ============================================================

def _cerrar_recursos(cursor=None, conexion=None):
    if cursor is not None:
        try:
            cursor.close()
        except Exception:
            pass

    if conexion is not None:
        try:
            conexion.close()
        except Exception:
            pass


def _tabla_existe(cursor, tabla):
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = %s
        )
        """,
        (tabla,),
    )

    resultado = cursor.fetchone()

    return bool(resultado and resultado[0])


def _obtener_columnas(cursor, tabla):
    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
        """,
        (tabla,),
    )

    return {
        fila[0]
        for fila in cursor.fetchall()
    }


def _primera_columna(columnas, opciones):
    for opcion in opciones:
        if opcion in columnas:
            return opcion

    return None


def _expresion_fecha(columnas, alias=None):
    prefijo = f"{alias}." if alias else ""

    opciones = [
        "fecha_creacion",
        "fecha_registro",
        "created_at",
        "fecha_practica",
        "fecha",
    ]

    disponibles = [
        f"{prefijo}{columna}"
        for columna in opciones
        if columna in columnas
    ]

    if not disponibles:
        return None

    if len(disponibles) == 1:
        return disponibles[0]

    return f"COALESCE({', '.join(disponibles)})"


def _normalizar_texto(valor):
    return str(valor or "").strip()


def _convertir_decimal(valor):
    if valor is None:
        return Decimal("0")

    if isinstance(valor, Decimal):
        return valor

    if isinstance(valor, (int, float)):
        try:
            return Decimal(str(valor))
        except InvalidOperation:
            return Decimal("0")

    texto = str(valor).strip().replace(",", ".")

    coincidencia = re.search(
        r"-?\d+(?:\.\d+)?",
        texto,
    )

    if not coincidencia:
        return Decimal("0")

    try:
        return Decimal(coincidencia.group())
    except InvalidOperation:
        return Decimal("0")


def _normalizar_numero(valor):
    numero = _convertir_decimal(valor)

    if numero == numero.to_integral_value():
        return int(numero)

    return float(round(numero, 2))


def _agregar_filtros(
    condiciones,
    parametros,
    columnas,
    fecha_sql,
    anio=None,
    carrera=None,
):
    if anio is not None and fecha_sql is not None:
        condiciones.append(
            f"""
            EXTRACT(
                YEAR FROM {fecha_sql}::timestamp
            )::integer = %s
            """
        )

        parametros.append(int(anio))

    columna_carrera = _primera_columna(
        columnas,
        [
            "carrera",
            "nombre_carrera",
        ],
    )

    if (
        carrera
        and carrera != "Todas"
        and columna_carrera is not None
    ):
        condiciones.append(
            f"""
            LOWER(TRIM({columna_carrera}::text))
            = LOWER(TRIM(%s))
            """
        )

        parametros.append(carrera)

    if not condiciones:
        return "", parametros

    return (
        " WHERE " + " AND ".join(condiciones),
        parametros,
    )


# ============================================================
# Resumen de laboratorios
# ============================================================

def obtener_resumen_laboratorios(
    anio=None,
    carrera=None,
):
    """
    Devuelve los indicadores principales del módulo.
    """

    conexion = None
    cursor = None

    resultado_vacio = {
        "total_laboratorios": 0,
        "con_pdf": 0,
        "sin_pdf": 0,
        "docentes": 0,
        "carreras": 0,
        "asignaturas": 0,
        "laboratorios_fisicos": 0,
        "registros_este_mes": 0,
    }

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        if not _tabla_existe(
            cursor,
            TABLA_LABORATORIOS,
        ):
            return resultado_vacio

        columnas = _obtener_columnas(
            cursor,
            TABLA_LABORATORIOS,
        )

        fecha_sql = _expresion_fecha(columnas)

        condiciones = []
        parametros = []

        where_sql, parametros = _agregar_filtros(
            condiciones,
            parametros,
            columnas,
            fecha_sql,
            anio,
            carrera,
        )

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {TABLA_LABORATORIOS}
            {where_sql}
            """,
            parametros,
        )

        total = int(cursor.fetchone()[0] or 0)

        columna_pdf = _primera_columna(
            columnas,
            [
                "pdf_url",
                "ruta_pdf",
                "pdf",
                "archivo_pdf",
            ],
        )

        con_pdf = 0

        if columna_pdf:
            condiciones_pdf = [
                f"{columna_pdf} IS NOT NULL",
                f"TRIM({columna_pdf}::text) <> ''",
            ]

            parametros_pdf = []

            where_pdf, parametros_pdf = _agregar_filtros(
                condiciones_pdf,
                parametros_pdf,
                columnas,
                fecha_sql,
                anio,
                carrera,
            )

            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM {TABLA_LABORATORIOS}
                {where_pdf}
                """,
                parametros_pdf,
            )

            con_pdf = int(cursor.fetchone()[0] or 0)

        sin_pdf = max(total - con_pdf, 0)

        columna_docente = _primera_columna(
            columnas,
            [
                "docente_responsable",
                "docente",
                "nombre_docente",
                "responsable",
            ],
        )

        docentes = _contar_distintos(
            cursor,
            columnas,
            fecha_sql,
            columna_docente,
            anio,
            carrera,
        )

        columna_carrera = _primera_columna(
            columnas,
            [
                "carrera",
                "nombre_carrera",
            ],
        )

        carreras = _contar_distintos(
            cursor,
            columnas,
            fecha_sql,
            columna_carrera,
            anio,
            carrera,
        )

        columna_asignatura = _primera_columna(
            columnas,
            [
                "asignatura",
                "materia",
            ],
        )

        asignaturas = _contar_distintos(
            cursor,
            columnas,
            fecha_sql,
            columna_asignatura,
            anio,
            carrera,
        )

        columna_laboratorio = _primera_columna(
            columnas,
            [
                "laboratorio",
                "nombre_laboratorio",
                "lugar_ejecucion",
            ],
        )

        laboratorios_fisicos = _contar_distintos(
            cursor,
            columnas,
            fecha_sql,
            columna_laboratorio,
            anio,
            carrera,
        )

        registros_este_mes = 0

        if fecha_sql:
            condiciones_mes = [
                f"""
                DATE_TRUNC(
                    'month',
                    {fecha_sql}::timestamp
                ) = DATE_TRUNC(
                    'month',
                    CURRENT_DATE
                )
                """
            ]

            parametros_mes = []

            where_mes, parametros_mes = _agregar_filtros(
                condiciones_mes,
                parametros_mes,
                columnas,
                fecha_sql,
                None,
                carrera,
            )

            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM {TABLA_LABORATORIOS}
                {where_mes}
                """,
                parametros_mes,
            )

            registros_este_mes = int(
                cursor.fetchone()[0] or 0
            )

        return {
            "total_laboratorios": total,
            "con_pdf": con_pdf,
            "sin_pdf": sin_pdf,
            "docentes": docentes,
            "carreras": carreras,
            "asignaturas": asignaturas,
            "laboratorios_fisicos": laboratorios_fisicos,
            "registros_este_mes": registros_este_mes,
        }

    except Exception as error:
        print(
            "\n========== ERROR RESUMEN LABORATORIOS =========="
        )
        print(error)
        print(
            "================================================\n"
        )

        return resultado_vacio

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


def _contar_distintos(
    cursor,
    columnas,
    fecha_sql,
    columna,
    anio=None,
    carrera=None,
):
    if columna is None:
        return 0

    condiciones = [
        f"{columna} IS NOT NULL",
        f"TRIM({columna}::text) <> ''",
    ]

    parametros = []

    where_sql, parametros = _agregar_filtros(
        condiciones,
        parametros,
        columnas,
        fecha_sql,
        anio,
        carrera,
    )

    cursor.execute(
        f"""
        SELECT COUNT(
            DISTINCT LOWER(
                TRIM({columna}::text)
            )
        )
        FROM {TABLA_LABORATORIOS}
        {where_sql}
        """,
        parametros,
    )

    return int(cursor.fetchone()[0] or 0)


# ============================================================
# Laboratorios por mes
# ============================================================

def obtener_laboratorios_por_mes(
    anio=None,
    carrera=None,
):
    nombres_meses = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    resultado = [
        {
            "numero_mes": numero,
            "mes": nombres_meses[numero - 1],
            "total": 0,
        }
        for numero in range(1, 13)
    ]

    conexion = None
    cursor = None

    try:
        if anio is None:
            anio = date.today().year

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        if not _tabla_existe(
            cursor,
            TABLA_LABORATORIOS,
        ):
            return resultado

        columnas = _obtener_columnas(
            cursor,
            TABLA_LABORATORIOS,
        )

        fecha_sql = _expresion_fecha(columnas)

        if fecha_sql is None:
            return resultado

        condiciones = []
        parametros = []

        where_sql, parametros = _agregar_filtros(
            condiciones,
            parametros,
            columnas,
            fecha_sql,
            anio,
            carrera,
        )

        cursor.execute(
            f"""
            SELECT
                EXTRACT(
                    MONTH FROM {fecha_sql}::timestamp
                )::integer AS numero_mes,
                COUNT(*) AS total

            FROM {TABLA_LABORATORIOS}

            {where_sql}

            GROUP BY numero_mes
            ORDER BY numero_mes
            """,
            parametros,
        )

        for numero_mes, total in cursor.fetchall():
            indice = int(numero_mes) - 1

            resultado[indice]["total"] = int(
                total or 0
            )

        return resultado

    except Exception as error:
        print(
            "\n========== ERROR LABORATORIOS POR MES =========="
        )
        print(error)
        print(
            "================================================\n"
        )

        return resultado

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Agrupaciones
# ============================================================

def _obtener_agrupacion(
    opciones_columna,
    nombre_clave,
    anio=None,
    carrera=None,
    limite=10,
):
    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        if not _tabla_existe(
            cursor,
            TABLA_LABORATORIOS,
        ):
            return []

        columnas = _obtener_columnas(
            cursor,
            TABLA_LABORATORIOS,
        )

        columna = _primera_columna(
            columnas,
            opciones_columna,
        )

        if columna is None:
            return []

        fecha_sql = _expresion_fecha(columnas)

        condiciones = [
            f"{columna} IS NOT NULL",
            f"TRIM({columna}::text) <> ''",
        ]

        parametros = []

        where_sql, parametros = _agregar_filtros(
            condiciones,
            parametros,
            columnas,
            fecha_sql,
            anio,
            carrera,
        )

        parametros.append(int(limite))

        cursor.execute(
            f"""
            SELECT
                TRIM({columna}::text) AS nombre,
                COUNT(*) AS total

            FROM {TABLA_LABORATORIOS}

            {where_sql}

            GROUP BY
                LOWER(TRIM({columna}::text)),
                TRIM({columna}::text)

            ORDER BY total DESC, nombre ASC

            LIMIT %s
            """,
            parametros,
        )

        return [
            {
                nombre_clave: fila[0],
                "total": int(fila[1] or 0),
            }
            for fila in cursor.fetchall()
        ]

    except Exception as error:
        print(
            "\n========== ERROR AGRUPANDO LABORATORIOS =========="
        )
        print(error)
        print(
            "=================================================\n"
        )

        return []

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


def obtener_laboratorios_mas_utilizados(
    anio=None,
    carrera=None,
    limite=10,
):
    return _obtener_agrupacion(
        opciones_columna=[
            "laboratorio",
            "nombre_laboratorio",
            "lugar_ejecucion",
        ],
        nombre_clave="laboratorio",
        anio=anio,
        carrera=carrera,
        limite=limite,
    )


def obtener_asignaturas_mas_utilizadas(
    anio=None,
    carrera=None,
    limite=10,
):
    return _obtener_agrupacion(
        opciones_columna=[
            "asignatura",
            "materia",
        ],
        nombre_clave="asignatura",
        anio=anio,
        carrera=carrera,
        limite=limite,
    )


def obtener_docentes_con_mas_registros(
    anio=None,
    carrera=None,
    limite=10,
):
    return _obtener_agrupacion(
        opciones_columna=[
            "docente_responsable",
            "docente",
            "nombre_docente",
            "responsable",
        ],
        nombre_clave="docente",
        anio=anio,
        carrera=carrera,
        limite=limite,
    )


def obtener_laboratorios_por_carrera(
    anio=None,
    limite=10,
):
    return _obtener_agrupacion(
        opciones_columna=[
            "carrera",
            "nombre_carrera",
        ],
        nombre_clave="carrera",
        anio=anio,
        carrera=None,
        limite=limite,
    )


# ============================================================
# Carreras disponibles
# ============================================================

def obtener_carreras_laboratorios():
    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        if not _tabla_existe(
            cursor,
            TABLA_LABORATORIOS,
        ):
            return ["Todas"]

        columnas = _obtener_columnas(
            cursor,
            TABLA_LABORATORIOS,
        )

        columna_carrera = _primera_columna(
            columnas,
            [
                "carrera",
                "nombre_carrera",
            ],
        )

        if columna_carrera is None:
            return ["Todas"]

        cursor.execute(
            f"""
            SELECT DISTINCT
                TRIM({columna_carrera}::text) AS carrera

            FROM {TABLA_LABORATORIOS}

            WHERE {columna_carrera} IS NOT NULL
              AND TRIM({columna_carrera}::text) <> ''

            ORDER BY carrera
            """
        )

        carreras = [
            fila[0]
            for fila in cursor.fetchall()
            if fila[0]
        ]

        return ["Todas"] + carreras

    except Exception as error:
        print(
            "\n========== ERROR CARRERAS LABORATORIOS =========="
        )
        print(error)
        print(
            "================================================\n"
        )

        return ["Todas"]

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Últimos laboratorios
# ============================================================

def obtener_ultimos_laboratorios(
    anio=None,
    carrera=None,
    limite=10,
):
    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        if not _tabla_existe(
            cursor,
            TABLA_LABORATORIOS,
        ):
            return []

        columnas = _obtener_columnas(
            cursor,
            TABLA_LABORATORIOS,
        )

        columna_id = _primera_columna(
            columnas,
            [
                "id",
                "laboratorio_id",
            ],
        )

        columna_codigo = _primera_columna(
            columnas,
            [
                "codigo",
                "codigo_laboratorio",
            ],
        )

        columna_carrera = _primera_columna(
            columnas,
            [
                "carrera",
                "nombre_carrera",
            ],
        )

        columna_laboratorio = _primera_columna(
            columnas,
            [
                "laboratorio",
                "nombre_laboratorio",
                "lugar_ejecucion",
            ],
        )

        columna_asignatura = _primera_columna(
            columnas,
            [
                "asignatura",
                "materia",
            ],
        )

        columna_docente = _primera_columna(
            columnas,
            [
                "docente_responsable",
                "docente",
                "nombre_docente",
                "responsable",
            ],
        )

        columna_pdf = _primera_columna(
            columnas,
            [
                "pdf_url",
                "ruta_pdf",
                "pdf",
                "archivo_pdf",
            ],
        )

        fecha_sql = _expresion_fecha(columnas)

        if columna_id is None or fecha_sql is None:
            return []

        condiciones = []
        parametros = []

        where_sql, parametros = _agregar_filtros(
            condiciones,
            parametros,
            columnas,
            fecha_sql,
            anio,
            carrera,
        )

        select_codigo = (
            f"{columna_codigo}::text"
            if columna_codigo
            else "''::text"
        )

        select_carrera = (
            f"{columna_carrera}::text"
            if columna_carrera
            else "''::text"
        )

        select_laboratorio = (
            f"{columna_laboratorio}::text"
            if columna_laboratorio
            else "''::text"
        )

        select_asignatura = (
            f"{columna_asignatura}::text"
            if columna_asignatura
            else "''::text"
        )

        select_docente = (
            f"{columna_docente}::text"
            if columna_docente
            else "''::text"
        )

        select_pdf = (
            f"{columna_pdf}::text"
            if columna_pdf
            else "''::text"
        )

        parametros.append(int(limite))

        cursor.execute(
            f"""
            SELECT
                {columna_id},
                {select_codigo},
                {fecha_sql} AS fecha,
                {select_carrera},
                {select_laboratorio},
                {select_asignatura},
                {select_docente},
                {select_pdf}

            FROM {TABLA_LABORATORIOS}

            {where_sql}

            ORDER BY
                {fecha_sql} DESC,
                {columna_id} DESC

            LIMIT %s
            """,
            parametros,
        )

        return [
            {
                "id": fila[0],
                "codigo": _normalizar_texto(fila[1]),
                "fecha": fila[2],
                "carrera": _normalizar_texto(fila[3]),
                "laboratorio": _normalizar_texto(fila[4]),
                "asignatura": _normalizar_texto(fila[5]),
                "docente": _normalizar_texto(fila[6]),
                "pdf_url": _normalizar_texto(fila[7]),
            }
            for fila in cursor.fetchall()
        ]

    except Exception as error:
        print(
            "\n========== ERROR ÚLTIMOS LABORATORIOS =========="
        )
        print(error)
        print(
            "================================================\n"
        )

        return []

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


# ============================================================
# Cantidades de materiales y reactivos
# ============================================================

def _sumar_tabla_detalle(
    tabla,
    anio=None,
    carrera=None,
):
    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        if not _tabla_existe(cursor, tabla):
            return 0

        columnas_detalle = _obtener_columnas(
            cursor,
            tabla,
        )

        columna_cantidad = _primera_columna(
            columnas_detalle,
            [
                "cantidad",
                "cantidad_utilizada",
                "cantidad_usada",
            ],
        )

        if columna_cantidad is None:
            return 0

        columna_relacion = _primera_columna(
            columnas_detalle,
            [
                "laboratorio_id",
                "id_laboratorio",
            ],
        )

        if (
            columna_relacion is None
            or not _tabla_existe(
                cursor,
                TABLA_LABORATORIOS,
            )
        ):
            cursor.execute(
                f"""
                SELECT {columna_cantidad}
                FROM {tabla}
                WHERE {columna_cantidad} IS NOT NULL
                """
            )

        else:
            columnas_laboratorio = _obtener_columnas(
                cursor,
                TABLA_LABORATORIOS,
            )

            columna_id = _primera_columna(
                columnas_laboratorio,
                [
                    "id",
                    "laboratorio_id",
                ],
            )

            fecha_sql = _expresion_fecha(
                columnas_laboratorio,
                alias="l",
            )

            if columna_id is None:
                return 0

            condiciones = [
                f"d.{columna_cantidad} IS NOT NULL"
            ]

            parametros = []

            if anio is not None and fecha_sql:
                condiciones.append(
                    f"""
                    EXTRACT(
                        YEAR FROM {fecha_sql}::timestamp
                    )::integer = %s
                    """
                )

                parametros.append(int(anio))

            columna_carrera = _primera_columna(
                columnas_laboratorio,
                [
                    "carrera",
                    "nombre_carrera",
                ],
            )

            if (
                carrera
                and carrera != "Todas"
                and columna_carrera
            ):
                condiciones.append(
                    f"""
                    LOWER(TRIM(l.{columna_carrera}::text))
                    = LOWER(TRIM(%s))
                    """
                )

                parametros.append(carrera)

            where_sql = (
                " WHERE " + " AND ".join(condiciones)
            )

            cursor.execute(
                f"""
                SELECT d.{columna_cantidad}

                FROM {tabla} d

                INNER JOIN {TABLA_LABORATORIOS} l
                    ON l.{columna_id} = d.{columna_relacion}

                {where_sql}
                """,
                parametros,
            )

        total = Decimal("0")

        for fila in cursor.fetchall():
            total += _convertir_decimal(fila[0])

        return _normalizar_numero(total)

    except Exception as error:
        print(
            f"\n========== ERROR SUMANDO {tabla} =========="
        )
        print(error)
        print(
            "============================================\n"
        )

        return 0

    finally:
        _cerrar_recursos(
            cursor,
            conexion,
        )


def obtener_total_reactivos_laboratorios(
    anio=None,
    carrera=None,
):
    return _sumar_tabla_detalle(
        TABLA_REACTIVOS,
        anio,
        carrera,
    )


def obtener_total_materiales_laboratorios(
    anio=None,
    carrera=None,
):
    return _sumar_tabla_detalle(
        TABLA_MATERIALES,
        anio,
        carrera,
    )


# ============================================================
# Prueba
# ============================================================

if __name__ == "__main__":
    anio_actual = date.today().year

    print(
        "\n========== RESUMEN LABORATORIOS =========="
    )
    print(
        obtener_resumen_laboratorios(
            anio=anio_actual
        )
    )

    print(
        "\n========== LABORATORIOS POR MES =========="
    )
    for registro in obtener_laboratorios_por_mes(
        anio=anio_actual
    ):
        print(registro)

    print(
        "\n========== LABORATORIOS MÁS UTILIZADOS =========="
    )
    for registro in obtener_laboratorios_mas_utilizados(
        anio=anio_actual
    ):
        print(registro)

    print(
        "\n========== ASIGNATURAS =========="
    )
    for registro in obtener_asignaturas_mas_utilizadas(
        anio=anio_actual
    ):
        print(registro)

    print(
        "\n========== DOCENTES =========="
    )
    for registro in obtener_docentes_con_mas_registros(
        anio=anio_actual
    ):
        print(registro)

    print(
        "\n========== CARRERAS =========="
    )
    for registro in obtener_laboratorios_por_carrera(
        anio=anio_actual
    ):
        print(registro)

    print(
        "\n========== CARRERAS DISPONIBLES =========="
    )
    print(
        obtener_carreras_laboratorios()
    )

    print(
        "\n========== ÚLTIMOS LABORATORIOS =========="
    )
    for registro in obtener_ultimos_laboratorios(
        anio=anio_actual
    ):
        print(registro)

    print(
        "\n========== TOTAL REACTIVOS =========="
    )
    print(
        obtener_total_reactivos_laboratorios(
            anio=anio_actual
        )
    )

    print(
        "\n========== TOTAL MATERIALES =========="
    )
    print(
        obtener_total_materiales_laboratorios(
            anio=anio_actual
        )
    )